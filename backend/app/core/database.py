# backend/app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import sys
import os

# --- 診断コード ---
# アプリケーションが実際に認識しているDATABASE_URLを、起動時にコンソールへ出力させます。
# これで、環境変数が正しく渡っているかを確実に確認できます。
db_url = settings.DATABASE_URL or ""

# auto-upgrade sync DSN to async if needed (postgresql -> postgresql+asyncpg)
if db_url.startswith("postgresql://"):
    upgraded = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    print("[database] INFO: Upgrading DATABASE_URL to asyncpg driver", file=sys.stderr)
    settings.DATABASE_URL = upgraded
    db_url = upgraded

if os.getenv("LOG_DB_URL", "0") == "1" and os.getenv("ENVIRONMENT", "").lower() != "production":
    print("=" * 50, file=sys.stderr)
    print("DEBUG: Attempting to connect with DATABASE_URL:", file=sys.stderr)
    print(f"'{db_url}'", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
# --- 診断コードここまで ---

engine = create_async_engine(
    db_url,
    echo=True,
    future=True
)

AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_async_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
