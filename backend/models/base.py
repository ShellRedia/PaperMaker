"""ML 模型抽象基类"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class ModelInfo:
    """模型元信息"""
    name: str
    display_name: str
    description: str
    input_type: str  # "text"
    output_type: str  # "text"
    task: str  # polish / summarize / extract
    onnx_path: Optional[str] = None
    loaded: bool = False


class BaseModel(ABC):
    """所有 ML 模型的抽象基类"""

    def __init__(self, info: ModelInfo):
        self.info = info

    @abstractmethod
    async def load(self):
        """加载模型到内存（懒加载入口）"""
        ...

    @abstractmethod
    async def predict(
        self, input_text: str, **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式推理 — 逐 token 产生输出"""
        ...

    @abstractmethod
    async def predict_batch(
        self, inputs: list[str], **kwargs
    ) -> list[str]:
        """批量推理"""
        ...

    def is_loaded(self) -> bool:
        return self.info.loaded
