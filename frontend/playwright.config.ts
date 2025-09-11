import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000',
    headless: true,
  },
  timeout: 30_000,
  reporter: [['list'], ['html', { outputFolder: 'playwright-report' }]],
});
