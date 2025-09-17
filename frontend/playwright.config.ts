// frontend/playwright.config.ts
import 'dotenv/config';
import { defineConfig, devices } from '@playwright/test';

const FRONTEND_BASE = process.env.FRONTEND_BASE || 'http://frontend';

export default defineConfig({
  testDir: './tests',
  timeout: 30_000,
  use: {
    baseURL: FRONTEND_BASE, // page.goto('/...') 用
    trace: 'on-first-retry',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
});
