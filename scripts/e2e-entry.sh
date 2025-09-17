#!/usr/bin/env bash
set -euo pipefail

echo ">> E2E entry"
node -v
npm -v

# スクリプト自身の場所からリポジトリルートを導出
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# フロントが必ず見つかるようにチェック
if [ ! -d "frontend" ] || [ ! -f "frontend/package.json" ]; then
  echo "!! frontend ディレクトリが見つかりません: $REPO_ROOT/frontend"
  echo "現在のツリー:"
  ls -la
  exit 1
fi

cd frontend

# 必要パッケージが無ければ npm ci（キャッシュあっても検出）
if [ ! -f node_modules/@playwright/test/package.json ] || [ ! -f node_modules/dotenv/package.json ]; then
  echo ">> Installing deps with npm ci"
  npm ci
else
  echo ">> node_modules cache hit (skip npm ci)"
fi

# ブラウザは冪等インストール
npx playwright install --with-deps

echo ">> Running Playwright tests"
npx playwright test -c playwright.config.ts --reporter=line
