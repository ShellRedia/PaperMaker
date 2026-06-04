"""导出服务 — PDF / LaTeX / Markdown"""

from typing import Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.schema import Document
from backend.utils.file_manager import file_manager


class ExportService:
    """文档导出"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def export(self, doc_id: str, fmt: str = "pdf") -> Dict[str, Any]:
        """导出文档为指定格式"""
        q = select(Document).where(Document.id == doc_id)
        doc = (await self.db.execute(q)).scalar_one_or_none()
        if not doc:
            raise ValueError("文档不存在")

        file_manager.ensure_directories()

        if fmt == "markdown":
            filename = f"{doc.title or 'document'}.md"
            filepath = file_manager.get_export_path(filename)
            filepath.write_text(doc.content, encoding="utf-8")

        elif fmt == "latex":
            filename = f"{doc.title or 'document'}.tex"
            filepath = file_manager.get_export_path(filename)
            # 简单包装为 LaTeX 文档
            latex_content = self._to_latex(doc.title, doc.content)
            filepath.write_text(latex_content, encoding="utf-8")

        elif fmt == "pdf":
            filename = f"{doc.title or 'document'}.pdf"
            filepath = file_manager.get_export_path(filename)
            # Phase 2: 使用 ReportLab 生成真实 PDF
            self._generate_simple_pdf(filepath, doc.title, doc.content)

        else:
            raise ValueError(f"不支持的导出格式: {fmt}")

        return {
            "format": fmt,
            "filename": filename,
            "path": str(filepath),
            "size": filepath.stat().st_size,
        }

    def _to_latex(self, title: str, content: str) -> str:
        """将 Markdown 内容包装为 LaTeX 文档"""
        return f"""\\documentclass{{article}}
\\title{{{title}}}
\\author{{PaperMaker}}
\\begin{{document}}
\\maketitle
{content}
\\end{{document}}
"""

    def _generate_simple_pdf(self, filepath, title: str, content: str):
        """使用 ReportLab 生成简单 PDF"""
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

        doc_pdf = SimpleDocTemplate(str(filepath), pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # 标题
        story.append(Paragraph(title or "Document", styles["Title"]))
        story.append(Spacer(1, 12))

        # 正文 (简单分行处理)
        for para in content.split("\n\n"):
            if para.strip():
                story.append(Paragraph(para.strip().replace("\n", "<br/>"), styles["BodyText"]))
                story.append(Spacer(1, 6))

        doc_pdf.build(story)
