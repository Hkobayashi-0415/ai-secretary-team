import os
import uuid

from starlette.testclient import TestClient

from app.main import app
from app.core.database import get_async_db
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, text
from app.models.models import User


def _override_db_factory(test_db_url: str):
    initialized = {"done": False}

    async def override_get_db():
        engine = create_async_engine(test_db_url, future=True)
        SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

        if not initialized["done"]:
            from alembic.config import Config as AlembicConfig
            from alembic import command as alembic_command
            import pathlib
            cfg = AlembicConfig(str((pathlib.Path(__file__).resolve().parents[3] / "alembic.ini").resolve()))
            cfg.set_main_option("sqlalchemy.url", test_db_url.replace("+asyncpg", ""))
            alembic_command.upgrade(cfg, "head")

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

    return override_get_db


def test_ws_chat_thinking_params(monkeypatch):
    # Force mock fallback and capture parameters passed to stream_reply
    captured = {}

    async def fake_stream_reply(user_text: str, **kwargs):
        captured["kwargs"] = kwargs
        yield "T"
        yield "K"

    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key")
    monkeypatch.setattr("app.services.llm.stream_reply", fake_stream_reply)
    monkeypatch.setattr("app.api.v1.endpoints.chat.stream_reply", fake_stream_reply)

    test_db_url = os.getenv(
        "TEST_DATABASE_URL",
        (
            "postgresql+asyncpg://ai_secretary_user:ai_secretary_password@postgres_test:5432/ai_secretary_test"
            if os.getenv("DOCKERIZED") == "1"
            else "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"
        ),
    )
    app.dependency_overrides[get_async_db] = _override_db_factory(test_db_url)

    with TestClient(app) as tc:
        a = tc.post("/api/v1/assistants/", json={"name": "WS-Thinking"})
        assert a.status_code == 201
        assistant_id = a.json()["id"]

        c = tc.post("/api/v1/conversations/", json={"assistant_id": assistant_id, "title": "WS-Thinking"})
        assert c.status_code == 201
        conv_id = c.json()["id"]

        with tc.websocket_connect(
            f"/api/v1/ws/chat?conversation_id={conv_id}&thinking_level=high&thinking_budget=2048&include_thoughts=true&model=gemini-3-pro-preview"
        ) as ws:
            ws.send_json({"type": "user_message", "text": "Hello"})
            # consume stream
            for _ in range(3):
                ws.receive_json()

    app.dependency_overrides.pop(get_async_db, None)

    kwargs = captured.get("kwargs") or {}
    assert kwargs.get("model") == "gemini-3-pro-preview"
    assert kwargs.get("thinking_level") == "high"
    assert kwargs.get("thinking_budget") == 2048
    assert kwargs.get("include_thoughts") is True


def test_ws_chat_fallback_on_error(monkeypatch):
    async def failing_stream_gemini_reply(user_text: str, **kwargs):
        if False:
            yield "x"  # make this an async generator to satisfy async for
        raise RuntimeError("gemini failure")

    async def mock_stream_reply(user_text: str, **kwargs):
        yield "M"

    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key")
    # Force gemini path to raise inside stream_reply, which should fallback to mock internally.
    monkeypatch.setattr("app.services.llm.stream_gemini_reply", failing_stream_gemini_reply)
    # Ensure chat uses latest stream_reply implementation
    from app.services.llm import stream_reply as latest_stream_reply
    monkeypatch.setattr("app.api.v1.endpoints.chat.stream_reply", latest_stream_reply)

    test_db_url = os.getenv(
        "TEST_DATABASE_URL",
        (
            "postgresql+asyncpg://ai_secretary_user:ai_secretary_password@postgres_test:5432/ai_secretary_test"
            if os.getenv("DOCKERIZED") == "1"
            else "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"
        ),
    )
    app.dependency_overrides[get_async_db] = _override_db_factory(test_db_url)

    with TestClient(app) as tc:
        a = tc.post("/api/v1/assistants/", json={"name": "WS-Fallback"})
        assert a.status_code == 201
        assistant_id = a.json()["id"]

        c = tc.post("/api/v1/conversations/", json={"assistant_id": assistant_id, "title": "WS-Fallback"})
        assert c.status_code == 201
        conv_id = c.json()["id"]

        with tc.websocket_connect(f"/api/v1/ws/chat?conversation_id={conv_id}") as ws:
            ws.send_json({"type": "user_message", "text": "Hello"})
            got_token = False
            for _ in range(5):
                evt = ws.receive_json()
                if evt.get("type") == "token":
                    got_token = True
                    break
            assert got_token

    app.dependency_overrides.pop(get_async_db, None)
