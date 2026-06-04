"""FastAPI 应用工厂"""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from backend.api.router import api_router
from backend.db.database import init_db
from backend.config import settings
from backend.utils.resource_path import resource_path


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    await init_db()
    yield


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用"""
    app = FastAPI(
        title="PaperMaker API",
        description="深度学习论文写作助手后端服务",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 🔑 health endpoint 必须在 static mount 之前注册
    @app.get("/health")
    async def health():
        return {"status": "ok"}

    # 注册 API 路由
    app.include_router(api_router, prefix="/api")

    # Serve 前端静态文件 — 必须放在最后（catch-all fallback）
    static_dir = resource_path("backend/static")
    if os.path.isdir(static_dir):
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

    return app
