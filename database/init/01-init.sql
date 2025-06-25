-- AI秘書チーム・プラットフォーム データベース初期化スクリプト
-- 作成日: 2025年1月

-- 拡張機能の有効化
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- スキーマ作成
CREATE SCHEMA IF NOT EXISTS ai_secretary;

-- ユーザー管理系テーブル
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_verified BOOLEAN NOT NULL DEFAULT false,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE user_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    default_assistant_id UUID,
    default_llm_model VARCHAR(100) DEFAULT 'gemini-pro',
    voice_enabled BOOLEAN NOT NULL DEFAULT true,
    default_voice_id UUID,
    auto_save_conversations BOOLEAN NOT NULL DEFAULT true,
    theme VARCHAR(20) DEFAULT 'light',
    language VARCHAR(10) DEFAULT 'ja',
    timezone VARCHAR(50) DEFAULT 'Asia/Tokyo',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- AI秘書管理系テーブル
CREATE TABLE voices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    voice_id VARCHAR(100) NOT NULL,
    language VARCHAR(10) NOT NULL,
    gender VARCHAR(10) CHECK (gender IN ('male', 'female', 'neutral')),
    settings JSONB,
    is_public BOOLEAN NOT NULL DEFAULT false,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE skill_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    skill_code VARCHAR(10) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    skill_type VARCHAR(50) NOT NULL,
    configuration JSONB NOT NULL,
    is_public BOOLEAN NOT NULL DEFAULT false,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, skill_code)
);

