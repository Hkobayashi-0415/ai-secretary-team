# backend/app/core/config.py
import os
from typing import List

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# .env を読む
load_dotenv()


class Settings(BaseSettings):
    """
    アプリ全体の設定。環境変数を優先して読み込みます。
    """

    # === 基本 ===
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite+aiosqlite:///:memory:"
    )
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_default_secret_key")

    # === 環境/挙動フラグ ===
    # test / ci / development / production など
    ENVIRONMENT: str = Field(default=os.getenv("ENVIRONMENT", "development"))
    # CI/テストで外部LLMの到達性チェック等を無効化したいときに 1/true
    DISABLE_LLM_VALIDATION: bool = Field(
        default=os.getenv("DISABLE_LLM_VALIDATION", "0").lower() in {"1", "true", "yes"}
    )

    # === CORS ===
    CORS_ORIGINS: str = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """カンマ区切り → list[str]"""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def offline_mode(self) -> bool:
        """
        テストやCIでは外部ネットワークに出ないよう各所で分岐できるフラグ。
        """
        return self.ENVIRONMENT in {"test", "ci"} or self.DISABLE_LLM_VALIDATION

    class Config:
        case_sensitive = True


settings = Settings()
