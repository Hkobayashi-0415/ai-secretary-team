"""解析されたタスクに最適なエージェント（プロンプト）を選択するクラス"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.routing.models.routing_models import AnalyzedTask
from app.models.phase2_models import Agent

class AgentSelector:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def select_agent(self, task: AnalyzedTask) -> Agent:
        """タスクに最も関連性の高いエージェントをベクトル検索で選択する"""
        print("AgentSelector: Selecting best agent...")
        # TODO: Implement vector search logic for agents
        # For now, return a dummy agent object
        class DummyAgent:
            file_path = "backend/app/agents/system/default.md"
        return DummyAgent()