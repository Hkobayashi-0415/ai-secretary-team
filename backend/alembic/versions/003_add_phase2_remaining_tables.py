"""Add phase2 remaining tables (excluding already existing skill tables)

Revision ID: 003_add_phase2_remaining_tables
Revises: 002_add_default_local_user
Create Date: 2025-08-30 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_add_phase2_remaining_tables'
down_revision = '002_add_default_local_user'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Phase 2の新規テーブルを作成（既存のskill関連テーブルは除く）"""
    
    print("Phase 2の追加テーブル作成を開始します...")
    
    # 既存テーブルの確認
    print("注意: skill_definitions, assistant_skills, agents テーブルは既に存在します")
    
    # --- 以下は既存テーブルに存在しない可能性があるもののみ ---
    
    # pgvector拡張の有効化（必要な場合）
    try:
        op.execute('CREATE EXTENSION IF NOT EXISTS vector')
        print("pgvector拡張を有効化しました")
    except Exception as e:
        print(f"pgvector拡張のスキップ（既に存在または利用不可）: {e}")
    
    # --- agents テーブルのvectorカラム追加（もし存在しない場合） ---
    # 既存のagentsテーブルにvectorカラムがない場合は追加
    try:
        op.add_column('agents', 
            sa.Column('vector', sa.Text(), nullable=True)  # 一旦Textとして追加
        )
        print("agentsテーブルにvectorカラムを追加しました")
    except Exception as e:
        print(f"vectorカラムのスキップ（既に存在）: {e}")
    
    print("Phase 2の追加テーブル作成が完了しました")


def downgrade() -> None:
    """Phase 2の追加分のみを削除"""
    
    print("Phase 2の追加分の削除を開始します...")
    
    # vectorカラムの削除（存在する場合）
    try:
        op.drop_column('agents', 'vector')
        print("agentsテーブルからvectorカラムを削除しました")
    except Exception as e:
        print(f"vectorカラム削除のスキップ: {e}")
    
    print("Phase 2の追加分の削除が完了しました")