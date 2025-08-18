# 技術仕様書：AI秘書チーム・プラットフォーム（統合版）

* **ドキュメントバージョン:** v1.0
* **作成日:** 2025年8月13日
* **目的:** AI秘書チーム・プラットフォームの統合版における技術的な実装仕様を定義する

---

## 1. 概要

### 1.1. ドキュメントの目的
本ドキュメントは、要件定義書と機能定義書で定義された機能を実現するための技術的な仕様を定義するものである。

### 1.2. 技術スタックの概要
- **バックエンド**: FastAPI + Python 3.11+
- **フロントエンド**: React 18 + TypeScript
- **データベース**: PostgreSQL 16 + Redis 7
- **知識管理**: Obsidian連携
- **配布方式**: インストーラー（PyInstaller等）

### 1.3. システム特性・前提条件
- **動作環境**: ローカルPC（Windows 10/11）での単独動作
- **同時接続**: 想定なし（シングルユーザー・ローカル環境）
- **配布方式**: 各自のPCで動作するハイブリッドアプリ（デスクトップ + Web技術）
- **カスタマイズ**: 各自のPCで独自にカスタマイズ可能
- **ネットワーク**: LLM API使用時のインターネット接続のみ（ローカルネットワーク不要）
- **外部連携**: 外部システム連携なし（ローカル完結型）
- **運用**: 開発者による基本運用で十分（24/7監視・専門運用チーム不要）
- **スケーラビリティ**: ローカル環境での動作に最適化（大規模システム・クラウド対応は不要）
- **機能範囲**: 基本機能に集中（高度な監査・セキュリティ・パフォーマンス最適化は不要）
- **設計レベル**: ローカル・シングルユーザー級（エンタープライズ級・大規模システム対応は不要）

---

## 2. アーキテクチャ設計

### 2.1. 全体アーキテクチャ

```mermaid
graph TD
    subgraph User Environment
        User("[👤 User]")
        Browser["🌐 Browser (React Frontend)"]
    end

    subgraph Application Layer
        API_GW["🚪 FastAPI Gateway"]
        subgraph AI Secretaries
            Secretary_A["🤖 Secretary A (Persona 1)"]
            Secretary_B["🤖 Secretary B (Persona 2)"]
            Secretary_C["🤖 Secretary C (Persona 3)"]
        end
        Librarian_AI["📚 Librarian AI (司書AI)"]
        WF_Engine["⚙️ Workflow Engine"]
    end

    subgraph Data Layer
        Postgres["🐘 PostgreSQL (Configs/Logs)"]
        Obsidian["📖 Obsidian Vault"]
        File_System["💾 File System"]
    end

    subgraph External Services
        LLM["💡 LLM APIs (Gemini/GPT/Claude)"]
        TTS["🗣️ TTS API (Optional)"]
    end

    User -- Interacts --> Browser
    Browser -- API Calls --> API_GW
    API_GW -- Routes to --> Secretary_A & Secretary_B & Secretary_C
    API_GW -- Routes to --> Librarian_AI
    API_GW -- Routes to --> WF_Engine

    Secretary_A & Secretary_B & Secretary_C -- Uses --> LLM
    Secretary_A & Secretary_B & Secretary_C -- Queries --> Librarian_AI
    Librarian_AI -- Manages --> Obsidian
    Librarian_AI -- Searches --> Obsidian

    WF_Engine -- Manages --> Secretary_A & Secretary_B & Secretary_C
    WF_Engine -- Stores Data --> Postgres

    Postgres -- Stores --> Configs & Logs
    Obsidian -- Stores --> Knowledge & Notes
    File_System -- Stores --> Application Files
```

### 2.2. コンポーネント構成

#### 2.2.1. フロントエンド（React）
- **メインアプリケーション**: アプリケーションのメインコンポーネント
- **ペルソナ管理**: ペルソナ・チームの管理画面
- **チャット画面**: AI秘書との対話画面
- **タスク管理**: ワークフローの管理画面
- **設定画面**: 各種設定の管理画面
- **知識画面**: Obsidianの内容表示・検索画面

