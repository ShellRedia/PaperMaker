"""API 路由总注册"""

from fastapi import APIRouter
from backend.api import documents, annotations, models, statistics, polish, export, settings, translate

api_router = APIRouter()

api_router.include_router(documents.router, prefix="/documents", tags=["文档管理"])
api_router.include_router(annotations.router, prefix="/annotations", tags=["数据标注"])
api_router.include_router(models.router, prefix="/models", tags=["ML 模型"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["数值统计"])
api_router.include_router(polish.router, prefix="/polish", tags=["文本润色"])
api_router.include_router(export.router, prefix="/export", tags=["导出"])
api_router.include_router(settings.router, prefix="/settings", tags=["全局设置"])
api_router.include_router(translate.router, prefix="/translate", tags=["LLM翻译"])
