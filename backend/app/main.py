# backend/app/main.py
from fastapi import FastAPI
from datetime import datetime

# FastAPIアプリケーションのインスタンスを作成します
app = FastAPI(
    title="AI秘書チーム・プラットフォーム",
    description="AI秘書チームによる統合的なプロジェクト管理・ワークフロー・知識管理プラットフォーム",
    version="1.0.0",
)

@app.get("/health", tags=["System"])
async def health_check():
    """
    アプリケーションの稼働状況を確認するためのヘルスチェックエンドポイントです。
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/", tags=["System"])
async def read_root():
    """
    ルートエンドポイントです。
    アプリケーションが正常に動作していることを示します。
    """
    return {"message": "AI秘書チーム・プラットフォームへようこそ！"}