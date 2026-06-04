"""文本润色模型任务"""

from typing import AsyncGenerator
from backend.models.base import ModelInfo
from backend.models.inference import ONNXInferenceModel


class TextPolishModel(ONNXInferenceModel):
    """文本润色 ONNX 模型"""

    def __init__(self):
        super().__init__(ModelInfo(
            name="text_polish",
            display_name="文本润色",
            description="基于深度学习的学术文本润色，优化表达清晰度和学术风格",
            input_type="text",
            output_type="text",
            task="polish",
            onnx_path="text_polish_q4.onnx",
        ))

    async def predict(
        self, input_text: str, **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式文本润色"""
        # Phase 2: 接入真实 ONNX 推理
        # 占位: 简单模拟逐词输出
        style = kwargs.get("style", "academic")
        words = input_text.split()
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")


# 注册到全局注册中心
from backend.models.registry import model_registry

model_registry.register(TextPolishModel, ModelInfo(
    name="text_polish",
    display_name="文本润色",
    description="基于深度学习的学术文本润色",
    input_type="text",
    output_type="text",
    task="polish",
))
