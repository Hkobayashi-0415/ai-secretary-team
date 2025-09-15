-- AI秘書チーム・プラットフォーム データベース初期化スクリプト
-- バージョン: 1.0
-- 作成日: 2025年1月

-- 拡張機能の有効化
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- スキーマ作成
CREATE SCHEMA IF NOT EXISTS ai_secretary;

-- 1. ユーザー管理テーブル
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
    auto_save_conversations BOOLEAN NOT NULL DEFAULT true,
    theme VARCHAR(20) DEFAULT 'light',
    language VARCHAR(10) DEFAULT 'ja',
    timezone VARCHAR(50) DEFAULT 'Asia/Tokyo',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 2. AI秘書管理テーブル
CREATE TABLE assistants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    system_prompt TEXT NOT NULL,
    personality_type VARCHAR(50),
    default_llm_model VARCHAR(100) DEFAULT 'gemini-pro',
    voice_id VARCHAR(100),
    avatar_url VARCHAR(500),
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_public BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE assistant_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assistant_id UUID NOT NULL REFERENCES assistants(id) ON DELETE CASCADE,
    skill_name VARCHAR(100) NOT NULL,
    skill_level INTEGER NOT NULL DEFAULT 1 CHECK (skill_level BETWEEN 1 AND 10),
    description TEXT,
    is_enabled BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(assistant_id, skill_name)
);

-- 3. 会話管理テーブル
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    assistant_id UUID NOT NULL REFERENCES assistants(id) ON DELETE CASCADE,
    title VARCHAR(255),
    conversation_type VARCHAR(50) DEFAULT 'chat',
    status VARCHAR(20) DEFAULT 'active',
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    content_type VARCHAR(20) DEFAULT 'text',
    metadata JSONB,
    parent_message_id UUID REFERENCES messages(id),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 4. ファイル管理テーブル
CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    message_id UUID REFERENCES messages(id) ON DELETE SET NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_type VARCHAR(20) NOT NULL,
    metadata JSONB,
    is_processed BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 5. ワークフロー管理テーブル
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    workflow_type VARCHAR(50) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_template BOOLEAN NOT NULL DEFAULT false,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE workflow_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    step_order INTEGER NOT NULL,
    step_name VARCHAR(255) NOT NULL,
    step_type VARCHAR(50) NOT NULL,
    assistant_id UUID REFERENCES assistants(id),
    prompt_template TEXT,
    input_mapping JSONB,
    output_mapping JSONB,
    conditions JSONB,
    is_enabled BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(workflow_id, step_order)
);

-- 6. 知識管理テーブル
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    content_type VARCHAR(50) NOT NULL,
    source_url VARCHAR(500),
    tags TEXT[],
    embedding_vector VECTOR(1536),
    metadata JSONB,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 7. 外部連携テーブル
CREATE TABLE external_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    service_name VARCHAR(100) NOT NULL,
    connection_name VARCHAR(255) NOT NULL,
    credentials JSONB NOT NULL,
    settings JSONB,
    is_active BOOLEAN NOT NULL DEFAULT true,
    last_sync_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, service_name, connection_name)
);

-- インデックス作成
-- users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_active ON users(is_active);

-- assistants
CREATE INDEX idx_assistants_user_id ON assistants(user_id);
CREATE INDEX idx_assistants_active ON assistants(is_active);
CREATE INDEX idx_assistants_public ON assistants(is_public);

-- assistant_skills
CREATE INDEX idx_assistant_skills_assistant_id ON assistant_skills(assistant_id);
CREATE INDEX idx_assistant_skills_enabled ON assistant_skills(is_enabled);

-- conversations
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_assistant_id ON conversations(assistant_id);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_created_at ON conversations(created_at);
CREATE INDEX idx_conversations_metadata ON conversations USING GIN(metadata);

-- messages
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_role ON messages(role);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_parent_id ON messages(parent_message_id);
CREATE INDEX idx_messages_metadata ON messages USING GIN(metadata);

-- files
CREATE INDEX idx_files_user_id ON files(user_id);
CREATE INDEX idx_files_conversation_id ON files(conversation_id);
CREATE INDEX idx_files_message_id ON files(message_id);
CREATE INDEX idx_files_type ON files(file_type);
CREATE INDEX idx_files_processed ON files(is_processed);
CREATE INDEX idx_files_metadata ON files USING GIN(metadata);

-- workflows
CREATE INDEX idx_workflows_user_id ON workflows(user_id);
CREATE INDEX idx_workflows_type ON workflows(workflow_type);
CREATE INDEX idx_workflows_active ON workflows(is_active);
CREATE INDEX idx_workflows_template ON workflows(is_template);

