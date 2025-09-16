# 007 を“安全版”に上書き
from alembic import op

revision = "007_enable_vector_ext"
down_revision = "004_add_sample_data"
branch_labels = None
depends_on = None

def upgrade():
    op.execute("""
    DO $do$
    BEGIN
      -- サーバに 'vector' 拡張がインストール可能として登録されている場合のみ実行
      IF EXISTS (SELECT 1 FROM pg_available_extensions WHERE name = 'vector') THEN
        EXECUTE 'CREATE EXTENSION IF NOT EXISTS "vector"';
      ELSE
        RAISE NOTICE 'pgvector extension not available on this server; skipping';
      END IF;
    END
    $do$;
    """)

def downgrade():
    op.execute("""
    DO $do$
    BEGIN
      IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector') THEN
        EXECUTE 'DROP EXTENSION IF EXISTS "vector"';
      END IF;
    END
    $do$;
    """)
