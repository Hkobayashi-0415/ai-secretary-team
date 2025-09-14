import { defineConfig } from '@playwright/test';

export default defineConfig({
  timeout: 45_000,
  use: {
    baseURL: process.env.E2E_BASE_URL ?? 'http://frontend', // ← ここが重要
    trace: 'retain-on-failure',
  },
});
