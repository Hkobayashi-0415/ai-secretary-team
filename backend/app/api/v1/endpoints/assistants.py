# backend/app/api/v1/endpoints/assistants.py
from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_async_db
from app.core.config import settings
from app.models.models import AIAssistant, User
from app.schemas.assistant import (
    AssistantCreate,
    AssistantResponse,
    AssistantUpdateFinal,
)

router = APIRouter()

# CI/本番共通で許可するモデルのホワイトリスト
ALLOWED_MODELS = {"gemini-pro", "gpt-4", "claude-3-opus"}


def validate_model(model: str) -> None:
    """
    default_llm_model の妥当性チェック。
    CI/テストでは外部へ出ず、ホワイトリストのみで検証します。
    本番で外部検証を足す場合はここに実装（短いタイムアウト推奨）。
    """
    if model not in ALLOWED_MODELS:
        raise HTTPException(status_code=422, detail="Unsupported model")
    # 本番のみネット到達性チェック等を行うなら、下に追加
    if settings.offline_mode:
        return
    # 例:
    # try:
    #     ping_provider(model, timeout=2.0)
    # except Exception:
    #     raise HTTPException(status_code=422, detail="Model provider unreachable")


@router.post("/", response_model=AssistantResponse, status_code=status.HTTP_201_CREATED)
async def create_assistant(
    *,
    db: AsyncSession = Depends(get_async_db),
    assistant_in: AssistantCreate,
):
    """
    新しい AI アシスタントを作成
    """
    # デフォルトユーザー（最初の1件）に紐付ける
    user_result = await db.execute(select(User).limit(1))
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Default user not found"
        )

    # モデル妥当性（外に出ない）
    validate_model(assistant_in.default_llm_model)

    db_assistant = AIAssistant(user_id=user.id, **assistant_in.model_dump())
    db.add(db_assistant)
    await db.commit()
    await db.refresh(db_assistant)
    return db_assistant


@router.get("/", response_model=List[AssistantResponse])
async def read_assistants(
    db: AsyncSession = Depends(get_async_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    アシスタント一覧
    """
    result = await db.execute(select(AIAssistant).offset(skip).limit(limit))
    assistants = result.scalars().all()
    return assistants


@router.get("/{assistant_id}", response_model=AssistantResponse)
async def read_assistant(
    *,
    db: AsyncSession = Depends(get_async_db),
    assistant_id: uuid.UUID,
):
    """
    単一アシスタント取得
    """
    result = await db.execute(
        select(AIAssistant).filter(AIAssistant.id == assistant_id)
    )
    assistant = result.scalars().first()
    if not assistant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Assistant not found"
        )
    return assistant


@router.put("/{assistant_id}", response_model=AssistantResponse)
async def update_assistant(
    *,
    db: AsyncSession = Depends(get_async_db),
    assistant_id: uuid.UUID,
    assistant_in: AssistantUpdateFinal,
):
    """
    アシスタント更新（部分更新）
    """
    result = await db.execute(
        select(AIAssistant).filter(AIAssistant.id == assistant_id)
    )
    assistant = result.scalars().first()
    if not assistant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Assistant not found"
        )

    update_data = assistant_in.model_dump(exclude_unset=True)

    # default_llm_model が更新される場合は検証
    if "default_llm_model" in update_data and update_data["default_llm_model"]:
        validate_model(update_data["default_llm_model"])

    for key, value in update_data.items():
        setattr(assistant, key, value)

    db.add(assistant)
    await db.commit()
    await db.refresh(assistant)
    return assistant


@router.delete("/{assistant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assistant(
    *,
    db: AsyncSession = Depends(get_async_db),
    assistant_id: uuid.UUID,
):
    """
    アシスタント削除
    """
    result = await db.execute(
        select(AIAssistant).filter(AIAssistant.id == assistant_id)
    )
    assistant = result.scalars().first()
    if not assistant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Assistant not found"
        )

    await db.delete(assistant)
    await db.commit()
    return None
