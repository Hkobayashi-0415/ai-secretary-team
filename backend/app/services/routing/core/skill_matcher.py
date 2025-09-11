# backend/app/services/routing/core/skill_matcher.py
"""解析されたタスクに必要なスキルを特定するクラス"""
from typing import List, Set
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.routing.models.routing_models import AnalyzedTask
from app.models.phase2_models import SkillDefinition, AssistantSkill


class SkillMatcher:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_required_skills(self, task: AnalyzedTask, assistant_id: UUID) -> List[SkillDefinition]:
        """タスクとアシスタントの保有スキルから、必要なスキルを特定する"""
        # 1. アシスタントが保有するアクティブなスキルを取得
        result = await self.db.execute(
            select(SkillDefinition)
            .join(AssistantSkill, AssistantSkill.skill_definition_id == SkillDefinition.id)
            .where(
                AssistantSkill.assistant_id == assistant_id,
                AssistantSkill.is_enabled == True,  # noqa: E712
                SkillDefinition.is_active == True,  # noqa: E712
            )
        )
        candidate_skills: List[SkillDefinition] = result.scalars().all()

        # 2. タスク情報と照合して必要なスキルのみを抽出
        task_terms: Set[str] = {kw.lower() for kw in task.keywords}
        if task.intent:
            task_terms.add(task.intent.lower())

        required: List[SkillDefinition] = []
        for skill in candidate_skills:
            config_keywords = set()
            if isinstance(skill.configuration, dict):
                config_keywords = {k.lower() for k in skill.configuration.get("keywords", [])}
            # スキルコードや名前もマッチング対象とする
            config_keywords.add(skill.skill_code.lower())
            config_keywords.add(skill.name.lower())

            if task_terms & config_keywords:
                required.append(skill)

        return required