-- workflow_steps
CREATE INDEX idx_workflow_steps_workflow_id ON workflow_steps(workflow_id);
CREATE INDEX idx_workflow_steps_order ON workflow_steps(workflow_id, step_order);
CREATE INDEX idx_workflow_steps_assistant_id ON workflow_steps(assistant_id);

-- knowledge_base
CREATE INDEX idx_knowledge_base_user_id ON knowledge_base(user_id);
CREATE INDEX idx_knowledge_base_content_type ON knowledge_base(content_type);
CREATE INDEX idx_knowledge_base_tags ON knowledge_base USING GIN(tags);
CREATE INDEX idx_knowledge_base_active ON knowledge_base(is_active);
CREATE INDEX idx_knowledge_base_embedding ON knowledge_base USING ivfflat (embedding_vector vector_cosine_ops);

-- external_connections
CREATE INDEX idx_external_connections_user_id ON external_connections(user_id);
CREATE INDEX idx_external_connections_service ON external_connections(service_name);
CREATE INDEX idx_external_connections_active ON external_connections(is_active);

-- ビュー作成
CREATE VIEW conversation_summary AS
SELECT 
    c.id,
    c.user_id,
    c.title,
    c.conversation_type,
    c.status,
    c.created_at,
    c.updated_at,
    a.name as assistant_name,
    COUNT(m.id) as message_count,
    MAX(m.created_at) as last_message_at
FROM conversations c
LEFT JOIN assistants a ON c.assistant_id = a.id
LEFT JOIN messages m ON c.id = m.conversation_id
GROUP BY c.id, c.user_id, c.title, c.conversation_type, c.status, c.created_at, c.updated_at, a.name;

-- トリガー関数作成
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- トリガー作成
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_assistants_updated_at BEFORE UPDATE ON assistants FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_assistant_skills_updated_at BEFORE UPDATE ON assistant_skills FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_messages_updated_at BEFORE UPDATE ON messages FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_files_updated_at BEFORE UPDATE ON files FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workflows_updated_at BEFORE UPDATE ON workflows FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workflow_steps_updated_at BEFORE UPDATE ON workflow_steps FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_knowledge_base_updated_at BEFORE UPDATE ON knowledge_base FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_external_connections_updated_at BEFORE UPDATE ON external_connections FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 初期データ挿入（サンプル）
INSERT INTO users (username, email, password_hash, first_name, last_name) VALUES
('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2', 'Admin', 'User');

-- デフォルトAI秘書の作成
INSERT INTO assistants (user_id, name, description, system_prompt, personality_type, default_llm_model) VALUES
(
    (SELECT id FROM users WHERE username = 'admin'),
    'メイン秘書',
    '汎用的なタスクをこなすメインのAI秘書',
    'あなたは優秀なAI秘書です。ユーザーの様々なタスクを効率的にサポートしてください。',
    'professional',
    'gemini-pro'
),
(
    (SELECT id FROM users WHERE username = 'admin'),
    'リサーチ秘書',
    '情報収集と分析を専門とするAI秘書',
    'あなたはリサーチ専門のAI秘書です。正確で包括的な情報収集と分析を行ってください。',
    'analytical',
    'gemini-pro'
),
(
    (SELECT id FROM users WHERE username = 'admin'),
    'クリエイティブ秘書',
    '創造的なコンテンツ作成を専門とするAI秘書',
    'あなたはクリエイティブ専門のAI秘書です。独創的で魅力的なコンテンツを作成してください。',
    'creative',
    'gemini-pro'
);

-- スキル設定
INSERT INTO assistant_skills (assistant_id, skill_name, skill_level, description) VALUES
((SELECT id FROM assistants WHERE name = 'メイン秘書'), 'general_assistance', 8, '一般的なタスクサポート'),
((SELECT id FROM assistants WHERE name = 'リサーチ秘書'), 'research', 10, '情報収集・分析'),
((SELECT id FROM assistants WHERE name = 'リサーチ秘書'), 'data_analysis', 9, 'データ分析'),
((SELECT id FROM assistants WHERE name = 'クリエイティブ秘書'), 'content_creation', 10, 'コンテンツ作成'),
((SELECT id FROM assistants WHERE name = 'クリエイティブ秘書'), 'writing', 9, '文章作成');

-- ユーザー設定
INSERT INTO user_preferences (user_id, default_assistant_id, default_llm_model, voice_enabled) VALUES
(
    (SELECT id FROM users WHERE username = 'admin'),
    (SELECT id FROM assistants WHERE name = 'メイン秘書'),
    'gemini-pro',
    true
);

COMMIT; 