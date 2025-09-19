import uuid
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field

Role = Literal["user", "assistant", "system", "tool"]

class MessageCreate(BaseModel):
    role: Role = Field(..., description="user|assistant|system|tool")
    content: str = Field(..., min_length=1)

class Message(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    role: Role
    content: str
    llm_model: Optional[str] = None
    token_count: Optional[int] = None
    created_at: datetime
    model_config = dict(from_attributes=True)
