// frontend/tests/_fixtures.ts
import {
  test as base,
  expect,
  request as pwRequest,   // ← これが .newContext() を持つ“モジュールの request”
  APIRequestContext,
} from '@playwright/test';

const API_BASE = process.env.API_BASE ?? 'http://backend:8000';

export const test = base.extend<{
  api: APIRequestContext;
}>({
  api: async ({}, use) => {
    // ここで新しい API コンテキストを作る
    const ctx = await pwRequest.newContext({ baseURL: API_BASE });
    try {
      await use(ctx);
    } finally {
      await ctx.dispose();
    }
  },
});

export { expect };
