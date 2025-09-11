import os
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# テスト用のデータベースURL
TEST_DATABASE_URL = (
    "postgresql+asyncpg://ai_secretary_user:ai_secretary_password@postgres_test:5432/ai_secretary_test"
)
os.environ.setdefault("DATABASE_URL", TEST_DATABASE_URL)

from app.main import app
from app.core.database import get_async_db
from app.models.models import Base

engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

# --- Fixtureの再構築 ---

@pytest.fixture(scope="session")
def event_loop(request) -> Generator:
    """テストセッション全体で一つのイベントループを作成する"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def db() -> AsyncGenerator[AsyncSession, None]:
    """
    テストごとに、まっさらなデータベースとセッションを提供するFixture
    """
    # テストの前に、すべてのテーブルを作成
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # テストにDBセッションを渡す
    async with TestingSessionLocal() as session:
        yield session

    # テストの後に、すべてのテーブルを削除
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    テスト用のAPIクライアントを提供するFixture
    """
    # アプリケーションのDB接続を、テスト用DBに向ける
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db

    app.dependency_overrides[get_async_db] = override_get_db

    # テスト用のクライアントを生成
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # テストが終わったらオーバーライドを元に戻す
    app.dependency_overrides.clear()
