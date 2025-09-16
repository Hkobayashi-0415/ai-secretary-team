import os
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from app.main import app
from app.core.database import get_async_db
from app.models.models import Base

# DOCKERIZED=1 のときは docker ネットワーク上の postgres を使う
DEFAULT_URL_DOCKER = "postgresql+asyncpg://ai_secretary_user:ai_secretary_password@postgres:5432/ai_secretary_test"
DEFAULT_URL_LOCAL  = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    DEFAULT_URL_DOCKER if os.getenv("DOCKERIZED") == "1" else DEFAULT_URL_LOCAL,
)

engine = create_async_engine(TEST_DATABASE_URL, future=True)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

@pytest.fixture(scope="session")
def event_loop(request) -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def db() -> AsyncGenerator[AsyncSession, None]:
    # まず拡張を有効化（権限がない環境でも無視して続行）
    async with engine.begin() as conn:
        try:
            await conn.exec_driver_sql('CREATE EXTENSION IF NOT EXISTS "vector";')
        except Exception:
            pass
        # その後テーブル作成
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    # 後片付け
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db
    app.dependency_overrides[get_async_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
