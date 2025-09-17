"""Add sample data for testing Phase 2 features

Revision ID: 004_add_sample_data
Revises: 003_add_phase2_remaining_tables
Create Date: 2025-09-01 10:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy.dialects import postgresql
import uuid
import json

# revision identifiers, used by Alembic.
revision = '004_add_sample_data'
down_revision = '006_phase2_updated_at'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """サンプルデータをデータベースに投入します。"""
    print("サンプルデータの投入を開始します...")

    # --- テーブルオブジェクトの定義 ---
    personality_templates_table = table('personality_templates',
        column('id', postgresql.UUID),
        column('user_id', postgresql.UUID),
        column('name', sa.String),
        column('description', sa.Text),
        column('personality_type', sa.String), # 正しいカラム名
        column('system_prompt', sa.Text),
        column('characteristics', postgresql.JSONB) # 正しいカラム名
    )
    # ...（他のテーブル定義は変更なし）...
    skill_definitions_table = table('skill_definitions',
        column('id', postgresql.UUID),
        column('skill_code', sa.String),
        column('name', sa.String),
        column('description', sa.Text),
        column('skill_type', sa.String),
        column('configuration', postgresql.JSONB)
    )
    assistants_table = table('assistants',
        column('id', postgresql.UUID),
        column('user_id', postgresql.UUID),
        column('name', sa.String),
        column('description', sa.String),
        column('personality_template_id', postgresql.UUID),
        column('default_llm_model', sa.String)
    )
    assistant_skills_table = table('assistant_skills',
        column('assistant_id', postgresql.UUID),
        column('skill_definition_id', postgresql.UUID)
    )

    # --- データの準備 ---
    local_user_id = '00000000-0000-0000-0000-000000000001'
    pt_kanade_id = str(uuid.uuid4())
    pt_kumiko_id = str(uuid.uuid4())
    sd_analysis_id = str(uuid.uuid4())
    sd_research_id = str(uuid.uuid4())
    sd_creative_id = str(uuid.uuid4())
    assistant_kanade_id = str(uuid.uuid4())
    assistant_kumiko_id = str(uuid.uuid4())

    # --- データ投入の実行 ---
    # 1. 性格テンプレート (PersonalityTemplates)
    op.bulk_insert(personality_templates_table, [
        {
            'id': pt_kanade_id, 
            'user_id': local_user_id, # ★ 必須項目を追加
            'name': '久石奏', 
            'description': '冷静沈着な現実主義者', 
            'personality_type': 'professional', # 正しいカラム名と有効な値
            'system_prompt': 'あなたは久石奏です。常に周囲を冷静に観察し、物事の本質を見抜いて最も効率的な道を考える現実主義者として振る舞ってください。',
            'characteristics': json.dumps({'formality': 'high', 'detail_level': 'high'}) # 正しいカラム名
        },
        {
            'id': pt_kumiko_id, 
            'user_id': local_user_id, # ★ 必須項目を追加
            'name': '黄前久美子', 
            'description': '流されやすいが芯は強い', 
            'personality_type': 'friendly', # 正しいカラム名と有効な値
            'system_prompt': 'あなたは黄前久美子です。少し優柔不斷に見えるかもしれませんが、いざという時には強い意志を見せるキャラクターとして応答してください。',
            'characteristics': json.dumps({'formality': 'low', 'detail_level': 'medium'}) # 正しいカラム名
        }
    ])
    print("-> 性格テンプレートを2件登録しました。")
    # ...（他のデータ投入処理は変更なし）...
    op.bulk_insert(skill_definitions_table, [
        {'id': sd_analysis_id, 'skill_code': 'ANALYSIS', 'name': 'データ分析', 'description': '複雑なデータから洞察を抽出するスキル', 'skill_type': 'analysis', 'configuration': json.dumps({'preferred': 'claude-3-opus', 'fallback': ['gemini-pro']})},
        {'id': sd_research_id, 'skill_code': 'RESEARCH', 'name': 'Webリサーチ', 'description': 'Web上の情報を効率的に収集・要約するスキル', 'skill_type': 'research', 'configuration': json.dumps({'preferred': 'gemini-pro', 'fallback': ['gpt-4-turbo']})},
        {'id': sd_creative_id, 'skill_code': 'CREATIVE', 'name': '創作・企画', 'description': '新しいアイデアや文章を創出するスキル', 'skill_type': 'creative', 'configuration': json.dumps({'preferred': 'gpt-4-turbo', 'fallback': []})}
    ])
    print("-> スキル定義を3件登録しました。")
    op.bulk_insert(assistants_table, [
        {'id': assistant_kanade_id, 'user_id': local_user_id, 'name': '久石 奏', 'description': 'ユーフォニアム奏者。現実主義者。', 'personality_template_id': pt_kanade_id, 'default_llm_model': 'claude-3-opus'},
        {'id': assistant_kumiko_id, 'user_id': local_user_id, 'name': '黄前 久美子', 'description': 'ユーフォニアム奏者。主人公。', 'personality_template_id': pt_kumiko_id, 'default_llm_model': 'gemini-pro'}
    ])
    print("-> アシスタント（キャラクター）を2件登録しました。")
    op.bulk_insert(assistant_skills_table, [
        {'assistant_id': assistant_kanade_id, 'skill_definition_id': sd_analysis_id},
        {'assistant_id': assistant_kanade_id, 'skill_definition_id': sd_creative_id},
        {'assistant_id': assistant_kumiko_id, 'skill_definition_id': sd_research_id}
    ])
    print("-> アシスタントとスキルを3件紐付けました。")

    print("サンプルデータの投入が完了しました。")


def downgrade() -> None:
    # ...（downgrade処理は変更なし）...
    print("サンプルデータの削除を開始します...")
    op.execute("DELETE FROM assistant_skills")
    op.execute("DELETE FROM assistants")
    op.execute("DELETE FROM skill_definitions")
    op.execute("DELETE FROM personality_templates")
    print("サンプルデータの削除が完了しました。")
