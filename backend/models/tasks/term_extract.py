"""术语提取模型任务"""

from typing import AsyncGenerator, List
from backend.models.base import BaseModel, ModelInfo


class TermExtractionModel(BaseModel):
    """术语提取 — 基于 spaCy + 规则"""

    def __init__(self):
        super().__init__(ModelInfo(
            name="term_extract",
            display_name="术语提取",
            description="从论文中提取关键术语和短语",
            input_type="text",
            output_type="json",
            task="extract",
        ))
        self._nlp = None

    async def load(self):
        """加载 spaCy 模型"""
        try:
            import spacy
            self._nlp = spacy.load("en_core_sci_sm")
        except OSError:
            # 兜底: 使用通用英文模型
            import spacy
            self._nlp = spacy.load("en_core_web_sm")
        self.info.loaded = True

    async def predict(
        self, input_text: str, **kwargs
    ) -> AsyncGenerator[str, None]:
        """提取术语 (非流式，但保持接口一致)"""
        if not self._nlp:
            await self.load()

        doc = self._nlp(input_text[:5000])  # 限制长度
        terms = set()

        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) >= 2:  # 至少两个词
                terms.add(chunk.text.lower())

        for ent in doc.ents:
            if ent.label_ in ("METHOD", "TOOL", "CONCEPT", "DISEASE", "CHEMICAL"):
                terms.add(ent.text.lower())

        result = ", ".join(sorted(terms)[:30])
        yield result

    async def predict_batch(self, inputs: list[str], **kwargs) -> list[str]:
        results = []
        for text in inputs:
            tokens = []
            async for token in self.predict(text, **kwargs):
                tokens.append(token)
            results.append("".join(tokens))
        return results


from backend.models.registry import model_registry

model_registry.register(TermExtractionModel, ModelInfo(
    name="term_extract",
    display_name="术语提取",
    description="从论文中提取关键术语和短语",
    input_type="text",
    output_type="json",
    task="extract",
))
