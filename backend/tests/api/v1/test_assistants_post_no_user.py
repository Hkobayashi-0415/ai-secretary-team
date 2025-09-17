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
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

@pytest.mark.asyncio
async def test_post_assistant_404_when_no_user(client: AsyncClient, db: AsyncSession):
    """
    ユーザーが1件も存在しない場合に POST /assistants が 404 を返すことを確認。
    事前に users/assistants を空にしておく（初期seedや他テストの副作用対策）。
    """
    # 他テストや初期seedの影響を排除
    # 権限の都合がなければ TRUNCATE の方が速いですが、互換重視で DELETE を採用
    await db.execute(text("DELETE FROM assistants;"))
    await db.execute(text("DELETE FROM users;"))
    await db.commit()

    resp = await client.post("/api/v1/assistants/", json={"name": "Should Fail"})
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Default user not found"}
