"""LLM 翻译 API — 中→英翻译润色→中 + 对话历史持久化"""

import json
import logging
import uuid
from typing import Optional, AsyncIterator
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
import httpx

from backend.db.database import get_db
from backend.db.schema import AppSettings, TranslationHistory

logger = logging.getLogger(__name__)
router = APIRouter()


class HistoryMessage(BaseModel):
    role: str = Field(..., description="角色: user / assistant")
    content: str = Field(..., description="消息内容")


class TranslateRequest(BaseModel):
    text: str = Field(..., description="待翻译的中文文本", min_length=1)
    history: list[HistoryMessage] = Field(default_factory=list, description="对话历史消息")
    document_id: Optional[str] = Field(default=None, description="关联的文档 ID — 用于持久化翻译历史")


class TranslateResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[dict] = None


class TranslationRecord(BaseModel):
    id: str
    document_id: str
    role: str
    content: str
    usage_json: str = ""
    created_at: str = ""


async def get_llm_config(db: AsyncSession) -> dict:
    """从数据库读取 LLM 配置"""
    result = await db.execute(
        select(AppSettings).where(
            AppSettings.key.in_(["llm_api_url", "llm_api_key", "llm_model_name"])
        )
    )
    rows = {r.key: r.value for r in result.scalars().all()}
    return {
        "api_url": rows.get("llm_api_url", ""),
        "api_key": rows.get("llm_api_key", ""),
        "model_name": rows.get("llm_model_name", ""),
    }


TRANSLATE_SYSTEM_PROMPT = """You are a professional academic translator. Your task is a two-step process:

Step 1: Translate the user's Chinese text into polished, academic English suitable for a top-tier computer science / deep learning paper. Use the standard academic style seen in NeurIPS, ICML, CVPR, ACL papers. Ensure the English is idiomatic, precise, and natural — not a literal word-for-word translation.

Step 2: Translate the polished English back into Chinese. The Chinese should reflect the improved structure and clarity of the English version.

You MUST respond with a valid JSON object only, no markdown code blocks, no extra text:
{"english": "...polished English text...", "chinese": "...back-translated Chinese text..."}"""


# ═══════════════════════════════════════════════════════
#  翻译端点
# ═══════════════════════════════════════════════════════

@router.post("", response_model=TranslateResponse)
async def translate_text(
    body: TranslateRequest,
    db: AsyncSession = Depends(get_db),
):
    """中文 → 英文润色 → 回译中文"""
    config = await get_llm_config(db)
    if not config["api_url"]:
        raise HTTPException(status_code=400, detail="请先在设置中配置 LLM API 地址")
    if not config["api_key"]:
        raise HTTPException(status_code=400, detail="请先在设置中配置 LLM API Key")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config['api_key']}",
    }

    messages = [{"role": "system", "content": TRANSLATE_SYSTEM_PROMPT}]
    for h in body.history:
        messages.append({"role": h.role, "content": h.content})
    messages.append({"role": "user", "content": body.text})

    payload = {
        "model": config["model_name"] or "gpt-4o",
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 4096,
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            f"{config['api_url'].rstrip('/')}/v1/chat/completions",
            headers=headers,
            json=payload,
        )

    if resp.status_code != 200:
        logger.error(f"LLM API error: {resp.status_code} {resp.text[:500]}")
        raise HTTPException(
            status_code=502,
            detail=f"LLM API 返回错误 ({resp.status_code}): {resp.text[:300]}",
        )

    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})

    try:
        content = content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:]) if lines[0].startswith("```") else content
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
        result = json.loads(content)
    except json.JSONDecodeError:
        result = {"english": content, "chinese": ""}

    result["usage"] = usage

    # ── 持久化 ──
    await _save_history(body.document_id, body.text, result, usage)

    return TranslateResponse(data=result)


