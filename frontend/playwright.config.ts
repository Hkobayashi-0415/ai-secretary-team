// frontend/playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

// Compose or local env から読む（dotenv は使わない）
const BASE_URL = process.env.E2E_BASE_URL ?? 'http://localhost:3000';
const API_BASE = process.env.API_BASE ?? 'http://localhost:8000';

export default defineConfig({
  testDir: './tests',
  timeout: 30_000,
  expect: { timeout: 10_000 },
  use: {
    baseURL: BASE_URL,
    trace: 'on-first-retry',
  },
  // 必要ならデバイス設定
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
  // テストから API ベースURL参照したい時のため（任意）
  metadata: { apiBase: API_BASE },
});
