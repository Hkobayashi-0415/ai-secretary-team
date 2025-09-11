# backend/tests/conftest.py
import os
import asyncio
import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import get_async_db
from app.models.models import Base, User

# Actionsのservicesで立てたDBを使う（workflowでセット）
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db",
)

# AsyncEngine / Session
engine = create_async_engine(DATABASE_URL, future=True)
TestingSessionLocal = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def prepare_db():
    # テーブル作成・破棄をセッションスコープで
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture()
async def db_session():
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture()
async def db(db_session):
    """Alias fixture for tests expecting `db`."""
    yield db_session

@pytest.fixture(autouse=True)
async def override_db(db_session):
    async def _get_db():
        yield db_session
    app.dependency_overrides[get_async_db] = _get_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture()
async def client(db_session, prepare_db):
    # 毎テスト、デフォルトユーザーを確実に用意
    user = User(
        id=uuid.uuid4(),
        username="default_user",
        email="default@example.com",
        password_hash="dummy-hash",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()

    # ★ 重要: ASGITransport でアプリ直結（DNSを介さない）
    transport = ASGITransport(app=app, lifespan="on")
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
