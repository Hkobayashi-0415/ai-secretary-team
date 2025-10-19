from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
import app.services.routing.orchestrator as orchestrator_mod
from app.services.routing.models.routing_models import RoutingDecision
from app.schemas.routing import RoutingRequest

router = APIRouter()

@router.post("/route", response_model=RoutingDecision)
async def get_routing_decision(
    request: RoutingRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    ユーザーのプロンプトとアシスタントIDに基づき、
    最適なLLMとエージェントを決定するルーティング処理（テスト用）
    """
    try:
        orch = orchestrator_mod.RoutingOrchestrator(db=db)
        decision = await orch.route(
            user_prompt=request.prompt, 
            assistant_id=str(request.assistant_id)
        )
        return decision
    except Exception as e:
        # 実際には、もっと詳細なエラーハンドリングを入れます
        raise HTTPException(status_code=500, detail=str(e))
