import pytest
from app.services.routing.core.task_analyzer import TaskAnalyzer
from app.services.routing.models.routing_models import AnalyzedTask


@pytest.mark.asyncio
async def test_task_analyzer_returns_analyzed_task():
    ta = TaskAnalyzer(db=None)
    result = await ta.analyze("find info about X")
    assert isinstance(result, AnalyzedTask)
    assert result.intent == "unknown"
    assert result.keywords

