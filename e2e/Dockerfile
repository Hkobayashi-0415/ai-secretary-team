# e2e/Dockerfile
FROM mcr.microsoft.com/playwright:v1.55.0-jammy

# Cache-buster: when CI passes a new build id, this layer changes and rebuilds
ARG E2E_VERSION=dev
LABEL ai-secretary.e2e.version=${E2E_VERSION}

WORKDIR /workspace/frontend

# 依存は build 時に固定（実行時に npm/apt は走らない）
COPY frontend/package*.json ./
# Allow fallback to npm install if lockfile is out of sync in PRs
RUN npm ci --ignore-scripts || npm install --ignore-scripts

# テスト一式と Playwright 設定をフロントから拝借
COPY frontend/tests ./tests
COPY frontend/playwright.config.ts ./playwright.config.ts

# そのまま実行
CMD ["npx", "playwright", "test", "-c", "."]
