-- Seed default_admin idempotently
\connect ai_secretary
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM users WHERE email = 'admin@example.com') THEN
    INSERT INTO users (id, username, email, password_hash, is_active, is_verified)
    VALUES (gen_random_uuid(), 'default_admin', 'admin@example.com', 'dev-hash', TRUE, TRUE);
  END IF;
END $$;

-- Optional: only if test DB already has the schema
\connect ai_secretary_test
DO $$
BEGIN
  IF to_regclass('public.users') IS NOT NULL THEN
    IF NOT EXISTS (SELECT 1 FROM users WHERE email = 'admin@example.com') THEN
      INSERT INTO users (id, username, email, password_hash, is_active, is_verified)
      VALUES (gen_random_uuid(), 'default_admin', 'admin@example.com', 'dev-hash', TRUE, TRUE);
    END IF;
  END IF;
END $$;
