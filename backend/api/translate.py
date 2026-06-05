"""LLM 翻译 API — 中→英翻译润色→中 + 对话历史持久化 + 翻译规则 + 优化"""

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


# ── 翻译规则模型 ──

class TranslationRuleItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="规则唯一ID")
    pattern: str = Field(..., description="待匹配的原文（中文词/缩写等）", min_length=1)
    replacement: str = Field(default="", description="替换为的目标翻译")
    rule_type: str = Field(default="replace", description="规则类型: replace / no_translate")


class TranslationRulesConfig(BaseModel):
    rules: list[TranslationRuleItem] = Field(default_factory=list)


# ── 优化请求模型 ──

class RefineRequest(BaseModel):
    original_input: str = Field(..., description="原始用户输入（中文）")
    current_english: str = Field(..., description="当前的英文翻译")
    refine_mode: str = Field(..., description="优化模式: concise / academic")
    document_id: Optional[str] = Field(default=None, description="关联的文档 ID")


# ── 翻译规则 CRUD ──

RULES_KEY = "translation_rules"


async def get_translation_rules(db: AsyncSession) -> TranslationRulesConfig:
    """从数据库读取翻译规则"""
    result = await db.execute(
        select(AppSettings).where(AppSettings.key == RULES_KEY)
    )
    row = result.scalar_one_or_none()
    if row and row.value:
        try:
            return TranslationRulesConfig.model_validate_json(row.value)
        except (json.JSONDecodeError, Exception):
            return TranslationRulesConfig()
    return TranslationRulesConfig()


async def save_translation_rules(db: AsyncSession, config: TranslationRulesConfig):
    """保存翻译规则到数据库"""
    from sqlalchemy.dialects.sqlite import insert as sqlite_upsert
    value = config.model_dump_json()
    stmt = sqlite_upsert(AppSettings).values(key=RULES_KEY, value=value).on_conflict_do_update(
        index_elements=["key"], set_=dict(value=value, updated_at=datetime.utcnow())
    )
    await db.execute(stmt)
    await db.commit()


def _build_rules_text(rules: list[TranslationRuleItem]) -> str:
    """将翻译规则列表构建为可注入系统提示的文本段落"""
    if not rules:
        return ""
    lines = ["\n## Translation Rules (MUST follow):"]
    for i, r in enumerate(rules, 1):
        if r.rule_type == "no_translate":
            lines.append(f'{i}. Keep "{r.pattern}" UNTRANSLATED — always output it as-is without any changes.')
        else:
            replacement = r.replacement or "[appropriate English equivalent]"
            lines.append(f'{i}. Translate "{r.pattern}" as "{replacement}" consistently.')
    return "\n".join(lines)


# ── 翻译系统提示 ──

TRANSLATE_SYSTEM_PROMPT = """You are a professional academic translator. Your task is a two-step process:

Step 1: Translate the user's Chinese text into polished, academic English suitable for a top-tier computer science / deep learning paper. Use the standard academic style seen in NeurIPS, ICML, CVPR, ACL papers. Ensure the English is idiomatic, precise, and natural — not a literal word-for-word translation.

Step 2: Translate the polished English back into Chinese. The Chinese should reflect the improved structure and clarity of the English version.

You MUST respond with a valid JSON object only, no markdown code blocks, no extra text:
{"english": "...polished English text...", "chinese": "...back-translated Chinese text..."}"""


# ── 优化系统提示 ──

REFINE_CONCISE_PROMPT = """You are a professional academic editor. Your task is to make the given English text MORE CONCISE while preserving all key information and academic rigor.

Guidelines:
- Remove redundant words and phrases
- Tighten sentence structures
- Eliminate unnecessary qualifiers (very, really, quite, etc.)
- Use shorter, more direct expressions where possible
- Keep all technical terms and key findings intact
- Target: reduce word count by at least 15-20% without losing meaning

After refining the English, also translate it back into Chinese.

You MUST respond with a valid JSON object only, no markdown code blocks, no extra text:
{"english": "...concise English text...", "chinese": "...back-translated Chinese text..."}"""