#### 2.2.2. バックエンド（FastAPI）
- **API Gateway**: リクエストの振り分け・認証
- **ペルソナサービス**: ペルソナ・チームの管理
- **ワークフローサービス**: タスク・ワークフローの管理
- **Obsidian連携サービス**: Obsidianとの連携
- **AI連携サービス**: 外部AI APIとの連携
- **認証サービス**: ユーザー認証・権限管理

#### 2.2.3. データ層
- **PostgreSQL**: 設定・ログ・履歴データ
- **Obsidian**: 知識・ノート・テンプレート
- **ファイルシステム**: アプリケーションファイル・設定ファイル

---

## 3. データベース設計

### 3.1. データベース概要
- **DBMS**: PostgreSQL 16 + Redis 7
- **文字エンコーディング**: UTF-8
- **タイムゾーン**: Asia/Tokyo
- **接続方式**: プール接続（SQLAlchemy）

### 3.2. テーブル設計

#### 3.2.1. ユーザー管理系
```sql
-- ユーザー基本情報
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

-- ユーザー設定
CREATE TABLE user_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    default_assistant_id UUID,
    default_llm_model VARCHAR(100) DEFAULT 'gemini-pro',
    voice_enabled BOOLEAN NOT NULL DEFAULT false,
    theme VARCHAR(20) DEFAULT 'light',
    language VARCHAR(10) DEFAULT 'ja',
    timezone VARCHAR(50) DEFAULT 'Asia/Tokyo',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

#### 3.2.2. AI秘書管理系
```sql
-- ペルソナ管理
CREATE TABLE personas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    personality_data JSONB NOT NULL, -- 性格・専門性等
    appearance_data JSONB, -- 外見・アバター等
    capabilities_data JSONB, -- スキル・制限等
    is_default BOOLEAN NOT NULL DEFAULT false,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- チーム管理
CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    workflow_data JSONB, -- ワークフロー設定
    is_default BOOLEAN NOT NULL DEFAULT false,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- チームメンバー
CREATE TABLE team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    persona_id UUID NOT NULL REFERENCES personas(id) ON DELETE CASCADE,
    role VARCHAR(100) NOT NULL,
    responsibilities TEXT[],
    authority_level VARCHAR(50) DEFAULT 'member',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 役割定義
CREATE TABLE role_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category VARCHAR(100) NOT NULL, -- 大項目（コーディング、リサーチ等）
    name VARCHAR(100) NOT NULL, -- 役割名
    description TEXT,
    parent_role_id UUID REFERENCES role_definitions(id),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

