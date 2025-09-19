# backend/app/scripts/ensure_default_user.py
from __future__ import annotations
import contextlib
from typing import Optional, Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.models.models import User  # 既存モデル

async def ensure_default_user(session: Optional[AsyncSession] = None) -> None:
    owns = False
    engine = None
    if session is None:
        engine = create_async_engine(settings.DATABASE_URL, future=True)
        session_maker = async_sessionmaker(engine, expire_on_commit=False)
        session = session_maker()
        owns = True

    try:
        async with session as db:  # type: ignore[assignment]
            # 既に1件あれば終了
            exists = await db.scalar(select(func.count()).select_from(User))
            if exists and int(exists) > 0:
                return

            # 必須列に応じて埋める（堅牢化）
            cols = {c.name: c for c in User.__table__.columns}
            payload: dict[str, Any] = {}

            if "email" in cols:
                payload["email"] = getattr(settings, "DEFAULT_ADMIN_EMAIL", "default_admin@example.com")
            if "username" in cols:
                payload["username"] = getattr(settings, "DEFAULT_ADMIN_NAME", "default_admin")
            elif "name" in cols:
                payload["name"] = getattr(settings, "DEFAULT_ADMIN_NAME", "default_admin")

            # よくある非NULL列をケア
            for key in ("hashed_password", "password_hash", "password"):
                if key in cols and not cols[key].nullable:
                    payload[key] = payload.get(key) or "!"  # ダミー値（ハッシュ不要なスキーマ想定）
            if "is_active" in cols and not cols["is_active"].nullable:
                payload["is_active"] = True
            if "is_superuser" in cols and not cols["is_superuser"].nullable:
                payload["is_superuser"] = True
            if "role" in cols and not cols["role"].nullable and "role" not in payload:
                payload["role"] = "admin"

            user = User(**payload)  # type: ignore[arg-type]
            db.add(user)
            await db.commit()
    finally:
        if owns and engine is not None:
            with contextlib.suppress(Exception):
                await engine.dispose()
