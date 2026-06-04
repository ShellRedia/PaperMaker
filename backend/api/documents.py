"""文档管理 API — CRUD + 版本历史"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.services.document_service import DocumentService

router = APIRouter()


# ── Request/Response Schemas ──

class DocumentCreate(BaseModel):
    title: str = "Untitled"
    content: str = ""
    file_type: str = "markdown"


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class DocumentResponse(BaseModel):
    id: str
    title: str
    content: str
    file_type: str
    created_at: str
    updated_at: str


class DocumentListItem(BaseModel):
    id: str
    title: str
    file_type: str
    updated_at: str


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[dict | list] = None


# ── Endpoints ──

@router.get("/", response_model=ApiResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """获取文档列表"""
    svc = DocumentService(db)
    result = await svc.list_documents(page, page_size)
    return ApiResponse(data=result)


@router.post("/", response_model=ApiResponse)
async def create_document(
    body: DocumentCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建新文档"""
    svc = DocumentService(db)
    doc = await svc.create_document(body.title, body.content, body.file_type)
    return ApiResponse(data={"id": doc.id, "title": doc.title})


@router.get("/{doc_id}", response_model=ApiResponse)
async def get_document(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
):
    """获取单个文档详情"""
    svc = DocumentService(db)
    doc = await svc.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    return ApiResponse(data={
        "id": doc.id,
        "title": doc.title,
        "content": doc.content,
        "file_type": doc.file_type,
        "created_at": doc.created_at.isoformat(),
        "updated_at": doc.updated_at.isoformat(),
    })


@router.put("/{doc_id}", response_model=ApiResponse)
async def update_document(
    doc_id: str,
    body: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新文档"""
    svc = DocumentService(db)
    doc = await svc.update_document(doc_id, body.title, body.content)
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    return ApiResponse(data={"id": doc.id, "updated_at": doc.updated_at.isoformat()})


@router.delete("/{doc_id}", response_model=ApiResponse)
async def delete_document(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
):
    """删除文档"""
    svc = DocumentService(db)
    success = await svc.delete_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="文档不存在")
    return ApiResponse(message="文档已删除")


@router.get("/{doc_id}/sections", response_model=ApiResponse)
async def get_sections(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
):
    """获取文档章节结构"""
    svc = DocumentService(db)
    sections = await svc.get_sections(doc_id)
    return ApiResponse(data=sections)
