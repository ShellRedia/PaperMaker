"""文本润色服务"""

from datetime import datetime
from typing import Dict, List, Optional, AsyncGenerator, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.schema import Document, PolishRecord


class PolishService:
    """文本润色流程编排"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def polish(
        self,
        document_id: str,
        text: str,
        context: str = "",
        style: str = "academic",
    ) -> Dict[str, Any]:
        """一次性文本润色（短文本）"""
        # Phase 2: 接入真实 ONNX 模型
        # 占位: 返回模拟润色结果
        polished = self._mock_polish(text, style)

        # 保存润色记录
        record = PolishRecord(
            document_id=document_id,
            original_text=text,
            polished_text=polished,
            style=style,
            model_name="mock_polish",
            created_at=datetime.utcnow(),
        )
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)

        return {
            "id": record.id,
            "original": text,
            "polished": polished,
            "diff": self._compute_simple_diff(text, polished),
        }

    async def get_history(self, doc_id: str) -> List[Dict]:
        """获取文档润色历史"""
        q = (
            select(PolishRecord)
            .where(PolishRecord.document_id == doc_id)
            .order_by(PolishRecord.created_at.desc())
            .limit(50)
        )
        records = (await self.db.execute(q)).scalars().all()

        return [
            {
                "id": r.id,
                "original_text": r.original_text[:200] + "..." if len(r.original_text) > 200 else r.original_text,
                "polished_text": r.polished_text[:200] + "..." if len(r.polished_text) > 200 else r.polished_text,
                "style": r.style,
                "model_name": r.model_name,
                "created_at": r.created_at.isoformat(),
            }
            for r in records
        ]

    def _mock_polish(self, text: str, style: str) -> str:
        """模拟润色 — Phase 2 替换为真实推理"""
        # 简单占位: 将原文标记为已润色
        return f"[{style}润色] {text}"

    def _compute_simple_diff(self, original: str, polished: str) -> List[Dict]:
        """简单逐词 diff"""
        import difflib
        diff = []
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(
            None, original.split(), polished.split()
        ).get_opcodes():
            diff.append({
                "op": tag,
                "original_words": original.split()[i1:i2],
                "polished_words": polished.split()[j1:j2],
            })
        return diff
