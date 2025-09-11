"""スキル定義に基づき、最適なLLMを選択するクラス"""
from typing import List

from app.models.phase2_models import SkillDefinition
from sqlalchemy.ext.asyncio import AsyncSession


class LLMRouter:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def select_llm(self, skills: List[SkillDefinition]) -> str:
        """スキルリストに基づき、最適なLLMモデル名を選択する"""
        print("LLMRouter: Selecting best LLM...")
        # TODO: Implement LLM selection logic based on skill configuration
        return "gemini-pro"
