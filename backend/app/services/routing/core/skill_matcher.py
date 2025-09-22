"""解析されたタスクに必要なスキルを特定するクラス"""

from __future__ import annotations

from typing import List, Tuple

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.phase2_models import AssistantSkill, SkillDefinition
from app.services.routing.models.routing_models import AnalyzedTask


class SkillMatcher:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_required_skills(
        self, task: AnalyzedTask, assistant_id: str
    ) -> List[SkillDefinition]:
        """タスクとアシスタントの保有スキルから、必要なスキルを特定する"""

        stmt: Select = (
            select(SkillDefinition, AssistantSkill.priority)
            .join(
                AssistantSkill, AssistantSkill.skill_definition_id == SkillDefinition.id
            )
            .where(
                AssistantSkill.assistant_id == assistant_id,
                AssistantSkill.is_enabled.is_(True),
                SkillDefinition.is_active.is_(True),
            )
        )

        result = await self.db.execute(stmt)
        rows: List[Tuple[SkillDefinition, int]] = result.all()

        if not rows:
            return []

        keyword_set = {kw.lower() for kw in task.keywords}
        matched: List[Tuple[float, SkillDefinition]] = []

        for skill, priority in rows:
            config = skill.configuration or {}
            conf_keywords = {kw.lower() for kw in config.get("keywords", [])}
            capabilities = {cap.lower() for cap in config.get("capabilities", [])}
            skill_category = (
                config.get("skill_category") or skill.skill_type or ""
            ).lower()

            keyword_overlap = len(keyword_set & conf_keywords)
            capability_overlap = len(keyword_set & capabilities)

            score = max(0.1, (10 - int(priority or 0)) * 0.1)
            score += keyword_overlap * 1.6 + capability_overlap * 1.2

            if task.intent and skill_category and task.intent.lower() == skill_category:
                score += 2.0
            if task.primary_skill and task.primary_skill == skill.name:
                score += 2.5

            if score > 0.5:
                matched.append((score, skill))

        if not matched:
            top_priority = min(priority for _, priority in rows)
            return [skill for skill, priority in rows if priority == top_priority]

        matched.sort(key=lambda item: item[0], reverse=True)
        return [skill for score, skill in matched]
