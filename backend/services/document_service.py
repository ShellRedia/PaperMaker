"""文档管理服务"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.schema import Document


class DocumentService:
    """文档 CRUD + 章节解析"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_documents(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """分页获取文档列表"""
        offset = (page - 1) * page_size

        count_q = select(func.count(Document.id))
        total = (await self.db.execute(count_q)).scalar()

        q = (
            select(Document)
            .order_by(Document.updated_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        docs = (await self.db.execute(q)).scalars().all()

        return {
            "items": [
                {
                    "id": d.id,
                    "title": d.title,
                    "file_type": d.file_type,
                    "updated_at": d.updated_at.isoformat(),
                }
                for d in docs
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def create_document(
        self, title: str, content: str = "", file_type: str = "markdown"
    ) -> Document:
        """创建新文档"""
        doc = Document(
            title=title,
            content=content,
            file_type=file_type,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(doc)
        await self.db.commit()
        await self.db.refresh(doc)
        return doc

    async def get_document(self, doc_id: str) -> Optional[Document]:
        """获取文档"""
        q = select(Document).where(Document.id == doc_id)
        result = await self.db.execute(q)
        return result.scalar_one_or_none()

    async def update_document(
        self, doc_id: str, title: Optional[str] = None, content: Optional[str] = None
    ) -> Optional[Document]:
        """更新文档"""
        doc = await self.get_document(doc_id)
        if not doc:
            return None

        if title is not None:
            doc.title = title
        if content is not None:
            doc.content = content
        doc.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(doc)
        return doc

    async def delete_document(self, doc_id: str) -> bool:
        """删除文档"""
        doc = await self.get_document(doc_id)
        if not doc:
            return False
        await self.db.delete(doc)
        await self.db.commit()
        return True

    async def get_sections(self, doc_id: str) -> List[Dict]:
        """获取文档章节结构"""
        doc = await self.get_document(doc_id)
        if not doc:
            return []

        if doc.file_type == "latex":
            from backend.utils.latex_parser import parse_latex_sections
            sections = parse_latex_sections(doc.content)
        else:
            from backend.utils.latex_parser import parse_markdown_sections
            sections = parse_markdown_sections(doc.content)

        def to_dict(sec):
            return {
                "title": sec.title,
                "level": sec.level,
                "start_line": sec.start_line,
                "children": [to_dict(c) for c in sec.children],
            }

        return [to_dict(s) for s in sections]
