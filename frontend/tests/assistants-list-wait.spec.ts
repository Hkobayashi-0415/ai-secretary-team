
import { test, expect } from '@playwright/test';

function pickList(json: any): any[] {
  if (Array.isArray(json)) return json;
  if (Array.isArray(json?.result)) return json.result;
  if (Array.isArray(json?.items)) return json.items;
  return [];
}

test('Assistants list renders same count as API (robust wait)', async ({ page, request }) => {
  const res = await request.get('http://backend:8000/api/v1/assistants');
  const apiList = pickList(await res.json());

  await page.goto('/assistants');
  await page.waitForResponse(r => r.url().includes('/api/v1/assistants') && r.ok());

  const rows = page.locator('[data-testid^="assistant-row-"]');
  await expect(rows).toHaveCount(apiList.length, { timeout: 15000 });
});
