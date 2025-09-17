import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import User

# -------------------------
# Create 時の 422（バリデーションエラー）
# -------------------------

@pytest.mark.asyncio
async def test_create_assistant_422_empty_name(client: AsyncClient, db: AsyncSession):
    """
    name は必須 & min_length=1 のため空文字は 422。
    ルータ内の「ユーザー存在チェック」を通すため、先にユーザーを1件だけ作成。
    """
    db.add(User(
        username="u1", email="u1@example.com",
        password_hash="x", is_active=True, is_verified=True
    ))
    await db.commit()

    resp = await client.post("/api/v1/assistants/", json={"name": ""})
    assert resp.status_code == 422

@pytest.mark.asyncio
async def test_create_assistant_422_description_too_long(client: AsyncClient, db: AsyncSession):
    """
    description は max_length=500。501文字は 422。
    """
    db.add(User(
        username="u2", email="u2@example.com",
        password_hash="x", is_active=True, is_verified=True
    ))
    await db.commit()

    payload = {"name": "ok", "description": "x" * 501}
    resp = await client.post("/api/v1/assistants/", json=payload)
    assert resp.status_code == 422


# -------------------------
# Update 時の「空文字→None」境界（200で成功 & None に正規化）
# -------------------------

@pytest.mark.asyncio
async def test_update_optional_fields_empty_string_becomes_none(client: AsyncClient, db: AsyncSession):
    """
    AssistantUpdateFinal の field_validator('*', pre=True) により
    空文字が None に正規化されることを確認。
    ※ name は NOT NULL 想定なので対象外。Optional な項目で検証。
    """
    # まずユーザー作成
    db.add(User(
        username="u3", email="u3@example.com",
        password_hash="x", is_active=True, is_verified=True
    ))
    await db.commit()

    # アシスタント作成（201）
    create = await client.post("/api/v1/assistants/", json={"name": "A"})
    assert create.status_code == 201
    created = create.json()
    aid = created["id"]

    # 空文字で Optional フィールドを更新 → None になって返る
    upd = await client.put(f"/api/v1/assistants/{aid}", json={
        "description": "",
        "default_llm_model": "",
        "custom_system_prompt": ""
    })
    assert upd.status_code == 200
    body = upd.json()
    assert body["description"] is None
    assert body["default_llm_model"] is None
    assert body["custom_system_prompt"] is None
