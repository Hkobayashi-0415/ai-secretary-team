"""widen alembic_version.version_num to 255"""
from alembic import op
import sqlalchemy as sa

# 直前のリビジョンはあなたの最新（例: 20250916_cnv_msg）に合わせて
revision = "008_widen_alembic_version"
down_revision = "20250916_cnv_msg"
branch_labels = None
depends_on = None

def upgrade():
    # 既存32→255へ（既に255でも問題なく通る）
    with op.batch_alter_table("alembic_version") as batch_op:
        batch_op.alter_column(
            "version_num",
            type_=sa.String(length=255),
            existing_type=sa.String(length=32),
            existing_nullable=False,
        )

def downgrade():
    with op.batch_alter_table("alembic_version") as batch_op:
        batch_op.alter_column(
            "version_num",
            type_=sa.String(length=32),
            existing_type=sa.String(length=255),
            existing_nullable=False,
        )
