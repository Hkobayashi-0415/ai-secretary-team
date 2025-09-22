"""ユーザーのプロンプトを解析するクラス"""

from __future__ import annotations

import re
from typing import Iterable, List, Optional, Tuple

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.phase2_models import (
    AssistantSkill,
    Conversation,
    Message,
    SkillDefinition,
)
from app.services.routing.models.routing_models import AnalyzedTask


class TaskAnalyzer:
    """ユーザープロンプトと会話履歴からタスクを解析する"""

    def __init__(self, db: AsyncSession | None = None):
        self.db = db

    async def analyze(
        self,
        user_prompt: str,
        assistant_id: str,
        conversation_id: str | None = None,
    ) -> AnalyzedTask:
        """ユーザープロンプトを解析し、構造化されたタスク情報に変換する"""

        if not user_prompt or not user_prompt.strip():
            raise ValueError("user_prompt must not be empty")

        history = await self._fetch_recent_history(assistant_id, conversation_id)
        combined_text = " ".join(
            [
                " ".join(
                    turn["content"] for turn in history if turn.get("role") == "user"
                ),
                user_prompt,
            ]
        ).strip()

        keywords = self._extract_keywords(combined_text)
        intent, confidence, primary_skill, matched_keywords = await self._infer_intent(
            assistant_id=assistant_id,
            keywords=keywords,
            user_prompt=user_prompt,
        )

        if matched_keywords:
            normalized_existing = {kw.lower(): kw for kw in keywords}
            for kw in matched_keywords:
                if not kw:
                    continue
                key = kw.lower()
                if key not in normalized_existing:
                    keywords.append(kw)
                    normalized_existing[key] = kw

        summary = self._build_summary(user_prompt, history)

        return AnalyzedTask(
            keywords=keywords,
            intent=intent,
            confidence=confidence,
            assistant_id=assistant_id,
            conversation_id=conversation_id,
            history=history,
            summary=summary,
            primary_skill=primary_skill,
        )

    async def _fetch_recent_history(
        self,
        assistant_id: str,
        conversation_id: str | None,
        limit: int = 6,
    ) -> List[dict]:
        """対象会話またはアシスタントの最新メッセージを取得する"""

        stmt: Select
        if conversation_id:
            stmt = (
                select(Message)
                .join(Conversation)
                .where(Conversation.id == conversation_id)
                .order_by(Message.created_at.desc())
                .limit(limit)
            )
        else:
            stmt = (
                select(Message)
                .join(Conversation)
                .where(Conversation.assistant_id == assistant_id)
                .order_by(Message.created_at.desc())
                .limit(limit)
            )

        result = await self.db.execute(stmt)
        messages = list(reversed(result.scalars().all()))

        history_payload: List[dict] = []
        for message in messages:
            history_payload.append(
                {
                    "message_id": str(message.id),
                    "role": message.role,
                    "content": message.content,
                    "created_at": message.created_at.isoformat()
                    if message.created_at
                    else None,
                }
            )
        return history_payload

    def _extract_keywords(self, text: str, max_keywords: int = 12) -> List[str]:
        """非常に軽量なキーワード抽出（正規表現ベース）"""

        if not text:
            return []

        tokens = re.findall(r"[\w一-龠ぁ-んァ-ヶー]+", text.lower())
        filtered = [token for token in tokens if len(token) > 2]
        seen = set()
        keywords: List[str] = []
        for token in filtered:
            if token not in seen:
                seen.add(token)
                keywords.append(token)
            if len(keywords) >= max_keywords:
                break
        return keywords

    async def _infer_intent(
        self,
        assistant_id: str,
        keywords: Iterable[str],
        user_prompt: str,
    ) -> Tuple[str, float, Optional[str], Optional[List[str]]]:
        """スキル定義と照合して意図と信頼度を推定する"""

        keyword_set = {kw.lower() for kw in keywords}
        prompt_lower = user_prompt.lower()

        stmt = (
            select(SkillDefinition)
            .join(
                AssistantSkill, AssistantSkill.skill_definition_id == SkillDefinition.id
            )
            .where(
                AssistantSkill.assistant_id == assistant_id,
                AssistantSkill.is_enabled.is_(True),
                SkillDefinition.is_active.is_(True),
            )
        )

        result = await self.db.execute(stmt)
        skills = result.scalars().all()

        best_skill: Optional[SkillDefinition] = None
        best_skill_keywords: List[str] | None = None
        best_score = 0.0

        for skill in skills:
            config = skill.configuration or {}
            skill_category = (
                config.get("skill_category") or skill.skill_type or skill.name
            ).lower()
            configured_keywords = config.get("keywords", [])
            keywords_conf = {kw.lower() for kw in configured_keywords if kw}
            capabilities = {
                cap.lower() for cap in config.get("capabilities", []) if cap
            }

            overlap = len(keyword_set & keywords_conf)
            capability_overlap = len(keyword_set & capabilities)
            substring_hits = sum(
                1
                for kw in configured_keywords
                if kw
                and (
                    kw.lower() in prompt_lower
                    or kw in user_prompt
                    or kw.lower() in keyword_set
                )
            )

            score = overlap * 1.5 + capability_overlap + substring_hits * 0.8

            if skill_category and skill_category in prompt_lower:
                score += 1.0
            if skill.name.lower() in prompt_lower:
                score += 0.5
            if overlap:
                score += min(1.5, overlap * 0.5)

            if score > best_score:
                best_score = score
                best_skill = skill
                best_skill_keywords = [kw for kw in configured_keywords if kw]

        if best_skill:
            config = best_skill.configuration or {}
            inferred_intent = (
                config.get("skill_category") or best_skill.skill_type or best_skill.name
            )
            confidence = min(0.95, 0.4 + best_score * 0.2)
            return inferred_intent, confidence, best_skill.name, best_skill_keywords

        fallback_intent = self._fallback_intent(keyword_set, prompt_lower)
        confidence = 0.45 if fallback_intent != "general" else 0.35
        return fallback_intent, confidence, None, None

    def _fallback_intent(self, keyword_set: set[str], prompt_lower: str) -> str:
        """スキルが一致しなかった場合のシンプルな意図推定"""

        heuristics = {
            "analysis": {"analy", "analysis", "report", "insight", "data"},
            "creative": {"story", "creative", "poem", "slogan", "copy"},
            "communication": {"email", "reply", "response", "message"},
            "research": {"research", "investigate", "summary", "findings"},
        }

        for intent, patterns in heuristics.items():
            if any(pattern in prompt_lower for pattern in patterns):
                return intent
            if any(
                keyword.startswith(pattern)
                for keyword in keyword_set
                for pattern in patterns
            ):
                return intent
        return "general"

    def _build_summary(self, user_prompt: str, history: Iterable[dict]) -> str:
        """会話履歴から200文字程度の簡易サマリーを生成"""

        history_text = " ".join(turn.get("content", "") for turn in history)
        base = f"Prompt: {user_prompt.strip()}"
        if history_text:
            base = f"{base} | History: {history_text.strip()}"
        return base[:200]
