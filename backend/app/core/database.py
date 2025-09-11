# backend/app/core/database.py
import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

logger = logging.getLogger(__name__)

def _mask_db_url(url: str) -> str:
    try:
        if "://" not in url or "@" not in url:
            return "***"
        scheme, rest = url.split("://", 1)
        _, after_at = rest.split("@", 1)
        return f"{scheme}://***@{after_at}"
    except Exception:
        return "***"

# 必要なときだけDB URLをDEBUGで出す（マスク付き）
if os.getenv("PRINT_DB_URL", "0") == "1":
    logger.debug("Connecting DB: %s", _mask_db_url(settings.DATABASE_URL))

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=os.getenv("SQLALCHEMY_ECHO", "0") == "1",
    future=True,
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
