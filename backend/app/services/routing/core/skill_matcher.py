# backend/app/services/routing/core/skill_matcher.py
"""解析されたタスクに必要なスキルを特定するクラス"""
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.routing.models.routing_models import AnalyzedTask
from app.models.phase2_models import SkillDefinition


class SkillMatcher:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_required_skills(self, task: AnalyzedTask, assistant_id: UUID) -> List[SkillDefinition]:
        """タスクとアシスタントの保有スキルから、必要なスキルを特定する"""
        # TODO: 実装（DB参照・マッチング）
        return []
