"""数据标注服务"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.schema import Annotation


class AnnotationService:
    """标注 CRUD"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_annotations(self, doc_id: str) -> List[Dict]:
        """获取文档所有标注"""
        q = select(Annotation).where(Annotation.document_id == doc_id)
        result = await self.db.execute(q)
        annotations = result.scalars().all()

        return [
            {
                "id": a.id,
                "document_id": a.document_id,
                "type": a.type,
                "label": a.label,
                "color": a.color,
                "page_index": a.page_index,
                "data": a.data,
                "comment": a.comment,
                "created_at": a.created_at.isoformat(),
            }
            for a in annotations
        ]

    async def create_annotation(
        self,
        document_id: str,
        ann_type: str,
        label: str,
        color: str,
        page_index: int,
        data: Dict,
        comment: str = "",
    ) -> Annotation:
        """创建标注"""
        ann = Annotation(
            document_id=document_id,
            type=ann_type,
            label=label,
            color=color,
            page_index=page_index,
            data=data,
            comment=comment,
            created_at=datetime.utcnow(),
        )
        self.db.add(ann)
        await self.db.commit()
        await self.db.refresh(ann)
        return ann

    async def update_annotation(self, ann_id: str, updates: Dict) -> Optional[Annotation]:
        """更新标注"""
        q = select(Annotation).where(Annotation.id == ann_id)
        result = await self.db.execute(q)
        ann = result.scalar_one_or_none()
        if not ann:
            return None

        for key, value in updates.items():
            if value is not None and hasattr(ann, key):
                setattr(ann, key, value)

        await self.db.commit()
        await self.db.refresh(ann)
        return ann

    async def delete_annotation(self, ann_id: str) -> bool:
        """删除标注"""
        q = select(Annotation).where(Annotation.id == ann_id)
        result = await self.db.execute(q)
        ann = result.scalar_one_or_none()
        if not ann:
            return False
        await self.db.delete(ann)
        await self.db.commit()
        return True
