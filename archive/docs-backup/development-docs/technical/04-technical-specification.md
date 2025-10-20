# 技術仕様書：AI秘書チーム・プラットフォーム（統合版）

* **ドキュメントバージョン:** v1.0
* **作成日:** 2025年8月13日
* **目的:** AI秘書チーム・プラットフォームの統合版における技術的な実装仕様を定義する

---

## 1. 概要

### 1.1. ドキュメントの目的
本ドキュメントは、要件定義書と機能定義書で定義された機能を実現するための技術的な仕様を定義するものである。

### 1.2. 技術スタックの概要
- **バックエンド**: FastAPI + Python 3.12
- **フロントエンド**: React 18 + TypeScript + Vite
- **データベース**: PostgreSQL 16 + Redis 7
- **AI統合**: LangGraph + Zen MCP Server
- **知識管理**: Obsidian連携
- **配布方式**: インストーラー（PyInstaller等）

### 1.3. システム特性・前提条件

#### **設計レベル**
- **設計レベル**: ローカル・シングルユーザー級（エンタープライズ級・大規模システム対応は不要）
- **対象規模**: 1ユーザー、1万-10万レコード
- **機能範囲**: 基本機能に集中（高度な監査・セキュリティ・パフォーマンス最適化は不要）

#### **動作環境**
- **動作環境**: ローカルPC（Windows 10/11）での単独動作
- **同時接続**: 想定なし（シングルユーザー・ローカル環境）
- **配布方式**: 各自のPCで動作するハイブリッドアプリ（デスクトップ + Web技術）
- **カスタマイズ**: 各自のPCで独自にカスタマイズ可能

#### **技術制約**
- **ネットワーク**: LLM API使用時のインターネット接続のみ（ローカルネットワーク不要）
- **外部連携**: 外部システム連携なし（ローカル完結型）
- **データ処理**: 大規模データ処理・分散処理・クラスタリングは不要
- **パフォーマンス**: ローカル環境での動作に最適化（高負荷・高可用性は不要）

#### **運用・保守**
- **運用**: 開発者による基本運用で十分（24/7監視・専門運用チーム不要）
- **保守**: 基本的なメンテナンス・バックアップで十分
- **スケーラビリティ**: 将来的な機能拡張の準備は維持（段階的実装）
- **セキュリティ**: 基本的なセキュリティ対策で十分（行レベルセキュリティ等の複雑機能は不要）

#### **設計思想**
- **実用性優先**: 実装可能な機能から段階的に構築
- **品質重視**: 基本機能の確実な動作・保守性の向上
- **ローカル最適化**: ローカル環境での動作に最適化された設計
- **将来拡張準備**: 基本的な拡張性は維持（過剰設計は排除）

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
        AI_Collab["🤝 AI Collaboration Engine"]
    end

    subgraph Data Layer
        Postgres["🐘 PostgreSQL (Configs/Logs)"]
        Redis["🔴 Redis (Cache/Session)"]
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
    API_GW -- Routes to --> AI_Collab

    Secretary_A & Secretary_B & Secretary_C -- Uses --> LLM
    Secretary_A & Secretary_B & Secretary_C -- Queries --> Librarian_AI
    Librarian_AI -- Manages --> Obsidian
    Librarian_AI -- Searches --> Obsidian

    WF_Engine -- Manages --> Secretary_A & Secretary_B & Secretary_C
    WF_Engine -- Stores Data --> Postgres

    AI_Collab -- Coordinates --> Secretary_A & Secretary_B & Secretary_C
    AI_Collab -- Stores --> Postgres

    Postgres -- Stores --> Configs & Logs
    Redis -- Stores --> Cache & Session Data
    Obsidian -- Stores --> Knowledge & Notes
    File_System -- Stores --> Application Files
```

### 2.2. コンポーネント構成

#### 2.2.1. フロントエンド（React + TypeScript）
- **メインアプリケーション**: アプリケーションのメインコンポーネント
- **ペルソナ管理**: ペルソナ・チームの管理画面
- **チャット画面**: AI秘書との対話画面
- **タスク管理**: ワークフローの管理画面
- **設定画面**: 各種設定の管理画面
- **知識画面**: Obsidianの内容表示・検索画面
- **AI協議管理**: AI同士の議論の閲覧・管理画面
- **プラン承認**: AIの提案プランの承認ワークフロー画面

#### 2.2.2. バックエンド（FastAPI + Python 3.12）
- **API Gateway**: リクエストの振り分け・認証
- **ペルソナサービス**: ペルソナ・チームの管理
- **ワークフローサービス**: タスク・ワークフローの管理
- **Obsidian連携サービス**: Obsidianとの連携
- **AI連携サービス**: 外部AI APIとの連携
- **認証サービス**: ユーザー認証・権限管理
- **AI協議サービス**: AI同士の議論管理
- **プラン承認サービス**: 提案プランの承認ワークフロー

#### 2.2.3. データ層
- **PostgreSQL 16**: 設定・ログ・履歴データ・AI協議・プラン承認
- **Redis 7**: キャッシュ・セッション管理・一時データ
- **Obsidian**: 知識・ノート・テンプレート
- **ファイルシステム**: アプリケーションファイル・設定ファイル

---

## 3. 技術的実装詳細

### 3.1. Python 3.12対応

#### 3.1.1. 言語機能
- **型ヒント**: 必須（mypy対応）
- **非同期処理**: async/await（FastAPI対応）
- **データ検証**: Pydantic v2（最新機能対応）
- **パフォーマンス**: 3.11からの継続最適化

#### 3.1.2. 依存関係
```python
# requirements.txt
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
sqlalchemy>=2.0.0
alembic>=1.12.0
pydantic>=2.5.0
langgraph>=0.0.20
redis>=5.0.0
psycopg2-binary>=2.9.0
python-multipart>=0.0.6
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
```

### 3.2. フロントエンド技術

#### 3.2.1. React 18 + TypeScript
- **コンポーネント**: 関数コンポーネント + Hooks
- **状態管理**: Zustand（軽量・型安全）
- **データ取得**: React Query（TanStack Query）
- **ルーティング**: React Router v6
- **UIライブラリ**: カスタムコンポーネント + CSS Modules

#### 3.2.2. ビルド・開発環境
- **Vite**: 高速ビルド・HMR
- **ESLint + Prettier**: コード品質・フォーマット
- **TypeScript**: 厳密な型チェック
- **テスト**: Jest + React Testing Library

### 3.3. データベース技術

#### 3.3.1. PostgreSQL 16
- **バージョン**: 16（最新安定版）
- **エンコーディング**: UTF-8
- **ロケール**: C（標準）
- **接続プール**: SQLAlchemy + asyncpg
- **マイグレーション**: Alembic

#### 3.3.2. Redis 7
- **バージョン**: 7（最新安定版）
- **永続化**: AOF（Append Only File）
- **セッション管理**: ユーザーセッション・AI状態
- **キャッシュ**: 頻繁アクセスデータ・検索結果

### 3.4. AI統合技術

#### 3.4.1. LangGraph
- **ワークフロー管理**: AI秘書のタスク実行フロー
- **状態管理**: 複雑なAI対話の状態管理
- **エラーハンドリング**: 堅牢なエラー処理
- **拡張性**: 新しいAI機能の追加

#### 3.4.2. Zen MCP Server
- **AI API統合**: Gemini、GPT、Claude等
- **ツール統合**: 外部API・データベース・ファイル
- **セキュリティ**: API キー管理・アクセス制御

---

## 4. パフォーマンス要件

### 4.1. レスポンス時間
- **API応答**: 200ms以下（90%ile）
- **ページ読み込み**: 1秒以下（初回）
- **AI応答**: 3秒以下（標準的な質問）
- **検索応答**: 500ms以下（Obsidian検索）

### 4.2. スループット
- **同時ユーザー**: 100ユーザー
- **API要求**: 1000 req/min
- **AI対話**: 100対話/min
- **ファイル処理**: 100ファイル/min

### 4.3. リソース使用量
- **メモリ**: 2GB以下（アプリケーション）
- **CPU**: 20%以下（通常時）
- **ディスク**: 1GB以下（ログ・キャッシュ）
- **ネットワーク**: 10MB/min以下

---

## 5. セキュリティ要件

### 5.1. 認証・認可
- **JWT認証**: トークンベース認証
- **パスワード**: bcrypt（強力なハッシュ）
- **セッション管理**: Redis + セキュアクッキー
- **権限管理**: ロールベースアクセス制御

### 5.2. データ保護
- **暗号化**: TLS 1.3（通信）、AES-256（保存）
- **入力検証**: Pydantic + カスタムバリデーター
- **SQLインジェクション**: パラメータ化クエリ
- **XSS対策**: React の自動エスケープ

### 5.3. API セキュリティ
- **レート制限**: 100 req/min（ユーザー単位）
- **CORS**: 適切なオリジン制限
- **ヘッダーセキュリティ**: セキュリティヘッダー設定
- **ログ監査**: セキュリティイベントの記録

---

## 6. 開発・テスト・運用技術

### 6.1. 開発環境
- **Docker**: 統一された開発環境
- **Make**: 環境管理コマンド
- **環境別設定**: 開発・テスト・本番環境の分離
- **依存関係管理**: requirements.txt、package.json

### 6.2. テスト戦略
- **ユニットテスト**: pytest（Python）、Jest（TypeScript）
- **統合テスト**: API エンドポイント・データベース
- **E2Eテスト**: Playwright（ブラウザ自動化）
- **パフォーマンステスト**: Locust（負荷テスト）

### 6.3. 運用・監視
- **ログ管理**: 構造化ログ（JSON形式）
- **メトリクス**: Prometheus + Grafana
- **アラート**: エラー率・レスポンス時間・リソース使用量
- **バックアップ**: データベース・設定ファイルの定期バックアップ

---

## 7. 配布・インストール技術

### 7.1. パッケージング
- **Python**: PyInstaller（単一実行ファイル）
- **インストーラー**: NSIS（Windows）、DMG（macOS）、AppImage（Linux）
- **依存関係**: 必要なライブラリの自動バンドル
- **設定ファイル**: 環境別設定の自動選択

### 7.2. インストール要件
- **OS**: Windows 10+、macOS 10.15+、Ubuntu 18.04+
- **Python**: 3.12（自動インストール）
- **PostgreSQL**: 16（自動インストール・設定）
- **Redis**: 7（自動インストール・設定）

### 7.3. 初期設定
- **環境チェック**: 必要なソフトウェアの自動検出
- **データベース初期化**: テーブル作成・初期データ投入
- **設定ファイル**: 環境に応じた自動設定
- **サービス起動**: 必要なサービスの自動起動

---

## 8. 将来拡張性

### 8.1. AI機能拡張
- **新しいAIモデル**: 簡単な追加・設定
- **カスタムペルソナ**: ユーザー定義ペルソナ
- **高度なワークフロー**: 複雑なタスク自動化
- **マルチモーダル**: 画像・音声・動画対応

### 8.2. 統合拡張
- **外部システム**: CRM、ERP、プロジェクト管理ツール
- **API連携**: Webhook、REST API、GraphQL
- **データ連携**: データベース、ファイル、クラウドストレージ
- **通知システム**: メール、Slack、Teams

### 8.3. スケーラビリティ
- **水平スケーリング**: 複数インスタンス対応
- **負荷分散**: ロードバランサー対応
- **クラスタリング**: 高可用性構成
- **マイクロサービス**: 機能別サービス分割

---

## 9. 技術的制約・リスク

### 9.1. 制約事項
- **Python 3.12**: ライブラリ互換性の確認が必要
- **PostgreSQL**: データベース管理者の知識が必要
- **Obsidian**: ユーザーのObsidian知識が必要
- **AI API**: 外部APIの利用制限・コスト

### 9.2. リスク要因
- **AI API制限**: レート制限・利用制限
- **データセキュリティ**: 機密情報の取り扱い
- **パフォーマンス**: 大量データ処理時の性能劣化
- **依存関係**: 外部ライブラリの脆弱性

### 9.3. 対策
- **AI API**: 複数プロバイダーの利用・フォールバック
- **セキュリティ**: 定期的なセキュリティ監査・更新
- **パフォーマンス**: キャッシュ戦略・クエリ最適化
- **依存関係**: 定期的な更新・脆弱性チェック

---

**作成日**: 2025-08-13  
**作成者**: AI Assistant  
**バージョン**: 1.0  
**次回更新予定**: 2025-09-13 