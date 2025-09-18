"""Add missing updated_at columns to Phase2 tables (consolidated)

Revision ID: 006_phase2_updated_at
Revises: 005_phase2_create_tables
Create Date: 2025-09-13 01:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = '006_phase2_updated_at'
down_revision: Union[str, None] = '005_phase2_create_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(conn, table: str, column: str) -> bool:
    insp = inspect(conn)
    if table not in insp.get_table_names():
        return False
    cols = {c['name'] for c in insp.get_columns(table)}
    return column in cols


def upgrade() -> None:
    bind = op.get_bind()

    # Ensure assistants boolean columns have safe server defaults for upcoming seed data
    with op.batch_alter_table('assistants') as batch_op:
        try:
            batch_op.alter_column('is_active', server_default=sa.text('true'))
        except Exception:
            pass
        try:
            batch_op.alter_column('is_public', server_default=sa.text('false'))
        except Exception:
            pass

    # skill_definitions.updated_at
    if not _has_column(bind, 'skill_definitions', 'updated_at'):
        with op.batch_alter_table('skill_definitions') as batch_op:
            batch_op.add_column(
                sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
            )

    # assistant_skills.updated_at
    if not _has_column(bind, 'assistant_skills', 'updated_at'):
        with op.batch_alter_table('assistant_skills') as batch_op:
            batch_op.add_column(
                sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
            )


def downgrade() -> None:
    bind = op.get_bind()
    # Revert server defaults on assistants booleans (optional)
    with op.batch_alter_table('assistants') as batch_op:
        try:
            batch_op.alter_column('is_public', server_default=None)
        except Exception:
            pass
        try:
            batch_op.alter_column('is_active', server_default=None)
        except Exception:
            pass

    if _has_column(bind, 'assistant_skills', 'updated_at'):
        with op.batch_alter_table('assistant_skills') as batch_op:
            batch_op.drop_column('updated_at')

    if _has_column(bind, 'skill_definitions', 'updated_at'):
        with op.batch_alter_table('skill_definitions') as batch_op:
            batch_op.drop_column('updated_at')
