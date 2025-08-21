# backend/app/schemas/assistant.py
import uuid
from pydantic import BaseModel, Field
from typing import Optional

class AssistantBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    default_llm_model: Optional[str] = Field("gemini-pro", max_length=100)

class AssistantCreate(AssistantBase):
    pass

class AssistantUpdate(AssistantBase):
    name: Optional[str] = Field(None, max_length=100)

class Assistant(AssistantBase):
    id: uuid.UUID
    user_id: uuid.UUID
    
    class Config:
        from_attributes = True