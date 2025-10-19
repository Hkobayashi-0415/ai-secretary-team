import pytest

from app.services.routing.core.skill_matcher import SkillMatcher
from app.services.routing.core.llm_router import LLMRouter
from app.services.routing.core.agent_selector import AgentSelector
from app.services.routing.models.routing_models import AnalyzedTask


@pytest.mark.asyncio
async def test_skill_matcher_returns_list():
    sm = SkillMatcher(db=None)
    skills = await sm.find_required_skills(AnalyzedTask(keywords=[], intent="x"), assistant_id="aid")
    assert isinstance(skills, list)


@pytest.mark.asyncio
async def test_llm_router_selects_default():
    lr = LLMRouter(db=None)
    model = await lr.select_llm([])
    assert model == "gemini-pro"


@pytest.mark.asyncio
async def test_agent_selector_returns_dummy_agent():
    ag = AgentSelector(db=None)
    agent = await ag.select_agent(AnalyzedTask(keywords=[], intent="x"))
    assert hasattr(agent, "file_path")
    assert agent.file_path.endswith("default.md")

