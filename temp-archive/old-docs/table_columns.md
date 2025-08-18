# データベース テーブル詳細カラム定義

* **ドキュメントバージョン:** v1.0
* **作成日:** 2025年1月
* **目的:** 各テーブルの詳細なカラム定義とデータ型を明確にする

---

## 1. ユーザー管理系テーブル

### 1.1. users テーブル
| カラム名 | データ型 | NULL | デフォルト値 | 説明 |
|---------|---------|------|-------------|------|
| `id` | UUID | NOT NULL | `gen_random_uuid()` | 主キー |
| `username` | VARCHAR(50) | NOT NULL | - | ユーザー名（ユニーク） |
| `email` | VARCHAR(255) | NOT NULL | - | メールアドレス（ユニーク） |
| `password_hash` | VARCHAR(255) | NOT NULL | - | パスワードハッシュ |
| `first_name` | VARCHAR(100) | NULL | - | 名 |
| `last_name` | VARCHAR(100) | NULL | - | 姓 |
| `is_active` | BOOLEAN | NOT NULL | `true` | アカウント有効フラグ |
| `is_verified` | BOOLEAN | NOT NULL | `false` | メール認証済みフラグ |
| `last_login_at` | TIMESTAMP WITH TIME ZONE | NULL | - | 最終ログイン日時 |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | `NOW()` | 作成日時 |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | `NOW()` | 更新日時 |

### 1.2. user_preferences テーブル
| カラム名 | データ型 | NULL | デフォルト値 | 説明 |
|---------|---------|------|-------------|------|
| `user_id` | UUID | NOT NULL | - | 主キー・外部キー（users.id） |
| `default_assistant_id` | UUID | NULL | - | デフォルトAI秘書ID |
| `default_llm_model` | VARCHAR(100) | NOT NULL | `'gemini-pro'` | デフォルトLLMモデル |
| `voice_enabled` | BOOLEAN | NOT NULL | `true` | 音声機能有効フラグ |
| `auto_save_conversations` | BOOLEAN | NOT NULL | `true` | 会話自動保存フラグ |
| `theme` | VARCHAR(20) | NOT NULL | `'light'` | UIテーマ |
| `language` | VARCHAR(10) | NOT NULL | `'ja'` | 言語設定 |
| `timezone` | VARCHAR(50) | NOT NULL | `'Asia/Tokyo'` | タイムゾーン |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | `NOW()` | 作成日時 |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | `NOW()` | 更新日時 |

---

## 2. AI秘書管理系テーブル

### 2.1. assistants テーブル
| カラム名 | データ型 | NULL | デフォルト値 | 説明 |
|---------|---------|------|-------------|------|
| `id` | UUID | NOT NULL | `gen_random_uuid()` | 主キー |
| `user_id` | UUID | NOT NULL | - | 外部キー（users.id） |
| `name` | VARCHAR(100) | NOT NULL | - | AI秘書名 |
| `description` | TEXT | NULL | - | 説明 |
| `system_prompt` | TEXT | NOT NULL | - | システムプロンプト |
| `personality_type` | VARCHAR(50) | NULL | - | 性格タイプ |
| `default_llm_model` | VARCHAR(100) | NOT NULL | `'gemini-pro'` | デフォルトLLMモデル |
| `voice_id` | VARCHAR(100) | NULL | - | 音声ID |
| `avatar_url` | VARCHAR(500) | NULL | - | アバター画像URL |
| `is_active` | BOOLEAN | NOT NULL | `true` | 有効フラグ |
| `is_public` | BOOLEAN | NOT NULL | `false` | 公開フラグ |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | `NOW()` | 作成日時 |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | `NOW()` | 更新日時 |

### 2.2. assistant_skills テーブル
| カラム名 | データ型 | NULL | デフォルト値 | 説明 |
|---------|---------|------|-------------|------|
| `id` | UUID | NOT NULL | `gen_random_uuid()` | 主キー |
| `assistant_id` | UUID | NOT NULL | - | 外部キー（assistants.id） |
| `skill_name` | VARCHAR(100) | NOT NULL | - | スキル名 |
| `skill_level` | INTEGER | NOT NULL | `1` | スキルレベル（1-10） |
| `description` | TEXT | NULL | - | スキル説明 |
| `is_enabled` | BOOLEAN | NOT NULL | `true` | 有効フラグ |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | `NOW()` | 作成日時 |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | `NOW()` | 更新日時 |

---

## 3. 会話管理系テーブル

