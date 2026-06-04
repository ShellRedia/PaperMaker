"""模型注册中心 — 懒加载管理"""

from typing import Dict, Optional, Type, List
from backend.models.base import BaseModel, ModelInfo


class ModelRegistry:
    """管理所有 ML 模型的注册与懒加载"""

    _instance: Optional["ModelRegistry"] = None
    _models: Dict[str, BaseModel] = {}
    _model_classes: Dict[str, Type[BaseModel]] = {}
    _model_infos: Dict[str, ModelInfo] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register(self, model_class: Type[BaseModel], info: ModelInfo):
        """注册模型类（不实例化）"""
        self._model_classes[info.name] = model_class
        self._model_infos[info.name] = info

    async def get_model(self, name: str) -> Optional[BaseModel]:
        """获取模型实例（懒加载：首次访问时加载）"""
        if name in self._models:
            return self._models[name]

        if name not in self._model_classes:
            return None

        info = self._model_infos[name]
        instance = self._model_classes[name](info)
        await instance.load()
        self._models[name] = instance
        return instance

    def list_models(self) -> List[ModelInfo]:
        """列出所有已注册模型"""
        return [
            ModelInfo(
                name=name,
                display_name=info.display_name,
                description=info.description,
                input_type=info.input_type,
                output_type=info.output_type,
                task=info.task,
                loaded=name in self._models,
            )
            for name, info in self._model_infos.items()
        ]

    def is_loaded(self, name: str) -> bool:
        return name in self._models


# 全局单例
model_registry = ModelRegistry()
