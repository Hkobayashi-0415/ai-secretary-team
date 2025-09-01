from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
import uuid

from app.core.database import get_async_db
# モデルのインポート
from app.models.models import AIAssistant, User
# 修正: 最終FIX版のスキーマをインポート
from app.schemas.assistant import AssistantCreate, AssistantResponse, AssistantUpdateFinal

router = APIRouter()

@router.post("/", response_model=AssistantResponse, status_code=status.HTTP_201_CREATED)
async def create_assistant(
    *,
    db: AsyncSession = Depends(get_async_db),
    assistant_in: AssistantCreate
):
    """
    新しいAIアシスタント（キャラクター）を作成します。
    """
    # TODO: 今後サービス層に分離する
    # シングルユーザー環境を前提とし、最初のユーザーを取得して紐づけます
    user_result = await db.execute(select(User).limit(1))
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Default user not found")

    # スキーマからモデルへデータを展開してインスタンス化
    db_assistant = AIAssistant(
        user_id=user.id,
        **assistant_in.dict()
    )
    db.add(db_assistant)
    await db.commit()
    await db.refresh(db_assistant)
    return db_assistant

@router.get("/", response_model=List[AssistantResponse])
async def read_assistants(
    db: AsyncSession = Depends(get_async_db),
    skip: int = 0,
    limit: int = 100
):
    """
    AIアシスタントのリストを取得します。
    """
    result = await db.execute(select(AIAssistant).offset(skip).limit(limit))
    assistants = result.scalars().all()
    return assistants

@router.get("/{assistant_id}", response_model=AssistantResponse)
async def read_assistant(
    *,
    db: AsyncSession = Depends(get_async_db),
    assistant_id: uuid.UUID
):
    """
    指定されたIDのAIアシスタントを取得します。
    """
    result = await db.execute(select(AIAssistant).filter(AIAssistant.id == assistant_id))
    assistant = result.scalars().first()
    if not assistant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assistant not found")
    return assistant

@router.put("/{assistant_id}", response_model=AssistantResponse)
async def update_assistant(
    *,
    db: AsyncSession = Depends(get_async_db),
    assistant_id: uuid.UUID,
    assistant_in: AssistantUpdateFinal # 柔軟な更新が可能な最終版スキーマを使用
):
    """
    AIアシスタントの情報を部分的に更新します。
    """
    result = await db.execute(select(AIAssistant).filter(AIAssistant.id == assistant_id))
    assistant = result.scalars().first()
    if not assistant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assistant not found")
    
    # model_dump(exclude_unset=True) を使い、リクエストで指定された項目のみを更新対象とします
    update_data = assistant_in.model_dump(exclude_unset=True)
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
    assistant_id: uuid.UUID
):
    """
    AIアシスタントを削除します。
    """
    result = await db.execute(select(AIAssistant).filter(AIAssistant.id == assistant_id))
    assistant = result.scalars().first()
    if not assistant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assistant not found")
    
    await db.delete(assistant)
    await db.commit()
    # 204 No Content ステータスコードの場合、レスポンスボディは返しません
    return None