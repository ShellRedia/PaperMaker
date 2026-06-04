"""ONNX 推理管道"""

import hashlib
from typing import AsyncGenerator, Optional
from backend.models.base import BaseModel, ModelInfo
from backend.config import settings


class ONNXInferenceModel(BaseModel):
    """ONNX Runtime 推理管道基类"""

    def __init__(self, info: ModelInfo):
        super().__init__(info)
        self._session = None
        self._tokenizer = None

    async def load(self):
        """加载 ONNX 模型和分词器"""
        import onnxruntime as ort

        # Phase 2: 从 AppData/models/ 加载，不存在则触发下载
        model_dir = settings.get_models_dir()
        onnx_file = model_dir / (self.info.onnx_path or f"{self.info.name}.onnx")

        if not onnx_file.exists():
            # 占位 — Phase 4 实现下载逻辑
            raise FileNotFoundError(
                f"模型文件未找到: {onnx_file}\n"
                f"请将 ONNX 模型放置到 {model_dir}"
            )

        self._session = ort.InferenceSession(
            str(onnx_file),
            providers=["CPUExecutionProvider"],
        )
        self.info.loaded = True

    async def predict(
        self, input_text: str, **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式推理 — 子类需实现具体分词和生成逻辑"""
        if not self._session:
            await self.load()

        # 子类实现具体逻辑
        raise NotImplementedError("子类需实现 predict 方法")

    async def predict_batch(self, inputs: list[str], **kwargs) -> list[str]:
        """批量推理"""
        results = []
        for text in inputs:
            tokens = []
            async for token in self.predict(text, **kwargs):
                tokens.append(token)
            results.append("".join(tokens))
        return results

    @staticmethod
    def hash_input(text: str) -> str:
        """生成输入文本的哈希 (用于缓存)"""
        return hashlib.sha256(text.encode()).hexdigest()[:16]
