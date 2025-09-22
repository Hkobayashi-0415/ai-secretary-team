"""解析されたタスクに最適なエージェント（プロンプト）を選択するクラス"""

from __future__ import annotations

from typing import Iterable, List

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.phase2_models import Agent, SkillDefinition
from app.services.routing.models.routing_models import AgentSelection, AnalyzedTask


class AgentSelector:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def select_agent(
        self,
        task: AnalyzedTask,
        skills: Iterable[SkillDefinition],
    ) -> AgentSelection:
        """タスクに最も関連性の高いエージェントをベクトル検索で選択する"""

        stmt: Select = (
            select(Agent)
            .options(selectinload(Agent.prompts))
            .where(Agent.is_active.is_(True))
        )
        result = await self.db.execute(stmt)
        agents: List[Agent] = result.scalars().unique().all()

        if not agents:
            raise RuntimeError("No agents configured in the database")

        keyword_set = {kw.lower() for kw in task.keywords}
        skill_names = {skill.name.lower() for skill in skills}

        best_agent: Agent | None = None
        best_score = -1.0

        for agent in agents:
            searchable = self._collect_searchable_text(agent)
            score = 0.0

            for keyword in keyword_set:
                if keyword and keyword in searchable:
                    score += 1.0

            for skill_name in skill_names:
                if skill_name and skill_name in searchable:
                    score += 0.5

            embedding = agent.embedding or {}
            if isinstance(embedding, dict):
                for keyword in keyword_set:
                    score += float(
                        embedding.get(
                            keyword, embedding.get(keyword.replace(" ", "_"), 0.0)
                        )
                    )

            specialty = (agent.agent_metadata or {}).get("specialty")
            if specialty and task.intent:
                if specialty.lower() in task.intent.lower():
                    score += 1.2

            if score > best_score:
                best_score = score
                best_agent = agent

        if best_agent is None:
            best_agent = agents[0]
            best_score = 0.0

        return AgentSelection(
            id=str(best_agent.id),
            name=best_agent.name,
            description=best_agent.description,
            file_path=best_agent.file_path,
            tags=best_agent.tags or [],
            score=round(best_score, 3),
        )

    def _collect_searchable_text(self, agent: Agent) -> str:
        chunks: List[str] = [
            agent.name or "",
            agent.description or "",
            " ".join(agent.tags or []),
            agent.system_prompt or "",
            agent.instructions or "",
        ]

        for prompt in agent.prompts or []:
            if not prompt.is_active:
                continue
            chunks.append(prompt.title or "")
            chunks.append(prompt.content or "")
            chunks.extend(prompt.tags or [])

        for value in (agent.agent_metadata or {}).values():
            if isinstance(value, str):
                chunks.append(value)

        return " ".join(chunks).lower()
