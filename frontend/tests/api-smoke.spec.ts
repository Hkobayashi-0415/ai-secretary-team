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

test("chat smoke: create conversation and post message", async ({ request }) => {
  const a = await api(request, "/assistants");
  const assistants = await a.get("").then(r => r.json());
  const assistantId = assistants[0].id;

  const u = await a.get("/users/default").then(r => r.json()); // 既存のdefault取得APIに合わせて
  const conv = await a.post("/conversations", { data: { assistant_id: assistantId, user_id: u.id } }).then(r => r.json());

  const msg = await a.post(`/conversations/${conv.id}/messages`, { data: { role: "user", content: "hello" } }).then(r => r.json());
  expect(msg.content).toBe("hello");
});