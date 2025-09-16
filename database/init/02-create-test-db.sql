-- create test DB and enable extensions
CREATE DATABASE ai_secretary_test OWNER ai_secretary_user;

\connect ai_secretary_test

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
