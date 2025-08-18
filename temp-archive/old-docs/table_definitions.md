# テーブル定義書：AI秘書チーム・プラットフォーム

* **ドキュメントバージョン:** v1.0 (最終版)
* **作成日:** 2025年1月
* **目的:** AI秘書チーム・プラットフォームの完全なテーブル定義を提供する

---

## 1. 概要

### 1.1. 設計方針
- **完全カスタマイズ**: ユーザーが名前、性格、ボイス、画像、スキルを自由に組み合わせ
- **柔軟性**: 音声あり/なし、システム提供/ユーザー作成の混在
- **拡張性**: 新しいコンポーネントの簡単追加
- **共有機能**: 良い組み合わせの他のユーザーとの共有

### 1.2. テーブル構成
- **ユーザー管理系**: 2テーブル
- **AI秘書管理系**: 6テーブル
- **会話管理系**: 2テーブル
- **ファイル管理系**: 1テーブル
- **ワークフロー管理系**: 2テーブル
- **知識管理系**: 1テーブル
- **外部連携系**: 1テーブル

**合計: 15テーブル**

---

## 2. 完全なテーブル定義

### 2.1. ユーザー管理系

#### users テーブル
```sql
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

-- インデックス
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_active ON users(is_active);
```

#### user_preferences テーブル
```sql
CREATE TABLE user_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    default_assistant_id UUID,
    default_llm_model VARCHAR(100) DEFAULT 'gemini-pro',
    voice_enabled BOOLEAN NOT NULL DEFAULT true,
    default_voice_id UUID REFERENCES voices(id),
    auto_save_conversations BOOLEAN NOT NULL DEFAULT true,
    theme VARCHAR(20) DEFAULT 'light',
    language VARCHAR(10) DEFAULT 'ja',
    timezone VARCHAR(50) DEFAULT 'Asia/Tokyo',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

### 2.2. AI秘書管理系

#### voices テーブル
```sql
CREATE TABLE voices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE, -- NULL = システム提供
    name VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL, -- 'google_tts', 'azure_speech', 'amazon_polly', 'custom'
    voice_id VARCHAR(100) NOT NULL,
    language VARCHAR(10) NOT NULL,
    gender VARCHAR(10), -- 'male', 'female', 'neutral'
    settings JSONB,
    is_public BOOLEAN NOT NULL DEFAULT false,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- インデックス
CREATE INDEX idx_voices_user_id ON voices(user_id);
CREATE INDEX idx_voices_provider ON voices(provider);
CREATE INDEX idx_voices_language ON voices(language);
CREATE INDEX idx_voices_public ON voices(is_public);
CREATE INDEX idx_voices_active ON voices(is_active);
```

#### skill_definitions テーブル
```sql
CREATE TABLE skill_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE, -- NULL = システム提供
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

