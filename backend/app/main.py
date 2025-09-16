from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.v1.api import api_router
from app.core.config import settings

import os
from fastapi.middleware.cors import CORSMiddleware
origins = [o.strip() for o in os.getenv("CORS_ORIGINS","").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # アプリケーション起動時に実行される処理
    print("アプリケーションを起動します...")
    
    # NOTE: データベースの初期化はAlembicマイグレーションで管理します
    # 開発環境では: alembic upgrade head
    # 本番環境では: CI/CDパイプラインでマイグレーションを実行
    
    yield
    # アプリケーション終了時に実行される処理
    print("アプリケーションを終了します...")

app = FastAPI(
    title="AI秘書チーム・プラットフォーム",
    description="AI秘書チームによる統合的なプロジェクト管理・ワークフロー・知識管理プラットフォーム",
    version="1.0.0",
    lifespan=lifespan
)

# CORS設定（環境変数から読み込み）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy"}