"""解析されたタスクに最適なエージェント（プロンプト）を選択するクラス"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.routing.models.routing_models import AnalyzedTask
from app.models.phase2_models import Agent
from app.core.logging import get_logger

class AgentSelector:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = get_logger(__name__)

    async def select_agent(self, task: AnalyzedTask) -> Agent:
        """タスクに最も関連性の高いエージェントをベクトル検索で選択する"""
        self.logger.debug("Selecting best agent", intent=task.intent)
        # TODO: Implement vector search logic for agents
        # For now, return a dummy agent object
        class DummyAgent:
            file_path = "backend/app/agents/system/default.md"
        return DummyAgent()