-- インデックス
CREATE INDEX idx_skill_definitions_user_id ON skill_definitions(user_id);
CREATE INDEX idx_skill_definitions_type ON skill_definitions(skill_type);
CREATE INDEX idx_skill_definitions_public ON skill_definitions(is_public);
CREATE INDEX idx_skill_definitions_active ON skill_definitions(is_active);
```

#### avatars テーブル
```sql
CREATE TABLE avatars (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE, -- NULL = システム提供
    name VARCHAR(100) NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    image_type VARCHAR(20) NOT NULL, -- 'character', 'icon', 'illustration'
    gender VARCHAR(10), -- 'male', 'female', 'neutral'
    style VARCHAR(50), -- 'anime', 'realistic', 'cartoon', 'professional'
    tags TEXT[], -- 検索用タグ
    is_public BOOLEAN NOT NULL DEFAULT false,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- インデックス
CREATE INDEX idx_avatars_user_id ON avatars(user_id);
CREATE INDEX idx_avatars_type ON avatars(image_type);
CREATE INDEX idx_avatars_gender ON avatars(gender);
CREATE INDEX idx_avatars_style ON avatars(style);
CREATE INDEX idx_avatars_tags ON avatars USING GIN(tags);
CREATE INDEX idx_avatars_public ON avatars(is_public);
CREATE INDEX idx_avatars_active ON avatars(is_active);
```

#### personality_templates テーブル
```sql
CREATE TABLE personality_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE, -- NULL = システム提供
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    personality_type VARCHAR(50) NOT NULL, -- 'professional', 'friendly', 'creative', 'analytical'
    system_prompt TEXT NOT NULL,
    characteristics JSONB, -- 性格の詳細特徴
    is_public BOOLEAN NOT NULL DEFAULT false,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- インデックス
CREATE INDEX idx_personality_templates_user_id ON personality_templates(user_id);
CREATE INDEX idx_personality_templates_type ON personality_templates(personality_type);
CREATE INDEX idx_personality_templates_public ON personality_templates(is_public);
CREATE INDEX idx_personality_templates_active ON personality_templates(is_active);
```

#### assistants テーブル
```sql
CREATE TABLE assistants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL, -- ユーザーが決める名前
    description TEXT,
    personality_template_id UUID REFERENCES personality_templates(id),
    voice_id UUID REFERENCES voices(id), -- NULL許可（音声なしも可能）
    avatar_id UUID REFERENCES avatars(id),
    default_llm_model VARCHAR(100) DEFAULT 'gemini-pro',
    custom_system_prompt TEXT, -- 性格テンプレートをベースにしたカスタムプロンプト
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_public BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- インデックス
CREATE INDEX idx_assistants_user_id ON assistants(user_id);
CREATE INDEX idx_assistants_personality ON assistants(personality_template_id);
CREATE INDEX idx_assistants_voice ON assistants(voice_id);
CREATE INDEX idx_assistants_avatar ON assistants(avatar_id);
CREATE INDEX idx_assistants_active ON assistants(is_active);
CREATE INDEX idx_assistants_public ON assistants(is_public);
```

#### assistant_skills テーブル
```sql
CREATE TABLE assistant_skills (
    assistant_id UUID NOT NULL REFERENCES assistants(id) ON DELETE CASCADE,
    skill_definition_id UUID NOT NULL REFERENCES skill_definitions(id) ON DELETE CASCADE,
    is_enabled BOOLEAN NOT NULL DEFAULT true,
    priority INTEGER NOT NULL DEFAULT 1,
    custom_settings JSONB, -- この秘書専用のスキル設定
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    PRIMARY KEY (assistant_id, skill_definition_id)
);

-- インデックス
CREATE INDEX idx_assistant_skills_assistant_id ON assistant_skills(assistant_id);
CREATE INDEX idx_assistant_skills_skill_id ON assistant_skills(skill_definition_id);
CREATE INDEX idx_assistant_skills_enabled ON assistant_skills(is_enabled);
CREATE INDEX idx_assistant_skills_priority ON assistant_skills(priority);
```

### 2.3. 会話管理系

#### conversations テーブル
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    assistant_id UUID NOT NULL REFERENCES assistants(id) ON DELETE CASCADE,
    title VARCHAR(255),
    conversation_type VARCHAR(50) DEFAULT 'chat', -- 'chat', 'research', 'document_creation', 'workflow'
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'archived', 'deleted'
    voice_enabled BOOLEAN NOT NULL DEFAULT true, -- 会話レベルでの音声制御
    voice_id UUID REFERENCES voices(id), -- 会話専用のボイス設定
    metadata JSONB, -- 会話のメタデータ
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- インデックス
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_assistant_id ON conversations(assistant_id);
CREATE INDEX idx_conversations_type ON conversations(conversation_type);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_voice_enabled ON conversations(voice_enabled);
CREATE INDEX idx_conversations_created_at ON conversations(created_at);
CREATE INDEX idx_conversations_metadata ON conversations USING GIN(metadata);
```

#### messages テーブル
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    content_type VARCHAR(20) DEFAULT 'text', -- 'text', 'image', 'file', 'audio'
    metadata JSONB, -- メッセージのメタデータ（音声設定、感情スコア等）
    parent_message_id UUID REFERENCES messages(id), -- スレッド対応
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- インデックス
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_role ON messages(role);
CREATE INDEX idx_messages_content_type ON messages(content_type);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_parent_id ON messages(parent_message_id);
CREATE INDEX idx_messages_metadata ON messages USING GIN(metadata);
```

### 2.4. ファイル管理系

#### files テーブル
```sql
CREATE TABLE files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    message_id UUID REFERENCES messages(id) ON DELETE SET NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_type VARCHAR(20) NOT NULL, -- 'image', 'document', 'audio', 'video'
    metadata JSONB, -- ファイルのメタデータ（OCR結果、音声認識結果等）
    is_processed BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- インデックス
CREATE INDEX idx_files_user_id ON files(user_id);
CREATE INDEX idx_files_conversation_id ON files(conversation_id);
CREATE INDEX idx_files_message_id ON files(message_id);
CREATE INDEX idx_files_type ON files(file_type);
CREATE INDEX idx_files_processed ON files(is_processed);
CREATE INDEX idx_files_metadata ON files USING GIN(metadata);
```

### 2.5. ワークフロー管理系

#### workflows テーブル
```sql
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    workflow_type VARCHAR(50) NOT NULL, -- 'research', 'document_creation', 'sns_post'
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_template BOOLEAN NOT NULL DEFAULT false,
    metadata JSONB, -- ワークフローの設定情報
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- インデックス
CREATE INDEX idx_workflows_user_id ON workflows(user_id);
CREATE INDEX idx_workflows_type ON workflows(workflow_type);
CREATE INDEX idx_workflows_active ON workflows(is_active);
CREATE INDEX idx_workflows_template ON workflows(is_template);
```

#### workflow_steps テーブル
```sql
CREATE TABLE workflow_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    step_order INTEGER NOT NULL,
    step_name VARCHAR(255) NOT NULL,
    step_type VARCHAR(50) NOT NULL, -- 'ai_task', 'api_call', 'condition', 'loop'
    assistant_id UUID REFERENCES assistants(id),
    prompt_template TEXT,
    input_mapping JSONB, -- 入力データのマッピング設定
    output_mapping JSONB, -- 出力データのマッピング設定
    conditions JSONB, -- 条件分岐の設定
    is_enabled BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(workflow_id, step_order)
);

