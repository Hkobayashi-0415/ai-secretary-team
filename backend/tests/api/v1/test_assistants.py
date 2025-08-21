import pytest
from httpx import AsyncClient
from fastapi import status
import uuid
from app.models.models import User

pytestmark = pytest.mark.asyncio

# 正常系のテスト
async def test_create_and_read_assistant(client: AsyncClient, db):
     # 0. テストの最初に、アシスタントのご主人様となるデフォルトユーザーを作成する
    default_user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    default_user = User(
        id=default_user_id,
        username="test_user",
        email="test@example.com",
        password_hash="test",
        is_active=True,
        is_verified=True
    )
    db.add(default_user)
    await db.commit()
    
    # 1. 最初はアシスタントがいないことを確認
    response = await client.get("/api/v1/assistants/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

    # 2. 新しいアシスタントを作成する
    new_assistant_data = {
        "name": "Test Assistant for Pytest",
        "description": "This is a test assistant created via API test."
    }
    response = await client.post("/api/v1/assistants/", json=new_assistant_data)
    
    # 3. 作成が成功したかを確認
    assert response.status_code == status.HTTP_200_OK
    created_assistant = response.json()
    assert created_assistant["name"] == new_assistant_data["name"]
    assert "id" in created_assistant

    # 4. 一覧に、作成したアシスタントが1件だけ存在することを確認
    response = await client.get("/api/v1/assistants/")
    assert response.status_code == status.HTTP_200_OK
    assistants_list = response.json()
    assert len(assistants_list) == 1
    assert assistants_list[0]["name"] == new_assistant_data["name"]

# --- ▼ ここからが意地悪なテストです ▼ ---

# テストケース1: 名前のないアシスタント
async def test_create_assistant_with_no_name_fails(client: AsyncClient):
    response = await client.post("/api/v1/assistants/", json={"description": "No name here"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

# テストケース2: 名前が長すぎるアシスタント
async def test_create_assistant_with_long_name_fails(client: AsyncClient):
    long_name = "a" * 101
    response = await client.post("/api/v1/assistants/", json={"name": long_name})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

# テストケース3: 存在しないアシスタントの更新 (これは将来の機能のためのテストです)
# async def test_update_nonexistent_assistant_fails(client: AsyncClient):
#     non_existent_id = uuid.uuid4()
#     response = await client.put(f"/api/v1/assistants/{non_existent_id}", json={"name": "ghost"})
#     assert response.status_code == status.HTTP_404_NOT_FOUND