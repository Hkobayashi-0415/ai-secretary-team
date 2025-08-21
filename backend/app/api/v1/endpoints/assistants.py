from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from sqlalchemy import select # <- selectをインポート
from typing import List

from app.schemas.assistant import Assistant, AssistantCreate
from app.core.database import get_async_db
from app.models.models import AIAssistant # <- AIAssistantモデルをインポート

router = APIRouter()

@router.get("/", response_model=List[Assistant])
async def read_assistants(db: AsyncSession = Depends(get_async_db)):
    """
    AIアシスタントの一覧を取得します。
    """
    # データベースからAIAssistantの全データを取得する
    result = await db.execute(select(AIAssistant))
    assistants = result.scalars().all()
    return assistants

@router.post("/", response_model=Assistant)
async def create_assistant(assistant_in: AssistantCreate, db: AsyncSession = Depends(get_async_db)):
    """
    新しいAIアシスタントを作成します。
    """
      
    # 仮の固定ユーザーIDを生成します（将来的には認証情報から取得します）
    mock_user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    
    # 受け取ったデータと仮のユーザーIDでAIAssistantオブジェクトを作成
    db_assistant = AIAssistant(
        **assistant_in.model_dump(), 
        user_id=mock_user_id
    )
    
    # データベースセッションに追加してコミット
    db.add(db_assistant)
    await db.commit()
    await db.refresh(db_assistant)
    return db_assistant