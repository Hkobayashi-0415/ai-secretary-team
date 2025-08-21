#!/bin/bash
# データベース初期化スクリプト

set -e

echo "Waiting for PostgreSQL to be ready..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is ready - executing Alembic migrations"

# Alembicマイグレーションを実行
alembic upgrade head

echo "Database initialization completed"