# backend/alembic/env.py
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config # <- 非同期エンジンを使います

from alembic import context
from app.core.config import settings

# この部分は先ほど編集していただいた通りです
from app.models.models import Base
# Ensure Phase2 models are imported so their tables register on Base.metadata
from app.models import phase2_models  # noqa: F401
try:
    from app.scripts.ensure_default_user import ensure_default_user  # type: ignore
except Exception:
    ensure_default_user = None  # type: ignore
target_metadata = Base.metadata

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Ensure sqlalchemy.url is set (fallback to env settings)
if config.get_main_option("sqlalchemy.url") in (None, ""):
    # Use app settings DATABASE_URL when not provided via alembic.ini
    config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """マイグレーションを実行するためのヘルパー関数"""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Create engine from configured URL (now ensured above)
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # 非同期で接続し、同期的なマイグレーション関数を呼び出します
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

    # Optionally ensure default user after migrations
    if 'ensure_default_user' in globals() and ensure_default_user:
        try:
            await ensure_default_user()  # type: ignore[misc]
        except TypeError:
            ensure_default_user()  # type: ignore[misc]


if context.is_offline_mode():
    run_migrations_offline()
else:
    # 非同期関数をasyncioで実行します
    asyncio.run(run_migrations_online())
