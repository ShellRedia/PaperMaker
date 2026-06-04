"""全局设置 API — LLM 配置等"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.db.database import get_db
from backend.db.schema import AppSettings

router = APIRouter()


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[dict | list | str] = None


class LLMConfigRequest(BaseModel):
    api_url: str = ""
    api_key: str = ""
    model_name: str = ""


@router.get("/llm-config", response_model=ApiResponse)
async def get_llm_config(db: AsyncSession = Depends(get_db)):
    """获取 LLM 配置"""
    result = await db.execute(
        select(AppSettings).where(AppSettings.key.in_(["llm_api_url", "llm_api_key", "llm_model_name"]))
    )
    rows = {r.key: r.value for r in result.scalars().all()}
    return ApiResponse(data={
        "api_url": rows.get("llm_api_url", ""),
        "api_key": rows.get("llm_api_key", ""),
        "model_name": rows.get("llm_model_name", ""),
    })


@router.put("/llm-config", response_model=ApiResponse)
async def update_llm_config(
    body: LLMConfigRequest,
    db: AsyncSession = Depends(get_db),
):
    """更新 LLM 配置"""
    updates = {
        "llm_api_url": body.api_url,
        "llm_api_key": body.api_key,
        "llm_model_name": body.model_name,
    }
    for key, value in updates.items():
        result = await db.execute(select(AppSettings).where(AppSettings.key == key))
        row = result.scalar_one_or_none()
        if row:
            row.value = value
        else:
            db.add(AppSettings(key=key, value=value))
    await db.commit()
    return ApiResponse(message="LLM 配置已更新")


@router.get("/{key}", response_model=ApiResponse)
async def get_setting(key: str, db: AsyncSession = Depends(get_db)):
    """获取单个设置项"""
    result = await db.execute(select(AppSettings).where(AppSettings.key == key))
    row = result.scalar_one_or_none()
    return ApiResponse(data=row.value if row else None)


@router.put("/{key}", response_model=ApiResponse)
async def update_setting(
    key: str,
    body: dict,
    db: AsyncSession = Depends(get_db),
):
    """更新单个设置项"""
    result = await db.execute(select(AppSettings).where(AppSettings.key == key))
    row = result.scalar_one_or_none()
    if row:
        row.value = body.get("value", "")
    else:
        db.add(AppSettings(key=key, value=body.get("value", "")))
    await db.commit()
    return ApiResponse(message="ok")
