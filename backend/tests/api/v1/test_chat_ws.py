import os
import uuid
import asyncio
from starlette.testclient import TestClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.core.database import get_async_db
from app.models.models import User  # ensure users table + seeding
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
import pathlib


def test_ws_chat_minimal_stream(monkeypatch):
    # Override DB dependency for this TestClient context with a fresh session
    test_db_url = os.getenv(
        "TEST_DATABASE_URL",
        (
            "postgresql+asyncpg://ai_secretary_user:ai_secretary_password@postgres_test:5432/ai_secretary_test"
            if os.getenv("DOCKERIZED") == "1"
            else "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"
        ),
    )

    initialized = {"done": False}
    # Force mock LLM for tests to avoid external API calls.
    os.environ["LLM_PROVIDER"] = "mock"
    os.environ.pop("GEMINI_API_KEY", None)
    # Deterministic stream to avoid flakiness
    async def fake_stream_reply(user_text: str, **kwargs):
        yield "Hello "
        yield "world"
    monkeypatch.setattr("app.api.v1.endpoints.chat.stream_reply", fake_stream_reply)

    async def override_get_db():
        # エンジン/セッションはこの依存が呼ばれるイベントループで生成する
        engine = create_async_engine(test_db_url, future=True)
        SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

        # 初回のみ、同一ループ上でテーブル作成とユーザー投入
        if not initialized["done"]:
            # Alembic upgrade to head (idempotent)
            cfg = AlembicConfig(str((pathlib.Path(__file__).resolve().parents[3] / "alembic.ini").resolve()))
            cfg.set_main_option("sqlalchemy.url", test_db_url.replace("+asyncpg", ""))
            alembic_command.upgrade(cfg, "head")

            # Truncate all tables except alembic_version
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
            async with SessionLocal() as s:
                existing = await s.execute(select(User).limit(1))
                if existing.scalars().first() is None:
                    s.add(
                        User(
                            id=uuid.uuid4(),
                            username="default_admin",
                            email="admin@example.com",
                            password_hash="dev-hash",
                            is_active=True,
                            is_verified=True,
                        )
                    )
                    await s.commit()
            initialized["done"] = True

        try:
            async with SessionLocal() as session:
                yield session
        finally:
            await engine.dispose()

    app.dependency_overrides[get_async_db] = override_get_db

    with TestClient(app) as tc:
        # Create assistant
        a = tc.post("/api/v1/assistants/", json={"name": "WSBot"})
        assert a.status_code == 201
        assistant_id = a.json()["id"]

        # Create conversation
        c = tc.post(
            "/api/v1/conversations/", json={"assistant_id": assistant_id, "title": "WS"}
        )
        assert c.status_code == 201
        conv_id = c.json()["id"]

        # WebSocket connect and stream
        with tc.websocket_connect(f"/api/v1/ws/chat?conversation_id={conv_id}") as ws:
            ws.send_json({"type": "user_message", "text": "Hello"})
            got_start = False
            got_end = False
            for _ in range(50):
                evt = ws.receive_json()
                if evt.get("type") == "assistant_start":
                    got_start = True
                if evt.get("type") == "assistant_end":
                    got_end = True
                    break
            assert got_start and got_end

    # cleanup overrides
    app.dependency_overrides.pop(get_async_db, None)
