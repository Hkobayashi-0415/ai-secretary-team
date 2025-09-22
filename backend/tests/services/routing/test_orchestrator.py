import asyncio
import os
import uuid
from datetime import datetime
from typing import Any, Iterable, List, Sequence

import pytest

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from app.models.phase2_models import (
    Agent,
    Conversation,
    Message,
    PromptTemplate,
    SkillDefinition,
)  # noqa: E402
from app.services.routing.core.agent_selector import AgentSelector  # noqa: E402
from app.services.routing.core.task_analyzer import TaskAnalyzer  # noqa: E402
from app.services.routing.models.routing_models import (  # noqa: E402
    AgentSelection,
    AnalyzedTask,
    LLMSelection,
)
from app.services.routing.orchestrator import RoutingOrchestrator  # noqa: E402


class StubScalarResult:
    def __init__(self, rows: Sequence[Any]):
        self._rows = list(rows)

    def all(self) -> List[Any]:
        return list(self._rows)

    def unique(self) -> "StubScalarResult":
        return self

    def first(self) -> Any:
        return self._rows[0] if self._rows else None

    def __iter__(self):
        return iter(self._rows)


class StubResult:
    def __init__(self, rows: Sequence[Any]):
        self._rows = list(rows)

    def scalars(self) -> StubScalarResult:
        return StubScalarResult(self._rows)

    def all(self) -> List[Any]:
        return list(self._rows)

    def scalar_one_or_none(self) -> Any:
        return self._rows[0] if self._rows else None


class ScalarValueResult:
    def __init__(self, value: Any):
        self.value = value

    def scalar_one_or_none(self) -> Any:
        return self.value


class InMemorySession:
    def __init__(
        self,
        *,
        messages: Sequence[Message] = (),
        skills: Sequence[SkillDefinition] = (),
        agents: Sequence[Agent] = (),
        default_model: str | None = None,
    ):
        self.messages = list(messages)
        self.skills = list(skills)
        self.agents = list(agents)
        self.default_model = default_model

    async def execute(self, statement, *args, **kwargs):
        entity = statement.column_descriptions[0]["entity"]
        if entity is Message:
            return StubResult(self.messages)
        if entity is SkillDefinition:
            return StubResult(self.skills)
        if entity is Agent:
            return StubResult(self.agents)
        from app.models.models import (
            AIAssistant,
        )  # lazy import to avoid test-time cycles

        if entity is AIAssistant:
            return ScalarValueResult(self.default_model)
        raise NotImplementedError(f"Unsupported statement for stub: {statement}")

    # Compatibility no-ops
    def add(self, obj):
        pass

    def add_all(self, objs):
        pass

    async def commit(self):
        pass

    async def flush(self):
        pass


