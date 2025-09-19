# backend/app/core/database.py
import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

# 既定の接続先（compose のサービス名に合わせる）
# 必要なら .env / 環境変数で DATABASE_URL を上書き
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://ai_secretary_user:password@postgres:5432/ai_secretary",
)

SQL_ECHO = os.getenv("SQL_ECHO", "").lower() in ("1", "true", "yes")

# プール監視と future=True を有効化
async_engine = create_async_engine(
    DATABASE_URL,
    echo=SQL_ECHO,
    pool_pre_ping=True,
    future=True,
)

# セッションファクトリ（依存関係注入で使用）
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI の Depends 用: 非同期セッションを供給
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