### 3.1. conversations テーブル
| カラム名 | データ型 | NULL | デフォルト値 | 説明 |
|---------|---------|------|-------------|------|
| `id` | UUID | NOT NULL | `gen_random_uuid()` | 主キー |
| `user_id` | UUID | NOT NULL | - | 外部キー（users.id） |
| `assistant_id` | UUID | NOT NULL | - | 外部キー（assistants.id） |
| `title` | VARCHAR(255) | NULL | - | 会話タイトル |
| `conversation_type` | VARCHAR(50) | NOT NULL | `'chat'` | 会話タイプ |
| `status` | VARCHAR(20) | NOT NULL | `'active'` | ステータス |
| `metadata` | JSONB | NULL | - | メタデータ |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | `NOW()` | 作成日時 |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | `NOW()` | 更新日時 |

### 3.2. messages テーブル
| カラム名 | データ型 | NULL | デフォルト値 | 説明 |
|---------|---------|------|-------------|------|
| `id` | UUID | NOT NULL | `gen_random_uuid()` | 主キー |
| `conversation_id` | UUID | NOT NULL | - | 外部キー（conversations.id） |
| `role` | VARCHAR(20) | NOT NULL | - | メッセージ役割 |
| `content` | TEXT | NOT NULL | - | メッセージ内容 |
| `content_type` | VARCHAR(20) | NOT NULL | `'text'` | コンテンツタイプ |
| `metadata` | JSONB | NULL | - | メタデータ |
| `parent_message_id` | UUID | NULL | - | 親メッセージID（自己参照） |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | `NOW()` | 作成日時 |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | `NOW()` | 更新日時 |

---

## 4. ファイル管理系テーブル

### 4.1. files テーブル
| カラム名 | データ型 | NULL | デフォルト値 | 説明 |
|---------|---------|------|-------------|------|
| `id` | UUID | NOT NULL | `gen_random_uuid()` | 主キー |
| `user_id` | UUID | NOT NULL | - | 外部キー（users.id） |
| `conversation_id` | UUID | NULL | - | 外部キー（conversations.id） |
| `message_id` | UUID | NULL | - | 外部キー（messages.id） |
| `file_name` | VARCHAR(255) | NOT NULL | - | ファイル名 |
| `file_path` | VARCHAR(500) | NOT NULL | - | ファイルパス |
| `file_size` | BIGINT | NOT NULL | - | ファイルサイズ（バイト） |
| `mime_type` | VARCHAR(100) | NOT NULL | - | MIMEタイプ |
| `file_type` | VARCHAR(20) | NOT NULL | - | ファイルタイプ |
| `metadata` | JSONB | NULL | - | メタデータ |
| `is_processed` | BOOLEAN | NOT NULL | `false` | 処理済みフラグ |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | `NOW()` | 作成日時 |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | `NOW()` | 更新日時 |

---

## 5. ワークフロー管理系テーブル

### 5.1. workflows テーブル
| カラム名 | データ型 | NULL | デフォルト値 | 説明 |
|---------|---------|------|-------------|------|
| `id` | UUID | NOT NULL | `gen_random_uuid()` | 主キー |
| `user_id` | UUID | NOT NULL | - | 外部キー（users.id） |
| `name` | VARCHAR(255) | NOT NULL | - | ワークフロー名 |
| `description` | TEXT | NULL | - | 説明 |
| `workflow_type` | VARCHAR(50) | NOT NULL | - | ワークフロータイプ |
| `is_active` | BOOLEAN | NOT NULL | `true` | 有効フラグ |
| `is_template` | BOOLEAN | NOT NULL | `false` | テンプレートフラグ |
| `metadata` | JSONB | NULL | - | メタデータ |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | `NOW()` | 作成日時 |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | `NOW()` | 更新日時 |

### 5.2. workflow_steps テーブル
| カラム名 | データ型 | NULL | デフォルト値 | 説明 |
|---------|---------|------|-------------|------|
| `id` | UUID | NOT NULL | `gen_random_uuid()` | 主キー |
| `workflow_id` | UUID | NOT NULL | - | 外部キー（workflows.id） |
| `step_order` | INTEGER | NOT NULL | - | ステップ順序 |
| `step_name` | VARCHAR(255) | NOT NULL | - | ステップ名 |
| `step_type` | VARCHAR(50) | NOT NULL | - | ステップタイプ |
| `assistant_id` | UUID | NULL | - | 外部キー（assistants.id） |
| `prompt_template` | TEXT | NULL | - | プロンプトテンプレート |
| `input_mapping` | JSONB | NULL | - | 入力マッピング |
| `output_mapping` | JSONB | NULL | - | 出力マッピング |
| `conditions` | JSONB | NULL | - | 条件設定 |
| `is_enabled` | BOOLEAN | NOT NULL | `true` | 有効フラグ |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | `NOW()` | 作成日時 |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | `NOW()` | 更新日時 |

---

## 6. 知識管理系テーブル

