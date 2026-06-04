"""文本润色 API — REST + WebSocket 流式"""

from typing import Optional
from fastapi import APIRouter, Depends, WebSocket, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.services.polish_service import PolishService

router = APIRouter()


class PolishRequest(BaseModel):
    document_id: str
    text: str
    context: str = ""
    style: str = "academic"  # academic / concise / expanded


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[dict | list] = None


@router.post("/", response_model=ApiResponse)
async def polish_text(
    body: PolishRequest,
    db: AsyncSession = Depends(get_db),
):
    """一次性文本润色（短文本）"""
    svc = PolishService(db)
    result = await svc.polish(body.document_id, body.text, body.context, body.style)
    return ApiResponse(data=result)


@router.get("/history/{doc_id}", response_model=ApiResponse)
async def get_polish_history(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
):
    """获取文档润色历史"""
    svc = PolishService(db)
    history = await svc.get_history(doc_id)
    return ApiResponse(data=history)


@router.websocket("/ws/stream/{task_id}")
async def polish_stream(websocket: WebSocket, task_id: str):
    """WebSocket 流式润色 — 逐 token 返回润色结果"""
    await websocket.accept()
    try:
        import asyncio
        received = await websocket.receive_json()
        text = received.get("text", "")
        style = received.get("style", "academic")

        # 占位: 模拟逐 token 润色
        tokens = text.split()
        for i in range(len(tokens)):
            await asyncio.sleep(0.06)
            await websocket.send_json({
                "type": "token",
                "payload": {
                    "index": i,
                    "token": tokens[i],
                    "progress": (i + 1) / len(tokens),
                },
            })

        await websocket.send_json({"type": "done", "payload": None})
    except Exception as e:
        await websocket.send_json({"type": "error", "payload": str(e)})