-- インデックス
CREATE INDEX idx_workflow_steps_workflow_id ON workflow_steps(workflow_id);
CREATE INDEX idx_workflow_steps_order ON workflow_steps(workflow_id, step_order);
CREATE INDEX idx_workflow_steps_assistant_id ON workflow_steps(assistant_id);
```

### 2.6. 知識管理系

#### knowledge_base テーブル
```sql
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    content_type VARCHAR(50) NOT NULL, -- 'document', 'web_page', 'note', 'conversation'
    source_url VARCHAR(500),
    tags TEXT[], -- タグ配列
    embedding_vector VECTOR(1536), -- pgvector拡張使用
    metadata JSONB,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- インデックス
CREATE INDEX idx_knowledge_base_user_id ON knowledge_base(user_id);
CREATE INDEX idx_knowledge_base_content_type ON knowledge_base(content_type);
CREATE INDEX idx_knowledge_base_tags ON knowledge_base USING GIN(tags);
CREATE INDEX idx_knowledge_base_active ON knowledge_base(is_active);
CREATE INDEX idx_knowledge_base_embedding ON knowledge_base USING ivfflat (embedding_vector vector_cosine_ops);
```

### 2.7. 外部連携系

#### external_connections テーブル
```sql
CREATE TABLE external_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    service_name VARCHAR(100) NOT NULL, -- 'google_drive', 'obsidian', 'twitter', 'slack'
    connection_name VARCHAR(255) NOT NULL,
    credentials JSONB NOT NULL, -- 暗号化された認証情報
    settings JSONB, -- 接続設定
    is_active BOOLEAN NOT NULL DEFAULT true,
    last_sync_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, service_name, connection_name)
);

-- インデックス
CREATE INDEX idx_external_connections_user_id ON external_connections(user_id);
CREATE INDEX idx_external_connections_service ON external_connections(service_name);
CREATE INDEX idx_external_connections_active ON external_connections(is_active);
```

---

## 3. ビューとトリガー

### 3.1. 便利なビュー

#### conversation_summary ビュー
```sql
CREATE VIEW conversation_summary AS
SELECT 
    c.id,
    c.user_id,
    c.title,
    c.conversation_type,
    c.status,
    c.voice_enabled,
    c.created_at,
    c.updated_at,
    a.name as assistant_name,
    v.name as voice_name,
    av.name as avatar_name,
    COUNT(m.id) as message_count,
    MAX(m.created_at) as last_message_at
FROM conversations c
LEFT JOIN assistants a ON c.assistant_id = a.id
LEFT JOIN voices v ON c.voice_id = v.id
LEFT JOIN avatars av ON a.avatar_id = av.id
LEFT JOIN messages m ON c.id = m.conversation_id
GROUP BY c.id, c.user_id, c.title, c.conversation_type, c.status, c.voice_enabled, 
         c.created_at, c.updated_at, a.name, v.name, av.name;
```

#### assistant_detail ビュー
```sql
CREATE VIEW assistant_detail AS
SELECT 
    a.id,
    a.user_id,
    a.name,
    a.description,
    a.default_llm_model,
    a.is_active,
    a.is_public,
    pt.name as personality_name,
    pt.personality_type,
    v.name as voice_name,
    v.provider as voice_provider,
    av.name as avatar_name,
    av.style as avatar_style,
    COUNT(as2.skill_definition_id) as skill_count,
    a.created_at,
    a.updated_at
FROM assistants a
LEFT JOIN personality_templates pt ON a.personality_template_id = pt.id
LEFT JOIN voices v ON a.voice_id = v.id
LEFT JOIN avatars av ON a.avatar_id = av.id
LEFT JOIN assistant_skills as2 ON a.id = as2.assistant_id AND as2.is_enabled = true
GROUP BY a.id, a.user_id, a.name, a.description, a.default_llm_model, a.is_active, a.is_public,
         pt.name, pt.personality_type, v.name, v.provider, av.name, av.style, a.created_at, a.updated_at;
