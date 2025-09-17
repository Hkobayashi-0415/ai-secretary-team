# tests/api/v1/test_assistants_notfound.py
import uuid
from sqlalchemy import text

async def test_create_assistant_404_when_no_user(client, db):
    # そのテスト回だけユーザーを消す
    await db.execute(text("DELETE FROM users"))
    await db.commit()
    r = await client.post("/api/v1/assistants/", json={"name": "X"})
    assert r.status_code == 404
    assert r.json()["detail"] == "Default user not found"

async def test_read_assistant_not_found(client):
    r = await client.get(f"/api/v1/assistants/{uuid.uuid4()}")
    assert r.status_code == 404

async def test_update_assistant_not_found(client):
    r = await client.put(
        f"/api/v1/assistants/{uuid.uuid4()}",
        json={"name": "A"}
    )
    assert r.status_code == 404

async def test_delete_assistant_not_found(client):
    r = await client.delete(f"/api/v1/assistants/{uuid.uuid4()}")
    assert r.status_code == 404
