"""摘要生成模型任务"""

from typing import AsyncGenerator
from backend.models.base import ModelInfo
from backend.models.inference import ONNXInferenceModel


class SummarizationModel(ONNXInferenceModel):
    """论文摘要生成模型"""

    def __init__(self):
        super().__init__(ModelInfo(
            name="summarization",
            display_name="摘要生成",
            description="自动生成论文章节摘要",
            input_type="text",
            output_type="text",
            task="summarize",
            onnx_path="summarizer_q4.onnx",
        ))

    async def predict(
        self, input_text: str, **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式生成摘要"""
        # 占位
        words = input_text.split()[:20]
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")


from backend.models.registry import model_registry

model_registry.register(SummarizationModel, ModelInfo(
    name="summarization",
    display_name="摘要生成",
    description="自动生成论文章节摘要",
    input_type="text",
    output_type="text",
    task="summarize",
))
