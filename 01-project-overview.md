# AI秘書チーム・プラットフォーム - プロジェクト概要

**作成日**: 2025年8月17日  
**作成者**: 中野五月（Claude Code）  
**バージョン**: 1.0

## 🎯 プロジェクト概要

### プロジェクト名
AI秘書チーム・プラットフォーム（統合版）

### 目的
統合型AI秘書チーム・プラットフォーム - 複数の専門性を持つAIアシスタントをチームとして編成し、ユーザーが「司令塔」としてタスクを委任・管理できるパーソナルオートメーションプラットフォーム。

### コンセプト
個人や組織に散在する情報を一元的に活用し、定型的なリサーチ、レポート作成、資料作成、SNS投稿などの知的労働を自動化・半自動化することで、ユーザーの生産性を飛躍的に向上させる。

## 🏗️ 技術スタック

### フロントエンド
- **React 18.2.0** + **TypeScript**
- **Vite** (ビルドツール)
- **Tailwind CSS** (スタイリング)
- **Shadcn UI** (コンポーネントライブラリ)
- **Zustand** (状態管理)
- **React Query** (データフェッチング)

### バックエンド
- **Python 3.12**
- **FastAPI 0.104.1** (Webフレームワーク)
- **LangGraph** (AIエージェントフレームワーク)
- **Google Gemini** (LLM)
- **PostgreSQL 16** (データベース)
- **Redis 7** (キャッシュ・セッション管理)

### インフラ
- **Docker** + **Docker Compose**
- **PostgreSQL 16** (pgvector拡張対応)
- **Redis 7**

## 📁 プロジェクト構造

```
ai-secretary-team/
├── frontend/                    # Reactフロントエンド
│   ├── src/
│   │   ├── components/         # UIコンポーネント
│   │   ├── pages/             # ページコンポーネント
│   │   ├── api/               # APIクライアント
│   │   └── types/             # TypeScript型定義
│   ├── package.json           # Node依存関係
│   └── Dockerfile*            # Docker設定
├── backend/                     # Pythonバックエンド
│   ├── app/
│   │   ├── api/               # APIエンドポイント
│   │   ├── models/            # データベースモデル
│   │   ├── schemas/           # Pydanticスキーマ
│   │   └── services/          # ビジネスロジック
│   ├── requirements.txt       # Python依存関係
│   └── Dockerfile*            # Docker設定
├── database/                    # データベース関連
│   ├── init/                  # 初期化スクリプト
│   └── pgadmin/               # pgAdmin設定
├── scripts/                     # 管理スクリプト
│   └── setup-env.sh           # 環境設定スクリプト
├── docs/                       # ドキュメント
│   ├── 01-foundation/         # 基礎設計
│   ├── 02-implementation/     # 実装関連
│   └── 03-github-original/    # GitHub由来文書
├── tools/                      # 開発ツール
│   ├── cipher-mcp/            # Cipher記憶システム
│   └── studio-agents/         # Contains Studioエージェント
├── docker-compose*.yml         # Docker Compose設定
├── Makefile                    # 管理コマンド
└── build.sh                    # ビルドスクリプト
```

## 🚀 主要機能

### Phase 1 (MVP)
- [x] 基本的なチャット機能（テキスト入力/出力）
- [x] 単一のAI秘書との対話
- [x] 基本的なファイルアップロード機能
- [x] シンプルなUI

### Phase 2 (開発中)
- [ ] 複数AI秘書の切り替え機能
- [ ] 音声入力/出力機能
- [ ] 基本的なワークフロー機能

### Phase 3 (計画中)
- [ ] 外部API連携（Google Drive、SNS等）
- [ ] 高度なワークフロー機能
- [ ] ベクトルDBによる知識管理

## 🔐 API管理方法

### セキュリティ方針
- **テスト環境でのみAPIキーを使用**
- **機密情報はGitにコミットしない**
- **環境別の設定ファイル管理**
- **GitHub Secretsを使用した本番環境管理**

### 推奨する管理方法

#### 1. 環境設定の自動化
```bash
# 開発環境の設定（推奨）
make setup-env

# タブレット環境の設定
make setup-env-tablet

# 本番環境の設定
make setup-env-prod
```

#### 2. APIキーの設定
```bash
# .envファイルを編集
nano .env

# 以下の行を編集
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

## 🐳 Docker環境でのセットアップ

### 前提条件
- Docker と Docker Compose がインストールされていること
- Google Gemini API キーを取得済みであること

### 1. 環境変数の設定

```bash
# 自動設定（推奨）
make setup-env

# タブレット環境の設定
make setup-env-tablet

# または手動設定
cp .env.development .env
# .envファイルを編集してGEMINI_API_KEYを設定
```

### 2. 環境別の開発環境起動

#### デスクトップVM用（推奨）
```bash
# デスクトップVM用開発環境を起動
make dev-desktop

# または個別にビルドして起動
make build-desktop
make up
```

#### WSL用（軽量）
```bash
# WSL用開発環境を起動
make dev-wsl

# または個別にビルドして起動
make build-wsl
docker-compose -f docker-compose.common.yml -f docker-compose.wsl.yml up -d
```

#### タブレット用（共有対応）
```bash
# タブレット用開発環境を起動
make dev-tablet

# または個別にビルドして起動
make build-tablet
docker-compose -f docker-compose.common.yml -f docker-compose.tablet.yml up -d
```

### 3. アクセスURL

起動後、以下のURLでアクセスできます：

- **フロントエンド**: http://localhost:3000
- **開発フロントエンド**: http://localhost:5173
- **バックエンドAPI**: http://localhost:8000
- **pgAdmin**: http://localhost:5050
  - メール: admin@ai-secretary.local
  - パスワード: admin123

#### タブレットからのアクセス
- **フロントエンド**: http://192.168.1.100:3000
- **バックエンドAPI**: http://192.168.1.100:8000

## 📋 開発ロードマップ

### 現在のフェーズ: Phase 1 MVP
- [ ] 基本的なチャットUIの実装
- [ ] Gemini APIとの連携
- [ ] ファイルアップロード機能
- [ ] レスポンシブデザイン

### 次のフェーズ: Phase 2
- [ ] 複数AI秘書の実装
- [ ] 音声機能の追加
- [ ] ワークフロー機能の基本実装

## 🤝 コントリビューション

このプロジェクトは開発中です。フィードバックや提案を歓迎します。

### 開発フロー
1. フォークしてブランチを作成
2. 機能を実装
3. テストを実行
4. プルリクエストを作成

### セキュリティ
- APIキーは絶対にコードにコミットしないでください
- セキュリティ関連のバグは直接報告してください

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。
