"""create conversations & messages (idempotent)

Revision ID: 20250916_cnv_msg
Revises: 007_enable_vector_ext
Create Date: 2025-09-16
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects import postgresql as psql

# revision identifiers, used by Alembic.
revision = "20250916_cnv_msg"
down_revision = "007_enable_vector_ext"
branch_labels = None
depends_on = None


def _table_exists(table: str) -> bool:
    conn = op.get_bind()
    return conn.execute(text("SELECT to_regclass(:t)"), {"t": f"public.{table}"}).scalar() is not None


def _enum_exists(enum_name: str) -> bool:
    conn = op.get_bind()
    return conn.execute(
        text("SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = :n)"),
        {"n": enum_name},
    ).scalar()


def upgrade() -> None:
    # --- conversations ---
    if not _table_exists("conversations"):
        op.create_table(
            "conversations",
            sa.Column(
                "id",
                psql.UUID(as_uuid=True),
                primary_key=True,
                server_default=sa.text("gen_random_uuid()"),
                nullable=False,
            ),
            # Correct FKs: user_id -> users.id, assistant_id -> assistants.id
            sa.Column("user_id", psql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("assistant_id", psql.UUID(as_uuid=True), sa.ForeignKey("assistants.id", ondelete="CASCADE"), nullable=False),
            sa.Column("title", sa.String(200)),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        )

    # --- message_role enum ---
    if not _enum_exists("message_role"):
        op.execute(
            sa.text(
                "DO $$ BEGIN "
                "IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'message_role') THEN "
                "CREATE TYPE message_role AS ENUM ('user','assistant','system'); "
                "END IF; END $$;"
            )
        )

    # --- messages ---
    if not _table_exists("messages"):
        # Avoid implicit CREATE TYPE by SQLAlchemy for existing enum
        role_enum = sa.Enum("user", "assistant", "system", name="message_role", create_type=False)
        op.create_table(
            "messages",
            sa.Column(
                "id",
                psql.UUID(as_uuid=True),
                primary_key=True,
                server_default=sa.text("gen_random_uuid()"),
                nullable=False,
            ),
            sa.Column(
                "conversation_id",
                psql.UUID(as_uuid=True),
                sa.ForeignKey("conversations.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("role", role_enum, nullable=False),
            sa.Column("content", sa.Text),
            sa.Column("content_type", sa.String(50)),
            sa.Column("parent_id", psql.UUID(as_uuid=True), sa.ForeignKey("messages.id")),
            sa.Column("metadata", psql.JSONB),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        )
        op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS messages CASCADE")
    op.execute("DROP TABLE IF EXISTS conversations CASCADE")
