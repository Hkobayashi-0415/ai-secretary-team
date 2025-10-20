# backend/tests/conftest.py
import os
import uuid
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text

from app.main import app
from app.core.database import get_async_db
from app.models.models import User

# Alembic for schema management in tests
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
import pathlib

# DOCKERIZED=1 のときは docker ネットワーク内 postgres を使う
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

_ALEMBIC_INI = str((pathlib.Path(__file__).resolve().parent.parent / "alembic.ini").resolve())

def _alembic_upgrade_head(url: str) -> None:
    cfg = AlembicConfig(_ALEMBIC_INI)
    cfg.set_main_option("sqlalchemy.url", url.replace("+asyncpg", ""))
    alembic_command.upgrade(cfg, "head")


@pytest.fixture(scope="session")
def event_loop(request) -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db() -> AsyncGenerator[AsyncSession, None]:
    # 必要な拡張を有効化
    async with engine.begin() as conn:
        await conn.exec_driver_sql(
            """
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_available_extensions WHERE name = 'vector') THEN
                    CREATE EXTENSION IF NOT EXISTS vector;
                END IF;
                IF EXISTS (SELECT 1 FROM pg_available_extensions WHERE name = 'pgcrypto') THEN
                    CREATE EXTENSION IF NOT EXISTS pgcrypto;
                END IF;
            END
            $$;
            """
        )

    # Alembic マイグレーションをheadへ（冪等）
    _alembic_upgrade_head(TEST_DATABASE_URL)

    # すべてのユーザーテーブルを空に（alembic_versionは保持）
    async with engine.begin() as conn:
        res = await conn.execute(
            text(
                """
                SELECT '"' || table_schema || '"."' || table_name || '"' AS fqname
                FROM information_schema.tables
                WHERE table_schema='public' AND table_type='BASE TABLE' AND table_name <> 'alembic_version'
                ORDER BY 1
                """
            )
        )
        names = [row[0] for row in res.fetchall()]
        if names:
            await conn.execute(text(f"TRUNCATE {', '.join(names)} RESTART IDENTITY CASCADE"))

    async with TestingSessionLocal() as session:
        # ---- デフォルトユーザーを最低限投入（必要なテストで利用）----
        exists = await session.execute(
            select(User).where(User.email == "admin@example.com")
        )
        if exists.scalars().first() is None:
            session.add(
                User(
                    id=uuid.uuid4(),
                    username="default_admin",
                    email="admin@example.com",
                    password_hash="dev-hash",
                    is_active=True,
                    is_verified=True,
                )
            )
            await session.commit()
        # ----------------------------------------------------------
        yield session

    # スキーマは保持（次のテストでもAlembic管理）


@pytest.fixture(scope="function")
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db

    app.dependency_overrides[get_async_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

