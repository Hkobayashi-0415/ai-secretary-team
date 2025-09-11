from uuid import UUID

from pydantic import BaseModel


class RoutingRequest(BaseModel):
    """ルーティングリクエストのスキーマ"""

    prompt: str
    assistant_id: UUID
