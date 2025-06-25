# データベース設計書：AI秘書チーム・プラットフォーム

* **ドキュメントバージョン:** v1.0
* **作成日:** 2025年1月
* **目的:** AI秘書チーム・プラットフォームのデータベース設計を定義する

---

## 1. 概要

### 1.1. データベース概要
- **DBMS:** PostgreSQL 15+
- **文字エンコーディング:** UTF-8
- **タイムゾーン:** Asia/Tokyo
- **接続方式:** プール接続（pgBouncer推奨）

### 1.2. 設計方針
- **マルチテナント対応:** user_idによるテナント分離
- **スケーラビリティ:** インデックス最適化、パーティショニング対応
- **データ整合性:** 外部キー制約、チェック制約の活用
- **監査機能:** created_at, updated_atの自動管理

---

## 2. テーブル設計

### 2.1. ユーザー管理

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
    auto_save_conversations BOOLEAN NOT NULL DEFAULT true,
    theme VARCHAR(20) DEFAULT 'light',
    language VARCHAR(10) DEFAULT 'ja',
    timezone VARCHAR(50) DEFAULT 'Asia/Tokyo',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

### 2.2. AI秘書管理

#### assistants テーブル
```sql
CREATE TABLE assistants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    system_prompt TEXT NOT NULL,
    personality_type VARCHAR(50), -- 'professional', 'friendly', 'creative', etc.
    default_llm_model VARCHAR(100) DEFAULT 'gemini-pro',
    voice_id VARCHAR(100),
    avatar_url VARCHAR(500),
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_public BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- インデックス
CREATE INDEX idx_assistants_user_id ON assistants(user_id);
CREATE INDEX idx_assistants_active ON assistants(is_active);
CREATE INDEX idx_assistants_public ON assistants(is_public);
```

#### assistant_skills テーブル
```sql
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

-- インデックス
CREATE INDEX idx_assistant_skills_assistant_id ON assistant_skills(assistant_id);
CREATE INDEX idx_assistant_skills_enabled ON assistant_skills(is_enabled);
```

### 2.3. 会話管理

#### conversations テーブル
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    assistant_id UUID NOT NULL REFERENCES assistants(id) ON DELETE CASCADE,
    title VARCHAR(255),
    conversation_type VARCHAR(50) DEFAULT 'chat', -- 'chat', 'research', 'document_creation'
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'archived', 'deleted'
    metadata JSONB, -- 会話のメタデータ（ファイル添付情報、ワークフロー情報等）
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- インデックス
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_assistant_id ON conversations(assistant_id);
CREATE INDEX idx_conversations_status ON conversations(status);
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
    metadata JSONB, -- メッセージのメタデータ（感情スコア、使用モデル、処理時間等）
    parent_message_id UUID REFERENCES messages(id), -- スレッド対応
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- インデックス
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_role ON messages(role);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_parent_id ON messages(parent_message_id);
CREATE INDEX idx_messages_metadata ON messages USING GIN(metadata);
```

### 2.4. ファイル管理

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

### 2.5. ワークフロー管理

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

### 2.6. 知識管理

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

### 2.7. 外部連携

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

## 3. ビューとファンクション

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
    c.created_at,
    c.updated_at,
    a.name as assistant_name,
    COUNT(m.id) as message_count,
    MAX(m.created_at) as last_message_at
FROM conversations c
LEFT JOIN assistants a ON c.assistant_id = a.id
LEFT JOIN messages m ON c.id = m.conversation_id
GROUP BY c.id, c.user_id, c.title, c.conversation_type, c.status, c.created_at, c.updated_at, a.name;
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
CREATE TRIGGER update_assistants_updated_at BEFORE UPDATE ON assistants FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_messages_updated_at BEFORE UPDATE ON messages FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
-- ... 他のテーブルにも同様に設定
```

---

## 4. マイグレーション戦略

### 4.1. 初期セットアップ
```sql
-- 拡張機能の有効化
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- スキーマ作成
CREATE SCHEMA IF NOT EXISTS ai_secretary;
```

### 4.2. 段階的移行
1. **Phase 1:** 基本テーブル（users, assistants, conversations, messages）
2. **Phase 2:** ファイル管理、ワークフロー管理
3. **Phase 3:** 知識管理、外部連携

---

## 5. パフォーマンス最適化

### 5.1. インデックス戦略
- 複合インデックスの活用
- 部分インデックスの使用（is_active = true等）
- GINインデックス（JSONB、配列）

### 5.2. パーティショニング
- conversationsテーブル：日付ベースパーティショニング
- messagesテーブル：conversation_idベースパーティショニング

### 5.3. アーカイブ戦略
- 古い会話の自動アーカイブ
- ファイルの段階的削除
- ログローテーション

---

## 6. セキュリティ

### 6.1. データ暗号化
- 機密情報（認証情報）の暗号化
- 転送時の暗号化（TLS）

### 6.2. アクセス制御
- Row Level Security (RLS) の実装
- ユーザー別データ分離

### 6.3. 監査ログ
- 重要な操作のログ記録
- データアクセス履歴の追跡 