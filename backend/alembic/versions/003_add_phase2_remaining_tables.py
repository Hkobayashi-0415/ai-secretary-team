"""Add phase2 remaining tables (excluding already existing skill tables)

Revision ID: 003_add_phase2_remaining_tables
Revises: 002_add_default_local_user
Create Date: 2025-08-30 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = '003_add_phase2_remaining_tables'
down_revision = '002_add_default_local_user'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create additional Phase 2 artifacts without breaking transactions.

    - Enable pgvector only if the extension is available
    - If an existing 'agents' table is present and lacks 'vector', add it
    """

    bind = op.get_bind()
    insp = inspect(bind)

    # Enable pgvector only when available to avoid errors
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_available_extensions WHERE name = 'vector'
            ) THEN
                CREATE EXTENSION IF NOT EXISTS vector;
            END IF;
        END
        $$;
        """
    )

    # Add vector column only if agents table already exists and column is missing
    if 'agents' in insp.get_table_names():
        cols = {c['name'] for c in insp.get_columns('agents')}
        if 'vector' not in cols:
            op.add_column('agents', sa.Column('vector', sa.Text(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)
    if 'agents' in insp.get_table_names():
        cols = {c['name'] for c in insp.get_columns('agents')}
        if 'vector' in cols:
            op.drop_column('agents', 'vector')

