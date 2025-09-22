from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.schemas.routing import RoutingRequest
from app.services.routing.models.routing_models import RoutingDecision
from app.services.routing.orchestrator import RoutingError, RoutingOrchestrator

router = APIRouter()


@router.post("/route", response_model=RoutingDecision)
async def get_routing_decision(
    request: RoutingRequest,
    db: AsyncSession = Depends(get_async_db),
):
    """ユーザーのプロンプトとアシスタントIDに基づいたルーティング処理"""

    orchestrator = RoutingOrchestrator(db=db)
    try:
        decision = await orchestrator.route(
            user_prompt=request.prompt,
            assistant_id=str(request.assistant_id),
            conversation_id=str(request.conversation_id)
            if request.conversation_id
            else None,
        )
        return decision
    except RoutingError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:  # pragma: no cover - unexpected errors
        raise HTTPException(status_code=500, detail="Routing pipeline failed") from exc
