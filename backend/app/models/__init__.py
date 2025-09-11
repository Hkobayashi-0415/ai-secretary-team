# backend/app/models/__init__.py
from .models import AIAssistant, Base, User
from .phase2_models import (
    Agent,
    AssistantSkill,
    Avatar,
    Conversation,
    File,
    Message,
    PersonalityTemplate,
    SkillDefinition,
    UserPreference,
    Voice,
)

__all__ = [
    # 既存モデル
    "Base",
    "User",
    "AIAssistant",
    # Phase 2モデル
    "SkillDefinition",
    "AssistantSkill",
    "Agent",
    "Voice",
    "Avatar",
    "PersonalityTemplate",
    "Conversation",
    "Message",
    "File",
    "UserPreference",
]
