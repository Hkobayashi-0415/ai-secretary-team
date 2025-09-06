"""ルーティングサービス内で使用するデータモデルを定義します。"""
from typing import List, Optional
from pydantic import BaseModel
import uuid

class AnalyzedTask(BaseModel):
    """タスク分析官によって解析されたタスクの情報"""
    keywords: List[str]
    intent: str
    confidence: float = 0.0

class RoutingDecision(BaseModel):
    """指揮者による最終的なルーティング決定"""
    llm_model: str
    agent_path: str
    skills: List[str]
    reasoning: Optional[str] = None