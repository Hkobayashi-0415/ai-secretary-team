#!/usr/bin/env bash
set -euo pipefail

echo ">> E2E entry"
node -v
npm -v

cd frontend

# 必要なパッケージが無ければ npm ci を実行（node_modules キャッシュあっても検出）
if [ ! -f node_modules/@playwright/test/package.json ] || [ ! -f node_modules/dotenv/package.json ]; then
  echo ">> Installing deps with npm ci"
  npm ci
else
  echo ">> node_modules cache hit (skip npm ci)"
fi

# ブラウザは idempotent にインストール
npx playwright install --with-deps

echo ">> Running Playwright tests"
npx playwright test -c playwright.config.ts --reporter=line
