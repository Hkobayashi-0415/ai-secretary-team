#!/usr/bin/env bash
set -euo pipefail
cd backend
HEADS=$(alembic heads --verbose | grep -Eo 'Revision ID: [^ ]+' | awk '{print $3}' | wc -l)
if [ "$HEADS" -ne 1 ]; then
  echo "NG: Multiple Alembic heads detected: $HEADS"
  alembic heads --verbose
  exit 1
fi
echo "OK: Alembic heads = 1"
