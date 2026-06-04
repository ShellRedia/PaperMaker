"""ML 模型 API — 推理端点 + WebSocket 流式"""

from typing import Optional
from fastapi import APIRouter, Depends, WebSocket
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db

router = APIRouter()


class InferRequest(BaseModel):
    model_name: str = "text_polish"
    input_text: str
    params: dict = {}


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[dict | list] = None


@router.get("/", response_model=ApiResponse)
async def list_models():
    """列出可用模型"""
    # 占位 — Phase 2 接入 ModelRegistry
    models = [
        {"name": "text_polish", "description": "文本润色", "status": "available"},
        {"name": "summarization", "description": "摘要生成", "status": "available"},
        {"name": "term_extract", "description": "术语提取", "status": "available"},
    ]
    return ApiResponse(data=models)


@router.post("/infer", response_model=ApiResponse)
async def infer(
    body: InferRequest,
    db: AsyncSession = Depends(get_db),
):
    """一次性推理（短文本）"""
    # 占位 — Phase 2 接入真实模型
    result = {
        "model": body.model_name,
        "output": f"[占位输出] 对文本 '{body.input_text[:50]}...' 的推理结果",
    }
    return ApiResponse(data=result)


@router.websocket("/ws/stream/{task_id}")
async def stream_infer(websocket: WebSocket, task_id: str):
    """WebSocket 流式推理 — 接收文本，逐 token 返回"""
    await websocket.accept()
    try:
        # 占位: 模拟流式输出
        import asyncio
        received = await websocket.receive_json()
        text = received.get("text", "")
        model = received.get("model", "text_polish")

        # 模拟逐 token 输出
        tokens = text.split()
        for i, token in enumerate(tokens):
            await asyncio.sleep(0.05)
            await websocket.send_json({
                "type": "token",
                "payload": {
                    "index": i,
                    "token": token,
                    "progress": (i + 1) / len(tokens),
                },
            })

        await websocket.send_json({"type": "done", "payload": None})
    except Exception as e:
        await websocket.send_json({"type": "error", "payload": str(e)})