REFINE_ACADEMIC_PROMPT = """You are a professional academic editor. Your task is to make the given English text MORE ACADEMIC and formal, suitable for a top-tier scientific publication.

Guidelines:
- Elevate vocabulary to more formal, precise academic terms
- Use more sophisticated sentence structures appropriate for scholarly writing
- Add appropriate hedging where claims need qualification
- Ensure the tone matches leading venues (NeurIPS, ICML, CVPR, ACL)
- Maintain all technical accuracy — do not change scientific meaning
- Use passive voice where appropriate for academic convention

After refining the English, also translate it back into Chinese.

You MUST respond with a valid JSON object only, no markdown code blocks, no extra text:
{"english": "...academic English text...", "chinese": "...back-translated Chinese text..."}"""


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


# ═══════════════════════════════════════════════════════
#  翻译端点
# ═══════════════════════════════════════════════════════

@router.post("", response_model=TranslateResponse)
async def translate_text(
    body: TranslateRequest,
    db: AsyncSession = Depends(get_db),
):
    """中文 → 英文润色 → 回译中文（含用户翻译规则）"""
    config = await get_llm_config(db)
    if not config["api_url"]:
        raise HTTPException(status_code=400, detail="请先在设置中配置 LLM API 地址")
    if not config["api_key"]:
        raise HTTPException(status_code=400, detail="请先在设置中配置 LLM API Key")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config['api_key']}",
    }

    # 加载翻译规则并构建动态系统提示
    rules_config = await get_translation_rules(db)
    rules_text = _build_rules_text(rules_config.rules)
    system_prompt = TRANSLATE_SYSTEM_PROMPT
    if rules_text:
        system_prompt = TRANSLATE_SYSTEM_PROMPT + "\n" + rules_text

    messages = [{"role": "system", "content": system_prompt}]
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
    """流式翻译 — SSE 逐 token 返回（含用户翻译规则）"""
    config = await get_llm_config(db)
    if not config["api_url"]:
        raise HTTPException(status_code=400, detail="请先在设置中配置 LLM API 地址")
    if not config["api_key"]:
        raise HTTPException(status_code=400, detail="请先在设置中配置 LLM API Key")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config['api_key']}",
    }

    # 加载翻译规则并构建动态系统提示
    rules_config = await get_translation_rules(db)
    rules_text = _build_rules_text(rules_config.rules)
    system_prompt = TRANSLATE_SYSTEM_PROMPT
    if rules_text:
        system_prompt = TRANSLATE_SYSTEM_PROMPT + "\n" + rules_text

    messages = [{"role": "system", "content": system_prompt}]
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
            logger.warning(f"LLM 返回非JSON内容 (len={len(buffer)}), 使用原始内容作为英文翻译")
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


# ═══════════════════════════════════════════════════════
#  优化端点 — 精简 / 学术化
# ═══════════════════════════════════════════════════════

