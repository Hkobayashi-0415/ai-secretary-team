#!/usr/bin/env bash
set -euo pipefail

CF="-f docker-compose.yml -f docker-compose.ci.yml"
TS="$(date +%Y%m%d_%H%M%S)"
OUT="_debug/${TS}"
mkdir -p "$OUT"

echo "[1/12] merged compose"
docker compose $CF config > "$OUT/compose-merged.yaml"

echo "[2/12] ps -a"
docker compose $CF ps -a > "$OUT/ps.txt"

echo "[3/12] backend logs"
docker compose $CF logs backend --no-color --timestamps > "$OUT/backend.log" || true

echo "[4/12] postgres logs"
docker compose $CF logs postgres --no-color --timestamps > "$OUT/postgres.log" || true

echo "[5/12] redis logs"
docker compose $CF logs redis --no-color --timestamps > "$OUT/redis.log" || true

echo "[6/12] backend env (sanitized)"
docker compose $CF exec -T backend env 2>/dev/null \
 | sort \
 | sed -E 's/(API_KEY|SECRET|PASSWORD|TOKEN)=.*/\1=****/' \
 > "$OUT/backend-env.txt" || true

echo "[7/12] alembic status"
docker compose $CF exec -T backend bash -lc "
  cd /app;
  echo '== current ==';
  alembic current;
  echo '== heads ==';
  alembic heads || true;
  echo '== history (20) ==';
  alembic history -20 || true;
" > "$OUT/alembic.txt" 2>&1 || true

echo "[8/12] DB schema & alembic table"
docker compose $CF exec -T postgres bash -lc "
  psql -U \$POSTGRES_USER -d \$POSTGRES_DB -c 'select * from alembic_version;';
  psql -U \$POSTGRES_USER -d \$POSTGRES_DB -c '\d+ public.conversations';
  psql -U \$POSTGRES_USER -d \$POSTGRES_DB -c '\d+ public.messages';
" > "$OUT/db-schema.txt" 2>&1 || true

echo "[9/12] model import smoke"
docker compose $CF run --rm -T backend python - <<'PY' > "$OUT/model-import.txt" 2>&1 || true
import importlib, json, traceback
out={}
for name in ["app.models.phase2_models","app.api.v1.api"]:
    try:
        m=importlib.import_module(name)
        out[name]="OK"
    except Exception as e:
        out[name]=f"ERR: {type(e).__name__}: {e}"
print(json.dumps(out, indent=2))
PY

echo "[10/12] API smoke (user→assistant→conversation→message)"
docker compose $CF exec -T backend bash -lc '
set -euo pipefail
API=http://localhost:8000
pyjson () { python - "$@" <<PY
import sys,json
d=json.load(sys.stdin)
for k in sys.argv[1:]:
    d=d[k]
print(d)
PY
}
for i in {1..30}; do curl -fsS "$API/health" && break || sleep 1; done
uid=$(curl -fsS "$API/api/v1/users/default" | pyjson id)
aid=$(curl -fsS -X POST "$API/api/v1/assistants/" -H "Content-Type: application/json" -d "{\"name\":\"LogProbe\"}" | pyjson id)
cid=$(curl -fsS -X POST "$API/api/v1/conversations/" -H "Content-Type: application/json" -d "{\"assistant_id\":\"$aid\",\"user_id\":\"$uid\",\"title\":\"probe\"}" | pyjson id)
curl -fsS -X POST "$API/api/v1/conversations/$cid/messages" -H "Content-Type: application/json" -d "{\"role\":\"user\",\"content\":\"ping\"}" || true
' > "$OUT/api-smoke.txt" 2>&1 || true

echo "[11/12] Tail of Tracebacks (backend)"
grep -n \"Traceback\" -n "$OUT/backend.log" -n || true
awk 'p;/Traceback/{p=1}' "$OUT/backend.log" > "$OUT/backend-tracebacks.txt" || true

echo "[12/12] Frontend test artifacts (if any)"
if [ -d frontend/test-results ]; then
  cp -r frontend/test-results "$OUT/test-results"
fi

echo "== Done =="
echo "Collected into: $OUT"
