"""文件管理 — AppData 目录、临时文件、导出"""

import os
import shutil
from pathlib import Path
from backend.config import settings


class FileManager:
    """管理 PaperMaker 的文件存储"""

    def __init__(self):
        self.app_data = settings.get_app_data_dir()
        self.models_dir = settings.get_models_dir()
        self.exports_dir = self.app_data / "exports"
        self.temp_dir = self.app_data / "temp"

    def ensure_directories(self):
        """确保所有必需目录存在"""
        for d in [self.app_data, self.models_dir, self.exports_dir, self.temp_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def get_document_path(self, doc_id: str, ext: str = ".md") -> Path:
        """获取文档文件路径"""
        docs_dir = self.app_data / "documents"
        docs_dir.mkdir(parents=True, exist_ok=True)
        return docs_dir / f"{doc_id}{ext}"

    def get_export_path(self, filename: str) -> Path:
        """获取导出文件路径"""
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        return self.exports_dir / filename

    def model_exists(self, model_name: str) -> bool:
        """检查模型文件是否存在（按需下载的场景）"""
        model_path = self.models_dir / model_name
        return model_path.exists()

    def clean_temp(self):
        """清理临时文件"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            self.temp_dir.mkdir(exist_ok=True)


# 全局单例
file_manager = FileManager()
