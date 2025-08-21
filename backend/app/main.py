from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uuid
from sqlalchemy import select

from app.api.v1.api import api_router
from app.core.database import engine, AsyncSessionLocal
from app.models.models import Base, User # Userモデルもインポート

@asynccontextmanager
async def lifespan(app: FastAPI):
    # アプリケーション起動時に実行される処理
    print("アプリケーションを起動します...")
    async with engine.begin() as conn:
        # テーブルを（もしなければ）作成する
        await conn.run_sync(Base.metadata.create_all)

    # デフォルトユーザーが存在するか確認し、存在しなければ作成する
    async with AsyncSessionLocal() as session:
        default_user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
        result = await session.execute(
            select(User).where(User.id == default_user_id)
        )
        if not result.scalar_one_or_none():
            print("デフォルトユーザーが存在しないため、作成します...")
            default_user = User(
                id=default_user_id,
                username="local_user",
                email="local@example.com",
                password_hash="not_used_in_local", # ローカルなのでハッシュは仮のものです
                is_active=True,
                is_verified=True
            )
            session.add(default_user)
            await session.commit()
            print("デフォルトユーザーを作成しました。")
        else:
            print("デフォルトユーザーは既に存在します。")
            
    yield
    # アプリケーション終了時に実行される処理
    print("アプリケーションを終了します...")

app = FastAPI(
    title="AI秘書チーム・プラットフォーム",
    description="AI秘書チームによる統合的なプロジェクト管理・ワークフロー・知識管理プラットフォーム",
    version="1.0.0",
    lifespan=lifespan
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy"}