@router.post("/stream")
async def translate_text_stream(
    body: TranslateRequest,
    db: AsyncSession = Depends(get_db),
):
    """流式翻译 — SSE 逐 token 返回"""
    config = await get_llm_config(db)
    if not config["api_url"]:
        raise HTTPException(status_code=400, detail="请先在设置中配置 LLM API 地址")
    if not config["api_key"]:
        raise HTTPException(status_code=400, detail="请先在设置中配置 LLM API Key")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config['api_key']}",
    }

    messages = [{"role": "system", "content": TRANSLATE_SYSTEM_PROMPT}]
    for h in body.history:
        messages.append({"role": h.role, "content": h.content})
    messages.append({"role": "user", "content": body.text})

    payload = {
        "model": config["model_name"] or "gpt-4o",
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 4096,
        "stream": True,
        "stream_options": {"include_usage": True},
    }

    doc_id = body.document_id

    async def event_generator() -> AsyncIterator[str]:
        buffer = ""
        usage: dict = {}
        async with httpx.AsyncClient(timeout=180.0) as client:
            async with client.stream(
                "POST",
                f"{config['api_url'].rstrip('/')}/v1/chat/completions",
                headers=headers,
                json=payload,
            ) as resp:
                if resp.status_code != 200:
                    body_bytes = await resp.aread()
                    yield f"data: {json.dumps({'type': 'error', 'payload': f'LLM API error ({resp.status_code}): {body_bytes.decode()[:200]}'})}\n\n"
                    return

                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        chunk_str = line[6:]
                        if chunk_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(chunk_str)
                            # 🔑 usage-only chunk（OpenAI 流式最后一个 chunk 只有 usage，无 choices）
                            if "usage" in chunk and "choices" not in chunk:
                                usage = chunk["usage"]
                                continue
                            delta = chunk["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            # 有些 API 在最后一个有 content 的 chunk 同时返回 usage
                            if "usage" in chunk:
                                usage = chunk["usage"]
                            if content:
                                buffer += content
                                yield f"data: {json.dumps({'type': 'token', 'payload': {'token': content}})}\n\n"
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue

        # 流结束后解析完整结果
        try:
            clean = buffer.strip()
            if clean.startswith("```"):
                lines = clean.split("\n")
                clean = "\n".join(lines[1:]) if lines[0].startswith("```") else clean
                if clean.endswith("```"):
                    clean = clean[:-3]
                clean = clean.strip()
            parsed = json.loads(clean)
            result = {"english": parsed.get("english", ""), "chinese": parsed.get("chinese", "")}
        except json.JSONDecodeError:
            result = {"english": buffer, "chinese": ""}

        # ── 持久化 ──
        await _save_history(doc_id, body.text, result, usage)

        yield f"data: {json.dumps({'type': 'done', 'payload': {**result, 'usage': usage}})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


async def _save_history(
    document_id: Optional[str],
    user_text: str,
    result: dict,
    usage: dict,
):
    """保存翻译对话历史到数据库（独立 session）"""
    if not document_id:
        return
    from backend.db.database import AsyncSessionLocal
    now = datetime.utcnow()
    try:
        async with AsyncSessionLocal() as session:
            session.add(TranslationHistory(
                document_id=document_id,
                role="user",
                content=user_text,
                usage_json="",
                created_at=now,
            ))
            session.add(TranslationHistory(
                document_id=document_id,
                role="assistant",
                content=json.dumps({
                    "english": result.get("english", ""),
                    "chinese": result.get("chinese", ""),
                }, ensure_ascii=False),
                usage_json=json.dumps(usage) if usage else "",
                created_at=now,
            ))
            await session.commit()
    except Exception as e:
        logger.error(f"保存翻译历史失败: {e}")


# ═══════════════════════════════════════════════════════
#  翻译历史 CRUD API
# ═══════════════════════════════════════════════════════

@router.get("/history/{document_id}")
async def get_translation_history(
    document_id: str,
    limit: int = Query(default=50, le=100),
    db: AsyncSession = Depends(get_db),
):
    """获取指定文档的翻译对话历史"""
    result = await db.execute(
        select(TranslationHistory)
        .where(TranslationHistory.document_id == document_id)
        .order_by(TranslationHistory.created_at.asc())
        .limit(limit)
    )
    rows = result.scalars().all()
    return {
        "code": 0,
        "message": "success",
        "data": [
            {
                "id": r.id,
                "document_id": r.document_id,
                "role": r.role,
                "content": r.content,
                "usage_json": r.usage_json,
                "created_at": r.created_at.isoformat() if r.created_at else "",
            }
            for r in rows
        ],
    }


@router.delete("/history/{document_id}")
async def clear_translation_history(
    document_id: str,
    db: AsyncSession = Depends(get_db),
):
    """清空指定文档的翻译历史"""
    await db.execute(
        delete(TranslationHistory).where(TranslationHistory.document_id == document_id)
    )
    await db.commit()
    return {"code": 0, "message": "历史已清空", "data": None}
