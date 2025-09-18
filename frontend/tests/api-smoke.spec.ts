// frontend/tests/api-smoke.spec.ts
import { test, expect } from './_fixtures';
import { pickList } from './_utils';


// 共通フィクスチャの `api` は baseURL=process.env.API_BASE で作成済み
test('backend health is OK', async ({ api }) => {
  const res = await api.get('/health');
  expect(res.status()).toBe(200);
});

test('assistants API returns >= 2 items (create before read)', async ({ api }) => {
  const a = await api.post('/api/v1/assistants/', { data: { name: 'Smoke A' } });
  expect(a.ok()).toBeTruthy();

  const b = await api.post('/api/v1/assistants/', { data: { name: 'Smoke B' } });
  expect(b.ok()).toBeTruthy();

  const res = await api.get('/api/v1/assistants/');
  expect(res.ok()).toBeTruthy();

  const list = pickList(await res.json());
  expect(Array.isArray(list)).toBe(true);
  expect(list.length).toBeGreaterThanOrEqual(2);
});

// 会話APIは未実装なので一旦退避（Phase 2で実装後にfixme→通常testへ）
test.fixme('Chat smoke (HTTP only parts)', async ({ api, page }) => {
  const a = await api.post('/api/v1/assistants/', { data: { name: 'WSBot' } });
  expect(a.ok()).toBeTruthy();
  const assistant_id = (await a.json()).id;

  const c = await api.post('/api/v1/conversations/', { data: { assistant_id } });
  expect(c.ok()).toBeTruthy();
  const conv_id = (await c.json()).id;

  await page.goto(`/chat/${conv_id}`);
  await expect(page.getByPlaceholder('Type message...')).toBeVisible();
});

test("chat smoke: create conversation and post message", async ({ api }) => {
  // 本命：APIが無ければ作成して返す（サーバ側実装）
  const uRes = await api.get("/api/v1/users/default");
  expect(uRes.ok()).toBeTruthy();
  const u = await uRes.json();

  // アシスタント作成 → ID取得
  const aRes = await api.post("/api/v1/assistants/", { data: { name: `WSBot ${Date.now()}` } });
  expect(aRes.ok()).toBeTruthy();
  const assistantId = (await aRes.json()).id;

  // 会話作成（user_id を明示送信）
  const cRes = await api.post("/api/v1/conversations/", { data: { assistant_id: assistantId, user_id: u.id } });
  expect(cRes.ok()).toBeTruthy();
  const conv = await cRes.json();

  // メッセージ投稿（ネスト）
  const mRes = await api.post(`/api/v1/conversations/${conv.id}/messages`, { data: { role: "user", content: "hello" } });
  expect(mRes.ok()).toBeTruthy();
  const msg = await mRes.json();
  expect(msg.content).toBe("hello");
});