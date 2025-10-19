"""remove characters/images/affinity tables (cleanup)

Revision ID: 012_remove_characters_stack
Revises: 010a_widen_avcol
Create Date: 2025-09-23 00:00:00
"""
from typing import Sequence, Union

from alembic import op


revision: str = "012_remove_characters_stack"
down_revision: Union[str, None] = "010a_widen_avcol"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop tables if they exist. This is a forward migration that cleans up
    # any leftover artifacts from an abandoned Characters stack.
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='user_character_affinity') THEN
                DROP TABLE IF EXISTS user_character_affinity CASCADE;
            END IF;
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='character_images') THEN
                DROP TABLE IF EXISTS character_images CASCADE;
            END IF;
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='characters') THEN
                DROP TABLE IF EXISTS characters CASCADE;
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    # No-op: we intentionally removed these tables. Restoring them is out of scope.
    pass

