// frontend/playwright.config.ts
import { defineConfig } from '@playwright/test';

// CIでは e2e コンテナから http://frontend を叩く。ローカル実行は 3000。
const baseURL =
  process.env.PLAYWRIGHT_BASE_URL ||
  (process.env.CI ? 'http://frontend' : 'http://localhost:3000');

export default defineConfig({
  testDir: './tests',
  use: {
    baseURL,
    headless: true,
  },
  timeout: 30_000,
  reporter: [['list'], ['html', { outputFolder: 'playwright-report' }]],
});
