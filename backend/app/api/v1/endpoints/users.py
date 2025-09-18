from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_async_db
from app.models.models import User

router = APIRouter()

@router.get("/users/default", status_code=status.HTTP_200_OK)
async def get_or_create_default_user(db: AsyncSession = Depends(get_async_db)):
    # 既存があればそれを返す
    result = await db.execute(select(User).order_by(User.created_at.asc()).limit(1))
    user = result.scalars().first()
    if user:
        return {"id": str(user.id), "name": getattr(user, "name", None)}

    # 無ければ最小項目で生成（必須列に合わせて調整）
    # name が NOT NULL/UNIQUE などの制約がある場合に備えて固定名
    try:
        user = User(name="default_admin")
    except TypeError:
        # 仮に name 列が無いスキーマでも落ちないように
        user = User()

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"id": str(user.id), "name": getattr(user, "name", None)}
