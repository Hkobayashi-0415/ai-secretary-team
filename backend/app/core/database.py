# backend/app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import sys 

# --- 診断コード ---
# アプリケーションが実際に認識しているDATABASE_URLを、起動時にコンソールへ出力させます。
# これで、環境変数が正しく渡っているかを確実に確認できます。
print("="*50, file=sys.stderr)
print(f"DEBUG: Attempting to connect with DATABASE_URL:", file=sys.stderr)
print(f"'{settings.DATABASE_URL}'", file=sys.stderr)
print("="*50, file=sys.stderr)
# --- 診断コードここまで ---

engine = create_async_engine(
    settings.DATABASE_URL,
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