@router.post("/refine/stream")
async def refine_translation_stream(
    body: RefineRequest,
    db: AsyncSession = Depends(get_db),
):
    """对上一句英文翻译进行优化（精简 或 学术化），流式返回"""
    if body.refine_mode not in ("concise", "academic"):
        raise HTTPException(status_code=400, detail="refine_mode 必须为 concise 或 academic")

    config = await get_llm_config(db)
    if not config["api_url"]:
        raise HTTPException(status_code=400, detail="请先在设置中配置 LLM API 地址")
    if not config["api_key"]:
        raise HTTPException(status_code=400, detail="请先在设置中配置 LLM API Key")

    system_prompt = REFINE_CONCISE_PROMPT if body.refine_mode == "concise" else REFINE_ACADEMIC_PROMPT
    mode_label = "精简" if body.refine_mode == "concise" else "学术化"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config['api_key']}",
    }

    user_content = f"Original Chinese input: {body.original_input}\n\nCurrent English translation to refine:\n{body.current_english}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]

    payload = {
        "model": config["model_name"] or "gpt-4o",
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 4096,
        "stream": True,
        "stream_options": {"include_usage": True},
    }

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
                            if "usage" in chunk and "choices" not in chunk:
                                usage = chunk["usage"]
                                continue
                            delta = chunk["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if "usage" in chunk:
                                usage = chunk["usage"]
                            if content:
                                buffer += content
                                yield f"data: {json.dumps({'type': 'token', 'payload': {'token': content}})}\n\n"
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue

        # 解析完整结果
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
            logger.warning(f"优化端 LLM 返回非JSON内容 (len={len(buffer)})")
            result = {"english": buffer, "chinese": ""}

        # ── 持久化优化结果（追加到最近一条 assistant 历史记录） ──
        await _append_refine_history(body.document_id, result, usage, body.refine_mode)

        yield f"data: {json.dumps({'type': 'done', 'payload': {**result, 'usage': usage, 'refine_mode': body.refine_mode}})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ═══════════════════════════════════════════════════════
#  翻译规则 CRUD API
# ═══════════════════════════════════════════════════════

@router.get("/rules")
async def get_rules(
    db: AsyncSession = Depends(get_db),
):
    """获取用户配置的翻译规则列表"""
    config = await get_translation_rules(db)
    return {"code": 0, "message": "success", "data": config.model_dump()}


@router.put("/rules")
async def update_rules(
    body: TranslationRulesConfig,
    db: AsyncSession = Depends(get_db),
):
    """保存翻译规则列表"""
    await save_translation_rules(db, body)
    return {"code": 0, "message": "翻译规则已保存", "data": body.model_dump()}


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
            # 保存 assistant 内容，包含可能的 refines 变体
            assistant_content = {
                "english": result.get("english", ""),
                "chinese": result.get("chinese", ""),
            }
            if result.get("refines"):
                assistant_content["refines"] = result["refines"]
            session.add(TranslationHistory(
                document_id=document_id,
                role="assistant",
                content=json.dumps(assistant_content, ensure_ascii=False),
                usage_json=json.dumps(usage) if usage else "",
                created_at=now,
            ))
            await session.commit()
    except Exception as e:
        logger.error(f"保存翻译历史失败: {e}")


async def _append_refine_history(
    document_id: Optional[str],
    result: dict,
    usage: dict,
    refine_mode: str,
):
    """将优化结果追加到最近一条 assistant 翻译历史的 refines 字段"""
    if not document_id:
        return
    from backend.db.database import AsyncSessionLocal
    try:
        async with AsyncSessionLocal() as session:
            # 查找该文档最近一条 assistant 记录
            r = await session.execute(
                select(TranslationHistory)
                .where(
                    TranslationHistory.document_id == document_id,
                    TranslationHistory.role == "assistant",
                )
                .order_by(TranslationHistory.created_at.desc())
                .limit(1)
            )
            last_assistant = r.scalar_one_or_none()
            if not last_assistant:
                return

            # 解析现有内容，追加 refines
            content = json.loads(last_assistant.content)
            refines = content.get("refines", [])
            refines.append({
                "label": "精简版" if refine_mode == "concise" else "学术版",
                "mode": refine_mode,
                "english": result.get("english", ""),
                "chinese": result.get("chinese", ""),
                "usage": usage,
            })

            content["refines"] = refines
            last_assistant.content = json.dumps(content, ensure_ascii=False)

            # 合并 usage
            if usage:
                existing_usage = {}
                if last_assistant.usage_json:
                    try:
                        existing_usage = json.loads(last_assistant.usage_json)
                    except json.JSONDecodeError:
                        pass
                merged = {
                    "prompt_tokens": (existing_usage.get("prompt_tokens", 0) or 0) + (usage.get("prompt_tokens", 0) or 0),
                    "completion_tokens": (existing_usage.get("completion_tokens", 0) or 0) + (usage.get("completion_tokens", 0) or 0),
                    "total_tokens": (existing_usage.get("total_tokens", 0) or 0) + (usage.get("total_tokens", 0) or 0),
                }
                last_assistant.usage_json = json.dumps(merged)

            await session.commit()
    except Exception as e:
        logger.error(f"追加优化历史失败: {e}")


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
