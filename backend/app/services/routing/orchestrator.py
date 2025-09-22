"""ルーティングプロセス全体を統括する指揮者クラス"""

from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.routing.core.agent_selector import AgentSelector
from app.services.routing.core.llm_router import LLMRouter
from app.services.routing.core.skill_matcher import SkillMatcher
from app.services.routing.core.task_analyzer import TaskAnalyzer
from app.services.routing.models.routing_models import RoutingDecision


class RoutingError(RuntimeError):
    """ルーティング処理中に発生した例外"""


class RoutingOrchestrator:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.task_analyzer = TaskAnalyzer(db=self.db)
        self.skill_matcher = SkillMatcher(db=self.db)
        self.llm_router = LLMRouter(db=self.db)
        self.agent_selector = AgentSelector(db=self.db)

    async def route(
        self,
        user_prompt: str,
        assistant_id: str,
        conversation_id: Optional[str] = None,
    ) -> RoutingDecision:
        """ユーザープロンプトから最適なルーティングを決定する一連の流れ"""

        reasoning_steps: list[str] = []

        try:
            analyzed_task = await self.task_analyzer.analyze(
                user_prompt=user_prompt,
                assistant_id=assistant_id,
                conversation_id=conversation_id,
            )
            reasoning_steps.append(
                f"Task intent inferred as '{analyzed_task.intent}' (confidence {analyzed_task.confidence:.2f})."
            )
        except Exception as exc:  # pragma: no cover - defensive guard
            raise RoutingError("Task analysis failed") from exc

        try:
            required_skills = await self.skill_matcher.find_required_skills(
                analyzed_task, assistant_id
            )
            if required_skills:
                skill_names = ", ".join(skill.name for skill in required_skills)
                reasoning_steps.append(f"Matched assistant skills: {skill_names}.")
            else:
                reasoning_steps.append(
                    "No dedicated skills matched; falling back to defaults."
                )
        except Exception as exc:  # pragma: no cover
            raise RoutingError("Skill matching failed") from exc

        try:
            llm_selection = await self.llm_router.select_llm(
                assistant_id=assistant_id,
                skills=required_skills,
                task=analyzed_task,
            )
            if llm_selection.reason:
                reasoning_steps.append(f"LLM selection: {llm_selection.reason}.")
            else:
                reasoning_steps.append(f"Selected LLM {llm_selection.model}.")
        except Exception as exc:  # pragma: no cover
            raise RoutingError("LLM selection failed") from exc

        try:
            agent_selection = await self.agent_selector.select_agent(
                analyzed_task, required_skills
            )
            reasoning_steps.append(
                f"Agent '{agent_selection.name}' selected for execution."
            )
        except Exception as exc:  # pragma: no cover
            raise RoutingError("Agent selection failed") from exc

        meta = {
            "assistant_id": assistant_id,
            "conversation_id": analyzed_task.conversation_id or "",
            "primary_skill": analyzed_task.primary_skill or "",
        }

        reasoning = " ".join(reasoning_steps)

        return RoutingDecision(
            llm=llm_selection,
            agent=agent_selection,
            skills=[skill.name for skill in required_skills],
            reasoning=reasoning,
            analysis=analyzed_task,
            meta={key: value for key, value in meta.items() if value},
        )
