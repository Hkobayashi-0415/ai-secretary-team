"""ルーティングサービス内で使用するデータモデルを定義します。"""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ConversationTurn(BaseModel):
    role: str
    content: str
    message_id: Optional[str] = None
    created_at: Optional[str] = None


class AnalyzedTask(BaseModel):
    """タスク分析官によって解析されたタスクの情報"""

    keywords: List[str]
    intent: str
    confidence: float = 0.0
    assistant_id: Optional[str] = None
    conversation_id: Optional[str] = None
    history: List[ConversationTurn] = Field(default_factory=list)
    summary: Optional[str] = None
    primary_skill: Optional[str] = None


class LLMSelection(BaseModel):
    model: str
    fallbacks: List[str] = Field(default_factory=list)
    reason: Optional[str] = None


class AgentSelection(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    file_path: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    score: Optional[float] = None


class RoutingDecision(BaseModel):
    """指揮者による最終的なルーティング決定"""

    llm: LLMSelection
    agent: AgentSelection
    skills: List[str]
    reasoning: Optional[str] = None
    analysis: AnalyzedTask
    meta: Dict[str, str] = Field(default_factory=dict)
