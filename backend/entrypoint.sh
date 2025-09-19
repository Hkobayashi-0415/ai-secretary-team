#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint] waiting for postgres ..."
# 例: 30秒リトライ（Pg側の start_period と足並みをそろえる）
ready=0
for i in {1..30}; do
  if command -v pg_isready >/dev/null 2>&1 && \
     pg_isready -h "${DB_HOST:-postgres}" -U "${DB_USER:-ai_secretary_user}" -d "${DB_NAME:-ai_secretary}" >/dev/null 2>&1; then
    ready=1
    break
  fi
  sleep 1
done
if [ "$ready" -ne 1 ]; then
  echo "[entrypoint][ERR] postgres not ready after retries" >&2
  exit 1
fi

echo "[entrypoint] running alembic upgrade head"
# 失敗したら必ず exit する。絶対に stamp で飛ばさない。
alembic upgrade head

echo "[entrypoint] starting uvicorn"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
