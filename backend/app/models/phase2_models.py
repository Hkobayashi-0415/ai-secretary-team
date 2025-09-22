"""SQLAlchemy models used by the routing subsystem.

The original design targets PostgreSQL, however the routing tests rely on an
in-memory SQLite database.  To keep the models portable we provide Python-side
defaults in addition to server defaults and avoid PostgreSQL only expressions
when running outside of that dialect.
"""

from __future__ import annotations

import os
import uuid

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship, synonym

from app.db.base import Base  # 統一された Base を使用

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://")
POSTGRESQL = DATABASE_URL.startswith("postgresql")

GEN_UUID = text("gen_random_uuid()")
SERVER_DEFAULT_TRUE = text("true") if POSTGRESQL else text("1")
SERVER_DEFAULT_NOW = text("now()") if POSTGRESQL else text("CURRENT_TIMESTAMP")
JEMPTY = text("'{}'::jsonb") if POSTGRESQL else text("'{}'")
JEMPTY_ARRAY = text("'[]'::jsonb") if POSTGRESQL else text("'[]'")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=GEN_UUID,
        default=uuid.uuid4,
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    assistant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("assistants.id", ondelete="CASCADE"),
        nullable=False,
    )

    title = Column(String(255))
    conversation_type = Column(
        String(50), nullable=False, server_default=text("'chat'::character varying")
    )
    status = Column(
        String(20), nullable=False, server_default=text("'active'::character varying")
    )

    voice_enabled = Column(Boolean, nullable=False, server_default=SERVER_DEFAULT_TRUE)
    # Optional reference to a voice asset; no FK to avoid missing table dependency
    voice_id = Column(UUID(as_uuid=True))

    # DB のカラム名は "metadata"、ORM 側も metadata に統一
    meta = Column("metadata", JSONB, server_default=JEMPTY, default=dict)
    conversation_metadata = synonym("meta")

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=SERVER_DEFAULT_NOW
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=SERVER_DEFAULT_NOW
    )

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=GEN_UUID,
        default=uuid.uuid4,
    )

    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    parent_message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"))

    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String(20), server_default=text("'text'::character varying"))

    # DB は "metadata"、ORM 側も metadata に統一
    meta = Column("metadata", JSONB, server_default=JEMPTY, default=dict)
    message_metadata = synonym("meta")

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=SERVER_DEFAULT_NOW
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=SERVER_DEFAULT_NOW
    )

    __table_args__ = (
        CheckConstraint(
            "role in ('user','assistant','system')", name="messages_role_check"
        ),
        CheckConstraint(
            "content_type in ('text','image','file','audio')",
            name="messages_content_type_check",
        ),
    )

    conversation = relationship(
        "Conversation", back_populates="messages", passive_deletes=True
    )
    parent = relationship("Message", remote_side=[id])


# ---- routing 用の軽量モデル ----
class SkillDefinition(Base):
    __tablename__ = "skill_definitions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=GEN_UUID,
        default=uuid.uuid4,
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    skill_code = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    skill_type = Column(String(50), nullable=False)
    configuration = Column(JSONB, nullable=False, server_default=JEMPTY, default=dict)
    is_public = Column(
        Boolean,
        nullable=False,
        server_default=text("false") if POSTGRESQL else text("0"),
        default=False,
    )
    is_active = Column(
        Boolean, nullable=False, server_default=SERVER_DEFAULT_TRUE, default=True
    )
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=SERVER_DEFAULT_NOW
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=SERVER_DEFAULT_NOW
    )

    assistant_links = relationship(
        "AssistantSkill",
        back_populates="skill",
        cascade="all, delete-orphan",
    )


class Agent(Base):
    __tablename__ = "agents"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=GEN_UUID,
        default=uuid.uuid4,
    )
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    category = Column(String(50))
    tags = Column(JSONB, server_default=JEMPTY_ARRAY, default=list)
    file_path = Column(String(255))
    system_prompt = Column(Text)
    instructions = Column(Text)
    meta = Column("metadata", JSONB, server_default=JEMPTY, default=dict)
    agent_metadata = synonym("meta")
    embedding = Column(JSONB, default=dict)
    is_active = Column(
        Boolean, nullable=False, server_default=SERVER_DEFAULT_TRUE, default=True
    )
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=SERVER_DEFAULT_NOW
    )

    prompts = relationship(
        "PromptTemplate",
        back_populates="agent",
        cascade="all, delete-orphan",
    )


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=GEN_UUID,
        default=uuid.uuid4,
    )
    agent_id = Column(
        UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False
    )
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    meta = Column("metadata", JSONB, server_default=JEMPTY, default=dict)
    prompt_metadata = synonym("meta")
    tags = Column(JSONB, server_default=JEMPTY_ARRAY, default=list)
    embedding = Column(JSONB, default=dict)
    is_active = Column(
        Boolean, nullable=False, server_default=SERVER_DEFAULT_TRUE, default=True
    )
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=SERVER_DEFAULT_NOW
    )

    agent = relationship("Agent", back_populates="prompts")


class AssistantSkill(Base):
    __tablename__ = "assistant_skills"
    assistant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("assistants.id", ondelete="CASCADE"),
        primary_key=True,
    )
    skill_definition_id = Column(
        UUID(as_uuid=True),
        ForeignKey("skill_definitions.id", ondelete="CASCADE"),
        primary_key=True,
    )
    is_enabled = Column(
        Boolean, nullable=False, server_default=SERVER_DEFAULT_TRUE, default=True
    )
    priority = Column(Integer, nullable=False, server_default=text("1"), default=1)
    custom_settings = Column(JSONB, default=dict)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=SERVER_DEFAULT_NOW
    )

    assistant = relationship("AIAssistant", backref="skills")
    skill = relationship("SkillDefinition", back_populates="assistant_links")
