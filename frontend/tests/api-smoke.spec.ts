import { test, expect, request, APIResponse } from '@playwright/test';

async function expectOk(res: APIResponse) {
  if (!res.ok()) {
    const body = await res.text().catch(() => '<no body>');
    throw new Error(`HTTP ${res.status()} ${res.url()} -> ${body}`);
  }
}

// Playwright のバージョン差異に影響されない「確実な JSON POST」ヘルパ
async function postJson(api: ReturnType<typeof request['newContext']> extends Promise<infer T> ? T : never, url: string, obj: unknown) {
  // data に JSON 文字列、かつ Content-Type を強制
  return api.post(url, {
    data: JSON.stringify(obj),
    headers: { 'Content-Type': 'application/json' },
  });
}

test('chat smoke: create conversation and post message', async () => {
  const API_BASE = process.env.API_BASE || 'http://backend:8000';
  const api = await request.newContext({
    baseURL: API_BASE,
    // 念のため Accept も固定
    extraHTTPHeaders: { 'Accept': 'application/json' },
  });

  // 1) デフォルトユーザ取得/作成
  const uRes = await api.get('/api/v1/users/default');
  await expectOk(uRes);
  const u = await uRes.json();
  expect(u.id).toBeTruthy();

  // 2) アシスタント作成（JSON を確実に送信）
  const aRes = await postJson(api, '/api/v1/assistants/', { name: 'ConvBot' });
  await expectOk(aRes);
  const a = await aRes.json();
  const assistantId = a.id as string;
  expect(assistantId).toBeTruthy();

  // 3) 会話作成
  const cRes = await postJson(api, '/api/v1/conversations/', {
    assistant_id: assistantId,
    user_id: u.id,
    title: 'Hello',
  });
  await expectOk(cRes);
  const conv = await cRes.json();
  const convId = conv.id as string;
  expect(convId).toBeTruthy();

  // 4) メッセージ投稿
  const mRes = await postJson(api, `/api/v1/conversations/${convId}/messages`, {
    role: 'user',
    content: 'hi',
  });
  await expectOk(mRes);
  const msg = await mRes.json();
  expect(msg.id).toBeTruthy();
  expect(msg.content).toBe('hi');

  // 5) メッセージ一覧
  const lRes = await api.get(`/api/v1/conversations/${convId}/messages`);
  await expectOk(lRes);
  const list = await lRes.json();
  expect(Array.isArray(list)).toBe(true);
  expect(list.length).toBeGreaterThanOrEqual(1);
  expect(list[0].content).toBe('hi');
});
