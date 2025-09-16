# backend/app/schemas/assistant.py
import uuid
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

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
    """アシスタント作成時のスキーマ"""
    pass

class AssistantUpdate(AssistantBase):
    """既存の更新スキーマ（後方互換性のため維持）"""
    name: Optional[str] = Field(None, max_length=100)

class AssistantUpdateFinal(BaseModel):
    """最終版：全フィールドOptionalの更新スキーマ"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    default_llm_model: Optional[str] = Field(None, max_length=100)
    custom_system_prompt: Optional[str] = Field(None, max_length=2000)
    personality_template_id: Optional[uuid.UUID] = None
    voice_id: Optional[uuid.UUID] = None
    avatar_id: Optional[uuid.UUID] = None
    
    @validator('*', pre=True)
    def empty_str_to_none(cls, v):
        """空文字列をNoneに変換"""
        if v == '':
            return None
        return v

class Assistant(AssistantBase):
    """アシスタント取得時のレスポンススキーマ"""
    id: uuid.UUID
    user_id: uuid.UUID
    is_active: bool = True
    is_public: bool = False
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# エイリアス（互換性のため）
AssistantResponse = Assistant