import uuid
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_conversation_and_messages_flow(client: AsyncClient):
    # アシスタントを1件作成
    a = await client.post("/api/v1/assistants/", json={"name": "ConvBot"})
    assert a.status_code == 201
    assistant_id = a.json()["id"]

    # 会話作成
    c = await client.post("/api/v1/conversations/", json={"assistant_id": assistant_id, "title": "Hello"})
    assert c.status_code == 201
    conv_id = c.json()["id"]

    # メッセージ追加
    m = await client.post(f"/api/v1/conversations/{conv_id}/messages", json={"role":"user","content":"hi"})
    assert m.status_code == 201

    # メッセージ一覧
    lst = await client.get(f"/api/v1/conversations/{conv_id}/messages")
    assert lst.status_code == 200
    assert len(lst.json()) == 1
