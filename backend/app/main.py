# backend/app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
import os


def _cors_origins() -> list[str]:
    # settings 優先。なければ環境変数 CORS_ORIGINS (カンマ区切り) を利用
    if getattr(settings, "cors_origins_list", None):
        return settings.cors_origins_list
    return [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("アプリケーションを起動します...")
    yield
    print("アプリケーションを終了します...")


app = FastAPI(
    title="AI秘書チーム・プラットフォーム",
    description="AI秘書チームによる統合的なプロジェクト管理・ワークフロー・知識管理プラットフォーム",
    version="1.0.0",
    lifespan=lifespan,
)

# --- CORS（1カ所だけで設定する）---
origins = _cors_origins()
if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
# -----------------------------------

app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy"}
