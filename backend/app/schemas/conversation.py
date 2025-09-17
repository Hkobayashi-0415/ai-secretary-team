from __future__ import annotations
from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.phase2_models import MessageRole

class ConversationCreate(BaseModel):
    assistant_id: UUID
    user_id: Optional[UUID] = None
    title: Optional[str] = None

class ConversationRead(BaseModel):
    id: UUID
    assistant_id: UUID
    user_id: UUID
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class MessageCreate(BaseModel):
    conversation_id: Optional[UUID] = None
    role: MessageRole = Field(default=MessageRole.user)
    content: str

class MessageRead(BaseModel):
    id: UUID
    conversation_id: UUID
    role: MessageRole
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
