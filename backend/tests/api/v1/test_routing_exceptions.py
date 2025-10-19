import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_routing_endpoint_handles_exceptions(client: AsyncClient, monkeypatch):
    # Force orchestrator to raise
    from app.services import routing as routing_pkg
    from app.services.routing import orchestrator as orch_mod

    class Boom:
        def __init__(self, db=None):
            pass

        async def route(self, *args, **kwargs):
            raise RuntimeError("boom")

    monkeypatch.setattr(orch_mod, "RoutingOrchestrator", Boom)

    payload = {
        "prompt": "route this",
        "assistant_id": "00000000-0000-0000-0000-000000000000",
    }
    r = await client.post("/api/v1/routing/route", json=payload)
    assert r.status_code == 500
    assert r.json()["detail"] == "boom"

