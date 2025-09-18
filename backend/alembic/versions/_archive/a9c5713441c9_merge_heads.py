"""merge heads

Revision ID: a9c5713441c9
Revises: 007_enable_vector_ext, 20250916_create_conversations_messages
Create Date: 2025-09-18 03:48:04.978534

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a9c5713441c9'
down_revision: Union[str, None] = ('007_enable_vector_ext', '20250916_create_conversations_messages')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
