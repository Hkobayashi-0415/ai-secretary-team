// frontend/tests/assistants-list-wait.spec.ts
import { test, expect } from '@playwright/test';
import { pickList } from './_utils';

test('Assistants list renders same count as API (robust wait)', async ({ page, request }) => {
  // ここも直 URL ではなく baseURL 相対 or fixture に寄せるのが理想
  // request の baseURL が未設定なら、環境変数側に寄せる:
  const apiBase = process.env.API_BASE ?? 'http://backend:8000';
  const res = await request.get(`${apiBase}/api/v1/assistants`);
  const apiList = pickList(await res.json());

  await page.goto('/assistants');
  await page.waitForResponse(r => r.url().includes('/api/v1/assistants') && r.ok());

  const rows = page.locator('[data-testid^="assistant-row-"]');
  await expect(rows).toHaveCount(apiList.length, { timeout: 15000 });
});
