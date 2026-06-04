import os
from pathlib import Path

# ⬇ PyInstaller onefile 模式下避免 pydantic_settings 导入了除 config 外不必要的依赖

class Settings:
    """PaperMaker 应用配置 (无 pydantic-settings 依赖)"""

    APP_NAME: str = "PaperMaker"
    APP_VERSION: str = "0.1.0"
    HOST: str = "127.0.0.1"
    PORT: int = 17890
    DATABASE_URL: str = ""

    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        db_dir = self.get_app_data_dir()
        db_dir.mkdir(parents=True, exist_ok=True)
        db_path = db_dir / "papermaker.db"
        return f"sqlite+aiosqlite:///{db_path}"

    @staticmethod
    def get_app_data_dir() -> Path:
        appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
        return Path(appdata) / "PaperMaker"

    @staticmethod
    def get_models_dir() -> Path:
        models_dir = Settings.get_app_data_dir() / "models"
        models_dir.mkdir(parents=True, exist_ok=True)
        return models_dir


settings = Settings()
