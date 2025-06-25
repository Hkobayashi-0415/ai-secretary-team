# データベース テーブル一覧・外部キー関係

* **ドキュメントバージョン:** v1.0
* **作成日:** 2025年1月
* **目的:** AI秘書チーム・プラットフォームのデータベース構造を俯瞰的に把握する

---

## 1. テーブル一覧

### 1.1. ユーザー管理系
| テーブル名 | 説明 | 主要機能 |
|-----------|------|----------|
| `users` | ユーザー基本情報 | ユーザーアカウント管理 |
| `user_preferences` | ユーザー設定 | 個人設定、デフォルト値管理 |

### 1.2. AI秘書管理系
| テーブル名 | 説明 | 主要機能 |
|-----------|------|----------|
| `assistants` | AI秘書基本情報 | AI秘書の定義・管理 |
| `assistant_skills` | AI秘書スキル | 各秘書の専門スキル管理 |

### 1.3. 会話管理系
| テーブル名 | 説明 | 主要機能 |
|-----------|------|----------|
| `conversations` | 会話セッション | 会話の単位管理 |
| `messages` | メッセージ | 個別メッセージ管理 |

### 1.4. ファイル管理系
| テーブル名 | 説明 | 主要機能 |
|-----------|------|----------|
| `files` | ファイル情報 | アップロードファイル管理 |

### 1.5. ワークフロー管理系
| テーブル名 | 説明 | 主要機能 |
|-----------|------|----------|
| `workflows` | ワークフロー定義 | 複合タスクの定義 |
| `workflow_steps` | ワークフローステップ | 各ステップの詳細 |

### 1.6. 知識管理系
| テーブル名 | 説明 | 主要機能 |
|-----------|------|----------|
| `knowledge_base` | 知識ベース | ベクトル検索対応の知識管理 |

### 1.7. 外部連携系
| テーブル名 | 説明 | 主要機能 |
|-----------|------|----------|
| `external_connections` | 外部サービス連携 | API連携設定管理 |

---

## 2. 外部キー関係図

### 2.1. 主要な関係性

```
users (1) ←→ (1) user_preferences
    ↓ (1:N)
assistants (1) ←→ (N) assistant_skills
    ↓ (1:N)
conversations (1) ←→ (N) messages
    ↓ (1:N)
files (N) ←→ (1) conversations
    ↓ (N:1)
messages (N) ←→ (1) files

users (1) ←→ (N) workflows (1) ←→ (N) workflow_steps
    ↓ (1:N)                           ↓ (N:1)
knowledge_base                    assistants

users (1) ←→ (N) external_connections
```

### 2.2. 詳細な外部キー関係

#### users テーブル（中心テーブル）
- **主キー:** `id` (UUID)
- **参照される側:**
  - `user_preferences.user_id` → `users.id`
  - `assistants.user_id` → `users.id`
  - `conversations.user_id` → `users.id`
  - `files.user_id` → `users.id`
  - `workflows.user_id` → `users.id`
  - `knowledge_base.user_id` → `users.id`
  - `external_connections.user_id` → `users.id`

#### assistants テーブル
- **主キー:** `id` (UUID)
- **外部キー:** `user_id` → `users.id`
- **参照される側:**
  - `assistant_skills.assistant_id` → `assistants.id`
  - `conversations.assistant_id` → `assistants.id`
  - `workflow_steps.assistant_id` → `assistants.id`
  - `user_preferences.default_assistant_id` → `assistants.id`

#### conversations テーブル
- **主キー:** `id` (UUID)
- **外部キー:**
  - `user_id` → `users.id`
  - `assistant_id` → `assistants.id`
- **参照される側:**
  - `messages.conversation_id` → `conversations.id`
  - `files.conversation_id` → `conversations.id`

#### messages テーブル
- **主キー:** `id` (UUID)
- **外部キー:**
  - `conversation_id` → `conversations.id`
  - `parent_message_id` → `messages.id` (自己参照)
- **参照される側:**
  - `files.message_id` → `messages.id`

#### files テーブル
- **主キー:** `id` (UUID)
- **外部キー:**
  - `user_id` → `users.id`
  - `conversation_id` → `conversations.id`
  - `message_id` → `messages.id`

#### workflows テーブル
- **主キー:** `id` (UUID)
- **外部キー:** `user_id` → `users.id`
- **参照される側:**
  - `workflow_steps.workflow_id` → `workflows.id`

#### workflow_steps テーブル
- **主キー:** `id` (UUID)
- **外部キー:**
  - `workflow_id` → `workflows.id`
  - `assistant_id` → `assistants.id`

#### knowledge_base テーブル
- **主キー:** `id` (UUID)
- **外部キー:** `user_id` → `users.id`

#### external_connections テーブル
- **主キー:** `id` (UUID)
- **外部キー:** `user_id` → `users.id`

---

## 3. テーブル間の関係性詳細

### 3.1. 1対1関係
- `users` ↔ `user_preferences` (ユーザーとその設定)

### 3.2. 1対多関係
- `users` → `assistants` (1ユーザーが複数のAI秘書を持つ)
- `users` → `conversations` (1ユーザーが複数の会話を持つ)
- `users` → `workflows` (1ユーザーが複数のワークフローを持つ)
- `users` → `knowledge_base` (1ユーザーが複数の知識を持つ)
- `users` → `external_connections` (1ユーザーが複数の外部連携を持つ)
- `assistants` → `assistant_skills` (1AI秘書が複数のスキルを持つ)
- `conversations` → `messages` (1会話が複数のメッセージを持つ)
- `workflows` → `workflow_steps` (1ワークフローが複数のステップを持つ)

### 3.3. 多対多関係（中間テーブルなし）
- `conversations` ↔ `files` (会話とファイルの関連)
- `messages` ↔ `files` (メッセージとファイルの関連)

### 3.4. 自己参照関係
- `messages.parent_message_id` → `messages.id` (スレッド対応)

---

## 4. データの流れ

### 4.1. 基本的な会話フロー
```
users → assistants → conversations → messages
                    ↓
                files (添付ファイル)
```

### 4.2. ワークフロー実行フロー
```
users → workflows → workflow_steps → assistants
```

### 4.3. 知識管理フロー
```
users → knowledge_base (ベクトル検索対応)
```

### 4.4. 外部連携フロー
```
users → external_connections → 外部サービス
```

---

## 5. 重要な制約

### 5.1. カスケード削除
- `users` 削除時 → 関連する全テーブルのデータが削除
- `conversations` 削除時 → `messages`, `files` が削除
- `assistants` 削除時 → `assistant_skills` が削除
- `workflows` 削除時 → `workflow_steps` が削除

### 5.2. 一意制約
- `users.username` (ユニーク)
- `users.email` (ユニーク)
- `assistant_skills.assistant_id + skill_name` (複合ユニーク)
- `workflow_steps.workflow_id + step_order` (複合ユニーク)
- `external_connections.user_id + service_name + connection_name` (複合ユニーク)

### 5.3. チェック制約
- `assistant_skills.skill_level` (1-10の範囲)
- `messages.role` ('user', 'assistant', 'system'のみ) 