import pytest
from app.services.routing.orchestrator import RoutingOrchestrator


@pytest.mark.asyncio
async def test_orchestrator_route_happy_path():
    orch = RoutingOrchestrator(db=None)
    decision = await orch.route("hello", assistant_id="aid")
    assert decision.llm_model == "gemini-pro"
    assert decision.agent_path.endswith("default.md")
    assert isinstance(decision.skills, list)
    assert isinstance(decision.reasoning, str)

