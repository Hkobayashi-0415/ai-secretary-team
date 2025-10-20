-- Database bootstrap (idempotent prerequisites only)
-- NOTE: All tables, indexes and data migrations are managed by Alembic.

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Optional placeholder schema for future use
CREATE SCHEMA IF NOT EXISTS ai_secretary;

-- No tables are created here on purpose. See backend/alembic for schema.
