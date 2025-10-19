"""ensure alembic_version.version_num can store long ids

Revision ID: 010a_widen_avcol
Revises: 010_apply_full_sample
Create Date: 2025-09-23 00:00:00
"""
from typing import Sequence, Union

from alembic import op


revision: str = "010a_widen_avcol"
down_revision: Union[str, None] = "010_apply_full_sample"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Guard: if stamped past 008, the column may still be VARCHAR(32)
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name='alembic_version'
                  AND column_name='version_num'
                  AND (character_maximum_length IS NULL OR character_maximum_length < 255)
            ) THEN
                ALTER TABLE alembic_version ALTER COLUMN version_num TYPE VARCHAR(255);
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    # keep 255; shrinking risks truncation
    pass

