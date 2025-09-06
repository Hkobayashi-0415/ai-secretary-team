from pydantic import BaseModel
from uuid import UUID

class RoutingRequest(BaseModel):
    """ルーティングリクエストのスキーマ"""
    prompt: str
    assistant_id: UUID