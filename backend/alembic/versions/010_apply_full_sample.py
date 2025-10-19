"""Apply full sample data adapted from archived 004

Revision ID: 010_apply_full_sample
Revises: 009_add_sample_data
Create Date: 2025-09-23 00:25:00.000000

"""
from typing import Sequence, Union
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "010_apply_full_sample"
down_revision: Union[str, None] = "009_add_sample_data"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ensure optional tables exist (minimal schema) so we can seed cross-env safely
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema='public' AND table_name='personality_templates') THEN
                CREATE TABLE personality_templates (
                    id uuid PRIMARY KEY,
                    user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    name varchar(100) NOT NULL,
                    description text,
                    personality_type varchar(50),
                    system_prompt text,
                    characteristics jsonb,
                    created_at timestamptz NOT NULL DEFAULT now(),
                    updated_at timestamptz NOT NULL DEFAULT now()
                );
            END IF;

            IF NOT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema='public' AND table_name='skill_definitions') THEN
                CREATE TABLE skill_definitions (
                    id uuid PRIMARY KEY,
                    skill_code varchar(100) UNIQUE,
                    name varchar(100) NOT NULL,
                    description text,
                    skill_type varchar(50),
                    configuration jsonb,
                    created_at timestamptz NOT NULL DEFAULT now(),
                    updated_at timestamptz NOT NULL DEFAULT now()
                );
            END IF;

            IF NOT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema='public' AND table_name='assistant_skills') THEN
                CREATE TABLE assistant_skills (
                    id uuid PRIMARY KEY,
                    assistant_id uuid NOT NULL REFERENCES assistants(id) ON DELETE CASCADE,
                    skill_definition_id uuid,
                    skill_id uuid,
                    skill_name varchar(100),
                    created_at timestamptz NOT NULL DEFAULT now()
                );
            END IF;
        END $$;
        """
    )

    # Seed or update assistants, templates, skills and links
    op.execute(
        """
        DO $$
        DECLARE
            u_id uuid;
            -- fixed IDs
            as_kanade uuid := '11111111-2222-3333-4444-555555555555';
            as_kumiko uuid := '22222222-3333-4444-5555-666666666666';
            pt_kanade uuid := '77777777-8888-9999-aaaa-bbbbbbbbbbbb';
            pt_kumiko uuid := 'cccccccc-dddd-eeee-ffff-000000000000';
            sd_analysis uuid := 'aaaa1111-bbbb-2222-cccc-333333333333';
            sd_research uuid := 'bbbb2222-cccc-3333-dddd-444444444444';
            sd_creative uuid := 'cccc3333-dddd-4444-eeee-555555555555';

            has_system_prompt boolean := false;
            has_personality boolean := false;
            has_link_skill_def boolean := false;
            has_link_skill_id boolean := false;
            has_link_skill_name boolean := false;
        BEGIN
            SELECT id INTO u_id FROM users ORDER BY created_at ASC LIMIT 1;
            IF u_id IS NULL THEN
                u_id := '00000000-0000-0000-0000-000000000001';
                INSERT INTO users (id, username, email, password_hash, is_active, is_verified, created_at, updated_at)
                VALUES (u_id, 'local_user', 'local@example.com', 'seed', true, true, now(), now())
                ON CONFLICT (id) DO NOTHING;
            END IF;

            -- assistants table capabilities
            SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='assistants' AND column_name='system_prompt')
            INTO has_system_prompt;
            SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='assistants' AND column_name='personality_template_id')
            INTO has_personality;

            -- templates (insert BEFORE assistant upserts to satisfy FK when personality_template_id exists)
            INSERT INTO personality_templates (id, user_id, name, description, personality_type, system_prompt, characteristics)
            VALUES
              (pt_kanade, u_id, 'プロフェッショナル', '緻密で丁寧なスタイル', 'professional', 'あなたはプロフェッショナルなアシスタントです。', '{"formality":"high","detail_level":"high"}'),
              (pt_kumiko, u_id, 'フレンドリー', '親しみやすい会話', 'friendly', 'あなたはフレンドリーなアシスタントです。', '{"formality":"low","detail_level":"medium"}')
            ON CONFLICT (id) DO NOTHING;

            -- upsert Kanade (convert existing Demo Assistant if present)
            IF has_system_prompt AND has_personality THEN
                INSERT INTO assistants (id, user_id, name, description, system_prompt, personality_template_id, default_llm_model, is_active, is_public)
                VALUES (as_kanade, u_id, 'Kanade', 'Professional, detail-oriented assistant', 'You are a professional assistant.', pt_kanade, 'claude-3-opus', true, false)
                ON CONFLICT (id) DO UPDATE
                  SET name='Kanade', description='Professional, detail-oriented assistant',
                      system_prompt='You are a professional assistant.', personality_template_id=pt_kanade,
                      default_llm_model='claude-3-opus', updated_at=now();
            ELSIF has_system_prompt THEN
                INSERT INTO assistants (id, user_id, name, description, system_prompt, default_llm_model, is_active, is_public)
                VALUES (as_kanade, u_id, 'Kanade', 'Professional, detail-oriented assistant', 'You are a professional assistant.', 'claude-3-opus', true, false)
                ON CONFLICT (id) DO UPDATE
                  SET name='Kanade', description='Professional, detail-oriented assistant',
                      system_prompt='You are a professional assistant.',
                      default_llm_model='claude-3-opus', updated_at=now();
            ELSIF has_personality THEN
                INSERT INTO assistants (id, user_id, name, description, personality_template_id, default_llm_model, is_active, is_public)
                VALUES (as_kanade, u_id, 'Kanade', 'Professional, detail-oriented assistant', pt_kanade, 'claude-3-opus', true, false)
                ON CONFLICT (id) DO UPDATE
                  SET name='Kanade', description='Professional, detail-oriented assistant',
                      personality_template_id=pt_kanade,
                      default_llm_model='claude-3-opus', updated_at=now();
            ELSE
                INSERT INTO assistants (id, user_id, name, description, default_llm_model, is_active, is_public)
                VALUES (as_kanade, u_id, 'Kanade', 'Professional, detail-oriented assistant', 'claude-3-opus', true, false)
                ON CONFLICT (id) DO UPDATE
                  SET name='Kanade', description='Professional, detail-oriented assistant',
                      default_llm_model='claude-3-opus', updated_at=now();
            END IF;

            -- insert Kumiko
            IF has_system_prompt AND has_personality THEN
                INSERT INTO assistants (id, user_id, name, description, system_prompt, personality_template_id, default_llm_model, is_active, is_public)
                VALUES (as_kumiko, u_id, 'Kumiko', 'Friendly and supportive assistant', 'You are a friendly assistant.', pt_kumiko, 'gemini-pro', true, false)
                ON CONFLICT (id) DO NOTHING;
            ELSIF has_system_prompt THEN
                INSERT INTO assistants (id, user_id, name, description, system_prompt, default_llm_model, is_active, is_public)
                VALUES (as_kumiko, u_id, 'Kumiko', 'Friendly and supportive assistant', 'You are a friendly assistant.', 'gemini-pro', true, false)
                ON CONFLICT (id) DO NOTHING;
            ELSIF has_personality THEN
                INSERT INTO assistants (id, user_id, name, description, personality_template_id, default_llm_model, is_active, is_public)
                VALUES (as_kumiko, u_id, 'Kumiko', 'Friendly and supportive assistant', pt_kumiko, 'gemini-pro', true, false)
                ON CONFLICT (id) DO NOTHING;
            ELSE
                INSERT INTO assistants (id, user_id, name, description, default_llm_model, is_active, is_public)
                VALUES (as_kumiko, u_id, 'Kumiko', 'Friendly and supportive assistant', 'gemini-pro', true, false)
                ON CONFLICT (id) DO NOTHING;
            END IF;

            -- skills
            INSERT INTO skill_definitions (id, skill_code, name, description, skill_type, configuration)
            VALUES
              (sd_analysis, 'ANALYSIS', 'データ分析', '高度な分析スキル', 'analysis', '{"preferred":"claude-3-opus","fallback":["gemini-pro"]}'),
              (sd_research, 'RESEARCH', 'Webリサーチ', 'Web情報収集', 'research', '{"preferred":"gemini-pro","fallback":["gpt-4-turbo"]}'),
              (sd_creative, 'CREATIVE', '創作・ライティング', '創造的出力', 'creative', '{"preferred":"gpt-4-turbo","fallback":[]}')
            ON CONFLICT (id) DO NOTHING;

            -- link assistants to skills as available
            SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='assistant_skills' AND column_name='skill_definition_id') INTO has_link_skill_def;
            SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='assistant_skills' AND column_name='skill_id') INTO has_link_skill_id;
            SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='assistant_skills' AND column_name='skill_name') INTO has_link_skill_name;

            IF has_link_skill_def THEN
                INSERT INTO assistant_skills (assistant_id, skill_definition_id)
                VALUES (as_kanade, sd_analysis), (as_kanade, sd_creative), (as_kumiko, sd_research)
                ON CONFLICT DO NOTHING;
            ELSIF has_link_skill_id THEN
                INSERT INTO assistant_skills (assistant_id, skill_id)
                VALUES (as_kanade, sd_analysis), (as_kanade, sd_creative), (as_kumiko, sd_research)
                ON CONFLICT DO NOTHING;
            ELSIF has_link_skill_name THEN
                INSERT INTO assistant_skills (assistant_id, skill_name)
                VALUES (as_kanade, 'ANALYSIS'), (as_kanade, 'CREATIVE'), (as_kumiko, 'RESEARCH')
                ON CONFLICT DO NOTHING;
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM assistant_skills 
          WHERE assistant_id IN ('11111111-2222-3333-4444-555555555555','22222222-3333-4444-5555-666666666666')
             OR skill_definition_id IN ('aaaa1111-bbbb-2222-cccc-333333333333','bbbb2222-cccc-3333-dddd-444444444444','cccc3333-dddd-4444-eeee-555555555555')
             OR skill_id IN ('aaaa1111-bbbb-2222-cccc-333333333333','bbbb2222-cccc-3333-dddd-444444444444','cccc3333-dddd-4444-eeee-555555555555')
             OR skill_name IN ('ANALYSIS','RESEARCH','CREATIVE');
        DELETE FROM skill_definitions WHERE id IN ('aaaa1111-bbbb-2222-cccc-333333333333','bbbb2222-cccc-3333-dddd-444444444444','cccc3333-dddd-4444-eeee-555555555555');
        DELETE FROM personality_templates WHERE id IN ('77777777-8888-9999-aaaa-bbbbbbbbbbbb','cccccccc-dddd-eeee-ffff-000000000000');
        -- assistants remain intact except seed IDs removed
        DELETE FROM assistants WHERE id IN ('22222222-3333-4444-5555-666666666666');
        -- Kanade (1111...) may have been an update; do not delete to avoid removing existing data
        """
    )
