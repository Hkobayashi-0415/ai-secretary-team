"""ユーザーのプロンプトを解析するクラス"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.routing.models.routing_models import AnalyzedTask
from app.core.logging import get_logger

class TaskAnalyzer:
    def __init__(self, db: AsyncSession = None):
        self.db = db
        self.logger = get_logger(__name__)

    async def analyze(self, user_prompt: str) -> AnalyzedTask:
        """ユーザープロンプトを解析し、構造化されたタスク情報に変換する"""
        self.logger.debug("TaskAnalyzer analyzing prompt", prompt=user_prompt)
        # TODO: Implement actual analysis logic
        return AnalyzedTask(keywords=["sample", "task"], intent="unknown", confidence=0.5)
