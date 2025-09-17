# backend/app/models/__init__.py
from .base import Base
from .models import User, AIAssistant

from .phase2_models import (
    SkillDefinition,
    AssistantSkill,
    Agent,
    Voice,
    Avatar,
    PersonalityTemplate,
    Conversation,
    Message,
    File,
    UserPreference
)

__all__ = [
    # 既存モデル
    'Base', 'User', 'AIAssistant',
    # Phase 2モデル
    'SkillDefinition', 'AssistantSkill', 'Agent',
    'Voice', 'Avatar', 'PersonalityTemplate',
    'Conversation', 'Message', 'File', 'UserPreference'
]