### 6.1. knowledge_base テーブル
| カラム名 | データ型 | NULL | デフォルト値 | 説明 |
|---------|---------|------|-------------|------|
| `id` | UUID | NOT NULL | `gen_random_uuid()` | 主キー |
| `user_id` | UUID | NOT NULL | - | 外部キー（users.id） |
| `title` | VARCHAR(255) | NOT NULL | - | タイトル |
| `content` | TEXT | NOT NULL | - | コンテンツ |
| `content_type` | VARCHAR(50) | NOT NULL | - | コンテンツタイプ |
| `source_url` | VARCHAR(500) | NULL | - | ソースURL |
| `tags` | TEXT[] | NULL | - | タグ配列 |
| `embedding_vector` | VECTOR(1536) | NULL | - | ベクトル（pgvector） |
| `metadata` | JSONB | NULL | - | メタデータ |
| `is_active` | BOOLEAN | NOT NULL | `true` | 有効フラグ |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | `NOW()` | 作成日時 |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | `NOW()` | 更新日時 |

---

## 7. 外部連携系テーブル

### 7.1. external_connections テーブル
| カラム名 | データ型 | NULL | デフォルト値 | 説明 |
|---------|---------|------|-------------|------|
| `id` | UUID | NOT NULL | `gen_random_uuid()` | 主キー |
| `user_id` | UUID | NOT NULL | - | 外部キー（users.id） |
| `service_name` | VARCHAR(100) | NOT NULL | - | サービス名 |
| `connection_name` | VARCHAR(255) | NOT NULL | - | 接続名 |
| `credentials` | JSONB | NOT NULL | - | 認証情報（暗号化） |
| `settings` | JSONB | NULL | - | 設定情報 |
| `is_active` | BOOLEAN | NOT NULL | `true` | 有効フラグ |
| `last_sync_at` | TIMESTAMP WITH TIME ZONE | NULL | - | 最終同期日時 |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | `NOW()` | 作成日時 |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | `NOW()` | 更新日時 |

---

## 8. 列挙値・制約詳細

### 8.1. 列挙値定義

#### conversation_type の値
- `'chat'` - 通常のチャット
- `'research'` - リサーチ会話
- `'document_creation'` - 資料作成
- `'workflow'` - ワークフロー実行

#### status の値
- `'active'` - アクティブ
- `'archived'` - アーカイブ済み
- `'deleted'` - 削除済み

#### role の値
- `'user'` - ユーザーメッセージ
- `'assistant'` - AI秘書メッセージ
- `'system'` - システムメッセージ

#### content_type の値
- `'text'` - テキスト
- `'image'` - 画像
- `'file'` - ファイル
- `'audio'` - 音声

#### file_type の値
- `'image'` - 画像ファイル
- `'document'` - 文書ファイル
- `'audio'` - 音声ファイル
- `'video'` - 動画ファイル

#### step_type の値
- `'ai_task'` - AIタスク
- `'api_call'` - API呼び出し
- `'condition'` - 条件分岐
- `'loop'` - ループ処理

#### personality_type の値
- `'professional'` - プロフェッショナル
- `'friendly'` - フレンドリー
- `'creative'` - クリエイティブ
- `'analytical'` - 分析的

### 8.2. 制約詳細

#### チェック制約
```sql
-- assistant_skills.skill_level
CHECK (skill_level BETWEEN 1 AND 10)

-- messages.role
CHECK (role IN ('user', 'assistant', 'system'))
```

#### 一意制約
```sql
-- users
UNIQUE(username)
UNIQUE(email)

-- assistant_skills
UNIQUE(assistant_id, skill_name)

-- workflow_steps
UNIQUE(workflow_id, step_order)

-- external_connections
UNIQUE(user_id, service_name, connection_name)
```

#### 外部キー制約
```sql
-- カスケード削除
ON DELETE CASCADE: user_preferences, assistants, conversations, files, workflows, knowledge_base, external_connections

-- SET NULL
ON DELETE SET NULL: files.conversation_id, files.message_id
```

---

## 9. データ型の選択理由

### 9.1. UUID の使用
- **理由:** 分散システムでの一意性保証、セキュリティ向上
- **使用箇所:** 全テーブルの主キー

### 9.2. JSONB の使用
- **理由:** 柔軟なスキーマ、効率的なクエリ、インデックス対応
- **使用箇所:** metadata カラム全般

### 9.3. VECTOR の使用
- **理由:** ベクトル検索の高速化（pgvector拡張）
- **使用箇所:** knowledge_base.embedding_vector

### 9.4. TEXT[] の使用
- **理由:** タグ管理の効率化、GINインデックス対応
- **使用箇所:** knowledge_base.tags 