CREATE TABLE avatars (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    image_type VARCHAR(20) NOT NULL CHECK (image_type IN ('character', 'icon', 'illustration')),
    gender VARCHAR(10) CHECK (gender IN ('male', 'female', 'neutral')),
    style VARCHAR(50),
    tags TEXT[],
    is_public BOOLEAN NOT NULL DEFAULT false,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE personality_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    personality_type VARCHAR(50) NOT NULL CHECK (personality_type IN ('professional', 'friendly', 'creative', 'analytical')),
    system_prompt TEXT NOT NULL,
    characteristics JSONB,
    is_public BOOLEAN NOT NULL DEFAULT false,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE assistants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    personality_template_id UUID REFERENCES personality_templates(id),
    voice_id UUID REFERENCES voices(id),
    avatar_id UUID REFERENCES avatars(id),
    default_llm_model VARCHAR(100) DEFAULT 'gemini-pro',
    custom_system_prompt TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_public BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE assistant_skills (
    assistant_id UUID NOT NULL REFERENCES assistants(id) ON DELETE CASCADE,
    skill_definition_id UUID NOT NULL REFERENCES skill_definitions(id) ON DELETE CASCADE,
    is_enabled BOOLEAN NOT NULL DEFAULT true,
    priority INTEGER NOT NULL DEFAULT 1,
    custom_settings JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    PRIMARY KEY (assistant_id, skill_definition_id)
);

-- 会話管理系テーブル
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    assistant_id UUID NOT NULL REFERENCES assistants(id) ON DELETE CASCADE,
    title VARCHAR(255),
    conversation_type VARCHAR(50) DEFAULT 'chat' CHECK (conversation_type IN ('chat', 'research', 'document_creation', 'workflow')),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted')),
    voice_enabled BOOLEAN NOT NULL DEFAULT true,
    voice_id UUID REFERENCES voices(id),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    content_type VARCHAR(20) DEFAULT 'text' CHECK (content_type IN ('text', 'image', 'file', 'audio')),
    metadata JSONB,
    parent_message_id UUID REFERENCES messages(id),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- ファイル管理系テーブル
CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    message_id UUID REFERENCES messages(id) ON DELETE SET NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_type VARCHAR(20) NOT NULL CHECK (file_type IN ('image', 'document', 'audio', 'video')),
    metadata JSONB,
    is_processed BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- インデックス作成
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_active ON users(is_active);

CREATE INDEX idx_voices_user_id ON voices(user_id);
CREATE INDEX idx_voices_provider ON voices(provider);
CREATE INDEX idx_voices_language ON voices(language);
CREATE INDEX idx_voices_public ON voices(is_public);
CREATE INDEX idx_voices_active ON voices(is_active);

CREATE INDEX idx_skill_definitions_user_id ON skill_definitions(user_id);
CREATE INDEX idx_skill_definitions_type ON skill_definitions(skill_type);
CREATE INDEX idx_skill_definitions_public ON skill_definitions(is_public);
CREATE INDEX idx_skill_definitions_active ON skill_definitions(is_active);

CREATE INDEX idx_avatars_user_id ON avatars(user_id);
CREATE INDEX idx_avatars_type ON avatars(image_type);
CREATE INDEX idx_avatars_gender ON avatars(gender);
CREATE INDEX idx_avatars_style ON avatars(style);
CREATE INDEX idx_avatars_tags ON avatars USING GIN(tags);
CREATE INDEX idx_avatars_public ON avatars(is_public);
CREATE INDEX idx_avatars_active ON avatars(is_active);

CREATE INDEX idx_personality_templates_user_id ON personality_templates(user_id);
CREATE INDEX idx_personality_templates_type ON personality_templates(personality_type);
CREATE INDEX idx_personality_templates_public ON personality_templates(is_public);
CREATE INDEX idx_personality_templates_active ON personality_templates(is_active);

CREATE INDEX idx_assistants_user_id ON assistants(user_id);
CREATE INDEX idx_assistants_personality ON assistants(personality_template_id);
CREATE INDEX idx_assistants_voice ON assistants(voice_id);
CREATE INDEX idx_assistants_avatar ON assistants(avatar_id);
CREATE INDEX idx_assistants_active ON assistants(is_active);
CREATE INDEX idx_assistants_public ON assistants(is_public);

CREATE INDEX idx_assistant_skills_assistant_id ON assistant_skills(assistant_id);
CREATE INDEX idx_assistant_skills_skill_id ON assistant_skills(skill_definition_id);
CREATE INDEX idx_assistant_skills_enabled ON assistant_skills(is_enabled);
CREATE INDEX idx_assistant_skills_priority ON assistant_skills(priority);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_assistant_id ON conversations(assistant_id);
CREATE INDEX idx_conversations_type ON conversations(conversation_type);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_voice_enabled ON conversations(voice_enabled);
CREATE INDEX idx_conversations_created_at ON conversations(created_at);
CREATE INDEX idx_conversations_metadata ON conversations USING GIN(metadata);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_role ON messages(role);
CREATE INDEX idx_messages_content_type ON messages(content_type);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_parent_id ON messages(parent_message_id);
CREATE INDEX idx_messages_metadata ON messages USING GIN(metadata);

CREATE INDEX idx_files_user_id ON files(user_id);
CREATE INDEX idx_files_conversation_id ON files(conversation_id);
CREATE INDEX idx_files_message_id ON files(message_id);
CREATE INDEX idx_files_type ON files(file_type);
CREATE INDEX idx_files_processed ON files(is_processed);
CREATE INDEX idx_files_metadata ON files USING GIN(metadata);

-- 複合インデックス
CREATE INDEX idx_conversations_user_status_created ON conversations(user_id, status, created_at DESC);
CREATE INDEX idx_messages_conversation_role_created ON messages(conversation_id, role, created_at);
CREATE INDEX idx_files_user_type_created ON files(user_id, file_type, created_at DESC);

-- 部分インデックス
CREATE INDEX idx_assistants_active_only ON assistants(user_id, name) WHERE is_active = true;
CREATE INDEX idx_conversations_active_only ON conversations(user_id, created_at DESC) WHERE status = 'active';

-- 自動更新トリガー関数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- トリガー設定
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_assistants_updated_at BEFORE UPDATE ON assistants FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_messages_updated_at BEFORE UPDATE ON messages FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_files_updated_at BEFORE UPDATE ON files FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 初期データ挿入（システム提供の基本データ）
INSERT INTO voices (id, user_id, name, provider, voice_id, language, gender, settings, is_public, is_active) VALUES
(gen_random_uuid(), NULL, '日本語女性1', 'google_tts', 'ja-JP-Neural2-F', 'ja', 'female', '{"speed": 1.0, "pitch": 0.0}', true, true),
(gen_random_uuid(), NULL, '日本語男性1', 'google_tts', 'ja-JP-Neural2-D', 'ja', 'male', '{"speed": 1.0, "pitch": 0.0}', true, true),
(gen_random_uuid(), NULL, '英語女性1', 'google_tts', 'en-US-Neural2-F', 'en', 'female', '{"speed": 1.0, "pitch": 0.0}', true, true),
(gen_random_uuid(), NULL, '英語男性1', 'google_tts', 'en-US-Neural2-D', 'en', 'male', '{"speed": 1.0, "pitch": 0.0}', true, true);

INSERT INTO personality_templates (id, user_id, name, description, personality_type, system_prompt, characteristics, is_public, is_active) VALUES
(gen_random_uuid(), NULL, 'プロフェッショナル', 'ビジネス向けの専門的で丁寧な性格', 'professional', 'あなたは専門的で丁寧なビジネスアシスタントです。常に正確で簡潔な回答を心がけてください。', '{"formality": "high", "detail_level": "medium", "tone": "professional"}', true, true),
(gen_random_uuid(), NULL, 'フレンドリー', '親しみやすく気さくな性格', 'friendly', 'あなたは親しみやすく気さくなアシスタントです。ユーザーと自然な会話を楽しみながらサポートします。', '{"formality": "low", "detail_level": "medium", "tone": "friendly"}', true, true),
(gen_random_uuid(), NULL, 'クリエイティブ', '創造的で独創的なアイデアを提供する性格', 'creative', 'あなたは創造的で独創的なアシスタントです。新しい視点や革新的なアイデアを提供します。', '{"formality": "medium", "detail_level": "high", "tone": "creative"}', true, true),
(gen_random_uuid(), NULL, 'アナリティカル', '論理的で分析的な性格', 'analytical', 'あなたは論理的で分析的なアシスタントです。データに基づいた客観的な分析を提供します。', '{"formality": "high", "detail_level": "high", "tone": "analytical"}', true, true);

-- 完了メッセージ
SELECT 'AI秘書チーム・プラットフォーム データベース初期化完了' as status; 