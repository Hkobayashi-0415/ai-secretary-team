"""Add default local user

Revision ID: 002_add_default_local_user
Revises: 21953cb59bd8
Create Date: 2025-08-21 00:45:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002_add_default_local_user"
down_revision: Union[str, None] = "21953cb59bd8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """デフォルトのローカルユーザーを作成"""
    # デフォルトユーザーのデータを挿入
    op.execute(
        """
        INSERT INTO users (
            id, username, email, password_hash,
            is_active, is_verified, created_at, updated_at
        ) VALUES (
            '00000000-0000-0000-0000-000000000001',
            'local_user',
            'local@example.com',
            'not_used_in_local',
            true,
            true,
            NOW(),
            NOW()
        )
        ON CONFLICT (id) DO NOTHING;
        """
    )


def downgrade() -> None:
    """デフォルトユーザーを削除"""
    op.execute(
        """
        DELETE FROM users
        WHERE id = '00000000-0000-0000-0000-000000000001';
        """
    )
