"""章节生成辅助模型"""

from typing import AsyncGenerator
from backend.models.base import ModelInfo
from backend.models.inference import ONNXInferenceModel


class SectionGenModel(ONNXInferenceModel):
    """章节生成辅助模型"""

    def __init__(self):
        super().__init__(ModelInfo(
            name="section_gen",
            display_name="章节生成",
            description="根据上下文辅助生成论文章节内容",
            input_type="text",
            output_type="text",
            task="generate",
        ))

    async def predict(
        self, input_text: str, **kwargs
    ) -> AsyncGenerator[str, None]:
        # 占位
        words = input_text.split()
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")


from backend.models.registry import model_registry

model_registry.register(SectionGenModel, ModelInfo(
    name="section_gen",
    display_name="章节生成",
    description="根据上下文辅助生成论文章节内容",
    input_type="text",
    output_type="text",
    task="generate",
))
