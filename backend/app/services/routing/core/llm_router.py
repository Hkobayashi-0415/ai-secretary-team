"""スキル定義に基づき、最適なLLMを選択するクラス"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import AIAssistant
from app.models.phase2_models import SkillDefinition
from app.services.routing.models.routing_models import AnalyzedTask, LLMSelection


class LLMRouter:
    """スキル構成とグローバルなモデルカタログを用いて最適なLLMを選択する"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.catalog = self._load_catalog()

    async def select_llm(
        self,
        assistant_id: str,
        skills: Iterable[SkillDefinition],
        task: AnalyzedTask,
    ) -> LLMSelection:
        """スキルリストに基づき、最適なLLMモデルを選択する"""

        default_model = await self._fetch_default_model(assistant_id)
        score_board: Dict[str, float] = defaultdict(float)
        fallbacks: List[str] = []
        reasons: List[str] = []

        for skill in skills:
            config = skill.configuration or {}
            routing = config.get("llm_routing") or {}
            preferred = routing.get("preferred")
            if preferred:
                perf = float(routing.get("performance_weight", 0.6))
                cost = float(routing.get("cost_weight", 0.4))
                score_board[preferred] += 1.0 + perf * 0.5 + (1 - cost) * 0.3
                reasons.append(f"{skill.name} prefers {preferred}")
            for idx, fallback in enumerate(routing.get("fallback", [])):
                bonus = max(0.1, 0.5 / (idx + 1))
                score_board[fallback] += bonus
                fallbacks.append(fallback)

        if task.intent:
            intent_lower = task.intent.lower()
            for model_name, meta in self.catalog.items():
                specialties = {s.lower() for s in meta.get("specialties", [])}
                if intent_lower in specialties:
                    score_board[model_name] += 0.6
                    fallbacks.extend(meta.get("fallback", []))
                    reasons.append(f"{model_name} specialises in {task.intent}")

        if not score_board and default_model:
            score_board[default_model] = 1.0
            reasons.append(f"using assistant default {default_model}")

        if not score_board:
            score_board["gemini-pro"] = 1.0
            reasons.append("fallback to global default gemini-pro")

        primary_model = max(score_board.items(), key=lambda item: item[1])[0]

        combined_fallbacks: List[str] = []
        catalog_fallbacks = self.catalog.get(primary_model, {}).get("fallback", [])
        for candidate in [*fallbacks, default_model, *catalog_fallbacks]:
            if (
                candidate
                and candidate != primary_model
                and candidate not in combined_fallbacks
            ):
                combined_fallbacks.append(candidate)

        reason_text = "; ".join(dict.fromkeys(reasons)) or None
        return LLMSelection(
            model=primary_model, fallbacks=combined_fallbacks, reason=reason_text
        )

    async def _fetch_default_model(self, assistant_id: str) -> str | None:
        stmt: Select = select(AIAssistant.default_llm_model).where(
            AIAssistant.id == assistant_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    def _load_catalog(self) -> Dict[str, Dict[str, Iterable[str]]]:
        """Gemini や GPT 系など既知モデルのメタデータをロード"""

        return {
            "gemini-pro": {
                "provider": "google",
                "specialties": ["analysis", "research", "reasoning"],
                "fallback": ["gpt-4o-mini", "claude-instant"],
            },
            "gpt-4o-mini": {
                "provider": "openai",
                "specialties": ["creative", "communication", "general"],
                "fallback": ["gpt-3.5-turbo", "gemini-pro"],
            },
            "claude-instant": {
                "provider": "anthropic",
                "specialties": ["research", "analysis"],
                "fallback": ["gemini-pro"],
            },
        }
