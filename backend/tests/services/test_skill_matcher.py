import uuid
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.services.routing.core.skill_matcher import SkillMatcher
from app.services.routing.models.routing_models import AnalyzedTask
from app.models.models import Base, User, AIAssistant
from app.models.phase2_models import SkillDefinition, AssistantSkill

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
    await engine.dispose()


async def test_find_required_skills(db):
    user = User(
        id=uuid.uuid4(),
        username="tester",
        email="tester@example.com",
        password_hash="x",
        is_active=True,
        is_verified=True,
    )
    assistant = AIAssistant(
        id=uuid.uuid4(),
        user_id=user.id,
        name="assistant",
    )
    skill1 = SkillDefinition(
        id=uuid.uuid4(),
        user_id=user.id,
        skill_code="ANALYSIS",
        name="Data Analysis",
        description="Analyze data",
        skill_type="analysis",
        configuration={"keywords": ["analysis", "data"]},
        is_public=True,
        is_active=True,
    )
    skill2 = SkillDefinition(
        id=uuid.uuid4(),
        user_id=user.id,
        skill_code="WRITING",
        name="Writing",
        description="Write things",
        skill_type="creative",
        configuration={"keywords": ["write", "text"]},
        is_public=True,
        is_active=True,
    )

    db.add_all([user, assistant, skill1, skill2])
    await db.flush()

    db.add_all([
        AssistantSkill(assistant_id=assistant.id, skill_definition_id=skill1.id, is_enabled=True),
        AssistantSkill(assistant_id=assistant.id, skill_definition_id=skill2.id, is_enabled=True),
    ])
    await db.commit()

    matcher = SkillMatcher(db)
    task = AnalyzedTask(keywords=["analysis", "report"], intent="analysis")

    skills = await matcher.find_required_skills(task, assistant.id)

    assert [s.id for s in skills] == [skill1.id]
