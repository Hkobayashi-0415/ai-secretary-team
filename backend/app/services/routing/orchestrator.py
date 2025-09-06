"""ルーティングプロセス全体を統括する指揮者クラス"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.routing.models.routing_models import RoutingDecision
from app.services.routing.core.task_analyzer import TaskAnalyzer
from app.services.routing.core.skill_matcher import SkillMatcher
from app.services.routing.core.llm_router import LLMRouter
from app.services.routing.core.agent_selector import AgentSelector

class RoutingOrchestrator:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.task_analyzer = TaskAnalyzer(db=self.db)
        self.skill_matcher = SkillMatcher(db=self.db)
        self.llm_router = LLMRouter(db=self.db)
        self.agent_selector = AgentSelector(db=self.db)

    async def route(self, user_prompt: str, assistant_id: str) -> RoutingDecision:
        """ユーザープロンプトから最適なルーティングを決定する一連の流れ"""
        # 1. タスク分析
        analyzed_task = await self.task_analyzer.analyze(user_prompt)

        # 2. スキルマッチング
        required_skills = await self.skill_matcher.find_required_skills(analyzed_task, assistant_id)

        # 3. LLM選択
        selected_llm = await self.llm_router.select_llm(required_skills)

        # 4. エージェント選択
        selected_agent = await self.agent_selector.select_agent(analyzed_task)

        return RoutingDecision(
            llm_model=selected_llm,
            agent_path=selected_agent.file_path,
            skills=[skill.name for skill in required_skills],
            reasoning="A decision was made based on the analysis." #仮
        )