#### 3.2.3. ワークフロー管理系
```sql
-- タスク管理
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL, -- 'simple', 'complex', 'workflow', 'periodic'
    priority VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'urgent'
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'running', 'paused', 'completed', 'failed'
    assignee_id UUID REFERENCES personas(id),
    team_id UUID REFERENCES teams(id),
    estimated_time INTEGER, -- 推定時間（分）
    actual_time INTEGER, -- 実際の時間（分）
    dependencies JSONB, -- 依存タスク
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- ワークフロー定義
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    workflow_data JSONB NOT NULL, -- ワークフロー定義
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- タスク履歴
CREATE TABLE task_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL, -- 'created', 'started', 'paused', 'resumed', 'completed', 'failed'
    details JSONB,
    executed_by UUID REFERENCES personas(id),
    executed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

#### 3.2.4. Obsidian連携系
```sql
-- Obsidian連携設定
CREATE TABLE obsidian_integration_settings (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    vault_path VARCHAR(500) NOT NULL,
    knowledge_base_dir VARCHAR(100) DEFAULT 'knowledge-base',
    enabled BOOLEAN NOT NULL DEFAULT false,
    last_sync TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 司書AI設定
CREATE TABLE librarian_assistant (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) DEFAULT '司書AI',
    description TEXT DEFAULT 'Obsidian知識ベースの管理・検索・タグ付けを担当する司書',
    system_prompt TEXT NOT NULL,
    personality_data JSONB,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- 検索履歴
CREATE TABLE search_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    results_count INTEGER,
    search_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

#### 3.2.5. セッション・ログ系
```sql
-- ローカル環境用状態管理
CREATE TABLE app_state (
    id SERIAL PRIMARY KEY,
    state_key VARCHAR(255) UNIQUE NOT NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- アプリケーションログ
CREATE TABLE application_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    level VARCHAR(20) NOT NULL, -- 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    message TEXT NOT NULL,
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

### 3.3. インデックス設計
```sql
-- 主要な検索用インデックス
CREATE INDEX idx_personas_user_id ON personas(user_id);
CREATE INDEX idx_personas_active ON personas(is_active);
CREATE INDEX idx_teams_user_id ON teams(user_id);
CREATE INDEX idx_teams_active ON teams(is_active);
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_assignee ON tasks(assignee_id);
CREATE INDEX idx_tasks_team ON tasks(team_id);
CREATE INDEX idx_search_history_user_id ON search_history(user_id);
CREATE INDEX idx_search_history_created_at ON search_history(created_at);
```

---

## 4. API設計

### 4.1. API概要
- **ベースURL**: `/api/v1`
- **認証方式**: ローカル自動認証
- **データ形式**: JSON
- **エンコーディング**: UTF-8

### 4.2. 認証・認可

#### 4.2.1. 認証エンドポイント
```http
POST /api/v1/auth/login
POST /api/v1/auth/register
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
```

#### 4.2.2. 認証ヘッダー
```http
Authorization: Bearer <jwt_token>
```

### 4.3. ペルソナ管理API

#### 4.3.1. ペルソナCRUD
```http
GET    /api/v1/personas              # ペルソナ一覧取得
POST   /api/v1/personas              # ペルソナ作成
GET    /api/v1/personas/{id}         # ペルソナ詳細取得
PUT    /api/v1/personas/{id}         # ペルソナ更新
DELETE /api/v1/personas/{id}         # ペルソナ削除
```

#### 4.3.2. ペルソナ関連
```http
GET    /api/v1/personas/{id}/teams   # ペルソナが所属するチーム
POST   /api/v1/personas/{id}/clone   # ペルソナ複製
```

### 4.4. チーム管理API

#### 4.4.1. チームCRUD
```http
GET    /api/v1/teams                 # チーム一覧取得
POST   /api/v1/teams                 # チーム作成
GET    /api/v1/teams/{id}            # チーム詳細取得
PUT    /api/v1/teams/{id}            # チーム更新
DELETE /api/v1/teams/{id}            # チーム削除
```

#### 4.4.2. チームメンバー管理
```http
GET    /api/v1/teams/{id}/members    # チームメンバー一覧
POST   /api/v1/teams/{id}/members    # メンバー追加
PUT    /api/v1/teams/{id}/members/{member_id}  # メンバー更新
DELETE /api/v1/teams/{id}/members/{member_id}  # メンバー削除
```

### 4.5. ワークフロー管理API

#### 4.5.1. タスク管理
```http
GET    /api/v1/tasks                 # タスク一覧取得
POST   /api/v1/tasks                 # タスク作成
GET    /api/v1/tasks/{id}            # タスク詳細取得
PUT    /api/v1/tasks/{id}            # タスク更新
DELETE /api/v1/tasks/{id}            # タスク削除
```

#### 4.5.2. タスク実行制御
```http
POST   /api/v1/tasks/{id}/start      # タスク開始
POST   /api/v1/tasks/{id}/pause      # タスク一時停止
POST   /api/v1/tasks/{id}/resume     # タスク再開
POST   /api/v1/tasks/{id}/complete   # タスク完了
POST   /api/v1/tasks/{id}/fail       # タスク失敗
```

#### 4.5.3. ワークフロー管理
```http
GET    /api/v1/workflows             # ワークフロー一覧取得
POST   /api/v1/workflows             # ワークフロー作成
GET    /api/v1/workflows/{id}        # ワークフロー詳細取得
PUT    /api/v1/workflows/{id}        # ワークフロー更新
DELETE /api/v1/workflows/{id}        # ワークフロー削除
POST   /api/v1/workflows/{id}/execute # ワークフロー実行
```

### 4.6. Obsidian連携API

#### 4.6.1. 設定管理
```http
GET    /api/v1/obsidian/settings     # 設定取得
PUT    /api/v1/obsidian/settings     # 設定更新
POST   /api/v1/obsidian/test         # 接続テスト
```

#### 4.6.2. 知識管理
```http
GET    /api/v1/obsidian/search       # 知識検索
GET    /api/v1/obsidian/categories   # カテゴリ一覧
GET    /api/v1/obsidian/notes        # ノート一覧
POST   /api/v1/obsidian/notes        # ノート作成
PUT    /api/v1/obsidian/notes/{id}   # ノート更新
DELETE /api/v1/obsidian/notes/{id}   # ノート削除
```

#### 4.6.3. 司書AI
```http
POST   /api/v1/obsidian/librarian/query    # 司書AIへの問い合わせ
GET    /api/v1/obsidian/librarian/history  # 問い合わせ履歴
```

### 4.7. チャットAPI

#### 4.7.1. チャットセッション
```http
GET    /api/v1/chat/sessions         # セッション一覧
POST   /api/v1/chat/sessions         # セッション作成
GET    /api/v1/chat/sessions/{id}    # セッション詳細
DELETE /api/v1/chat/sessions/{id}    # セッション削除
```

#### 4.7.2. メッセージ
```http
GET    /api/v1/chat/sessions/{id}/messages     # メッセージ一覧
POST   /api/v1/chat/sessions/{id}/messages     # メッセージ送信
```

### 4.8. エラーレスポンス

#### 4.8.1. エラー形式
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "エラーメッセージ",
    "details": "詳細情報",
    "timestamp": "2025-08-13T10:00:00Z"
  }
}
```

#### 4.8.2. 主要エラーコード
- `AUTHENTICATION_FAILED`: 認証失敗
- `AUTHORIZATION_FAILED`: 認可失敗
- `VALIDATION_ERROR`: バリデーションエラー
- `NOT_FOUND`: リソースが見つからない
- `INTERNAL_ERROR`: 内部エラー

---

## 5. 技術スタック詳細

### 5.1. バックエンド技術

#### 5.1.1. フレームワーク
- **FastAPI**: Web APIフレームワーク
- **SQLAlchemy**: ORM
- **Alembic**: データベースマイグレーション
- **Pydantic**: データバリデーション

#### 5.1.2. 認証・セキュリティ
- **ローカル認証**: アプリ起動時自動接続
- **Passlib**: パスワードハッシュ化
- **python-multipart**: ファイルアップロード

#### 5.1.3. 非同期処理
- **asyncio**: 非同期処理
- **aiofiles**: 非同期ファイル操作
- **httpx**: 非同期HTTPクライアント

### 5.2. フロントエンド技術

#### 5.2.1. フレームワーク
- **React 18**: UIライブラリ
- **TypeScript**: 型安全なJavaScript
- **Vite**: ビルドツール

#### 5.2.2. 状態管理
- **Zustand**: 軽量状態管理
- **React Query**: サーバー状態管理

#### 5.2.3. UIコンポーネント
- **Tailwind CSS**: ユーティリティファーストCSS
- **Shadcn UI**: 再利用可能なUIコンポーネント

### 5.3. データベース技術

#### 5.3.1. データベース
- **PostgreSQL 16 + Redis 7**: リレーショナルデータベース + キャッシュ専用（オプション）
- **pgvector**: ベクトル検索拡張（将来の拡張用）

#### 5.3.2. 接続管理
- **asyncpg**: 非同期PostgreSQLドライバ
- **SQLAlchemy**: ORM・接続プール

### 5.4. 外部連携技術

#### 5.4.1. AI API
- **OpenAI API**: GPTモデル
- **Google Gemini API**: Geminiモデル
- **Anthropic API**: Claudeモデル

#### 5.4.2. 音声合成
- **Google Text-to-Speech**: 音声合成
- **Azure Speech Service**: 音声合成（オプション）

---

## 6. 配布パッケージ化

### 6.1. パッケージ化技術

#### 6.1.1. Pythonアプリケーション
- **PyInstaller**: 単一実行ファイル化
- **cx_Freeze**: クロスプラットフォーム対応
- **py2exe**: Windows専用（非推奨）

#### 6.1.2. インストーラー
- **NSIS**: Windowsインストーラー作成
- **Inno Setup**: Windowsインストーラー作成
- **WiX Toolset**: Windowsインストーラー作成

### 6.2. 依存関係管理

#### 6.2.1. Python依存関係
- **requirements.txt**: 依存関係リスト
- **pip**: パッケージ管理
- **virtualenv**: 仮想環境管理

#### 6.2.2. システム依存関係
- **PostgreSQL**: データベースエンジン
- **Python 3.11+**: 実行環境
- **Windows 10/11**: 対象OS

### 6.3. 配布パッケージ構成

#### 6.3.1. 基本構成
```
AI-Secretary-Platform/
├── ai_secretary.exe          # メインアプリケーション
├── config/                   # 設定ファイル
│   ├── database.ini         # データベース設定
│   ├── obsidian.ini         # Obsidian設定
│   └── app.ini              # アプリケーション設定
├── data/                     # データディレクトリ
│   ├── logs/                # ログファイル
│   └── temp/                # 一時ファイル
├── docs/                     # ドキュメント
│   ├── README.txt           # インストールガイド
│   └── user_manual.pdf      # ユーザーマニュアル
└── uninstall.exe            # アンインストーラー
```

#### 6.3.2. インストーラー機能
- **自動環境構築**: Python、PostgreSQLの自動インストール
- **設定ファイル生成**: 初期設定ファイルの自動作成
- **ショートカット作成**: デスクトップ・スタートメニュー
- **アンインストール**: 完全なアンインストール

---

## 7. パフォーマンス・セキュリティ

### 7.1. パフォーマンス要件

#### 7.1.1. 応答時間
- **API応答**: 1秒以内
- **検索応答**: 3秒以内
- **ファイル操作**: 5秒以内
- **起動時間**: 30秒以内

#### 7.1.2. スループット
- **同時ユーザー**: 10ユーザー
- **API要求**: 100 req/min
- **ファイル処理**: 50 files/min

#### 7.1.3. リソース使用量
- **メモリ**: 1GB以内
- **CPU**: 10%以内（アイドル時）
- **ディスク**: 100MB以内（アプリケーション）

### 7.2. セキュリティ要件

#### 7.2.1. 認証・認可
- **パスワード**: 強力なパスワード要求
- **状態管理**: ローカルアプリケーション状態
- **権限**: ロールベースアクセス制御

#### 7.2.2. データ保護
- **暗号化**: 機密データの暗号化
- **バックアップ**: 重要なデータのバックアップ
- **ログ**: セキュリティ関連のログ記録

#### 7.2.3. 外部連携
- **API Key**: 安全なAPI Key管理
- **通信**: HTTPS通信の強制
- **検証**: 外部API応答の検証

---

## 8. 開発・テスト・運用

### 8.1. 開発環境

#### 8.1.1. 開発ツール
- **IDE**: Visual Studio Code、PyCharm
- **バージョン管理**: Git
- **コード品質**: Black、Flake8、MyPy

#### 8.1.2. 開発環境
- **Python**: 3.11+
- **Node.js**: 18+
- **PostgreSQL**: 15+
- **OS**: Windows 10/11

### 8.2. テスト戦略

#### 8.2.1. テストレベル
- **ユニットテスト**: 個別機能のテスト
- **統合テスト**: コンポーネント間の連携テスト
- **E2Eテスト**: エンドツーエンドの動作テスト

#### 8.2.2. テストツール
- **Python**: pytest、pytest-asyncio
- **フロントエンド**: Jest、React Testing Library
- **E2E**: Playwright、Cypress

### 8.3. 運用・保守

#### 8.3.1. ログ管理
- **アプリケーションログ**: 構造化ログ
- **エラーログ**: エラー詳細・スタックトレース
- **パフォーマンスログ**: 実行時間・リソース使用量

#### 8.3.2. 監視・アラート
- **ヘルスチェック**: アプリケーション状態の監視
- **パフォーマンス監視**: 応答時間・スループット
- **エラー監視**: エラー発生率・種類

#### 8.3.3. バックアップ・復旧
- **データベース**: 定期的なバックアップ
- **設定ファイル**: 設定のバックアップ
- **復旧手順**: 障害時の復旧手順書

---

*このドキュメントは、AI秘書チーム・プラットフォーム（統合版）の技術仕様を提供するものである。* 