def _build_message(role: str, content: str, conversation_id: uuid.UUID) -> Message:
    return Message(
        id=uuid.uuid4(),
        conversation_id=conversation_id,
        role=role,
        content=content,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


def _build_skill(
    *,
    name: str,
    category: str,
    keywords: Iterable[str],
    capabilities: Iterable[str],
) -> SkillDefinition:
    skill = SkillDefinition(
        id=uuid.uuid4(),
        skill_code=name[:8].upper(),
        name=name,
        description=f"Skill {name}",
        skill_type=category,
        configuration={
            "skill_category": category,
            "keywords": list(keywords),
            "capabilities": list(capabilities),
            "llm_routing": {
                "preferred": "gemini-pro",
                "fallback": ["claude-instant"],
            },
        },
        is_public=True,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    return skill


@pytest.mark.asyncio
async def test_task_analyzer_infers_intent_from_history():
    conversation_id = uuid.uuid4()
    messages = [
        _build_message("user", "先週の売上データを分析して要点を教えて", conversation_id),
        _build_message("assistant", "売上は前年比+8%です", conversation_id),
    ]
    skill = _build_skill(
        name="Data Analysis",
        category="analysis",
        keywords=["分析", "売上", "analysis"],
        capabilities=["data_analysis"],
    )
    session = InMemorySession(messages=messages, skills=[skill])
    analyzer = TaskAnalyzer(db=session)

    analyzed = await analyzer.analyze(
        user_prompt="最新の売上データを分析してレポート形式でまとめて",
        assistant_id=str(uuid.uuid4()),
        conversation_id=str(conversation_id),
    )

    assert analyzed.intent == "analysis"
    assert "分析" in analyzed.keywords or "analysis" in analyzed.keywords
    assert analyzed.primary_skill == "Data Analysis"
    assert len(analyzed.history) == 2


@pytest.mark.asyncio
async def test_agent_selector_prefers_matching_agent():
    agent1 = Agent(
        id=uuid.uuid4(),
        name="Data Analyst Agent",
        description="分析タスクに特化",
        tags=["analysis", "report"],
        agent_metadata={"specialty": "analysis"},
        embedding={"analysis": 0.9},
        file_path="agents/system/data-analyst.md",
        created_at=datetime.utcnow(),
        is_active=True,
    )
    agent1.prompts = [
        PromptTemplate(
            id=uuid.uuid4(),
            agent_id=agent1.id,
            title="Analysis Prompt",
            content="Provide insightful analysis",
            created_at=datetime.utcnow(),
            is_active=True,
        )
    ]
    agent2 = Agent(
        id=uuid.uuid4(),
        name="Creative Writer",
        description="クリエイティブライティング",
        tags=["story"],
        agent_metadata={"specialty": "creative"},
        embedding={"story": 0.8},
        file_path="agents/system/creative-writer.md",
        created_at=datetime.utcnow(),
        is_active=True,
    )
    agent2.prompts = []

    session = InMemorySession(agents=[agent1, agent2])
    selector = AgentSelector(db=session)

    analyzed_task = AnalyzedTask(
        keywords=["analysis", "report", "insight"],
        intent="analysis",
        confidence=0.8,
        history=[],
    )

    selected = await selector.select_agent(analyzed_task, skills=[])

    assert selected.name == "Data Analyst Agent"
    assert selected.file_path.endswith("data-analyst.md")


@pytest.mark.asyncio
async def test_routing_orchestrator_compiles_reasoning():
    session = InMemorySession()
    orchestrator = RoutingOrchestrator(db=session)

    analyzed_task = AnalyzedTask(
        keywords=["analysis", "report"],
        intent="analysis",
        confidence=0.9,
        history=[],
        primary_skill="Data Analysis",
    )
    skill = SkillDefinition(
        id=uuid.uuid4(),
        skill_code="ANALYSIS",
        name="Data Analysis",
        description="",
        skill_type="analysis",
        configuration={},
        is_public=True,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    async def fake_analyze(*args, **kwargs):
        return analyzed_task

    async def fake_match(*args, **kwargs):
        return [skill]

    async def fake_llm(*args, **kwargs):
        return LLMSelection(
            model="gemini-pro",
            fallbacks=["claude-instant"],
            reason="Skill Data Analysis prefers gemini-pro",
        )

    async def fake_agent(*args, **kwargs):
        return AgentSelection(
            id=str(uuid.uuid4()),
            name="Data Analyst Agent",
            description="",
            file_path="agents/system/data-analyst.md",
            tags=["analysis"],
            score=2.5,
        )

    orchestrator.task_analyzer = type("StubAnalyzer", (), {"analyze": fake_analyze})()
    orchestrator.skill_matcher = type(
        "StubMatcher", (), {"find_required_skills": fake_match}
    )()
    orchestrator.llm_router = type("StubLLM", (), {"select_llm": fake_llm})()
    orchestrator.agent_selector = type("StubAgent", (), {"select_agent": fake_agent})()

    decision = await orchestrator.route(
        user_prompt="分析をお願いします",
        assistant_id=str(uuid.uuid4()),
    )

    assert decision.llm.model == "gemini-pro"
    assert decision.agent.name == "Data Analyst Agent"
    assert decision.skills == ["Data Analysis"]
    assert "Task intent inferred" in (decision.reasoning or "")
