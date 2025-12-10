from pydantic import BaseModel, Field
from typing import Optional


class TextGenerationRequest(BaseModel):
    prompt: str = Field(..., description="User prompt text")
    model: Optional[str] = Field(None, description="Gemini model id")
    provider: Optional[str] = Field(None, description="gemini or mock override")
    stream: bool = Field(False, description="Use websocket for streaming; REST returns 400 if true")
    thinking_level: Optional[str] = Field(None, description="Gemini 3: low/high")
    thinking_budget: Optional[int] = Field(None, description="Gemini 2.5: budget tokens")
    include_thoughts: bool = Field(False, description="Include thought summaries when supported")


class TextGenerationResponse(BaseModel):
    text: str
    thoughts: Optional[str] = None
    provider: str
    model: Optional[str] = None


class ImageGenerationRequest(BaseModel):
    prompt: str = Field(..., description="Image prompt")
    model: Optional[str] = Field(None, description="Image model id (e.g., imagen-3.0-*)")
    provider: Optional[str] = Field(None, description="gemini or mock override")
    size: Optional[str] = Field(None, description="e.g. 512x512 (mock only)")


class ImageGenerationResponse(BaseModel):
    mime_type: str
    data_base64: str
    provider: str
    model: Optional[str] = None
