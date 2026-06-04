"""数值统计 API"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.services.statistics_service import StatisticsService

router = APIRouter()


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[dict | list] = None


@router.get("/document/{doc_id}", response_model=ApiResponse)
async def get_statistics(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
):
    """获取文档统计数据 (计算并缓存)"""
    svc = StatisticsService(db)
    stats = await svc.compute_statistics(doc_id)
    return ApiResponse(data=stats)


@router.get("/document/{doc_id}/readability", response_model=ApiResponse)
async def get_readability(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
):
    """获取可读性指标"""
    svc = StatisticsService(db)
    scores = await svc.compute_readability(doc_id)
    return ApiResponse(data=scores)


@router.get("/document/{doc_id}/terms", response_model=ApiResponse)
async def get_term_frequencies(
    doc_id: str,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """获取术语频率"""
    svc = StatisticsService(db)
    terms = await svc.get_term_frequencies(doc_id, limit)
    return ApiResponse(data=terms)
