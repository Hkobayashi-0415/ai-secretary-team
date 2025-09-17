# tests/api/v1/test_assistants_update_delete.py
import uuid
import pytest
from httpx import AsyncClient

API_BASE = "/api/v1/assistants/"  # 末尾スラッシュ重要（307回避）

async def _create_assistant(client: AsyncClient, name: str = "Tmp"):
    r = await client.post(API_BASE, json={"name": name})
    assert r.status_code == 201, r.text
    data = r.json()
    return uuid.UUID(data["id"]), data

@pytest.mark.asyncio
async def test_update_assistant_partial_and_empty_to_none(client: AsyncClient):
    # 1) まず作成
    a_id, created = await _create_assistant(client, "Before")

    # 2) 部分更新（name変更 + 空文字はNoneに正規化されることを確認）
    payload = {
        "name": "After",
        "description": ""  # field_validator により None になる想定
    }
    r = await client.put(f"{API_BASE}{a_id}", json=payload)
    assert r.status_code == 200, r.text
    updated = r.json()

    assert updated["id"] == str(a_id)
    assert updated["name"] == "After"
    assert updated["description"] is None  # 空文字→None
    # 変更されていないフィールドは元のまま（デフォルト値）
    assert updated["default_llm_model"] == created["default_llm_model"]

@pytest.mark.asyncio
async def test_update_assistant_no_changes_is_ok(client: AsyncClient):
    # 空ボディ（全Optional）でも200でそのまま返る想定
    a_id, before = await _create_assistant(client, "NoChange")
    r = await client.put(f"{API_BASE}{a_id}", json={})
    assert r.status_code == 200, r.text
    after = r.json()
    assert after["id"] == str(a_id)
    assert after["name"] == before["name"]

@pytest.mark.asyncio
async def test_delete_assistant_then_404_on_get(client: AsyncClient):
    a_id, _ = await _create_assistant(client, "ToDelete")

    # 削除
    r = await client.delete(f"{API_BASE}{a_id}")
    assert r.status_code == 204, r.text

    # もう取れない
    r = await client.get(f"{API_BASE}{a_id}")
    assert r.status_code == 404

@pytest.mark.asyncio
async def test_update_nonexistent_returns_404(client: AsyncClient):
    fake_id = uuid.uuid4()
    r = await client.put(f"{API_BASE}{fake_id}", json={"name": "x"})
    assert r.status_code == 404

@pytest.mark.asyncio
async def test_delete_nonexistent_returns_404(client: AsyncClient):
    fake_id = uuid.uuid4()
    r = await client.delete(f"{API_BASE}{fake_id}")
    assert r.status_code == 404
