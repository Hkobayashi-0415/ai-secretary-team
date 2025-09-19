#!/bin/sh
set -eu
API=${API:-http://localhost:8000}

# Read JSON from stdin and print .id (POSIX sh safe)
py_id() {
  python -c 'import sys,json; print(json.load(sys.stdin).get("id",""))'
}

echo "0) health"
curl -sS "$API/health" | python -m json.tool || { echo "[ERR] health NG"; curl -iS "$API/health" || true; exit 1; }

echo "1) default user"
uid=$(curl -sS "$API/api/v1/users/default" | py_id)
test -n "$uid" || { echo "[ERR] users/default が不正"; curl -iS "$API/api/v1/users/default"; exit 1; }
echo "uid=$uid"

echo "2) assistant"
aid=$(curl -sS -X POST "$API/api/v1/assistants/" -H "Content-Type: application/json" -d '{"name":"ConvBot"}' | py_id)
test -n "$aid" || { echo "[ERR] assistants 作成が不正"; exit 1; }
echo "aid=$aid"

echo "3) conversation"
cid=$(curl -sS -X POST "$API/api/v1/conversations/" -H "Content-Type: application/json" \
  -d "{\"assistant_id\":\"$aid\",\"user_id\":\"$uid\",\"title\":\"Hello\"}" | py_id)
test -n "$cid" || { echo "[ERR] conversations 作成が不正"; exit 1; }
echo "cid=$cid"

echo "4) message POST"
curl -iS -X POST "$API/api/v1/conversations/$cid/messages" -H "Content-Type: application/json" \
  -d '{"role":"user","content":"hi"}'

echo "5) messages LIST"
curl -sS "$API/api/v1/conversations/$cid/messages" | python -m json.tool
