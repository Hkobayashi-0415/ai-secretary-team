from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_async_db
from app.models.models import AIAssistant
from app.models.phase2_models import Conversation, Message
from app.schemas.conversation import (
    ConversationCreate,
    ConversationOut,
    MessageCreate,
    MessageOut,
)

router = APIRouter(prefix="/conversations", tags=["conversations"])

@router.post("/", response_model=ConversationOut, status_code=status.HTTP_201_CREATED)
async def create_conversation(payload: ConversationCreate, db: AsyncSession = Depends(get_async_db)):
    # assistant 存在チェック
    res = await db.execute(select(AIAssistant).where(AIAssistant.id == payload.assistant_id))
    assistant = res.scalars().first()
    if not assistant:
        raise HTTPException(status_code=404, detail="Assistant not found")

    # user_id 未指定なら assistant の所有者を採用
    user_id = getattr(payload, "user_id", None) or assistant.user_id

    conv = Conversation(
        user_id=user_id,
        assistant_id=payload.assistant_id,
        title=getattr(payload, "title", None),
        conversation_type=getattr(payload, "conversation_type", None),
        status=getattr(payload, "status", None),
        voice_enabled=getattr(payload, "voice_enabled", False),
        voice_id=getattr(payload, "voice_id", None),
        conversation_metadata=getattr(payload, "metadata", None),
    )
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return conv

@router.post("/{conversation_id}/messages", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
async def post_message(conversation_id: str, payload: MessageCreate, db: AsyncSession = Depends(get_async_db)):
    # 会話存在チェック（なければ 404）
    res = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conv = res.scalars().first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    msg = Message(
        conversation_id=conv.id,
        role=payload.role,
        content=payload.content,
        content_type=getattr(payload, "content_type", "text"),
        parent_id=getattr(payload, "parent_id", None),
        message_metadata=getattr(payload, "metadata", None),
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg
