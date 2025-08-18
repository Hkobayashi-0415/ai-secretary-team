# データベース設計書

## 1. 概要

### 1.1 目的
AI秘書チーム・プラットフォーム（統合版）のデータベース設計書。統合版プラットフォームの新機能（AI協議管理・プラン承認システム）を含む包括的なデータベース設計を定義する。

**設計レベル**: ローカル・シングルユーザー級（エンタープライズ級・大規模システム対応は不要）
**動作環境**: ローカルPC（Windows 10/11）での単独動作
**同時接続**: 想定なし（シングルユーザー・ローカル環境）

### 1.2 対象読者
- データベース管理者
- バックエンド開発者
- システム設計者
- 運用担当者

### 1.3 技術仕様
- **データベース**: PostgreSQL 16 + Redis 7
- **ORM**: SQLAlchemy 2.0+
- **マイグレーション**: Alembic
- **接続プール**: asyncpg
- **バックアップ**: pg_dump + WAL

## 2. データベース基本設計

### 2.1 データベース構成
```
ai_secretary_platform (メインデータベース)
├── ユーザー管理スキーマ
├── AI秘書管理スキーマ
├── ワークフロー管理スキーマ
├── 会話管理スキーマ
├── Obsidian連携スキーマ
├── AI協議管理スキーマ（新機能）
└── プラン承認スキーマ（新機能）
```

### 2.2 命名規則
- **テーブル名**: スネークケース（例: `ai_assistants`）
- **カラム名**: スネークケース（例: `created_at`）
- **制約名**: `{table}_{column}_{constraint_type}`（例: `users_email_unique`）
- **インデックス名**: `idx_{table}_{columns}`（例: `idx_users_email`）

### 2.3 共通フィールド
```sql
-- 全テーブルに共通するフィールド
id BIGSERIAL PRIMARY KEY,
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
```

## 3. テーブル設計

### 3.1 ユーザー管理

#### 3.1.1 users（ユーザー）
```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP WITH TIME ZONE,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
);

-- インデックス
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_users_deleted ON users(deleted_at);
```

<!-- user_sessionsテーブルは削除済み -->
<!-- ローカル・シングルユーザー環境ではセッション管理不要 -->

### 3.2 AI秘書管理

#### 3.2.1 ai_assistants（AI秘書）
```sql
CREATE TABLE ai_assistants (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    ai_provider VARCHAR(50) NOT NULL CHECK (ai_provider IN ('openai', 'claude', 'gemini')),
    model VARCHAR(100) NOT NULL,
    api_key_encrypted TEXT NOT NULL,
    persona_id BIGINT REFERENCES personas(id),
    team_id BIGINT REFERENCES teams(id),
    is_active BOOLEAN DEFAULT true,
    settings JSONB DEFAULT '{}',
    last_used TIMESTAMP WITH TIME ZONE,
    usage_count BIGINT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
);

-- インデックス
CREATE INDEX idx_ai_assistants_provider ON ai_assistants(ai_provider);
CREATE INDEX idx_ai_assistants_persona ON ai_assistants(persona_id);
CREATE INDEX idx_ai_assistants_team ON ai_assistants(team_id);
CREATE INDEX idx_ai_assistants_active ON ai_assistants(is_active);
```

#### 3.2.2 assistant_skills（AI秘書スキル）
```sql
CREATE TABLE assistant_skills (
    id BIGSERIAL PRIMARY KEY,
    assistant_id BIGINT NOT NULL REFERENCES ai_assistants(id),
    skill_name VARCHAR(100) NOT NULL,
    skill_level INTEGER CHECK (skill_level BETWEEN 1 AND 10),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(assistant_id, skill_name)
);

-- インデックス
CREATE INDEX idx_assistant_skills_assistant ON assistant_skills(assistant_id);
CREATE INDEX idx_assistant_skills_name ON assistant_skills(skill_name);
```

### 3.3 ペルソナ・チーム管理

#### 3.3.1 personas（ペルソナ）
```sql
CREATE TABLE personas (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    personality TEXT NOT NULL,
    role_id BIGINT REFERENCES roles(id),
    is_default BOOLEAN DEFAULT false,
    
    -- アイコン・画像設定
    icon_url VARCHAR(500),
    image_url VARCHAR(500),
    icon_type VARCHAR(50) DEFAULT 'preset', -- 'preset', 'upload', 'ai_generated'
    icon_metadata JSONB DEFAULT '{}', -- アイコンの詳細設定（色、スタイル等）
    
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
);

-- インデックス
CREATE INDEX idx_personas_role ON personas(role_id);
CREATE INDEX idx_personas_default ON personas(is_default);
CREATE INDEX idx_personas_icon_type ON personas(icon_type);
```

#### 3.3.2 teams（チーム）
```sql
CREATE TABLE teams (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    team_type VARCHAR(50) DEFAULT 'general',
    max_members INTEGER DEFAULT 10,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
);

-- インデックス
CREATE INDEX idx_teams_type ON teams(team_type);
CREATE INDEX idx_teams_active ON teams(is_active);
```

#### 3.3.3 team_members（チームメンバー）
```sql
CREATE TABLE team_members (
    id BIGSERIAL PRIMARY KEY,
    team_id BIGINT NOT NULL REFERENCES teams(id),
    assistant_id BIGINT NOT NULL REFERENCES ai_assistants(id),
    role VARCHAR(50) DEFAULT 'member',
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    UNIQUE(team_id, assistant_id)
);

-- インデックス
CREATE INDEX idx_team_members_team ON team_members(team_id);
CREATE INDEX idx_team_members_assistant ON team_members(assistant_id);
```

#### 3.3.4 roles（役割）
```sql
CREATE TABLE roles (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(50),
    permissions JSONB DEFAULT '{}',
    is_system BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- インデックス
CREATE INDEX idx_roles_category ON roles(category);
CREATE INDEX idx_roles_subcategory ON roles(subcategory);
```

### 3.4 ワークフロー・タスク管理

#### 3.4.1 workflows（ワークフロー）
```sql
CREATE TABLE workflows (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    workflow_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'paused', 'completed', 'cancelled')),
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    created_by BIGINT REFERENCES users(id),
    assigned_team_id BIGINT REFERENCES teams(id),
    estimated_duration INTERVAL,
    actual_duration INTERVAL,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
);

-- インデックス
CREATE INDEX idx_workflows_status ON workflows(status);
CREATE INDEX idx_workflows_type ON workflows(workflow_type);
CREATE INDEX idx_workflows_team ON workflows(assigned_team_id);
CREATE INDEX idx_workflows_created_by ON workflows(created_by);
```

#### 3.4.2 tasks（タスク）
```sql
CREATE TABLE tasks (
    id BIGSERIAL PRIMARY KEY,
    workflow_id BIGINT REFERENCES workflows(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    task_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'assigned', 'in_progress', 'completed', 'cancelled')),
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    assigned_assistant_id BIGINT REFERENCES ai_assistants(id),
    estimated_hours DECIMAL(5,2),
    actual_hours DECIMAL(5,2),
    dependencies TEXT[], -- 依存タスクIDの配列
    due_date TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
);

-- インデックス
CREATE INDEX idx_tasks_workflow ON tasks(workflow_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_assigned ON tasks(assigned_assistant_id);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
```

#### 3.4.3 task_history（タスク履歴）
```sql
CREATE TABLE task_history (
    id BIGSERIAL PRIMARY KEY,
    task_id BIGINT NOT NULL REFERENCES tasks(id),
    action VARCHAR(50) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    changed_by BIGINT REFERENCES users(id),
    change_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- インデックス
CREATE INDEX idx_task_history_task ON task_history(task_id);
CREATE INDEX idx_task_history_action ON task_history(action);
CREATE INDEX idx_task_history_created ON task_history(created_at);
```

### 3.5 会話管理

#### 3.5.1 conversations（会話）
```sql
CREATE TABLE conversations (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(200),
    conversation_type VARCHAR(50) DEFAULT 'chat' CHECK (conversation_type IN ('chat', 'task', 'workflow')),
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted')),
    created_by BIGINT REFERENCES users(id),
    participant_assistant_ids BIGINT[], -- 参加AI秘書IDの配列
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
);

-- インデックス
CREATE INDEX idx_conversations_type ON conversations(conversation_type);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_created_by ON conversations(created_by);
CREATE INDEX idx_conversations_participants ON conversations USING GIN(participant_assistant_ids);
```

#### 3.5.2 messages（メッセージ）
```sql
CREATE TABLE messages (
    id BIGSERIAL PRIMARY KEY,
    conversation_id BIGINT NOT NULL REFERENCES conversations(id),
    sender_type VARCHAR(20) NOT NULL CHECK (sender_type IN ('user', 'assistant', 'system')),
    sender_id BIGINT, -- user_id または assistant_id
    content TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text' CHECK (message_type IN ('text', 'image', 'file', 'command')),
    metadata JSONB DEFAULT '{}',
    is_edited BOOLEAN DEFAULT false,
    edited_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- インデックス
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_sender ON messages(sender_type, sender_id);
CREATE INDEX idx_messages_created ON messages(created_at);
CREATE INDEX idx_messages_content ON messages USING GIN(to_tsvector('english', content));
```

### 3.6 Obsidian連携

#### 3.6.1 obsidian_integration_settings（Obsidian連携設定）
```sql
CREATE TABLE obsidian_integration_settings (
    id BIGSERIAL PRIMARY KEY,
    vault_path TEXT NOT NULL,
    is_enabled BOOLEAN DEFAULT true,
    auto_sync BOOLEAN DEFAULT true,
    sync_interval_minutes INTEGER DEFAULT 5,
    file_extensions TEXT[] DEFAULT ARRAY['.md', '.txt'],
    excluded_folders TEXT[] DEFAULT ARRAY[],
    template_folder TEXT DEFAULT 'templates',
    category_mappings JSONB DEFAULT '{}',
    last_sync_at TIMESTAMP WITH TIME ZONE,
    sync_status VARCHAR(50) DEFAULT 'idle',
    error_log TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- インデックス
CREATE INDEX idx_obsidian_enabled ON obsidian_integration_settings(is_enabled);
CREATE INDEX idx_obsidian_sync_status ON obsidian_integration_settings(sync_status);
```

#### 3.6.2 librarian_assistant（司書AI）
```sql
CREATE TABLE librarian_assistant (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) DEFAULT '司書AI',
    description TEXT DEFAULT 'Obsidian知識管理を専門とするAI秘書',
    ai_provider VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    api_key_encrypted TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    specialization TEXT[] DEFAULT ARRAY['知識管理', '情報検索', 'タグ付け', 'テンプレート管理'],
    search_strategies JSONB DEFAULT '{}',
    knowledge_categories JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- インデックス
CREATE INDEX idx_librarian_active ON librarian_assistant(is_active);
```

### 3.7 AI協議管理（新機能）

#### 3.7.1 ai_discussions（AI協議）
```sql
CREATE TABLE ai_discussions (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    topic VARCHAR(100) NOT NULL,
    discussion_type VARCHAR(50) NOT NULL CHECK (discussion_type IN ('collaborative', 'debate', 'brainstorming', 'problem_solving')),
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed', 'terminated')),
    max_participants INTEGER DEFAULT 5,
    current_participant_count INTEGER DEFAULT 0,
    settings JSONB DEFAULT '{}',
    consensus_reached BOOLEAN DEFAULT false,
    consensus_summary TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
);

-- インデックス
CREATE INDEX idx_ai_discussions_type ON ai_discussions(discussion_type);
CREATE INDEX idx_ai_discussions_status ON ai_discussions(status);
CREATE INDEX idx_ai_discussions_topic ON ai_discussions(topic);
CREATE INDEX idx_ai_discussions_started ON ai_discussions(started_at);
```

#### 3.7.2 discussion_participants（協議参加者）
```sql
CREATE TABLE discussion_participants (
    id BIGSERIAL PRIMARY KEY,
    discussion_id BIGINT NOT NULL REFERENCES ai_discussions(id),
    assistant_id BIGINT NOT NULL REFERENCES ai_assistants(id),
    role VARCHAR(50) DEFAULT 'participant' CHECK (role IN ('moderator', 'participant', 'observer')),
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    left_at TIMESTAMP WITH TIME ZONE,
    contribution_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    UNIQUE(discussion_id, assistant_id)
);

-- インデックス
CREATE INDEX idx_discussion_participants_discussion ON discussion_participants(discussion_id);
CREATE INDEX idx_discussion_participants_assistant ON discussion_participants(assistant_id);
CREATE INDEX idx_discussion_participants_active ON discussion_participants(is_active);
```

#### 3.7.3 discussion_messages（協議メッセージ）
```sql
CREATE TABLE discussion_messages (
    id BIGSERIAL PRIMARY KEY,
    discussion_id BIGINT NOT NULL REFERENCES ai_discussions(id),
    participant_id BIGINT NOT NULL REFERENCES discussion_participants(id),
    message_type VARCHAR(50) DEFAULT 'contribution' CHECK (message_type IN ('contribution', 'question', 'answer', 'proposal', 'agreement', 'disagreement')),
    content TEXT NOT NULL,
    reasoning TEXT,
    confidence_level INTEGER CHECK (confidence_level BETWEEN 1 AND 10),
    references TEXT[],
    is_consensus_forming BOOLEAN DEFAULT false,
    parent_message_id BIGINT REFERENCES discussion_messages(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- インデックス
CREATE INDEX idx_discussion_messages_discussion ON discussion_messages(discussion_id);
CREATE INDEX idx_discussion_messages_participant ON discussion_messages(participant_id);
CREATE INDEX idx_discussion_messages_type ON discussion_messages(message_type);
CREATE INDEX idx_discussion_messages_parent ON discussion_messages(parent_message_id);
CREATE INDEX idx_discussion_messages_consensus ON discussion_messages(is_consensus_forming);
```

#### 3.7.4 discussion_interruptions（協議割込み）
```sql
CREATE TABLE discussion_interruptions (
    id BIGSERIAL PRIMARY KEY,
    discussion_id BIGINT NOT NULL REFERENCES ai_discussions(id),
    interruption_type VARCHAR(50) NOT NULL CHECK (interruption_type IN ('pause', 'redirect', 'terminate', 'clarify')),
    message TEXT NOT NULL,
    redirect_topic VARCHAR(100),
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    initiated_by VARCHAR(20) NOT NULL CHECK (initiated_by IN ('user', 'assistant', 'system')),
    initiator_id BIGINT, -- user_id または assistant_id
    discussion_status_before VARCHAR(50),
    discussion_status_after VARCHAR(50),
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- インデックス
CREATE INDEX idx_discussion_interruptions_discussion ON discussion_interruptions(discussion_id);
CREATE INDEX idx_discussion_interruptions_type ON discussion_interruptions(interruption_type);
CREATE INDEX idx_discussion_interruptions_priority ON discussion_interruptions(priority);
CREATE INDEX idx_discussion_interruptions_initiator ON discussion_interruptions(initiated_by, initiator_id);
```

### 3.8 プラン承認システム（新機能）

#### 3.8.1 plans（プラン）
```sql
CREATE TABLE plans (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    objective TEXT NOT NULL,
    scope TEXT,
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'submitted', 'under_review', 'approved', 'rejected', 'revision_requested')),
    version INTEGER DEFAULT 1,
    assistant_id BIGINT NOT NULL REFERENCES ai_assistants(id),
    workflow_id BIGINT REFERENCES workflows(id),
    timeline JSONB NOT NULL, -- 開始日、終了日、マイルストーン
    resources JSONB NOT NULL, -- 必要なリソース、コスト、依存関係
    risk_assessment TEXT,
    success_criteria TEXT[],
    submitted_at TIMESTAMP WITH TIME ZONE,
    approved_at TIMESTAMP WITH TIME ZONE,
    rejected_at TIMESTAMP WITH TIME ZONE,
    rejection_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE DEFAULT NULL
);

-- インデックス
CREATE INDEX idx_plans_status ON plans(status);
CREATE INDEX idx_plans_assistant ON plans(assistant_id);
CREATE INDEX idx_plans_workflow ON plans(workflow_id);
CREATE INDEX idx_plans_submitted ON plans(submitted_at);
CREATE INDEX idx_plans_approved ON plans(approved_at);
```

#### 3.8.2 plan_approvals（プラン承認）
```sql
CREATE TABLE plan_approvals (
    id BIGSERIAL PRIMARY KEY,
    plan_id BIGINT NOT NULL REFERENCES plans(id),
    approver_type VARCHAR(20) NOT NULL CHECK (approver_type IN ('user', 'assistant', 'system')),
    approver_id BIGINT, -- user_id または assistant_id
    action VARCHAR(20) NOT NULL CHECK (action IN ('approve', 'reject', 'request_revision')),
    comments TEXT,
    conditions TEXT[],
    approval_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'revision_requested')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- インデックス
CREATE INDEX idx_plan_approvals_plan ON plan_approvals(plan_id);
CREATE INDEX idx_plan_approvals_approver ON plan_approvals(approver_type, approver_id);
CREATE INDEX idx_plan_approvals_action ON plan_approvals(action);
CREATE INDEX idx_plan_approvals_status ON plan_approvals(status);
```

#### 3.8.3 plan_versions（プランバージョン）
```sql
CREATE TABLE plan_versions (
    id BIGSERIAL PRIMARY KEY,
    plan_id BIGINT NOT NULL REFERENCES plans(id),
    version_number INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    objective TEXT NOT NULL,
    scope TEXT,
    timeline JSONB NOT NULL,
    resources JSONB NOT NULL,
    risk_assessment TEXT,
    success_criteria TEXT[],
    change_summary TEXT,
    created_by BIGINT REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(plan_id, version_number)
);

-- インデックス
CREATE INDEX idx_plan_versions_plan ON plan_versions(plan_id);
CREATE INDEX idx_plan_versions_version ON plan_versions(version_number);
CREATE INDEX idx_plan_versions_created_by ON plan_versions(created_by);
```

## 4. リレーションシップ設計

### 4.1 ER図（Mermaid）
```mermaid
erDiagram
    users ||--o{ ai_assistants : "creates/manages"
    users ||--o{ workflows : "creates"
    users ||--o{ conversations : "creates"
    users ||--o{ plan_approvals : "approves"
    
    teams ||--o{ ai_assistants : "contains"
    teams ||--o{ team_members : "has"
    teams ||--o{ workflows : "assigned_to"
    
    personas ||--o{ ai_assistants : "applied_to"
    roles ||--o{ personas : "defines"
    
    workflows ||--o{ tasks : "contains"
    workflows ||--o{ plans : "generates"
    
    ai_assistants ||--o{ tasks : "assigned_to"
    ai_assistants ||--o{ conversations : "participates_in"
    ai_assistants ||--o{ ai_discussions : "participates_in"
    ai_assistants ||--o{ plans : "creates"
    
    conversations ||--o{ messages : "contains"
    
    ai_discussions ||--o{ discussion_participants : "has"
    ai_discussions ||--o{ discussion_messages : "contains"
    ai_discussions ||--o{ discussion_interruptions : "interrupted_by"
    
    discussion_participants ||--o{ discussion_messages : "sends"
    
    plans ||--o{ plan_approvals : "requires"
    plans ||--o{ plan_versions : "has"
    
    discussion_messages ||--o{ discussion_messages : "replies_to"
```

### 4.2 外部キー制約
```sql
-- 主要な外部キー制約の例
ALTER TABLE ai_assistants 
ADD CONSTRAINT fk_ai_assistants_persona 
FOREIGN KEY (persona_id) REFERENCES personas(id);

ALTER TABLE team_members 
ADD CONSTRAINT fk_team_members_team 
FOREIGN KEY (team_id) REFERENCES teams(id);

ALTER TABLE tasks 
ADD CONSTRAINT fk_tasks_workflow 
FOREIGN KEY (workflow_id) REFERENCES workflows(id);

ALTER TABLE discussion_participants 
ADD CONSTRAINT fk_discussion_participants_discussion 
FOREIGN KEY (discussion_id) REFERENCES ai_discussions(id);
```

## 5. インデックス戦略

### 5.1 パフォーマンスインデックス
```sql
-- 複合インデックス（よく使用されるクエリパターン）
CREATE INDEX idx_tasks_workflow_status ON tasks(workflow_id, status);
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at);
CREATE INDEX idx_plans_assistant_status ON plans(assistant_id, status);
CREATE INDEX idx_discussions_type_status ON ai_discussions(discussion_type, status);

-- 部分インデックス（特定条件のレコードのみ）
CREATE INDEX idx_active_workflows ON workflows(id) WHERE status = 'active';
CREATE INDEX idx_active_tasks ON tasks(id) WHERE status IN ('pending', 'assigned', 'in_progress');
CREATE INDEX idx_active_discussions ON ai_discussions(id) WHERE status = 'active';

-- GINインデックス（JSONB・配列検索）
CREATE INDEX idx_plans_timeline ON plans USING GIN(timeline);
CREATE INDEX idx_plans_resources ON plans USING GIN(resources);
CREATE INDEX idx_assistant_skills_skills ON assistant_skills USING GIN(skills);
```

### 5.2 全文検索インデックス
```sql
-- メッセージ内容の全文検索
CREATE INDEX idx_messages_content_search ON messages USING GIN(to_tsvector('english', content));

-- プラン説明の全文検索
CREATE INDEX idx_plans_description_search ON plans USING GIN(to_tsvector('english', description));

-- タスク説明の全文検索
CREATE INDEX idx_tasks_description_search ON tasks USING GIN(to_tsvector('english', description));
```

## 6. データ整合性・制約

### 6.1 チェック制約
```sql
-- ステータス値の制約
ALTER TABLE workflows ADD CONSTRAINT chk_workflow_status 
CHECK (status IN ('draft', 'active', 'paused', 'completed', 'cancelled'));

ALTER TABLE tasks ADD CONSTRAINT chk_task_status 
CHECK (status IN ('pending', 'assigned', 'in_progress', 'completed', 'cancelled'));

ALTER TABLE ai_discussions ADD CONSTRAINT chk_discussion_type 
CHECK (discussion_type IN ('collaborative', 'debate', 'brainstorming', 'problem_solving'));

-- 数値範囲の制約
ALTER TABLE assistant_skills ADD CONSTRAINT chk_skill_level 
CHECK (skill_level BETWEEN 1 AND 10);

ALTER TABLE discussion_messages ADD CONSTRAINT chk_confidence_level 
CHECK (confidence_level BETWEEN 1 AND 10);
```

### 6.2 トリガー・関数
```sql
-- 更新日時の自動更新
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 各テーブルにトリガーを適用
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ai_assistants_updated_at BEFORE UPDATE ON ai_assistants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- その他のテーブルにも同様に適用
```

## 7. パフォーマンス最適化

### 7.1 パーティショニング戦略
```sql
-- メッセージテーブルの日付パーティショニング（大量データ対応）
CREATE TABLE messages_2025_08 PARTITION OF messages
FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');

CREATE TABLE messages_2025_09 PARTITION OF messages
FOR VALUES FROM ('2025-09-01') TO ('2025-10-01');

-- タスク履歴の日付パーティショニング
CREATE TABLE task_history_2025_08 PARTITION OF task_history
FOR VALUES FROM ('2025-08-01') TO ('2025-09-01');
```

### 7.2 キャッシュ戦略
```sql
-- マテリアライズドビュー（集計データの事前計算）
CREATE MATERIALIZED VIEW workflow_summary AS
SELECT 
    w.id,
    w.name,
    w.status,
    COUNT(t.id) as total_tasks,
    COUNT(CASE WHEN t.status = 'completed' THEN 1 END) as completed_tasks,
    AVG(t.actual_hours) as avg_task_hours
FROM workflows w
LEFT JOIN tasks t ON w.id = t.workflow_id
GROUP BY w.id, w.name, w.status;

-- 定期的な更新
REFRESH MATERIALIZED VIEW workflow_summary;
```

## 8. セキュリティ設計

### 8.1 行レベルセキュリティ（RLS）
```sql
-- ユーザーは自分のデータのみアクセス可能
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY users_own_data ON users
    FOR ALL USING (id = current_user_id());

-- チームメンバーのみチームデータにアクセス可能
ALTER TABLE team_members ENABLE ROW LEVEL SECURITY;

CREATE POLICY team_members_access ON team_members
    FOR ALL USING (
        team_id IN (
            SELECT team_id FROM team_members 
            WHERE assistant_id IN (
                SELECT id FROM ai_assistants 
                WHERE created_by = current_user_id()
            )
        )
    );
```

### 8.2 暗号化
```sql
-- 機密データの暗号化（API Key等）
-- 注意: 実際の実装では適切な暗号化ライブラリを使用

-- パスワードハッシュの例
-- bcrypt等の適切なハッシュ関数を使用
```

## 9. バックアップ・復旧

### 9.1 バックアップ戦略
```bash
# 日次フルバックアップ
pg_dump -h localhost -U postgres -d ai_secretary_platform > backup_$(date +%Y%m%d).sql

# WALアーカイブ（継続的バックアップ）
# postgresql.conf設定
wal_level = replica
archive_mode = on
archive_command = 'cp %p /var/lib/postgresql/archive/%f'
```

### 9.2 復旧手順
```sql
-- ポイントインタイム復旧
-- 特定の時点までデータベースを復旧
SELECT pg_create_restore_point('before_major_update');

-- 復旧実行
-- pg_restore または pg_basebackup を使用
```

## 10. 監視・メンテナンス

### 10.1 パフォーマンス監視
```sql
-- スロークエリの特定
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- テーブルサイズ監視
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 10.2 メンテナンスタスク
```sql
-- 統計情報の更新
ANALYZE;

-- テーブルの最適化
VACUUM ANALYZE;

-- インデックスの再構築
REINDEX TABLE messages;
```

## 11. 移行計画

### 11.1 既存データベースからの移行
```sql
-- 統合版プラットフォームからの移行
-- PostgreSQL 16 最適化スクリプト

-- 1. スキーマ作成
-- 2. データ変換・移行
-- 3. インデックス作成
-- 4. 制約適用
-- 5. データ検証
```

### 11.2 段階的移行
```sql
-- Phase 1: 基本テーブル作成
-- Phase 2: 既存データ移行
-- Phase 3: 新機能テーブル追加
-- Phase 4: インデックス・制約最適化
-- Phase 5: パフォーマンステスト
```

## 12. 今後の拡張予定

### 12.1 短期（3ヶ月以内）
- ファイル管理テーブルの追加
- 通知システムの実装
- 監査ログの強化

### 12.2 中期（6ヶ月以内）
- シングルユーザー対応（ローカル環境）
- データアーカイブ機能
- 分散データベース対応

### 12.3 長期（1年以内）
- 時系列データベース統合
- リアルタイム分析機能
- AI予測モデルの統合

---

**作成日**: 2025-08-13  
**作成者**: AI Assistant  
**バージョン**: 1.0  
**次回更新予定**: 2025-08-20 

## 13. Redis 7設計

### 13.1 Redis基本構成

#### 13.1.1 Redis設定
```yaml
# docker-compose.yml Redis設定
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data
    - ./redis/redis.conf:/usr/local/etc/redis/redis.conf
  command: redis-server /usr/local/etc/redis/redis.conf
  environment:
    - REDIS_PASSWORD=your_secure_password
  networks:
    - ai_secretary_network

volumes:
  redis_data:
    driver: local
```

```conf
# redis.conf 主要設定
# 永続化設定
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec

# メモリ管理
maxmemory 512mb
maxmemory-policy allkeys-lru

# セキュリティ
requirepass your_secure_password

# パフォーマンス
tcp-keepalive 300
timeout 0
```

#### 13.1.2 Redis接続設定
```python
# config/redis_config.py
import redis.asyncio as redis
from typing import Optional

class RedisConfig:
    HOST: str = "localhost"
    PORT: int = 6379
    PASSWORD: Optional[str] = "your_secure_password"
    DB: int = 0
    MAX_CONNECTIONS: int = 20
    SOCKET_TIMEOUT: int = 5
    SOCKET_CONNECT_TIMEOUT: int = 5
    
    @classmethod
    def get_connection_pool(cls) -> redis.ConnectionPool:
        return redis.ConnectionPool(
            host=cls.HOST,
            port=cls.PORT,
            password=cls.PASSWORD,
            db=cls.DB,
            max_connections=cls.MAX_CONNECTIONS,
            socket_timeout=cls.SOCKET_TIMEOUT,
            socket_connect_timeout=cls.SOCKET_CONNECT_TIMEOUT,
            decode_responses=True
        )
```

<!-- セッション管理設計は削除済み -->
<!-- ローカル・シングルユーザー環境ではセッション管理不要 -->
```python
# Redis キー設計: キャッシュ専用（簡素化）
# セッション管理は削除（ローカル環境では不要）
# 形式: cache:{entity_type}:{entity_id}

# セッションデータ構造
session_data = {
    "user_id": "123",
    "username": "john_doe",
    "role": "admin",
    "permissions": ["read", "write", "admin"],
    "last_activity": "2025-08-13T10:00:00Z",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "preferences": {
        "theme": "dark",
        "language": "ja",
        "notifications": True
    }
}

# Redis操作例
# セッション作成
await redis.hset(f"session:{user_id}:{session_id}", mapping=session_data)
await redis.expire(f"session:{user_id}:{session_id}", 86400)

# セッション取得
session = await redis.hgetall(f"session:{user_id}:{session_id}")

# セッション更新
await redis.hset(f"session:{user_id}:{session_id}", "last_activity", current_time)
await redis.expire(f"session:{user_id}:{session_id}", 86400)

# セッション削除
await redis.delete(f"session:{user_id}:{session_id}")
```

#### 13.2.2 AI秘書セッション管理
```python
# Redis キー設計: AI秘書セッション
# 形式: ai_session:{assistant_id}:{session_id}
# TTL: 1時間（3600秒）

# AI秘書セッションデータ構造
ai_session_data = {
    "assistant_id": "456",
    "persona_id": "789",
    "team_id": "101",
    "current_context": "workflow_execution",
    "memory_context": {
        "recent_conversations": ["conv_1", "conv_2"],
        "current_task": "task_123",
        "workflow_state": "in_progress"
    },
    "ai_state": {
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 2000,
        "conversation_history": ["msg_1", "msg_2"]
    },
    "last_activity": "2025-08-13T10:00:00Z",
    "session_duration": 1800  # 30分
}

# Redis操作例
# AIセッション作成
await redis.hset(f"ai_session:{assistant_id}:{session_id}", mapping=ai_session_data)
await redis.expire(f"ai_session:{assistant_id}:{session_id}", 3600)

# AIセッション状態更新
await redis.hset(f"ai_session:{assistant_id}:{session_id}", "ai_state", updated_ai_state)
await redis.expire(f"ai_session:{assistant_id}:{session_id}", 3600)
```

#### 13.2.3 セッション検索・管理
```python
# セッション検索・管理機能
class SessionManager:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def get_active_sessions(self, user_id: str) -> List[Dict]:
        """ユーザーのアクティブセッション取得"""
        pattern = f"session:{user_id}:*"
        keys = await self.redis.keys(pattern)
        sessions = []
        
        for key in keys:
            session_data = await self.redis.hgetall(key)
            if session_data:
                sessions.append(session_data)
        
        return sessions
    
    async def get_ai_sessions_by_team(self, team_id: str) -> List[Dict]:
        """チームのAIセッション取得"""
        pattern = f"ai_session:*"
        keys = await self.redis.keys(pattern)
        team_sessions = []
        
        for key in keys:
            session_data = await self.redis.hgetall(key)
            if session_data.get("team_id") == team_id:
                team_sessions.append(session_data)
        
        return team_sessions
    
    async def cleanup_expired_sessions(self):
        """期限切れセッションのクリーンアップ"""
        # Redisの自動TTL機能により自動削除される
        # 定期的な監視ログ出力
        pass
```

### 13.3 キャッシュ戦略設計

#### 13.3.1 データキャッシュ
```python
# Redis キー設計: データキャッシュ
# 形式: cache:{data_type}:{identifier}
# TTL: データタイプ別に設定

# キャッシュ設定
CACHE_TTL = {
    "user_profile": 3600,      # 1時間
    "team_info": 1800,         # 30分
    "workflow_status": 300,    # 5分
    "ai_assistant": 7200,      # 2時間
    "search_results": 1800,    # 30分
    "statistics": 3600,        # 1時間
    "configuration": 86400     # 24時間
}

# キャッシュデータ構造例
cache_data = {
    "user_profile": {
        "user_id": "123",
        "username": "john_doe",
        "full_name": "John Doe",
        "role": "admin",
        "preferences": {...},
        "last_updated": "2025-08-13T10:00:00Z"
    },
    "team_info": {
        "team_id": "101",
        "name": "開発チーム",
        "members": [...],
        "workflows": [...],
        "last_updated": "2025-08-13T10:00:00Z"
    }
}

# Redis操作例
# キャッシュ設定
await redis.hset(f"cache:user_profile:{user_id}", mapping=cache_data["user_profile"])
await redis.expire(f"cache:user_profile:{user_id}", CACHE_TTL["user_profile"])

# キャッシュ取得
cached_data = await redis.hgetall(f"cache:user_profile:{user_id}")

# キャッシュ削除
await redis.delete(f"cache:user_profile:{user_id}")
```

#### 13.3.2 検索結果キャッシュ
```python
# Redis キー設計: 検索結果キャッシュ
# 形式: search:{query_hash}:{filters_hash}
# TTL: 30分（1800秒）

# 検索クエリハッシュ生成
import hashlib
import json

def generate_query_hash(query: str, filters: Dict) -> str:
    """検索クエリとフィルターのハッシュ生成"""
    query_data = {
        "query": query,
        "filters": filters,
        "timestamp": int(time.time() // 300)  # 5分単位でグループ化
    }
    return hashlib.md5(json.dumps(query_data, sort_keys=True).encode()).hexdigest()

# 検索結果キャッシュ例
search_cache_data = {
    "query": "AI秘書 ワークフロー",
    "filters": {"status": "active", "team_id": "101"},
    "results": [...],
    "total_count": 25,
    "cached_at": "2025-08-13T10:00:00Z",
    "expires_at": "2025-08-13T10:30:00Z"
}

# Redis操作例
# 検索結果キャッシュ
query_hash = generate_query_hash(query, filters)
await redis.hset(f"search:{query_hash}", mapping=search_cache_data)
await redis.expire(f"search:{query_hash}", 1800)

# 検索結果取得
cached_results = await redis.hgetall(f"search:{query_hash}")
```

#### 13.3.3 キャッシュ管理・無効化
```python
# キャッシュ管理・無効化機能
class CacheManager:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def invalidate_user_cache(self, user_id: str):
        """ユーザー関連キャッシュの無効化"""
        patterns = [
            f"cache:user_profile:{user_id}",
            f"cache:user_preferences:{user_id}",
            f"cache:user_sessions:{user_id}"
        ]
        
        for pattern in patterns:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
    
    async def invalidate_team_cache(self, team_id: str):
        """チーム関連キャッシュの無効化"""
        patterns = [
            f"cache:team_info:{team_id}",
            f"cache:team_members:{team_id}",
            f"cache:team_workflows:{team_id}"
        ]
        
        for pattern in patterns:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
    
    async def invalidate_workflow_cache(self, workflow_id: str):
        """ワークフロー関連キャッシュの無効化"""
        patterns = [
            f"cache:workflow_status:{workflow_id}",
            f"cache:workflow_tasks:{workflow_id}"
        ]
        
        for pattern in patterns:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
    
    async def get_cache_stats(self) -> Dict:
        """キャッシュ統計情報取得"""
        cache_keys = await self.redis.keys("cache:*")
        session_keys = await self.redis.keys("session:*")
        ai_session_keys = await self.redis.keys("ai_session:*")
        
        return {
            "cache_count": len(cache_keys),
            "session_count": len(session_keys),
            "ai_session_count": len(ai_session_keys),
            "total_memory": await self.redis.info("memory")
        }
```

### 13.4 リアルタイム通信・状態管理

#### 13.4.1 WebSocket接続管理
```python
# Redis キー設計: WebSocket接続管理
# 形式: ws_connection:{user_id}:{connection_id}
# TTL: 接続中は永続、切断時削除

# WebSocket接続データ構造
ws_connection_data = {
    "user_id": "123",
    "connection_id": "ws_456",
    "connected_at": "2025-08-13T10:00:00Z",
    "last_heartbeat": "2025-08-13T10:00:00Z",
    "subscriptions": ["notifications", "workflow_updates", "ai_discussions"],
    "client_info": {
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0...",
        "platform": "web"
    }
}

# Redis操作例
# WebSocket接続登録
await redis.hset(f"ws_connection:{user_id}:{connection_id}", mapping=ws_connection_data)

# WebSocket接続取得
connection_data = await redis.hgetall(f"ws_connection:{user_id}:{connection_id}")

# WebSocket接続削除
await redis.delete(f"ws_connection:{user_id}:{connection_id}")
```

#### 13.4.2 リアルタイム通知管理
```python
# Redis キー設計: リアルタイム通知
# 形式: notification:{user_id}:{notification_id}
# TTL: 7日（604800秒）

# 通知データ構造
notification_data = {
    "notification_id": "notif_789",
    "type": "workflow_update",
    "title": "ワークフロー完了",
    "message": "プロジェクトAのワークフローが完了しました",
    "priority": "medium",
    "read": False,
    "action_url": "/workflows/123",
    "created_at": "2025-08-13T10:00:00Z",
    "expires_at": "2025-08-20T10:00:00Z"
}

# Redis操作例
# 通知作成
await redis.hset(f"notification:{user_id}:{notification_id}", mapping=notification_data)
await redis.expire(f"notification:{user_id}:{notification_id}", 604800)

# 通知取得
notifications = await self.redis.keys(f"notification:{user_id}:*")
notification_list = []
for key in notifications:
    data = await self.redis.hgetall(key)
    if data:
        notification_list.append(data)

# 通知既読
await redis.hset(f"notification:{user_id}:{notification_id}", "read", True)
```

#### 13.4.3 AI協議リアルタイム状態管理
```python
# Redis キー設計: AI協議リアルタイム状態
# 形式: ai_discussion_state:{discussion_id}
# TTL: 協議中は永続、終了時削除

# AI協議状態データ構造
ai_discussion_state = {
    "discussion_id": "disc_101",
    "status": "active",
    "current_topic": "プロジェクト計画の最適化",
    "participants": [
        {"assistant_id": "456", "role": "moderator", "status": "active"},
        {"assistant_id": "789", "role": "participant", "status": "thinking"},
        {"assistant_id": "101", "role": "participant", "status": "speaking"}
    ],
    "current_speaker": "789",
    "discussion_flow": [
        {"step": 1, "action": "topic_introduction", "assistant_id": "456"},
        {"step": 2, "action": "brainstorming", "assistant_id": "789"},
        {"step": 3, "action": "analysis", "assistant_id": "101"}
    ],
    "consensus_progress": 0.6,
    "last_activity": "2025-08-13T10:00:00Z",
    "estimated_completion": "2025-08-13T11:00:00Z"
}

# Redis操作例
# AI協議状態更新
await redis.hset(f"ai_discussion_state:{discussion_id}", mapping=ai_discussion_state)

# AI協議状態取得
discussion_state = await redis.hgetall(f"ai_discussion_state:{discussion_id}")

# AI協議状態削除
await redis.delete(f"ai_discussion_state:{discussion_id}")
```

### 13.5 パフォーマンス最適化

#### 13.5.1 Redis パフォーマンス設定
```conf
# redis.conf パフォーマンス最適化設定
# メモリ管理
maxmemory 1gb
maxmemory-policy allkeys-lru
maxmemory-samples 10

# 永続化最適化
appendonly yes
appendfsync everysec
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# ネットワーク最適化
tcp-keepalive 300
timeout 0
tcp-backlog 511

# クライアント接続最適化
maxclients 10000
client-output-buffer-limit normal 0 0 0
client-output-buffer-limit slave 256mb 64mb 60
client-output-buffer-limit pubsub 32mb 8mb 60
```

#### 13.5.2 Redis クラスタリング（将来拡張）
```yaml
# docker-compose.cluster.yml Redis クラスター設定
version: '3.8'
services:
  redis-node-1:
    image: redis:7-alpine
    ports:
      - "7001:6379"
    command: redis-server --port 6379 --cluster-enabled yes --cluster-config-file nodes.conf --cluster-node-timeout 5000
    volumes:
      - redis_node_1:/data

  redis-node-2:
    image: redis:7-alpine
    ports:
      - "7002:6379"
    command: redis-server --port 6379 --cluster-enabled yes --cluster-config-file nodes.conf --cluster-node-timeout 5000
    volumes:
      - redis_node_2:/data

  redis-node-3:
    image: redis:7-alpine
    ports:
      - "7003:6379"
    command: redis-server --port 6379 --cluster-enabled yes --cluster-config-file nodes.conf --cluster-node-timeout 5000
    volumes:
      - redis_node_3:/data

volumes:
  redis_node_1:
  redis_node_2:
  redis_node_3:
```

#### 13.5.3 Redis 監視・メトリクス
```python
# Redis 監視・メトリクス収集
class RedisMonitor:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def get_performance_metrics(self) -> Dict:
        """Redis パフォーマンスメトリクス取得"""
        info = await self.redis.info()
        
        return {
            "memory_usage": info.get("used_memory_human"),
            "connected_clients": info.get("connected_clients"),
            "total_commands_processed": info.get("total_commands_processed"),
            "keyspace_hits": info.get("keyspace_hits"),
            "keyspace_misses": info.get("keyspace_misses"),
            "hit_rate": self._calculate_hit_rate(info),
            "slow_log": await self.redis.slowlog_get(10)
        }
    
    def _calculate_hit_rate(self, info: Dict) -> float:
        """キャッシュヒット率計算"""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        
        if total == 0:
            return 0.0
        
        return (hits / total) * 100
    
    async def get_memory_usage_by_pattern(self, pattern: str) -> Dict:
        """パターン別メモリ使用量取得"""
        keys = await self.redis.keys(pattern)
        total_memory = 0
        
        for key in keys:
            memory = await self.redis.memory_usage(key)
            if memory:
                total_memory += memory
        
        return {
            "pattern": pattern,
            "key_count": len(keys),
            "total_memory_bytes": total_memory,
            "total_memory_human": self._format_bytes(total_memory)
        }
    
    def _format_bytes(self, bytes_value: int) -> str:
        """バイト値を人間が読みやすい形式に変換"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} TB"
```

### 13.6 Redis セキュリティ・バックアップ

#### 13.6.1 Redis セキュリティ設定
```conf
# redis.conf セキュリティ設定
# 認証
requirepass your_very_secure_password

# ネットワークセキュリティ
bind 127.0.0.1
protected-mode yes
port 6379

# コマンド制限
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command DEBUG ""
rename-command CONFIG ""

# 接続制限
maxclients 100
timeout 300
tcp-keepalive 300
```

#### 13.6.2 Redis バックアップ・復旧
```bash
#!/bin/bash
# redis_backup.sh Redis バックアップスクリプト

# 設定
REDIS_HOST="localhost"
REDIS_PORT="6379"
REDIS_PASSWORD="your_secure_password"
BACKUP_DIR="/backup/redis"
DATE=$(date +%Y%m%d_%H%M%S)

# バックアップディレクトリ作成
mkdir -p $BACKUP_DIR

# RDB バックアップ
redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD BGSAVE

# AOF バックアップ
redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD BGREWRITEAOF

# バックアップファイルコピー
cp /var/lib/redis/dump.rdb $BACKUP_DIR/dump_$DATE.rdb
cp /var/lib/redis/appendonly.aof $BACKUP_DIR/appendonly_$DATE.aof

# 古いバックアップファイル削除（30日以上古いもの）
find $BACKUP_DIR -name "*.rdb" -mtime +30 -delete
find $BACKUP_DIR -name "*.aof" -mtime +30 -delete

echo "Redis backup completed: $DATE"
```

---

**作成日**: 2025-08-13  
**作成者**: AI Assistant  
**バージョン**: 1.0  
**次回更新予定**: 2025-08-20 

## 14. マイグレーション設計（Alembic）

### 14.1 Alembic基本構成

#### 14.1.1 Alembic設定ファイル
```python
# alembic.ini 主要設定
[alembic]
script_location = alembic
sqlalchemy.url = postgresql+asyncpg://username:password@localhost/ai_secretary_platform

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

#### 14.1.2 Alembic環境設定
```python
# alembic/env.py
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from app.core.config import settings
from app.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def get_url():
    return settings.DATABASE_URL

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

def run_async_migrations():
    """非同期マイグレーション実行"""
    asyncio.run(run_migrations_online())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_async_migrations()
```

### 14.2 マイグレーション戦略

#### 14.2.1 段階的マイグレーション計画
```python
# マイグレーション戦略: 段階的アプローチ
MIGRATION_PHASES = {
    "phase_1": {
        "name": "基本テーブル作成",
        "description": "ユーザー管理・AI秘書管理・ペルソナ管理の基本テーブル",
        "migrations": [
            "001_create_users_table",
            "002_create_personas_table",
            "003_create_roles_table",
            "004_create_teams_table",
            "005_create_ai_assistants_table"
        ],
        "estimated_duration": "1日",
        "rollback_strategy": "テーブル削除・データ復旧"
    },
    "phase_2": {
        "name": "ワークフロー管理テーブル",
        "description": "ワークフロー・タスク・履歴管理テーブル",
        "migrations": [
            "006_create_workflows_table",
            "007_create_tasks_table",
            "008_create_task_history_table"
        ],
        "estimated_duration": "1日",
        "rollback_strategy": "テーブル削除・データ復旧"
    },
    "phase_3": {
        "name": "会話管理テーブル",
        "description": "会話・メッセージ管理テーブル",
        "migrations": [
            "009_create_conversations_table",
            "010_create_messages_table"
        ],
        "estimated_duration": "0.5日",
        "rollback_strategy": "テーブル削除・データ復旧"
    },
    "phase_4": {
        "name": "Obsidian連携テーブル",
        "description": "Obsidian連携・司書AI管理テーブル",
        "migrations": [
            "011_create_obsidian_integration_settings_table",
            "012_create_librarian_assistant_table"
        ],
        "estimated_duration": "0.5日",
        "rollback_strategy": "テーブル削除・データ復旧"
    },
    "phase_5": {
        "name": "AI協議管理テーブル",
        "description": "AI協議・参加者・メッセージ・割込み管理テーブル",
        "migrations": [
            "013_create_ai_discussions_table",
            "014_create_discussion_participants_table",
            "015_create_discussion_messages_table",
            "016_create_discussion_interruptions_table"
        ],
        "estimated_duration": "1日",
        "rollback_strategy": "テーブル削除・データ復旧"
    },
    "phase_6": {
        "name": "プラン承認システムテーブル",
        "description": "プラン・承認・バージョン管理テーブル",
        "migrations": [
            "017_create_plans_table",
            "018_create_plan_approvals_table",
            "019_create_plan_versions_table"
        ],
        "estimated_duration": "1日",
        "rollback_strategy": "テーブル削除・データ復旧"
    },
    "phase_7": {
        "name": "インデックス・制約最適化",
        "description": "パフォーマンスインデックス・制約・トリガーの最適化",
        "migrations": [
            "020_create_performance_indexes",
            "021_create_constraints_triggers",
            "022_create_materialized_views"
        ],
        "estimated_duration": "1日",
        "rollback_strategy": "インデックス・制約削除"
    }
}
```

#### 14.2.2 マイグレーション実行順序
```python
# マイグレーション実行順序管理
class MigrationManager:
    def __init__(self, alembic_config):
        self.config = alembic_config
        self.phases = MIGRATION_PHASES
    
    async def execute_phase(self, phase_name: str) -> bool:
        """指定されたフェーズのマイグレーション実行"""
        if phase_name not in self.phases:
            raise ValueError(f"Unknown phase: {phase_name}")
        
        phase = self.phases[phase_name]
        print(f"Starting phase: {phase['name']}")
        print(f"Description: {phase['description']}")
        print(f"Estimated duration: {phase['estimated_duration']}")
        
        try:
            for migration in phase['migrations']:
                await self._execute_migration(migration)
            
            print(f"Phase {phase_name} completed successfully")
            return True
            
        except Exception as e:
            print(f"Phase {phase_name} failed: {str(e)}")
            await self._rollback_phase(phase_name)
            return False
    
    async def _execute_migration(self, migration_name: str):
        """個別マイグレーション実行"""
        print(f"Executing migration: {migration_name}")
        # alembic upgrade コマンド実行
        # 実際の実装では subprocess または alembic API を使用
    
    async def _rollback_phase(self, phase_name: str):
        """フェーズのロールバック"""
        phase = self.phases[phase_name]
        print(f"Rolling back phase: {phase_name}")
        print(f"Rollback strategy: {phase['rollback_strategy']}")
        # ロールバック処理の実装
```

### 14.3 初期データ設計

#### 14.3.1 システム初期データ
```python
# alembic/versions/023_insert_initial_data.py
"""Insert initial system data

Revision ID: 023
Revises: 022
Create Date: 2025-08-13 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '023'
down_revision = '022'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # システムロールの初期データ
    op.execute("""
        INSERT INTO roles (name, description, category, subcategory, permissions, is_system) VALUES
        ('admin', 'システム管理者', 'system', 'administration', '{"all": true}', true),
        ('user', '一般ユーザー', 'user', 'basic', '{"read": true, "write": true}', true),
        ('ai_assistant', 'AI秘書', 'ai', 'assistant', '{"read": true, "write": true, "ai_operations": true}', true),
        ('team_leader', 'チームリーダー', 'team', 'leadership', '{"read": true, "write": true, "team_management": true}', true),
        ('workflow_manager', 'ワークフロー管理者', 'workflow', 'management', '{"read": true, "write": true, "workflow_management": true}', true)
    """)
    
    # デフォルトペルソナの初期データ
    op.execute("""
        INSERT INTO personas (name, description, personality, role_id, is_default, icon_type, icon_metadata, metadata) VALUES
        ('プロジェクトマネージャー', 'プロジェクト管理を専門とするAI秘書', '論理的で効率的、チームワークを重視し、明確なコミュニケーションを心がける', 
         (SELECT id FROM roles WHERE name = 'team_leader'), true, 'preset',
         '{"icon_name": "project_manager", "color": "#3B82F6", "style": "professional"}',
         '{"specialization": ["プロジェクト管理", "チーム調整", "進捗管理"], "communication_style": "professional"}'),
        
        ('技術アーキテクト', '技術設計・アーキテクチャを専門とするAI秘書', '創造的で革新的、技術的詳細に精通し、最適解を見つけることに情熱を持つ', 
         (SELECT id FROM roles WHERE name = 'ai_assistant'), true, 'preset',
         '{"icon_name": "tech_architect", "color": "#10B981", "style": "technical"}',
         '{"specialization": ["システム設計", "技術選定", "パフォーマンス最適化"], "communication_style": "technical"}'),
        
        ('クリエイティブディレクター', 'デザイン・創造性を専門とするAI秘書', '芸術的で直感的、美しさと機能性のバランスを取り、革新的なアイデアを生み出す', 
         (SELECT id FROM roles WHERE name = 'ai_assistant'), true, 'preset',
         '{"icon_name": "creative_director", "color": "#8B5CF6", "style": "creative"}',
         '{"specialization": ["デザイン思考", "ブランディング", "ユーザー体験"], "communication_style": "creative"}'),
        
        ('データアナリスト', 'データ分析・洞察を専門とするAI秘書', '分析的で正確、データに基づく意思決定を支援し、パターンとトレンドを見つける', 
         (SELECT id FROM roles WHERE name = 'ai_assistant'), true, 'preset',
         '{"icon_name": "data_analyst", "color": "#F59E0B", "style": "analytical"}',
         '{"specialization": ["データ分析", "統計", "ビジネスインテリジェンス"], "communication_style": "analytical"}'),
        
        ('司書AI', '知識管理・情報検索を専門とするAI秘書', '体系的で整理好き、情報の分類・検索・管理に長け、知識の共有を促進する', 
         (SELECT id FROM roles WHERE name = 'ai_assistant'), true, 'preset',
         '{"icon_name": "librarian", "color": "#EF4444", "style": "organized"}',
         '{"specialization": ["知識管理", "情報検索", "タグ付け", "テンプレート管理"], "communication_style": "organized"}')
    """)
    
    # デフォルトチームの初期データ
    op.execute("""
        INSERT INTO teams (name, description, team_type, max_members) VALUES
        ('開発チーム', 'ソフトウェア開発を担当するチーム', 'development', 10),
        ('デザインチーム', 'UI/UXデザインを担当するチーム', 'design', 8),
        ('プロジェクト管理チーム', 'プロジェクト管理を担当するチーム', 'management', 5),
        ('データ分析チーム', 'データ分析・洞察を担当するチーム', 'analytics', 6),
        ('知識管理チーム', '知識管理・情報整理を担当するチーム', 'knowledge', 4)
    """)

def downgrade() -> None:
    # 初期データの削除
    op.execute("DELETE FROM personas WHERE is_default = true")
    op.execute("DELETE FROM teams WHERE team_type IN ('development', 'design', 'management', 'analytics', 'knowledge')")
    op.execute("DELETE FROM roles WHERE is_system = true")
```

#### 14.3.2 テストデータ設計
```python
# alembic/versions/024_insert_test_data.py
"""Insert test data for development

Revision ID: 024
Revises: 023
Create Date: 2025-08-13 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '024'
down_revision = '023'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # テストユーザーの作成
    op.execute("""
        INSERT INTO users (username, email, password_hash, full_name, role, is_active) VALUES
        ('test_admin', 'admin@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.sm6.', 'Test Admin', 'admin', true),
        ('test_user', 'user@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.sm6.', 'Test User', 'user', true),
        ('test_leader', 'leader@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.sm6.', 'Test Leader', 'team_leader', true)
    """)
    
    # テストAI秘書の作成
    op.execute("""
        INSERT INTO ai_assistants (name, description, ai_provider, model, api_key_encrypted, persona_id, team_id, is_active) VALUES
        ('プロジェクトマネージャーAI', 'プロジェクト管理を専門とするAI秘書', 'openai', 'gpt-4', 'encrypted_key_1', 
         (SELECT id FROM personas WHERE name = 'プロジェクトマネージャー'), 
         (SELECT id FROM teams WHERE name = 'プロジェクト管理チーム'), true),
        
        ('技術アーキテクトAI', '技術設計・アーキテクチャを専門とするAI秘書', 'openai', 'gpt-4', 'encrypted_key_2', 
         (SELECT id FROM personas WHERE name = '技術アーキテクト'), 
         (SELECT id FROM teams WHERE name = '開発チーム'), true),
        
        ('デザイナーAI', 'UI/UXデザインを専門とするAI秘書', 'openai', 'gpt-4', 'encrypted_key_3', 
         (SELECT id FROM personas WHERE name = 'クリエイティブディレクター'), 
         (SELECT id FROM teams WHERE name = 'デザインチーム'), true)
    """)
    
    # テストワークフローの作成
    op.execute("""
        INSERT INTO workflows (name, description, workflow_type, status, priority, created_by, assigned_team_id) VALUES
        ('テストプロジェクトA', '開発チームのテストプロジェクト', 'development', 'active', 'high', 
         (SELECT id FROM users WHERE username = 'test_admin'), 
         (SELECT id FROM teams WHERE name = '開発チーム')),
        
        ('UI/UX改善プロジェクト', 'デザインチームのUI/UX改善プロジェクト', 'design', 'active', 'medium', 
         (SELECT id FROM users WHERE username = 'test_leader'), 
         (SELECT id FROM teams WHERE name = 'デザインチーム'))
    """)
    
    # テストタスクの作成
    op.execute("""
        INSERT INTO tasks (workflow_id, name, description, task_type, status, priority, assigned_assistant_id) VALUES
        ((SELECT id FROM workflows WHERE name = 'テストプロジェクトA'), 'データベース設計', 'PostgreSQL 16を使用したデータベース設計', 'design', 'in_progress', 'high',
         (SELECT id FROM ai_assistants WHERE name = '技術アーキテクトAI')),
        
        ((SELECT id FROM workflows WHERE name = 'テストプロジェクトA'), 'API設計', 'RESTful APIの設計・実装', 'development', 'pending', 'medium',
         (SELECT id FROM ai_assistants WHERE name = '技術アーキテクトAI')),
        
        ((SELECT id FROM workflows WHERE name = 'UI/UX改善プロジェクト'), 'デザインシステム設計', '統一的なデザインシステムの設計', 'design', 'in_progress', 'high',
         (SELECT id FROM ai_assistants WHERE name = 'デザイナーAI'))
    """)

def downgrade() -> None:
    # テストデータの削除
    op.execute("DELETE FROM tasks WHERE workflow_id IN (SELECT id FROM workflows WHERE name LIKE 'テスト%')")
    op.execute("DELETE FROM workflows WHERE name LIKE 'テスト%'")
    op.execute("DELETE FROM ai_assistants WHERE name LIKE '%AI'")
    op.execute("DELETE FROM users WHERE username LIKE 'test_%'")
```

### 14.4 データベースバージョン管理

#### 14.4.1 バージョン管理戦略
```python
# データベースバージョン管理戦略
class DatabaseVersionManager:
    def __init__(self, alembic_config):
        self.config = alembic_config
    
    async def get_current_version(self) -> str:
        """現在のデータベースバージョン取得"""
        # alembic current コマンドの実行結果を取得
        pass
    
    async def get_version_history(self) -> List[Dict]:
        """バージョン履歴取得"""
        # alembic history コマンドの実行結果を取得
        pass
    
    async def check_version_compatibility(self, target_version: str) -> bool:
        """バージョン互換性チェック"""
        current_version = await self.get_current_version()
        # バージョン互換性ロジック
        pass
    
    async def create_version_snapshot(self, version: str, description: str) -> str:
        """バージョンスナップショット作成"""
        # データベースのスナップショット作成
        pass
    
    async def restore_version_snapshot(self, snapshot_id: str) -> bool:
        """バージョンスナップショット復元"""
        # スナップショットからの復元
        pass
```

#### 14.4.2 ロールバック戦略
```python
# ロールバック戦略
class RollbackStrategy:
    def __init__(self, alembic_config):
        self.config = alembic_config
    
    async def rollback_to_version(self, target_version: str) -> bool:
        """指定バージョンへのロールバック"""
        try:
            # alembic downgrade コマンド実行
            print(f"Rolling back to version: {target_version}")
            return True
        except Exception as e:
            print(f"Rollback failed: {str(e)}")
            return False
    
    async def rollback_phase(self, phase_name: str) -> bool:
        """フェーズ単位でのロールバック"""
        phase = MIGRATION_PHASES.get(phase_name)
        if not phase:
            return False
        
        # フェーズ内のマイグレーションを逆順でロールバック
        migrations = phase['migrations'][::-1]
        for migration in migrations:
            await self._rollback_migration(migration)
        
        return True
    
    async def _rollback_migration(self, migration_name: str):
        """個別マイグレーションのロールバック"""
        print(f"Rolling back migration: {migration_name}")
        # alembic downgrade コマンド実行
```

### 14.5 マイグレーション自動化

#### 14.5.1 CI/CD統合
```yaml
# .github/workflows/database-migration.yml
name: Database Migration

on:
  push:
    branches: [ main, develop ]
    paths: [ 'alembic/**', 'app/models/**' ]
  pull_request:
    branches: [ main, develop ]
    paths: [ 'alembic/**', 'app/models/**' ]

jobs:
  test-migration:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install alembic psycopg2-binary redis
    
    - name: Run database migrations
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379
      run: |
        alembic upgrade head
    
    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379
      run: |
        pytest tests/ -v
    
    - name: Rollback test
      if: always()
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379
      run: |
        alembic downgrade base
```

#### 14.5.2 マイグレーション監視
```python
# マイグレーション監視システム
class MigrationMonitor:
    def __init__(self, alembic_config):
        self.config = alembic_config
    
    async def monitor_migration_status(self) -> Dict:
        """マイグレーション状況の監視"""
        current_version = await self.get_current_version()
        target_version = await self.get_target_version()
        
        return {
            "current_version": current_version,
            "target_version": target_version,
            "is_up_to_date": current_version == target_version,
            "pending_migrations": await self.get_pending_migrations(),
            "last_migration_time": await self.get_last_migration_time(),
            "migration_health": await self.check_migration_health()
        }
    
    async def get_pending_migrations(self) -> List[str]:
        """保留中のマイグレーション取得"""
        # alembic heads と current の差分を取得
        pass
    
    async def get_last_migration_time(self) -> str:
        """最後のマイグレーション実行時刻取得"""
        # マイグレーション履歴から最新時刻を取得
        pass
    
    async def check_migration_health(self) -> str:
        """マイグレーション健全性チェック"""
        # データベーススキーマの整合性チェック
        pass
```

---

**作成日**: 2025-08-13  
**作成者**: AI Assistant  
**バージョン**: 1.0  
**次回更新予定**: 2025-08-20 

## 15. SQLAlchemy 2.0モデル設計

### 15.1 基本モデル構成

#### 15.1.1 ベースモデル定義
```python
# app/models/base.py
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    """SQLAlchemy 2.0 ベースクラス"""
    pass

class TimestampMixin:
    """タイムスタンプ管理ミキシン"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )

class SoftDeleteMixin:
    """論理削除管理ミキシン"""
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True, 
        default=None
    )

class BaseModel(Base, TimestampMixin, SoftDeleteMixin):
    """基本モデルクラス"""
    __abstract__ = True
    
    def soft_delete(self):
        """論理削除実行"""
        self.deleted_at = datetime.utcnow()
    
    def restore(self):
        """論理削除復元"""
        self.deleted_at = None
    
    @property
    def is_deleted(self) -> bool:
        """論理削除状態確認"""
        return self.deleted_at is not None
```

#### 15.1.2 共通フィールド定義
```python
# app/models/common.py
from typing import Optional, List
from sqlalchemy import String, Text, Boolean, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column

class CommonFields:
    """共通フィールド定義"""
    
    # 基本識別子
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # 名前・説明
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 状態管理
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # メタデータ
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, default={}, nullable=True)
    
    # 優先度
    priority: Mapped[Optional[str]] = mapped_column(
        String(20), 
        default='medium', 
        nullable=True
    )
    
    # カテゴリ・タグ
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, default=[], nullable=True)
```

### 15.2 ユーザー管理モデル

#### 15.2.1 ユーザーモデル
```python
# app/models/user.py
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

class User(BaseModel):
    """ユーザーモデル"""
    __tablename__ = "users"
    
    # 基本情報
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # 認証・認可
    role: Mapped[str] = mapped_column(String(50), default='user', nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # 設定・プリファレンス
    preferences: Mapped[Optional[dict]] = mapped_column(JSON, default={}, nullable=True)
    
    # リレーションシップ
    ai_assistants: Mapped[List["AIAssistant"]] = relationship(
        "AIAssistant", 
        back_populates="created_by_user",
        cascade="all, delete-orphan"
    )
    
    workflows: Mapped[List["Workflow"]] = relationship(
        "Workflow", 
        back_populates="created_by_user",
        cascade="all, delete-orphan"
    )
    
    conversations: Mapped[List["Conversation"]] = relationship(
        "Conversation", 
        back_populates="created_by_user",
        cascade="all, delete-orphan"
    )
    
    # インデックス
    __table_args__ = (
        # 複合インデックス
        Index('idx_users_username_email', 'username', 'email'),
        Index('idx_users_role_active', 'role', 'is_active'),
        # 部分インデックス
        Index('idx_users_active_only', 'id', 'username', 'email') 
        .where(is_active == True),
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"

class UserSession(BaseModel):
    """ユーザーセッションモデル"""
    __tablename__ = "user_sessions"
    
    # セッション情報
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), 
        nullable=False
    )
    session_token: Mapped[str] = mapped_column(
        String(255), 
        unique=True, 
        nullable=False
    )
    refresh_token: Mapped[str] = mapped_column(
        String(255), 
        unique=True, 
        nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False
    )
    
    # 接続情報
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # リレーションシップ
    user: Mapped["User"] = relationship("User", back_populates="sessions")
    
    # インデックス
    __table_args__ = (
        Index('idx_user_sessions_user_id', 'user_id'),
        Index('idx_user_sessions_token', 'session_token'),
        Index('idx_user_sessions_expires', 'expires_at'),
        Index('idx_user_sessions_active', 'user_id', 'is_active')
        .where(is_active == True),
    )
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, expires_at={self.expires_at})>"
```

#### 15.2.2 ユーザープリファレンスモデル
```python
# app/models/user_preferences.py
from typing import Optional, Dict, Any
from sqlalchemy import String, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

class UserPreferences(BaseModel):
    """ユーザープリファレンスモデル"""
    __tablename__ = "user_preferences"
    
    # ユーザー関連
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), 
        nullable=False, 
        unique=True
    )
    
    # UI設定
    theme: Mapped[str] = mapped_column(String(20), default='light', nullable=False)
    language: Mapped[str] = mapped_column(String(10), default='ja', nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default='Asia/Tokyo', nullable=False)
    
    # 通知設定
    notifications: Mapped[Dict[str, Any]] = mapped_column(
        JSON, 
        default={
            "email": True,
            "push": True,
            "workflow_updates": True,
            "ai_discussions": True,
            "plan_approvals": True
        }, 
        nullable=False
    )
    
    # ワークフロー設定
    workflow_settings: Mapped[Dict[str, Any]] = mapped_column(
        JSON, 
        default={
            "auto_assign": True,
            "priority_threshold": "medium",
            "default_view": "kanban"
        }, 
        nullable=False
    )
    
    # AI設定
    ai_settings: Mapped[Dict[str, Any]] = mapped_column(
        JSON, 
        default={
            "preferred_model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2000,
            "auto_summarize": True
        }, 
        nullable=False
    )
    
    # リレーションシップ
    user: Mapped["User"] = relationship("User", back_populates="preferences")
    
    def __repr__(self):
        return f"<UserPreferences(user_id={self.user_id}, theme='{self.theme}')>"
```

### 15.3 AI秘書管理モデル

#### 15.3.1 AI秘書モデル
```python
# app/models/ai_assistant.py
from typing import Optional, List
from sqlalchemy import String, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

class AIAssistant(BaseModel):
    """AI秘書モデル"""
    __tablename__ = "ai_assistants"
    
    # 基本情報
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # AI設定
    ai_provider: Mapped[str] = mapped_column(
        String(50), 
        nullable=False,
        comment="AIプロバイダー（openai, claude, gemini等）"
    )
    model: Mapped[str] = mapped_column(
        String(100), 
        nullable=False,
        comment="使用するAIモデル名"
    )
    api_key_encrypted: Mapped[str] = mapped_column(
        Text, 
        nullable=False,
        comment="暗号化されたAPIキー"
    )
    
    # 関連情報
    persona_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("personas.id"), 
        nullable=True
    )
    team_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("teams.id"), 
        nullable=True
    )
    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"), 
        nullable=False
    )
    
    # 状態・使用状況
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_used: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    usage_count: Mapped[int] = mapped_column(
        Integer, 
        default=0, 
        nullable=False
    )
    
    # 設定・メタデータ
    settings: Mapped[Optional[dict]] = mapped_column(JSON, default={}, nullable=True)
    
    # リレーションシップ
    persona: Mapped[Optional["Persona"]] = relationship("Persona", back_populates="ai_assistants")
    team: Mapped[Optional["Team"]] = relationship("Team", back_populates="ai_assistants")
    created_by_user: Mapped["User"] = relationship("User", back_populates="ai_assistants")
    
    # スキル・タスク関連
    skills: Mapped[List["AssistantSkill"]] = relationship(
        "AssistantSkill", 
        back_populates="assistant",
        cascade="all, delete-orphan"
    )
    
    assigned_tasks: Mapped[List["Task"]] = relationship(
        "Task", 
        back_populates="assigned_assistant"
    )
    
    # インデックス
    __table_args__ = (
        Index('idx_ai_assistants_provider', 'ai_provider'),
        Index('idx_ai_assistants_persona', 'persona_id'),
        Index('idx_ai_assistants_team', 'team_id'),
        Index('idx_ai_assistants_active', 'is_active'),
        Index('idx_ai_assistants_created_by', 'created_by'),
        # 複合インデックス
        Index('idx_ai_assistants_team_active', 'team_id', 'is_active')
        .where(is_active == True),
    )
    
    def __repr__(self):
        return f"<AIAssistant(id={self.id}, name='{self.name}', provider='{self.ai_provider}')>"

class AssistantSkill(BaseModel):
    """AI秘書スキルモデル"""
    __tablename__ = "assistant_skills"
    
    # スキル情報
    assistant_id: Mapped[int] = mapped_column(
        ForeignKey("ai_assistants.id"), 
        nullable=False
    )
    skill_name: Mapped[str] = mapped_column(String(100), nullable=False)
    skill_level: Mapped[int] = mapped_column(
        Integer, 
        nullable=False,
        comment="スキルレベル（1-10）"
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # リレーションシップ
    assistant: Mapped["AIAssistant"] = relationship("AIAssistant", back_populates="skills")
    
    # 制約
    __table_args__ = (
        UniqueConstraint('assistant_id', 'skill_name', name='uq_assistant_skill'),
        Index('idx_assistant_skills_assistant', 'assistant_id'),
        Index('idx_assistant_skills_name', 'skill_name'),
        CheckConstraint('skill_level >= 1 AND skill_level <= 10', name='chk_skill_level'),
    )
    
    def __repr__(self):
        return f"<AssistantSkill(assistant_id={self.assistant_id}, skill='{self.skill_name}', level={self.skill_level})>"
```

### 15.4 ペルソナ・チーム管理モデル

#### 15.4.1 ペルソナモデル
```python
# app/models/persona.py
from typing import Optional, List
from sqlalchemy import String, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

class Persona(BaseModel):
    """ペルソナモデル"""
    __tablename__ = "personas"
    
    # 基本情報
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    personality: Mapped[str] = mapped_column(Text, nullable=False)
    
    # 役割・設定
    role_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("roles.id"), 
        nullable=True
    )
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # アイコン・画像設定
    icon_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    icon_type: Mapped[str] = mapped_column(String(50), default='preset', nullable=False)
    icon_metadata: Mapped[Optional[dict]] = mapped_column(JSON, default={}, nullable=True)
    
    # メタデータ
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, default={}, nullable=True)
    
    # リレーションシップ
    role: Mapped[Optional["Role"]] = relationship("Role", back_populates="personas")
    ai_assistants: Mapped[List["AIAssistant"]] = relationship(
        "AIAssistant", 
        back_populates="persona"
    )
    
    # インデックス
    __table_args__ = (
        Index('idx_personas_role', 'role_id'),
        Index('idx_personas_default', 'is_default'),
        Index('idx_personas_name', 'name'),
        Index('idx_personas_icon_type', 'icon_type'),
    )
    
    def __repr__(self):
        return f"<Persona(id={self.id}, name='{self.name}', role_id={self.role_id})>"

