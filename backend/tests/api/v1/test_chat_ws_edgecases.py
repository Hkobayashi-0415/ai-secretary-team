import os
import uuid
import pytest
from starlette.testclient import TestClient

from app.main import app
from app.core.database import get_async_db
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.db.base import Base
from sqlalchemy import select
from app.models.models import User
from starlette.websockets import WebSocketDisconnect


def _override_db_factory(test_db_url: str):
    initialized = {"done": False}

    async def override_get_db():
        engine = create_async_engine(test_db_url, future=True)
        SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

        if not initialized["done"]:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
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


def test_ws_chat_empty_message_emits_error():
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
        a = tc.post("/api/v1/assistants/", json={"name": "WS-EC"})
        assert a.status_code == 201
        assistant_id = a.json()["id"]

        c = tc.post("/api/v1/conversations/", json={"assistant_id": assistant_id, "title": "WS-EC"})
        assert c.status_code == 201
        conv_id = c.json()["id"]

        with tc.websocket_connect(f"/api/v1/ws/chat?conversation_id={conv_id}") as ws:
            ws.send_json({"type": "user_message", "text": ""})
            evt = ws.receive_json()
            assert evt.get("type") == "error"
            assert evt.get("message") == "empty text"

    app.dependency_overrides.pop(get_async_db, None)


def test_ws_chat_invalid_conversation_id_closes_with_4404():
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
        bad_id = uuid.uuid4()
        with pytest.raises(WebSocketDisconnect) as exc:
            with tc.websocket_connect(f"/api/v1/ws/chat?conversation_id={bad_id}"):
                pass
        assert exc.value.code == 4404

    app.dependency_overrides.pop(get_async_db, None)
