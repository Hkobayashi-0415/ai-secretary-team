"""ユーザーのプロンプトを解析するクラス"""
from app.services.routing.models.routing_models import AnalyzedTask
from sqlalchemy.ext.asyncio import AsyncSession


class TaskAnalyzer:
    def __init__(self, db: AsyncSession = None):
        self.db = db

    async def analyze(self, user_prompt: str) -> AnalyzedTask:
        """ユーザープロンプトを解析し、構造化されたタスク情報に変換する"""
        print(f"TaskAnalyzer: Analyzing prompt: '{user_prompt}'")
        # TODO: Implement actual analysis logic
        return AnalyzedTask(
            keywords=["sample", "task"], intent="unknown", confidence=0.5
        )
