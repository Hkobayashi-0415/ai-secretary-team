# backend/app/api/v1/endpoints/users.py
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_async_db
from app.models.models import User
from app.scripts.ensure_default_user import ensure_default_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/default")
async def get_or_create_default_user(db: AsyncSession = Depends(get_async_db)):
    res = await db.execute(select(User).limit(1))
    user = res.scalars().first()
    if not user:
        await ensure_default_user(db)
        res = await db.execute(select(User).limit(1))
        user = res.scalars().first()
        if not user:
            raise HTTPException(500, "Failed to ensure default user")
    return {"id": str(user.id)}
