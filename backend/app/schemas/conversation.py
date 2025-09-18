# Pydantic v1/v2 どちらでも動く互換ベース
try:
    from pydantic import BaseModel, ConfigDict
    class ORMBase(BaseModel):
        model_config = ConfigDict(from_attributes=True)
except Exception:
    from pydantic import BaseModel
    class ORMBase(BaseModel):
        class Config:
            orm_mode = True

from typing import Optional
from uuid import UUID
from datetime import datetime

# --- Conversations ---
class ConversationCreate(ORMBase):
    assistant_id: UUID
    user_id: Optional[UUID] = None
    title: Optional[str] = None
    conversation_type: Optional[str] = None
    status: Optional[str] = None
    voice_enabled: Optional[bool] = False
    voice_id: Optional[UUID] = None
    metadata: Optional[dict] = None

class ConversationOut(ORMBase):
    id: UUID
    user_id: UUID
    assistant_id: Optional[UUID] = None
    title: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# --- Messages ---
class MessageCreate(ORMBase):
    role: str
    content: str
    content_type: Optional[str] = "text"
    parent_id: Optional[UUID] = None
    metadata: Optional[dict] = None

class MessageOut(ORMBase):
    id: UUID
    conversation_id: UUID
    role: str
    content: Optional[str] = None
    content_type: Optional[str] = None
    parent_id: Optional[UUID] = None
    created_at: Optional[datetime] = None
