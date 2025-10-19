"""Fix FK on conversations.user_id and assistant_id to correct tables

Revision ID: 013_fix_conversations_fk
Revises: 012_remove_characters_stack
Create Date: 2025-10-20 00:00:00
"""
from typing import Sequence, Union

from alembic import op


revision: str = "013_fix_conversations_fk"
down_revision: Union[str, None] = "012_remove_characters_stack"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        DECLARE
          _has_conversations boolean := EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema='public' AND table_name='conversations'
          );
        BEGIN
          IF NOT _has_conversations THEN
            RETURN; -- nothing to do
          END IF;

          -- Drop any FK on conversations.user_id
          PERFORM 1 FROM pg_constraint c
            JOIN pg_class t ON t.oid=c.conrelid
            WHERE t.relname='conversations' AND c.contype='f'
              AND EXISTS (
                SELECT 1 FROM unnest(c.conkey) a
                WHERE a = (
                  SELECT attnum FROM pg_attribute 
                   WHERE attrelid=t.oid AND attname='user_id'
                )
              );
          IF FOUND THEN
            FOR r IN 
              SELECT conname FROM pg_constraint c
               JOIN pg_class t ON t.oid=c.conrelid
               WHERE t.relname='conversations' AND c.contype='f'
                 AND EXISTS (
                   SELECT 1 FROM unnest(c.conkey) a
                   WHERE a = (
                     SELECT attnum FROM pg_attribute 
                      WHERE attrelid=t.oid AND attname='user_id'
                   )
                 )
            LOOP
              EXECUTE format('ALTER TABLE conversations DROP CONSTRAINT %I', r.conname);
            END LOOP;
          END IF;

          -- Drop any FK on conversations.assistant_id
          PERFORM 1 FROM pg_constraint c
            JOIN pg_class t ON t.oid=c.conrelid
            WHERE t.relname='conversations' AND c.contype='f'
              AND EXISTS (
                SELECT 1 FROM unnest(c.conkey) a
                WHERE a = (
                  SELECT attnum FROM pg_attribute 
                   WHERE attrelid=t.oid AND attname='assistant_id'
                )
              );
          IF FOUND THEN
            FOR r IN 
              SELECT conname FROM pg_constraint c
               JOIN pg_class t ON t.oid=c.conrelid
               WHERE t.relname='conversations' AND c.contype='f'
                 AND EXISTS (
                   SELECT 1 FROM unnest(c.conkey) a
                   WHERE a = (
                     SELECT attnum FROM pg_attribute 
                      WHERE attrelid=t.oid AND attname='assistant_id'
                   )
                 )
            LOOP
              EXECUTE format('ALTER TABLE conversations DROP CONSTRAINT %I', r.conname);
            END LOOP;
          END IF;

          -- Recreate correct FKs if not already present
          IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='users') THEN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='fk_conversations_user_id_users') THEN
              ALTER TABLE conversations
                ADD CONSTRAINT fk_conversations_user_id_users
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
            END IF;
          END IF;

          IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='assistants') THEN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='fk_conversations_assistant_id_assistants') THEN
              ALTER TABLE conversations
                ADD CONSTRAINT fk_conversations_assistant_id_assistants
                FOREIGN KEY (assistant_id) REFERENCES assistants(id) ON DELETE CASCADE;
            END IF;
          END IF;
        END $$;
        """
    )


def downgrade() -> None:
    # Best-effort: drop the constraints we add if present
    op.execute(
        """
        DO $$
        BEGIN
          IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname='fk_conversations_user_id_users') THEN
            ALTER TABLE IF EXISTS conversations DROP CONSTRAINT fk_conversations_user_id_users;
          END IF;
          IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname='fk_conversations_assistant_id_assistants') THEN
            ALTER TABLE IF EXISTS conversations DROP CONSTRAINT fk_conversations_assistant_id_assistants;
          END IF;
        END $$;
        """
    )

