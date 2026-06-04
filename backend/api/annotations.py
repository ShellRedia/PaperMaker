"""数据标注 API"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.services.annotation_service import AnnotationService

router = APIRouter()


class AnnotationData(BaseModel):
    """标注数据 — 根据类型携带不同字段"""
    bbox: Optional[dict] = None       # {x, y, width, height}
    points: Optional[List[dict]] = None  # 多边形顶点 [{x,y}, ...]
    from_id: Optional[str] = None     # 关系连线起点
    to_id: Optional[str] = None       # 关系连线终点
    relation_type: Optional[str] = None
    start_offset: Optional[int] = None  # 文本标注
    end_offset: Optional[int] = None


class AnnotationCreate(BaseModel):
    document_id: str
    type: str = "bbox"   # bbox / polygon / relation / text_span
    label: str = "default"
    color: str = "#3B82F6"
    page_index: int = 0
    data: AnnotationData = Field(default_factory=AnnotationData)
    comment: str = ""


class AnnotationUpdate(BaseModel):
    label: Optional[str] = None
    color: Optional[str] = None
    data: Optional[AnnotationData] = None
    comment: Optional[str] = None


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[dict | list] = None


@router.get("/document/{doc_id}", response_model=ApiResponse)
async def list_annotations(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
):
    """获取文档的所有标注"""
    svc = AnnotationService(db)
    annotations = await svc.list_annotations(doc_id)
    return ApiResponse(data=annotations)


@router.post("/", response_model=ApiResponse)
async def create_annotation(
    body: AnnotationCreate,
    db: AsyncSession = Depends(get_db),
):
    """创建标注"""
    svc = AnnotationService(db)
    ann = await svc.create_annotation(
        body.document_id, body.type, body.label, body.color,
        body.page_index, body.data.model_dump(), body.comment,
    )
    return ApiResponse(data={"id": ann.id})


@router.put("/{ann_id}", response_model=ApiResponse)
async def update_annotation(
    ann_id: str,
    body: AnnotationUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新标注"""
    svc = AnnotationService(db)
    ann = await svc.update_annotation(ann_id, body.model_dump(exclude_none=True))
    if not ann:
        raise HTTPException(status_code=404, detail="标注不存在")
    return ApiResponse(data={"id": ann.id})


@router.delete("/{ann_id}", response_model=ApiResponse)
async def delete_annotation(
    ann_id: str,
    db: AsyncSession = Depends(get_db),
):
    """删除标注"""
    svc = AnnotationService(db)
    success = await svc.delete_annotation(ann_id)
    if not success:
        raise HTTPException(status_code=404, detail="标注不存在")
    return ApiResponse(message="标注已删除")
