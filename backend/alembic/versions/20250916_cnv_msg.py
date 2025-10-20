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
            sa.Column("title", sa.String(255)),
            sa.Column("conversation_type", sa.String(50), server_default=sa.text("'chat'"), nullable=False),
            sa.Column("status", sa.String(20), server_default=sa.text("'active'"), nullable=False),
            sa.Column("voice_enabled", sa.Boolean, server_default=sa.text("true"), nullable=False),
            sa.Column("voice_id", psql.UUID(as_uuid=True)),
            sa.Column("metadata", psql.JSONB, server_default=sa.text("'{}'::jsonb")),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        )

    # Ensure conversations/messages optional columns match ORM expectations if tables pre-exist
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='conversations') THEN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='conversations' AND column_name='conversation_type') THEN
                    ALTER TABLE conversations ADD COLUMN conversation_type varchar(50) NOT NULL DEFAULT 'chat';
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='conversations' AND column_name='status') THEN
                    ALTER TABLE conversations ADD COLUMN status varchar(20) NOT NULL DEFAULT 'active';
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='conversations' AND column_name='voice_enabled') THEN
                    ALTER TABLE conversations ADD COLUMN voice_enabled boolean NOT NULL DEFAULT true;
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='conversations' AND column_name='voice_id') THEN
                    ALTER TABLE conversations ADD COLUMN voice_id uuid;
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='conversations' AND column_name='metadata') THEN
                    ALTER TABLE conversations ADD COLUMN metadata jsonb DEFAULT '{}'::jsonb;
                END IF;
            END IF;

            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='messages') THEN
                IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='messages' AND column_name='parent_id') AND
                   NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='messages' AND column_name='parent_message_id') THEN
                    ALTER TABLE messages RENAME COLUMN parent_id TO parent_message_id;
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='messages' AND column_name='updated_at') THEN
                    ALTER TABLE messages ADD COLUMN updated_at timestamptz NOT NULL DEFAULT now();
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='messages' AND column_name='metadata') THEN
                    ALTER TABLE messages ADD COLUMN metadata jsonb DEFAULT '{}'::jsonb;
                END IF;
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='messages' AND column_name='content_type') THEN
                    ALTER TABLE messages ADD COLUMN content_type varchar(20) DEFAULT 'text';
                END IF;
            END IF;
        END $$;
        """
    )

    # message role: ORM uses String + CHECK; avoid native ENUM to match ORM

    # --- messages ---
    if not _table_exists("messages"):
        # Use String with CHECK constraint via ORM; keep DB neutral on ENUM
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
            sa.Column("role", sa.String(20), nullable=False),
            sa.Column("content", sa.Text, nullable=False),
            sa.Column("content_type", sa.String(20), server_default=sa.text("'text'")),
            sa.Column("parent_message_id", psql.UUID(as_uuid=True), sa.ForeignKey("messages.id")),
            sa.Column("metadata", psql.JSONB, server_default=sa.text("'{}'::jsonb")),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        )
        op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS messages CASCADE")
    op.execute("DROP TABLE IF EXISTS conversations CASCADE")
