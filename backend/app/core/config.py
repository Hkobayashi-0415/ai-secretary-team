# backend/app/core/config.py
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings,  SettingsConfigDict

# .envファイルから環境変数を読み込みます
load_dotenv()

class Settings(BaseSettings):
    """
    アプリケーションの設定を管理するクラスです。
    環境変数から値を読み込みます。
    """
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_default_secret_key")
    
    # CORS設定
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
    
    @property
    def cors_origins_list(self) -> list[str]:
        """CORS_ORIGINSをリストに変換"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",          # 旧 Config.extra = "ignore"
        case_sensitive=False     # 旧 Config.case_sensitive
    )

settings = Settings()