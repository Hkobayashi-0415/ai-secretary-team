# backend/app/api/v1/endpoints/conversations.py
from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.models.models import AIAssistant
from app.models.phase2_models import Conversation, Message
from app.schemas.conversation import (
    ConversationCreate,
    ConversationOut,
    ConversationUpdate,
    MessageCreate,
    MessageOut,
    MessagePage,
)

router = APIRouter()

@router.post(
    "/",
    response_model=ConversationOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_conversation(
    payload: ConversationCreate,
    db: AsyncSession = Depends(get_async_db),
):
    # assistant check + user_id fallback
    res = await db.execute(select(AIAssistant).where(AIAssistant.id == payload.assistant_id))
    assistant = res.scalars().first()
    if not assistant:
        raise HTTPException(status_code=404, detail="Assistant not found")

    user_id = payload.user_id or assistant.user_id

    conv = Conversation(
        user_id=user_id,
        assistant_id=payload.assistant_id,
        title=payload.title,
        conversation_type=(payload.conversation_type or "chat"),
        status="active",
        # voice_enabled defaults to true in DB; explicit is fine too
        voice_enabled=True if payload.voice_enabled is None else payload.voice_enabled,
        voice_id=payload.voice_id,
        # ORM 属性は metadata（DB のカラム名も "metadata"）
        metadata=payload.metadata,
    )
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return conv


@router.post(
    "/{conversation_id}/messages",
    response_model=MessageOut,
    status_code=status.HTTP_201_CREATED,
)
async def add_message(
    conversation_id: uuid.UUID,
    payload: MessageCreate,
    db: AsyncSession = Depends(get_async_db),
):
    # conversation存在チェック
    res = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conv = res.scalars().first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if not payload.content:
        raise HTTPException(status_code=400, detail="content is required")

    msg = Message(
        conversation_id=conversation_id,
        role=(payload.role or "user"),
        content=payload.content,
        content_type=(payload.content_type or "text"),
        # ORM 属性は metadata（DB のカラム名も "metadata"）
        metadata=payload.metadata,
        # IMPORTANT: match DB column name
        parent_message_id=payload.parent_id,
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg


@router.get(
    "/{conversation_id}/messages",
    response_model=List[MessageOut],
    status_code=status.HTTP_200_OK,
)
async def list_messages(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
):
    # optional: check existence
    res = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    if not res.scalars().first():
        raise HTTPException(status_code=404, detail="Conversation not found")

    q = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    res = await db.execute(q)
    return list(res.scalars().all())


@router.get(
    "/{conversation_id}/messages/page",
    response_model=MessagePage,
    status_code=status.HTTP_200_OK,
)
async def list_messages_paged(
    conversation_id: uuid.UUID,
    before_id: uuid.UUID | None = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_async_db),
):
    # conversation existence check
    res = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    if not res.scalars().first():
        raise HTTPException(status_code=404, detail="Conversation not found")

    rows: list[Message]
    if before_id is not None:
        # older than the anchor, return ascending
        anchor = await db.get(Message, before_id)
        if anchor is None or anchor.conversation_id != conversation_id:
            return MessagePage(messages=[], has_more=False)
        q = (
            select(Message)
            .where((Message.conversation_id == conversation_id) & (Message.created_at < anchor.created_at))
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        rows = (await db.execute(q)).scalars().all()
    else:
        # latest page: take last `limit` by desc, then return asc
        q_desc = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        latest_desc = (await db.execute(q_desc)).scalars().all()
        rows = list(reversed(latest_desc))

    has_more = False
    if rows:
        first_ts = rows[0].created_at
        older_exists_q = (
            select(Message.id)
            .where((Message.conversation_id == conversation_id) & (Message.created_at < first_ts))
            .limit(1)
        )
        has_more = (await db.execute(older_exists_q)).first() is not None

    return MessagePage(messages=rows, has_more=has_more)


# ---- Additional CRUD for Conversation ----

@router.get(
    "/{conversation_id}",
    response_model=ConversationOut,
    status_code=status.HTTP_200_OK,
)
async def get_conversation(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
):
    res = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conv = res.scalars().first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@router.get(
    "/",
    response_model=List[ConversationOut],
    status_code=status.HTTP_200_OK,
)
async def list_conversations(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_async_db),
):
    q = (
        select(Conversation)
        .order_by(Conversation.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    res = await db.execute(q)
    return list(res.scalars().all())


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_conversation(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
):
    res = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conv = res.scalars().first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    await db.delete(conv)
    await db.commit()
    return None


@router.patch(
    "/{conversation_id}",
    response_model=ConversationOut,
    status_code=status.HTTP_200_OK,
)
async def update_conversation(
    conversation_id: uuid.UUID,
    payload: ConversationUpdate,
    db: AsyncSession = Depends(get_async_db),
):
    res = await db.execute(select(Conversation).where(Conversation.id == conversation_id))
    conv = res.scalars().first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if payload.title is not None:
        conv.title = payload.title or None

    await db.commit()
    await db.refresh(conv)
    return conv
