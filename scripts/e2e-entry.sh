#!/usr/bin/env bash
set -Eeuo pipefail
set -x

# Compose が未設定ならデフォルト http://frontend
BASE_URL="${E2E_BASE_URL:-http://frontend}"
echo "E2E_BASE_URL=${E2E_BASE_URL:-<empty>}  BASE_URL=${BASE_URL}"

# Windows ボリュームの遅さ/権限回避のため /tmp にコピーして実行
rm -rf /tmp/frontend || true
cp -r /workspace/frontend /tmp/
cd /tmp/frontend

# lock があれば ci、なければ install
if [ -f package-lock.json ]; then
  npm ci
else
  npm install
fi

# ブラウザ依存物を入れる
npx playwright install --with-deps

# フロントが応答するまで待機
for i in {1..60}; do
  curl -fsS "${BASE_URL}/assistants" >/dev/null 2>&1 && break
  sleep 2
done

# 実行
E2E_BASE_URL="${BASE_URL}" npx playwright test --reporter=line
