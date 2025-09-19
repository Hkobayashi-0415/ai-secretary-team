#!/usr/bin/env bash
set -euo pipefail

API_BASE="${API_BASE:-http://backend:8000}"
MAX_RETRY="${MAX_RETRY:-60}"

echo ">> Waiting for backend: ${API_BASE}"
i=0
until curl -sf "${API_BASE}/health" >/dev/null 2>&1; do
  i=$((i+1))
  if [ "$i" -ge "$MAX_RETRY" ]; then
    echo "!! Backend not ready: ${API_BASE}" >&2
    exit 1
  fi
  sleep 1
done
echo ">> Backend is ready."

cd /workspace/frontend

# リポジトリをボリュームマウントしているケースに対応（node_modules が消える場合がある）
if [ ! -d node_modules ]; then
  echo ">> Running npm ci (frontend)…"
  npm ci
fi

echo ">> Running Playwright tests…"
API_BASE="${API_BASE}" npx playwright test --reporter=line
