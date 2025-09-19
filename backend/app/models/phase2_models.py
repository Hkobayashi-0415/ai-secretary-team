# backend/app/models/phase2_models.py
from __future__ import annotations

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    Integer,
    CheckConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship, synonym
from app.db.base import Base  # 統一された Base を使用

GEN_UUID = text("gen_random_uuid()")
SERVER_DEFAULT_TRUE = text("true")
SERVER_DEFAULT_NOW = text("now()")
JEMPTY = text("'{}'::jsonb")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=GEN_UUID)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    assistant_id = Column(UUID(as_uuid=True), ForeignKey("assistants.id", ondelete="CASCADE"), nullable=False)

    title = Column(String(255))
    conversation_type = Column(String(50), nullable=False, server_default=text("'chat'::character varying"))
    status = Column(String(20), nullable=False, server_default=text("'active'::character varying"))

    voice_enabled = Column(Boolean, nullable=False, server_default=SERVER_DEFAULT_TRUE)
    # Optional reference to a voice asset; no FK to avoid missing table dependency
    voice_id = Column(UUID(as_uuid=True))

    # DB のカラム名は "metadata"、ORM 側も metadata に統一
    meta = Column("metadata", JSONB, server_default=JEMPTY)
    conversation_metadata = synonym("meta")

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=SERVER_DEFAULT_NOW)
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=SERVER_DEFAULT_NOW)

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=GEN_UUID)

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
    meta = Column("metadata", JSONB, server_default=JEMPTY)
    message_metadata = synonym("meta")

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=SERVER_DEFAULT_NOW)
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=SERVER_DEFAULT_NOW)

    __table_args__ = (
        CheckConstraint("role in ('user','assistant','system')", name="messages_role_check"),
        CheckConstraint("content_type in ('text','image','file','audio')", name="messages_content_type_check"),
    )

    conversation = relationship("Conversation", back_populates="messages", passive_deletes=True)
    parent = relationship("Message", remote_side=[id])


# ---- routing 用の軽量モデル ----
class Agent(Base):
    __tablename__ = "agents"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=GEN_UUID)
    name = Column(String(100), nullable=False, unique=True)


class SkillDefinition(Base):
    __tablename__ = "skill_definitions"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=GEN_UUID)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)


class AssistantSkill(Base):
    __tablename__ = "assistant_skills"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=GEN_UUID)
    assistant_id = Column(UUID(as_uuid=True), ForeignKey("assistants.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skill_definitions.id", ondelete="CASCADE"), nullable=False)
    level = Column(Integer, server_default=text("0"))
