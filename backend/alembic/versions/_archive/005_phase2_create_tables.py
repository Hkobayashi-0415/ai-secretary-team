"""Create Phase2 core tables if missing

Revision ID: 005_phase2_create_tables
Revises: 004_add_sample_data
Create Date: 2025-09-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '005_phase2_create_tables'
down_revision: Union[str, None] = '003_add_phase2_remaining_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(conn, name: str) -> bool:
    insp = inspect(conn)
    return name in insp.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()

    # 1) skill_definitions
    if not _has_table(bind, 'skill_definitions'):
        op.create_table(
            'skill_definitions',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE')),
            sa.Column('skill_code', sa.String(10), nullable=False),
            sa.Column('name', sa.String(100), nullable=False),
            sa.Column('description', sa.Text(), nullable=False),
            sa.Column('skill_type', sa.String(50), nullable=False),
            sa.Column('configuration', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
            sa.Column('is_public', sa.Boolean(), nullable=False, server_default=sa.text('false')),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        )

    # 2) assistant_skills (association)
    if not _has_table(bind, 'assistant_skills'):
        op.create_table(
            'assistant_skills',
            sa.Column('assistant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('assistants.id', ondelete='CASCADE'), primary_key=True),
            sa.Column('skill_definition_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('skill_definitions.id', ondelete='CASCADE'), primary_key=True),
            sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
            sa.Column('priority', sa.Integer(), nullable=False, server_default='1'),
            sa.Column('custom_settings', postgresql.JSONB(astext_type=sa.Text())),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        )

    # 3) agents
    if not _has_table(bind, 'agents'):
        op.create_table(
            'agents',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('name', sa.String(100), nullable=False, unique=True),
            sa.Column('description', sa.Text()),
            sa.Column('file_path', sa.String(255), nullable=False, unique=True),
            # Keep vector as TEXT to avoid requiring pgvector immediately
            sa.Column('vector', sa.Text()),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        )

    # 4) voices
    if not _has_table(bind, 'voices'):
        op.create_table(
            'voices',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE')),
            sa.Column('name', sa.String(100), nullable=False),
            sa.Column('provider', sa.String(50)),
            sa.Column('voice_id', sa.String(100)),
            sa.Column('language', sa.String(10)),
            sa.Column('gender', sa.String(20)),
            sa.Column('age_group', sa.String(20)),
            sa.Column('description', sa.Text()),
            sa.Column('sample_url', sa.String(500)),
            sa.Column('settings', postgresql.JSONB(astext_type=sa.Text())),
            sa.Column('is_active', sa.Boolean(), server_default=sa.text('true')),
            sa.Column('is_public', sa.Boolean(), server_default=sa.text('false')),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        )

    # 5) avatars
    if not _has_table(bind, 'avatars'):
        op.create_table(
            'avatars',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE')),
            sa.Column('name', sa.String(100), nullable=False),
            sa.Column('avatar_type', sa.String(50)),
            sa.Column('image_url', sa.String(500)),
            sa.Column('animated_url', sa.String(500)),
            sa.Column('style', sa.String(50)),
            sa.Column('gender', sa.String(20)),
            sa.Column('age_appearance', sa.String(20)),
            sa.Column('tags', postgresql.ARRAY(sa.String())),
            sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text())),
            sa.Column('is_active', sa.Boolean(), server_default=sa.text('true')),
            sa.Column('is_public', sa.Boolean(), server_default=sa.text('false')),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        )

    # 6) personality_templates
    if not _has_table(bind, 'personality_templates'):
        op.create_table(
            'personality_templates',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE')),
            sa.Column('name', sa.String(100), nullable=False),
            sa.Column('description', sa.Text()),
            sa.Column('personality_type', sa.String(50)),
            sa.Column('system_prompt', sa.Text()),
            sa.Column('characteristics', postgresql.JSONB(astext_type=sa.Text())),
            sa.Column('is_active', sa.Boolean(), server_default=sa.text('true')),
            sa.Column('is_public', sa.Boolean(), server_default=sa.text('false')),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        )

    # 7) conversations
    if not _has_table(bind, 'conversations'):
        op.create_table(
            'conversations',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('assistant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('assistants.id')),
            sa.Column('title', sa.String(255)),
            sa.Column('conversation_type', sa.String(50)),
            sa.Column('status', sa.String(20)),
            sa.Column('voice_enabled', sa.Boolean(), server_default=sa.text('false')),
            sa.Column('voice_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('voices.id')),
            sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text())),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        )

    # 8) messages
    if not _has_table(bind, 'messages'):
        op.create_table(
            'messages',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('conversation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False),
            sa.Column('role', sa.String(50), nullable=False),
            sa.Column('content', sa.Text()),
            sa.Column('content_type', sa.String(50)),
            sa.Column('parent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('messages.id')),
            sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text())),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        )

    # 9) files
    if not _has_table(bind, 'files'):
        op.create_table(
            'files',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('conversation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('conversations.id')),
            sa.Column('message_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('messages.id')),
            sa.Column('file_name', sa.String(255), nullable=False),
            sa.Column('file_type', sa.String(100)),
            sa.Column('file_size', sa.Integer()),
            sa.Column('storage_path', sa.String(500)),
            sa.Column('mime_type', sa.String(100)),
            sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text())),
            sa.Column('is_processed', sa.Boolean(), server_default=sa.text('false')),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        )

    # 10) user_preferences
    if not _has_table(bind, 'user_preferences'):
        op.create_table(
            'user_preferences',
            sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
            sa.Column('theme', sa.String(50)),
            sa.Column('language', sa.String(10)),
            sa.Column('timezone', sa.String(50)),
            sa.Column('notification_settings', postgresql.JSONB(astext_type=sa.Text())),
            sa.Column('privacy_settings', postgresql.JSONB(astext_type=sa.Text())),
            sa.Column('default_assistant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('assistants.id')),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        )


def downgrade() -> None:
    # Drop tables in reverse order if they exist
    bind = op.get_bind()
    for name in [
        'user_preferences', 'files', 'messages', 'conversations',
        'personality_templates', 'avatars', 'voices', 'agents',
        'assistant_skills', 'skill_definitions'
    ]:
        if _has_table(bind, name):
            op.drop_table(name)
