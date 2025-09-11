"""Add phase2 remaining tables (excluding already existing skill tables)

Revision ID: 003_add_phase2_remaining_tables
Revises: 002_add_default_local_user
Create Date: 2025-08-30 23:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '003_add_phase2_remaining_tables'
down_revision = '002_add_default_local_user'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Phase 2 の追加（pgvector が無い環境でも落ちないようガード）"""
    print("Phase 2 の追加テーブル作成を開始します...")
    print("注意: skill_definitions, assistant_skills, agents テーブルは既に存在します")

    conn = op.get_bind()

    # 1) vector 拡張が“インストール可能”か確認してから CREATE EXTENSION
    #    → 無ければ何もしない（例外を起こさない）
    try:
        available = conn.exec_driver_sql(
            "SELECT 1 FROM pg_available_extensions WHERE name='vector'"
        ).scalar()
    except Exception:
        available = 0

    if available:
        conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS vector")
        print("pgvector拡張を有効化 or 既存を確認しました")
    else:
        print("pgvector拡張がシステムに未インストールのためスキップします（CIなど想定）")

    # 2) agents.vector カラムの有無を確認してから追加
    insp = inspect(conn)
    try:
        cols = [c["name"] for c in insp.get_columns("agents")]
    except Exception:
        cols = []

    if "vector" not in cols:
        op.add_column("agents", sa.Column("vector", sa.Text(), nullable=True))
        print("agents テーブルに vector カラムを追加しました")
    else:
        print("agents.vector は既に存在するためスキップ")

    print("Phase 2 の追加テーブル作成が完了しました")


def downgrade() -> None:
    """Phase 2 の追加分のみ削除（存在チェックあり）"""
    print("Phase 2 の追加分の削除を開始します...")

    conn = op.get_bind()
    insp = inspect(conn)
    try:
        cols = [c["name"] for c in insp.get_columns("agents")]
    except Exception:
        cols = []

    if "vector" in cols:
        op.drop_column("agents", "vector")
        print("agents テーブルから vector カラムを削除しました")
    else:
        print("agents.vector は存在しないためスキップ")

    print("Phase 2 の追加分の削除が完了しました")
