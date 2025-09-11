# backend/app/schemas/assistant.py
import uuid
from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field, ConfigDict, model_validator


class AssistantBase(BaseModel):
    """アシスタントの基本フィールド"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    default_llm_model: Optional[str] = Field("gemini-pro", max_length=100)
    custom_system_prompt: Optional[str] = Field(None, max_length=2000)
    personality_template_id: Optional[uuid.UUID] = None
    voice_id: Optional[uuid.UUID] = None
    avatar_id: Optional[uuid.UUID] = None


class AssistantCreate(AssistantBase):
    """アシスタント作成スキーマ"""
    pass


class AssistantUpdate(AssistantBase):
    """既存の更新スキーマ（後方互換のため維持）"""
    name: Optional[str] = Field(None, max_length=100)


class AssistantUpdateFinal(BaseModel):
    """最終版：全フィールド Optional の更新スキーマ"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    default_llm_model: Optional[str] = Field(None, max_length=100)
    custom_system_prompt: Optional[str] = Field(None, max_length=2000)
    personality_template_id: Optional[uuid.UUID] = None
    voice_id: Optional[uuid.UUID] = None
    avatar_id: Optional[uuid.UUID] = None

    @model_validator(mode="before")
    @classmethod
    def empty_str_to_none(cls, data: Any):
        """空文字列を None に変換（v2 互換の一括前処理）"""
        if isinstance(data, dict):
            return {k: (None if v == "" else v) for k, v in data.items()}
        return data


class Assistant(AssistantBase):
    """レスポンス用スキーマ"""
    id: uuid.UUID
    user_id: uuid.UUID
    is_active: bool = True
    is_public: bool = False
    created_at: datetime
    updated_at: datetime

    # Pydantic v2 スタイル設定
    model_config = ConfigDict(from_attributes=True)


# エイリアス（互換性のため）
AssistantResponse = Assistant
