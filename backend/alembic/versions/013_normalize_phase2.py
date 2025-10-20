"""Normalize phase2 schema to canonical shape (constraints, columns, indexes)

Revision ID: 013_normalize_phase2
Revises: 012_remove_characters_stack
Create Date: 2025-10-20 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "013_normalize_phase2"
down_revision: Union[str, None] = "012_remove_characters_stack"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1) Conversations/messages column normalization (idempotent)
    op.execute(
        """
        DO $$
        BEGIN
            -- Conversations: ensure canonical columns exist
            IF to_regclass('public.conversations') IS NOT NULL THEN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='conversations' AND column_name='conversation_type' AND table_schema='public'
                ) THEN
                    ALTER TABLE conversations ADD COLUMN conversation_type varchar(50) NOT NULL DEFAULT 'chat';
                END IF;
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='conversations' AND column_name='status' AND table_schema='public'
                ) THEN
                    ALTER TABLE conversations ADD COLUMN status varchar(20) NOT NULL DEFAULT 'active';
                END IF;
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='conversations' AND column_name='voice_enabled' AND table_schema='public'
                ) THEN
                    ALTER TABLE conversations ADD COLUMN voice_enabled boolean NOT NULL DEFAULT true;
                END IF;
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='conversations' AND column_name='voice_id' AND table_schema='public'
                ) THEN
                    ALTER TABLE conversations ADD COLUMN voice_id uuid;
                END IF;
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='conversations' AND column_name='metadata' AND table_schema='public'
                ) THEN
                    ALTER TABLE conversations ADD COLUMN metadata jsonb DEFAULT '{}'::jsonb;
                END IF;
                -- Title length unify to 255
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='conversations' AND column_name='title' AND table_schema='public'
                ) THEN
                    ALTER TABLE conversations ALTER COLUMN title TYPE varchar(255);
                END IF;
            END IF;

            -- Messages: rename, ensure columns, convert types when needed
            IF to_regclass('public.messages') IS NOT NULL THEN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='messages' AND column_name='parent_id' AND table_schema='public'
                ) AND NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='messages' AND column_name='parent_message_id' AND table_schema='public'
                ) THEN
                    ALTER TABLE messages RENAME COLUMN parent_id TO parent_message_id;
                END IF;

                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='messages' AND column_name='updated_at' AND table_schema='public'
                ) THEN
                    ALTER TABLE messages ADD COLUMN updated_at timestamptz NOT NULL DEFAULT now();
                END IF;
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='messages' AND column_name='metadata' AND table_schema='public'
                ) THEN
                    ALTER TABLE messages ADD COLUMN metadata jsonb DEFAULT '{}'::jsonb;
                END IF;
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='messages' AND column_name='content_type' AND table_schema='public'
                ) THEN
                    ALTER TABLE messages ADD COLUMN content_type varchar(20) DEFAULT 'text';
                END IF;

                -- Convert ENUM message_role -> varchar when present
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='messages' AND column_name='role' AND udt_name='message_role' AND table_schema='public'
                ) THEN
                    ALTER TABLE messages ALTER COLUMN role TYPE varchar USING role::text;
                END IF;

                -- Add CHECK constraints if missing
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint WHERE conname='messages_role_check'
                ) THEN
                    ALTER TABLE messages
                        ADD CONSTRAINT messages_role_check
                        CHECK (role in ('user','assistant','system'));
                END IF;
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint WHERE conname='messages_content_type_check'
                ) THEN
                    ALTER TABLE messages
                        ADD CONSTRAINT messages_content_type_check
                        CHECK (content_type in ('text','image','file','audio'));
                END IF;
            END IF;
        END $$;
        """
    )

    # 2) Indexes (idempotent)
    op.execute("CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_conversations_assistant_id ON conversations(assistant_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_conversations_metadata ON conversations USING GIN(metadata);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_messages_parent_message_id ON messages(parent_message_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_messages_metadata ON messages USING GIN(metadata);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);")

    # 3) assistant_skills normalization to canonical (assistant_id, skill_id)
    op.execute(
        """
        DO $$
        BEGIN
            IF to_regclass('public.assistant_skills') IS NOT NULL THEN
                -- Add target column
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='assistant_skills' AND column_name='skill_id' AND table_schema='public'
                ) THEN
                    ALTER TABLE assistant_skills ADD COLUMN skill_id uuid;
                END IF;

                -- Prefer skill_definition_id when present
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='assistant_skills' AND column_name='skill_definition_id' AND table_schema='public'
                ) THEN
                    UPDATE assistant_skills s
                    SET skill_id = COALESCE(skill_id, skill_definition_id)
                    WHERE skill_id IS NULL AND skill_definition_id IS NOT NULL;
                END IF;

                -- Map skill_name -> skill_definitions.id via code or name
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='assistant_skills' AND column_name='skill_name' AND table_schema='public'
                ) THEN
                    UPDATE assistant_skills s
                    SET skill_id = sd.id
                    FROM skill_definitions sd
                    WHERE s.skill_id IS NULL
                      AND s.skill_name IS NOT NULL
                      AND (sd.skill_code = s.skill_name OR sd.name = s.skill_name);
                END IF;

                -- Add FK if missing
                IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='assistant_skills_skill_id_fkey') THEN
                    ALTER TABLE assistant_skills
                    ADD CONSTRAINT assistant_skills_skill_id_fkey
                    FOREIGN KEY (skill_id) REFERENCES skill_definitions(id) ON DELETE CASCADE;
                END IF;

                -- Set NOT NULL when data is complete
                IF NOT EXISTS (
                    SELECT 1 FROM assistant_skills WHERE skill_id IS NULL
                ) THEN
                    ALTER TABLE assistant_skills ALTER COLUMN skill_id SET NOT NULL;
                END IF;

                -- Drop legacy columns if present
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='assistant_skills' AND column_name='skill_definition_id' AND table_schema='public'
                ) THEN
                    ALTER TABLE assistant_skills DROP COLUMN skill_definition_id;
                END IF;
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='assistant_skills' AND column_name='skill_name' AND table_schema='public'
                ) THEN
                    ALTER TABLE assistant_skills DROP COLUMN skill_name;
                END IF;

                -- Helpful indexes
                CREATE INDEX IF NOT EXISTS ix_assistant_skills_assistant_id ON assistant_skills(assistant_id);
                CREATE INDEX IF NOT EXISTS ix_assistant_skills_skill_id ON assistant_skills(skill_id);
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    # Non-destructive downgrade placeholders; indices can be dropped safely
    op.execute("DROP INDEX IF EXISTS idx_messages_metadata;")
    op.execute("DROP INDEX IF EXISTS idx_messages_parent_message_id;")
    op.execute("DROP INDEX IF EXISTS idx_conversations_metadata;")
