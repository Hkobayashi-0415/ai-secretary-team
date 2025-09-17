// frontend/tests/api-smoke.spec.ts
import { test, expect } from './_fixtures';
import { pickList } from './_utils';

test('backend health is OK', async ({ api }) => {
  const res = await api.get('/health');
  expect(res.status()).toBe(200);
});

test('assistants API returns >= 2 items (create before read)', async ({ api }) => {
  const createA = await api.post('/api/v1/assistants/', { data: { name: 'Smoke A' } });
  expect(createA.ok()).toBeTruthy();

  const createB = await api.post('/api/v1/assistants/', { data: { name: 'Smoke B' } });
  expect(createB.ok()).toBeTruthy();

  const res = await api.get('/api/v1/assistants/');
  expect(res.ok()).toBeTruthy();

  const list = pickList(await res.json());
  expect(Array.isArray(list)).toBe(true);
  expect(list.length).toBeGreaterThanOrEqual(2);
});
