"""スキル定義に基づき、最適なLLMを選択するクラス"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.phase2_models import SkillDefinition
from typing import List
from app.core.logging import get_logger

class LLMRouter:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = get_logger(__name__)

    async def select_llm(self, skills: List[SkillDefinition]) -> str:
        """スキルリストに基づき、最適なLLMモデル名を選択する"""
        self.logger.debug("Selecting best LLM", skills=[getattr(s, "name", "?") for s in skills])
        # TODO: Implement LLM selection logic based on skill configuration
        return "gemini-pro"
