"""导出 API — PDF / LaTeX / Markdown"""

from typing import Optional
from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.services.export_service import ExportService

router = APIRouter()


class ExportRequest(BaseModel):
    document_id: str
    format: str = "pdf"  # pdf / latex / markdown


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[dict | list] = None


@router.post("/", response_model=ApiResponse)
async def export_document(
    body: ExportRequest,
    db: AsyncSession = Depends(get_db),
):
    """导出文档为指定格式，返回文件路径"""
    svc = ExportService(db)
    result = await svc.export(body.document_id, body.format)
    return ApiResponse(data=result)


@router.get("/download/{filename}")
async def download_export(filename: str):
    """下载导出文件"""
    from backend.utils.file_manager import file_manager
    file_path = file_manager.get_export_path(filename)
    if not file_path.exists():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="文件不存在")
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/octet-stream",
    )
