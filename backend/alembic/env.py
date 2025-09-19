from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Alembic Config object
config = context.config

# Logger
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Ensure only app models are imported (never API/services)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_ROOT = os.path.abspath(os.path.join(BASE_DIR, "app"))
if APP_ROOT not in sys.path:
    sys.path.insert(0, os.path.abspath(os.path.join(BASE_DIR, "..")))

from app.db.base import Base
import app.models.models          # users / assistants
import app.models.phase2_models   # conversations / messages / others

target_metadata = Base.metadata


def run_migrations_offline():
    url = os.getenv("DATABASE_URL")
    if not url:
        async_url = os.getenv("DATABASE_URL", "")
        url = async_url.replace("+asyncpg", "")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    configuration = config.get_section(config.config_ini_section) or {}
    url = os.getenv("DATABASE_URL", "")
    if url:
        configuration["sqlalchemy.url"] = url.replace("+asyncpg", "")
    connectable = engine_from_config(configuration, prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

