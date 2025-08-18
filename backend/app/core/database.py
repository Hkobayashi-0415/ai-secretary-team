# backend/app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .config import settings

# 非同期データベースエンジンを作成します
# connect_args はSSLモードを無効にするためのものです（ローカル開発用）
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True, # SQLクエリをコンソールに出力します
    future=True
)

# 非同期セッションを作成するための設定です
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_async_db() -> AsyncSession:
    """
    APIエンドポイントでデータベースセッションを取得するための依存性注入関数です。
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()