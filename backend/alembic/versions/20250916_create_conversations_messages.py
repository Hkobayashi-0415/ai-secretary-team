"""create conversations & messages (idempotent)

Revision ID: 20250916_create_conversations_messages
Revises: 007_enable_vector_ext
Create Date: 2025-09-16
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects import postgresql as psql

# revision identifiers, used by Alembic.
revision = "20250916_create_conversations_messages"
down_revision = "007_enable_vector_ext"
branch_labels = None
depends_on = None


def _table_exists(table: str) -> bool:
    conn = op.get_bind()
    # public スキーマ前提。必要なら settings から読む
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
            sa.Column("user_id", psql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            # AIAssistant の実テーブル名に合わせる（多くは ai_assistants）
            sa.Column("assistant_id", psql.UUID(as_uuid=True), sa.ForeignKey("ai_assistants.id", ondelete="CASCADE"), nullable=False),
            sa.Column("title", sa.String(200)),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        )

    # --- message_role enum（無ければ作る） ---
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
            sa.Column("role", sa.Enum("user", "assistant", "system", name="message_role"), nullable=False),
            sa.Column("content", sa.Text),
            sa.Column("content_type", sa.String(50)),
            sa.Column("parent_id", psql.UUID(as_uuid=True), sa.ForeignKey("messages.id")),
            sa.Column("metadata", psql.JSONB),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        )
        op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])


def downgrade() -> None:
    # 依存関係の都合で messages → conversations の順で落とす
    op.execute("DROP TABLE IF EXISTS messages CASCADE")
    op.execute("DROP TABLE IF EXISTS conversations CASCADE")
    # Enum は他でも使う可能性があるので残す（必要なら DROP TYPE IF EXISTS message_role）
