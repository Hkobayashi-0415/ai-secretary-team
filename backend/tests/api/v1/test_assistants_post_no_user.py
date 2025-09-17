import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_post_assistant_404_when_no_user(client: AsyncClient):
    """
    ユーザーが1件も存在しない場合に POST /assistants が 404 を返すことを確認。
    conftest.py のDBはテストごとに空なので、ユーザーを作らずに叩けばOK。
    """
    resp = await client.post("/api/v1/assistants/", json={"name": "Should Fail"})
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Default user not found"}
