from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_async_db
from app.models.models import User

router = APIRouter()

@router.get("/default", status_code=status.HTTP_200_OK)
async def get_or_create_default_user(db: AsyncSession = Depends(get_async_db)):
    # 既存があればそれを返す（最古を採用）
    result = await db.execute(select(User).order_by(User.created_at.asc()).limit(1))
    user = result.scalars().first()
    if user:
        return {"id": str(user.id)}

    # 無ければ最小必須列で作成
    user = User(
        username="default_admin",
        email="admin@example.com",
        password_hash="dev-hash",
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"id": str(user.id)}
