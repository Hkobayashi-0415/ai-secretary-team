-- 必要拡張（すべて IF NOT EXISTS で冪等）
CREATE EXTENSION IF NOT EXISTS pgcrypto;    -- gen_random_uuid() 用
CREATE EXTENSION IF NOT EXISTS "pg_trgm";   -- 既に使っているインデックス用
-- （uuid-ossp は不要。gen_random_uuid は pgcrypto 側です）