```

### 3.2. 自動更新トリガー

#### updated_at 自動更新関数
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 各テーブルにトリガーを設定
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_assistants_updated_at BEFORE UPDATE ON assistants FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_messages_updated_at BEFORE UPDATE ON messages FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_files_updated_at BEFORE UPDATE ON files FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workflows_updated_at BEFORE UPDATE ON workflows FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workflow_steps_updated_at BEFORE UPDATE ON workflow_steps FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_knowledge_base_updated_at BEFORE UPDATE ON knowledge_base FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_external_connections_updated_at BEFORE UPDATE ON external_connections FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## 4. 制約と列挙値

### 4.1. チェック制約
```sql
-- messages.role
CHECK (role IN ('user', 'assistant', 'system'))

-- conversation_type
CHECK (conversation_type IN ('chat', 'research', 'document_creation', 'workflow'))

-- status
CHECK (status IN ('active', 'archived', 'deleted'))

-- content_type
CHECK (content_type IN ('text', 'image', 'file', 'audio'))

-- file_type
CHECK (file_type IN ('image', 'document', 'audio', 'video'))

-- step_type
CHECK (step_type IN ('ai_task', 'api_call', 'condition', 'loop'))

-- personality_type
CHECK (personality_type IN ('professional', 'friendly', 'creative', 'analytical'))

-- image_type
CHECK (image_type IN ('character', 'icon', 'illustration'))

-- gender
CHECK (gender IN ('male', 'female', 'neutral'))
```

### 4.2. 一意制約
```sql
-- users
UNIQUE(username)
UNIQUE(email)

-- skill_definitions
UNIQUE(user_id, skill_code)

-- workflow_steps
UNIQUE(workflow_id, step_order)

-- external_connections
UNIQUE(user_id, service_name, connection_name)
```

### 4.3. 外部キー制約
```sql
-- カスケード削除
ON DELETE CASCADE: user_preferences, assistants, conversations, files, workflows, knowledge_base, external_connections, assistant_skills, workflow_steps

-- SET NULL
ON DELETE SET NULL: files.conversation_id, files.message_id, conversations.voice_id, assistants.voice_id, assistants.avatar_id, assistants.personality_template_id
```

---

## 5. 初期セットアップ

### 5.1. 拡張機能の有効化
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
```

### 5.2. スキーマ作成
```sql
CREATE SCHEMA IF NOT EXISTS ai_secretary;
```

---

## 6. パフォーマンス最適化

### 6.1. 複合インデックス
```sql
-- 会話検索用
CREATE INDEX idx_conversations_user_status_created ON conversations(user_id, status, created_at DESC);

-- メッセージ検索用
CREATE INDEX idx_messages_conversation_role_created ON messages(conversation_id, role, created_at);

-- ファイル検索用
CREATE INDEX idx_files_user_type_created ON files(user_id, file_type, created_at DESC);
```

### 6.2. 部分インデックス
```sql
-- アクティブな秘書のみ
CREATE INDEX idx_assistants_active_only ON assistants(user_id, name) WHERE is_active = true;

-- アクティブな会話のみ
CREATE INDEX idx_conversations_active_only ON conversations(user_id, created_at DESC) WHERE status = 'active';
```

---

## 7. セキュリティ

### 7.1. Row Level Security (RLS)
```sql
-- ユーザー別データ分離のためのRLS設定
ALTER TABLE assistants ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
-- 他のテーブルにも同様に設定
```

### 7.2. 暗号化
```sql
-- 機密情報の暗号化（実装時に対応）
-- external_connections.credentials 等
```

---

## 8. マイグレーション戦略

### 8.1. Phase 1 (MVP)
- users, user_preferences
- voices, skill_definitions, avatars, personality_templates
- assistants, assistant_skills
- conversations, messages

### 8.2. Phase 2
- files
- workflows, workflow_steps

### 8.3. Phase 3
- knowledge_base
- external_connections

---

## 9. 監査とログ

### 9.1. 変更履歴
```sql
-- 重要なテーブルの変更履歴を記録するためのテーブル（実装時に対応）
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    user_id UUID REFERENCES users(id),
    action VARCHAR(20) NOT NULL, -- 'INSERT', 'UPDATE', 'DELETE'
    old_values JSONB,
    new_values JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

---

## 10. バックアップと復旧

### 10.1. バックアップ戦略
- 日次フルバックアップ
- 1時間ごとの増分バックアップ
- ポイントインタイムリカバリ対応

### 10.2. アーカイブ戦略
- 古い会話の自動アーカイブ（3ヶ月以上）
- 大きなファイルの段階的削除
- ログローテーション 