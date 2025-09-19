import { defineConfig, devices } from '@playwright/test';

const API_BASE = process.env.API_BASE || 'http://backend:8000';

export default defineConfig({
  testDir: './tests',
  timeout: 30_000,
  expect: { timeout: 5_000 },
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 3 : undefined,
  reporter: 'line',
  use: {
    // UI テストの baseURL 用。API テストは個別に API_BASE を使うので必須ではない。
    baseURL: process.env.FRONTEND_URL || 'http://frontend:80',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'API-Chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  // Web サーバ（フロント）は別コンテナで起動する想定なので起動管理しない
});
