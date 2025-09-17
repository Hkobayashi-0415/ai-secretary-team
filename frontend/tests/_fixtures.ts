// frontend/tests/_fixtures.ts  ← 新規作成（またはあなたの未追跡ファイルをこれで確定）
import { test as base, expect, request, APIRequestContext } from '@playwright/test';

const API_BASE = process.env.API_BASE ?? 'http://backend:8000';

export const test = base.extend<{
  api: APIRequestContext;
}>({
  api: async ({ request }, use) => {
    const ctx = await request.newContext({ baseURL: API_BASE });
    await use(ctx);
    await ctx.dispose();
  },
});

export { expect };
