# e2e/Dockerfile
FROM mcr.microsoft.com/playwright:v1.55.0-jammy

WORKDIR /workspace/frontend

# 依存は build 時に固定（実行時に npm/apt は走らない）
COPY frontend/package*.json ./
RUN npm ci

# テスト一式と Playwright 設定をフロントから拝借
COPY frontend/tests ./tests
COPY frontend/playwright.config.ts ./playwright.config.ts

# そのまま実行
CMD ["npx", "playwright", "test", "-c", "."]
