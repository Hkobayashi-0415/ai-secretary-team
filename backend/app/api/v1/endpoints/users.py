from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_async_db
from app.models.models import User

try:
    from app.scripts.ensure_default_user import ensure_default_user  # type: ignore
except Exception:
    ensure_default_user = None  # type: ignore

router = APIRouter()

@router.get("/users/default", status_code=status.HTTP_200_OK)
async def get_or_create_default_user(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User).order_by(User.created_at.asc()).limit(1))
    user = result.scalars().first()

    if not user:
        if ensure_default_user:
            try:
                maybe = ensure_default_user()
                if hasattr(maybe, "__await__"):
                    await maybe  # async 対応
                result = await db.execute(select(User).order_by(User.created_at.asc()).limit(1))
                user = result.scalars().first()
            except Exception:
                user = None

        if not user:
            user = User(name="default_admin")
            db.add(user)
            await db.commit()
            await db.refresh(user)

    return {"id": str(user.id), "name": getattr(user, "name", None)}
