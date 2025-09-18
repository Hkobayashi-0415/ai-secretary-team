# backend/app/models/phase2_models.py
"""
Phase 2: インテリジェント・ルーティング基盤のためのモデル定義
既存のデータベーススキーマに完全準拠
"""

import uuid
import enum
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, DateTime, Boolean,
    ForeignKey, JSON, Integer, ARRAY, Enum,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from .base import Base  # Base は循環回避のため base 直 import

# --- Mixins ---

class TimestampMixin:
    """タイムスタンプを管理するMixin"""
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


# --- Chat用 Enum（Pydantic スキーマが import する） ---

class MessageRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


# --- 1. スキル管理系（既存テーブルに準拠） ---

class SkillDefinition(Base, TimestampMixin):
    """スキル定義モデル（既存テーブル構造に完全準拠）"""
    __tablename__ = "skill_definitions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))  # NULL = システム提供
    skill_code = Column(String(10), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    skill_type = Column(String(50), nullable=False)  # 'analysis', 'research', 'creative'など
    configuration = Column(JSONB, nullable=False)  # LLMルーティングルールを格納
    is_public = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)

    # リレーションシップ
    assistant_skills = relationship(
        "AssistantSkill",
        back_populates="skill_definition",
        cascade="all, delete-orphan",
    )

    # ユニーク制約など（必要に応じて拡張）
    __table_args__ = (
        {"schema": None, "extend_existing": True},
    )


class AssistantSkill(Base, TimestampMixin):
    """アシスタントとスキルの関連付けモデル（既存テーブル構造に準拠）"""
    __tablename__ = "assistant_skills"

    assistant_id = Column(UUID(as_uuid=True), ForeignKey("ai_assistants.id", ondelete="CASCADE"), primary_key=True)
    skill_definition_id = Column(UUID(as_uuid=True), ForeignKey("skill_definitions.id", ondelete="CASCADE"), primary_key=True)
    is_enabled = Column(Boolean, nullable=False, default=True)
    priority = Column(Integer, nullable=False, default=1)  # スキルの優先順位
    custom_settings = Column(JSONB)  # この秘書専用の設定

    # リレーションシップ
    assistant = relationship("AIAssistant", backref="assistant_skills")
    skill_definition = relationship("SkillDefinition", back_populates="assistant_skills")


# --- 2. エージェント管理系（既存テーブルに準拠） ---

class Agent(Base, TimestampMixin):
    """エージェント（手順書）モデル"""
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    file_path = Column(String(255), nullable=False, unique=True)
    vector = Column(Vector(768))  # ベクトル検索用（pgvector使用）


# --- 3. コンポーネント系（既存テーブルに準拠） ---

class Voice(Base, TimestampMixin):
    """音声設定モデル"""
    __tablename__ = "voices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String(100), nullable=False)
    provider = Column(String(50))
    voice_id = Column(String(100))
    language = Column(String(10))
    gender = Column(String(20))
    age_group = Column(String(20))
    description = Column(Text)
    sample_url = Column(String(500))
    settings = Column(JSONB)
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)


class Avatar(Base, TimestampMixin):
    """アバター設定モデル"""
    __tablename__ = "avatars"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String(100), nullable=False)
    avatar_type = Column(String(50))
    image_url = Column(String(500))
    animated_url = Column(String(500))
    style = Column(String(50))
    gender = Column(String(20))
    age_appearance = Column(String(20))
    tags = Column(ARRAY(String))
    avatar_metadata = Column("metadata", JSONB)
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)


class PersonalityTemplate(Base, TimestampMixin):
    """パーソナリティテンプレートモデル"""
    __tablename__ = "personality_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String(100), nullable=False)
    description = Column(Text)
    template_type = Column(String(50))
    system_prompt = Column(Text)
    parameters = Column(JSONB)
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)


# --- 4. 会話管理系（既存テーブルに準拠） ---

class Conversation(Base, TimestampMixin):
    """会話セッションモデル"""
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    # AIAssistant のテーブル名に合わせる（多くは "ai_assistants"）
    assistant_id = Column(UUID(as_uuid=True), ForeignKey("ai_assistants.id"))
    title = Column(String(200))
    conversation_type = Column(String(50))  # 'chat', 'task', 'workflow'
    status = Column(String(50))  # 'active', 'archived'
    voice_enabled = Column(Boolean, default=False)
    voice_id = Column(UUID(as_uuid=True), ForeignKey("voices.id"))
    conversation_metadata = Column("metadata", JSONB)
    started_at = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))

    # リレーションシップ
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )


class Message(Base):
    """メッセージ履歴モデル"""
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    # 文字列 → Enum(MessageRole) に変更
    role = Column(
        Enum(MessageRole, name="message_role"),
        nullable=False,
    )
    content = Column(Text)
    content_type = Column(String(50))  # 'text', 'image', 'file'
    parent_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"))
    message_metadata = Column("metadata", JSONB)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # リレーションシップ
    conversation = relationship("Conversation", back_populates="messages")


# --- 5. ファイル管理系 ---

class File(Base, TimestampMixin):
    """ファイル管理モデル"""
    __tablename__ = "files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"))
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"))
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(100))
    file_size = Column(Integer)
    storage_path = Column(String(500))
    mime_type = Column(String(100))
    is_processed = Column(Boolean, default=False)
    file_metadata = Column("metadata", JSONB)


# --- 6. ユーザー設定系 ---

class UserPreference(Base, TimestampMixin):
    """ユーザー設定モデル"""
    __tablename__ = "user_preferences"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    theme = Column(String(50))
    language = Column(String(10))
    timezone = Column(String(50))
    notification_settings = Column(JSONB)
    privacy_settings = Column(JSONB)
    default_assistant_id = Column(UUID(as_uuid=True), ForeignKey("ai_assistants.id"))


# 明示エクスポート（Pydantic/他モジュールからの import 用）
__all__ = ["MessageRole", "Conversation", "Message"]
