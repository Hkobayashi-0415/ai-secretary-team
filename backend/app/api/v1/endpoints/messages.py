from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.deps import get_db
from app.models.phase2_models import Message, Conversation
from app.schemas.conversation import MessageCreate, MessageRead

router = APIRouter(prefix="/messages", tags=["messages"])

@router.post("", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
async def create_message(payload: MessageCreate, db: AsyncSession = Depends(get_db)):
    # conversation存在チェック
    c = await db.scalar(select(Conversation).where(Conversation.id == payload.conversation_id))
    if not c:
        raise HTTPException(status_code=404, detail="Conversation not found")
    m = Message(**payload.model_dump())
    db.add(m)
    await db.commit()
    await db.refresh(m)
    return m

@router.get("/by-conversation/{conversation_id}", response_model=list[MessageRead])
async def list_messages(conversation_id: str, db: AsyncSession = Depends(get_db), limit: int = 100, offset: int = 0):
    stmt = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).limit(limit).offset(offset)
    res = await db.execute(stmt)
    return list(res.scalars().all())