class Role(BaseModel):
    """役割モデル"""
    __tablename__ = "roles"
    
    # 基本情報
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # カテゴリ分類
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    subcategory: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # 権限・設定
    permissions: Mapped[Optional[dict]] = mapped_column(JSON, default={}, nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # リレーションシップ
    personas: Mapped[List["Persona"]] = relationship("Persona", back_populates="role")
    
    # インデックス
    __table_args__ = (
        Index('idx_roles_category', 'category'),
        Index('idx_roles_subcategory', 'subcategory'),
        Index('idx_roles_system', 'is_system'),
    )
    
    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}', category='{self.category}')>"
```

#### 15.4.2 チーム管理モデル
```python
# app/models/team.py
from typing import Optional, List
from sqlalchemy import String, Text, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

class Team(BaseModel):
    """チームモデル"""
    __tablename__ = "teams"
    
    # 基本情報
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # チーム設定
    team_type: Mapped[str] = mapped_column(
        String(50), 
        default='general', 
        nullable=False
    )
    max_members: Mapped[int] = mapped_column(
        Integer, 
        default=10, 
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # リレーションシップ
    ai_assistants: Mapped[List["AIAssistant"]] = relationship(
        "AIAssistant", 
        back_populates="team"
    )
    
    team_members: Mapped[List["TeamMember"]] = relationship(
        "TeamMember", 
        back_populates="team",
        cascade="all, delete-orphan"
    )
    
    workflows: Mapped[List["Workflow"]] = relationship(
        "Workflow", 
        back_populates="assigned_team"
    )
    
    # インデックス
    __table_args__ = (
        Index('idx_teams_type', 'team_type'),
        Index('idx_teams_active', 'is_active'),
        Index('idx_teams_name', 'name'),
    )
    
    def __repr__(self):
        return f"<Team(id={self.id}, name='{self.name}', type='{self.team_type}')>"

class TeamMember(BaseModel):
    """チームメンバーモデル"""
    __tablename__ = "team_members"
    
    # メンバー情報
    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id"), 
        nullable=False
    )
    assistant_id: Mapped[int] = mapped_column(
        ForeignKey("ai_assistants.id"), 
        nullable=False
    )
    
    # 役割・状態
    role: Mapped[str] = mapped_column(
        String(50), 
        default='member', 
        nullable=False
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=func.now(), 
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # リレーションシップ
    team: Mapped["Team"] = relationship("Team", back_populates="team_members")
    assistant: Mapped["AIAssistant"] = relationship("AIAssistant")
    
    # 制約・インデックス
    __table_args__ = (
        UniqueConstraint('team_id', 'assistant_id', name='uq_team_member'),
        Index('idx_team_members_team', 'team_id'),
        Index('idx_team_members_assistant', 'assistant_id'),
        Index('idx_team_members_active', 'team_id', 'is_active')
        .where(is_active == True),
    )
    
    def __repr__(self):
        return f"<TeamMember(team_id={self.team_id}, assistant_id={self.assistant_id}, role='{self.role}')>"
```

### 15.5 ワークフロー・タスク管理モデル

#### 15.5.1 ワークフローモデル
```python
# app/models/workflow.py
from typing import Optional, List
from sqlalchemy import String, Text, ForeignKey, Interval, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

class Workflow(BaseModel):
    """ワークフローモデル"""
    __tablename__ = "workflows"
    
    # 基本情報
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    workflow_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # 状態・優先度
    status: Mapped[str] = mapped_column(
        String(50), 
        default='draft', 
        nullable=False
    )
    priority: Mapped[str] = mapped_column(
        String(20), 
        default='medium', 
        nullable=False
    )
    
    # 関連情報
    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"), 
        nullable=False
    )
    assigned_team_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("teams.id"), 
        nullable=True
    )
    
    # 時間管理
    estimated_duration: Mapped[Optional[Interval]] = mapped_column(Interval, nullable=True)
    actual_duration: Mapped[Optional[Interval]] = mapped_column(Interval, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    
    # メタデータ
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, default={}, nullable=True)
    
    # リレーションシップ
    created_by_user: Mapped["User"] = relationship("User", back_populates="workflows")
    assigned_team: Mapped[Optional["Team"]] = relationship("Team", back_populates="workflows")
    
    tasks: Mapped[List["Task"]] = relationship(
        "Task", 
        back_populates="workflow",
        cascade="all, delete-orphan"
    )
    
    plans: Mapped[List["Plan"]] = relationship(
        "Plan", 
        back_populates="workflow"
    )
    
    # インデックス
    __table_args__ = (
        Index('idx_workflows_status', 'status'),
        Index('idx_workflows_type', 'workflow_type'),
        Index('idx_workflows_team', 'assigned_team_id'),
        Index('idx_workflows_created_by', 'created_by'),
        Index('idx_workflows_priority', 'priority'),
        # 複合インデックス
        Index('idx_workflows_team_status', 'assigned_team_id', 'status'),
        Index('idx_workflows_priority_status', 'priority', 'status'),
        # 部分インデックス
        Index('idx_active_workflows', 'id', 'name', 'status')
        .where(status == 'active'),
    )
    
    def __repr__(self):
        return f"<Workflow(id={self.id}, name='{self.name}', status='{self.status}')>"
```

### 15.6 モデル関係性管理

#### 15.6.1 リレーションシップ定義
```python
# app/models/relationships.py
from typing import List, Optional
from sqlalchemy.orm import relationship, back_populates
from sqlalchemy import ForeignKey, Table, Column, Integer

# 多対多関係の定義
workflow_participants = Table(
    'workflow_participants',
    Base.metadata,
    Column('workflow_id', Integer, ForeignKey('workflows.id'), primary_key=True),
    Column('assistant_id', Integer, ForeignKey('ai_assistants.id'), primary_key=True)
)

# リレーションシップの定義
class Workflow(BaseModel):
    """ワークフローモデル（リレーションシップ拡張）"""
    __tablename__ = "workflows"
    
    # 既存フィールド...
    
    # 参加者管理
    participants: Mapped[List["AIAssistant"]] = relationship(
        "AIAssistant",
        secondary=workflow_participants,
        back_populates="participating_workflows"
    )
    
    # 依存関係管理
    dependencies: Mapped[List["Workflow"]] = relationship(
        "Workflow",
        secondary="workflow_dependencies",
        primaryjoin="Workflow.id==workflow_dependencies.c.workflow_id",
        secondaryjoin="Workflow.id==workflow_dependencies.c.dependency_id",
        back_populates="dependent_workflows"
    )
    
    dependent_workflows: Mapped[List["Workflow"]] = relationship(
        "Workflow",
        secondary="workflow_dependencies",
        primaryjoin="Workflow.id==workflow_dependencies.c.dependency_id",
        secondaryjoin="Workflow.id==workflow_dependencies.c.workflow_id",
        back_populates="dependencies"
    )

class AIAssistant(BaseModel):
    """AI秘書モデル（リレーションシップ拡張）"""
    __tablename__ = "ai_assistants"
    
    # 既存フィールド...
    
    # 参加ワークフロー
    participating_workflows: Mapped[List["Workflow"]] = relationship(
        "Workflow",
        secondary=workflow_participants,
        back_populates="participants"
    )
    
    # 担当タスク
    assigned_tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="assigned_assistant",
        cascade="all, delete-orphan"
    )
    
    # 参加協議
    participating_discussions: Mapped[List["DiscussionParticipant"]] = relationship(
        "DiscussionParticipant",
        back_populates="assistant",
        cascade="all, delete-orphan"
    )
```

#### 15.6.2 カスケード削除設定
```python
# カスケード削除の設定例
class Workflow(BaseModel):
    """ワークフローモデル（カスケード設定）"""
    __tablename__ = "workflows"
    
    # 既存フィールド...
    
    # カスケード削除設定
    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="workflow",
        cascade="all, delete-orphan",  # ワークフロー削除時、タスクも削除
        passive_deletes=True
    )
    
    plans: Mapped[List["Plan"]] = relationship(
        "Plan",
        back_populates="workflow",
        cascade="all, delete-orphan",  # ワークフロー削除時、プランも削除
        passive_deletes=True
    )

class Task(BaseModel):
    """タスクモデル（カスケード設定）"""
    __tablename__ = "tasks"
    
    # 既存フィールド...
    
    # カスケード削除設定
    task_history: Mapped[List["TaskHistory"]] = relationship(
        "TaskHistory",
        back_populates="task",
        cascade="all, delete-orphan",  # タスク削除時、履歴も削除
        passive_deletes=True
    )
```

### 15.7 モデルバリデーション

#### 15.7.1 Pydantic統合
```python
# app/models/validation.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    """ユーザー作成バリデーション"""
    username: str = Field(..., min_length=3, max_length=50, regex=r'^[a-zA-Z0-9_]+$')
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(default='user')
    
    @validator('username')
    def username_must_be_valid(cls, v):
        if not v.isalnum() and '_' not in v:
            raise ValueError('Username must contain only alphanumeric characters and underscores')
        return v
    
    @validator('email')
    def email_must_be_valid(cls, v):
        if '@' not in v or '.' not in v:
            raise ValueError('Invalid email format')
        return v

class AIAssistantCreate(BaseModel):
    """AI秘書作成バリデーション"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    ai_provider: str = Field(..., regex=r'^(openai|claude|gemini)$')
    model: str = Field(..., min_length=1, max_length=100)
    api_key: str = Field(..., min_length=1)
    persona_id: Optional[int] = None
    team_id: Optional[int] = None
    
    @validator('ai_provider')
    def validate_ai_provider(cls, v):
        valid_providers = ['openai', 'claude', 'gemini']
        if v not in valid_providers:
            raise ValueError(f'AI provider must be one of: {valid_providers}')
        return v

class WorkflowCreate(BaseModel):
    """ワークフロー作成バリデーション"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    workflow_type: str = Field(..., regex=r'^(development|design|management|analysis|knowledge)$')
    priority: str = Field(default='medium', regex=r'^(low|medium|high|urgent)$')
    assigned_team_id: Optional[int] = None
    estimated_duration_hours: Optional[float] = Field(None, ge=0)
    
    @validator('priority')
    def validate_priority(cls, v):
        valid_priorities = ['low', 'medium', 'high', 'urgent']
        if v not in valid_priorities:
            raise ValueError(f'Priority must be one of: {valid_priorities}')
        return v
    
    @validator('estimated_duration_hours')
    def validate_duration(cls, v):
        if v is not None and v < 0:
            raise ValueError('Duration must be non-negative')
        return v
```

---

**作成日**: 2025-08-13  
**作成者**: AI Assistant  
**バージョン**: 1.0  
**次回更新予定**: 2025-08-20