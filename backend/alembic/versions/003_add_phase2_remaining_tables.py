"""Add phase2 remaining tables (excluding already existing skill tables)

Revision ID: 003_add_phase2_remaining_tables
Revises: 002_add_default_local_user
Create Date: 2025-08-30 23:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "003_add_phase2_remaining_tables"
down_revision = "002_add_default_local_user"
branch_labels = None
depends_on = None


def _table_exists(inspector, name: str, schema: str | None = None) -> bool:
    return name in inspector.get_table_names(schema=schema)


def _column_exists(inspector, table: str, column: str, schema: str | None = None) -> bool:
    return any(c["name"] == column for c in inspector.get_columns(table, schema=schema))


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # --- pgvector を“あるときだけ”有効化（未インストール環境では何もしない・失敗しない）
    op.execute(
        """
        DO $$
        BEGIN
          IF EXISTS (SELECT 1 FROM pg_available_extensions WHERE name = 'vector') THEN
            CREATE EXTENSION IF NOT EXISTS vector;
          END IF;
        END$$;
        """
    )

    # --- agents に vector カラムを“テーブルがある場合かつ未作成の場合のみ”追加
    if _table_exists(inspector, "agents") and not _column_exists(inspector, "agents", "vector"):
        op.add_column("agents", sa.Column("vector", sa.Text(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _table_exists(inspector, "agents") and _column_exists(inspector, "agents", "vector"):
        op.drop_column("agents", "vector")
