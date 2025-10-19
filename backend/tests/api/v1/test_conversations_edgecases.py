import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_add_message_404_for_missing_conversation(client: AsyncClient):
    missing_id = uuid.uuid4()
    resp = await client.post(
        f"/api/v1/conversations/{missing_id}/messages",
        json={"role": "user", "content": "hi"},
    )
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Conversation not found"}


@pytest.mark.asyncio
async def test_add_message_400_for_empty_content(client: AsyncClient):
    # Prepare assistant + conversation
    a = await client.post("/api/v1/assistants/", json={"name": "ConvEC"})
    assert a.status_code == 201
    assistant_id = a.json()["id"]

    c = await client.post(
        "/api/v1/conversations/",
        json={"assistant_id": assistant_id, "title": "Edge"},
    )
    assert c.status_code == 201
    conv_id = c.json()["id"]

    # Empty content should be 400
    r = await client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        json={"role": "user", "content": ""},
    )
    assert r.status_code == 400
    assert r.json() == {"detail": "content is required"}


@pytest.mark.asyncio
async def test_list_messages_paged_anchor_invalid(client: AsyncClient):
    # Prepare assistant + conversation + one message
    a = await client.post("/api/v1/assistants/", json={"name": "ConvPg"})
    assert a.status_code == 201
    assistant_id = a.json()["id"]

    c = await client.post(
        "/api/v1/conversations/",
        json={"assistant_id": assistant_id, "title": "Pg"},
    )
    assert c.status_code == 201
    conv_id = c.json()["id"]

    m = await client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        json={"role": "user", "content": "hi"},
    )
    assert m.status_code == 201

    # Use a random before_id that does not belong to this conversation -> empty page
    page = await client.get(
        f"/api/v1/conversations/{conv_id}/messages/page",
        params={"before_id": str(uuid.uuid4()), "limit": 10},
    )
    assert page.status_code == 200
    data = page.json()
    assert data["messages"] == []
    assert data["has_more"] is False


@pytest.mark.asyncio
async def test_update_and_delete_404_for_missing_conversation(client: AsyncClient):
    missing_id = uuid.uuid4()
    # update
    u = await client.patch(
        f"/api/v1/conversations/{missing_id}", json={"title": "x"}
    )
    assert u.status_code == 404
    assert u.json() == {"detail": "Conversation not found"}
    # delete
    d = await client.delete(f"/api/v1/conversations/{missing_id}")
    assert d.status_code == 404
    assert d.json() == {"detail": "Conversation not found"}

