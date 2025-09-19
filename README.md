# AI秘書チーム・プラットフォーム

統合型AI秘書チーム・プラットフォーム - 複数の専門性を持つAIアシスタントをチームとして編成し、ユーザーが「司令塔」としてタスクを委任・管理できるパーソナルオートメーションプラットフォーム。

## 🎯 プロジェクト概要

本プロジェクトは、個人や組織に散在する情報を一元的に活用し、定型的なリサーチ、レポート作成、資料作成、SNS投稿などの知的労働を自動化・半自動化することで、ユーザーの生産性を飛躍的に向上させることを目的としています。

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

## 🏗️ 技術スタック

### フロントエンド
- **React 18** + **TypeScript**
- **Vite** (ビルドツール)
- **Tailwind CSS** (スタイリング)
- **Shadcn UI** (コンポーネントライブラリ)
- **Zustand** (状態管理)

### バックエンド
- **Python 3.11+**
- **FastAPI** (Webフレームワーク)
- **LangGraph** (AIエージェントフレームワーク)
- **Google Gemini** (LLM)
- **PostgreSQL** (データベース)
- **Redis** (キャッシュ・セッション管理)

### インフラ
- **Docker** + **Docker Compose**
- **PostgreSQL 16** (pgvector拡張対応)
- **Redis 7**

## 📁 プロジェクト構造

```
ai-secretary-team/
├── frontend/                    # Reactフロントエンド
│   ├── Dockerfile.common       # 共通Dockerfile
│   ├── Dockerfile.desktop      # デスクトップVM用
│   ├── Dockerfile.wsl          # WSL用
│   ├── Dockerfile.production   # 本番環境用
│   └── Dockerfile.dev          # 開発用
├── backend/                     # Pythonバックエンド
│   ├── Dockerfile.common       # 共通Dockerfile
│   ├── Dockerfile.desktop      # デスクトップVM用
│   ├── Dockerfile.wsl          # WSL用
│   ├── Dockerfile.production   # 本番環境用
│   └── requirements.txt        # Python依存関係
├── database/                    # データベース関連
│   ├── init/                   # 初期化スクリプト
│   └── pgadmin/                # pgAdmin設定
├── scripts/                     # 管理スクリプト
│   └── setup-env.sh            # 環境設定スクリプト
├── .github/                     # GitHub Actions
│   └── workflows/              # CI/CDワークフロー
├── docs/                       # ドキュメント
├── reference-repo/              # 参考リポジトリ
├── docker-compose.common.yml   # 共通設定（DB、Redis等）
├── docker-compose.desktop.yml  # デスクトップVM用設定
├── docker-compose.wsl.yml      # WSL用設定
├── docker-compose.tablet.yml   # タブレット用設定
├── build.sh                    # 環境別ビルドスクリプト
├── Makefile                    # 管理コマンド
├── .env.example                # 環境変数サンプル
├── .env.development            # 開発環境設定
├── .env.production             # 本番環境設定
├── .env.tablet                 # タブレット環境設定
├── .gitignore                  # Git除外設定
└── README.md                   # このファイル
```

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

#### 3. セキュリティチェック
```bash
# APIキーが正しく設定されているか確認
grep GEMINI_API_KEY .env
```

### 環境別の設定ファイル

| ファイル | 用途 | 説明 |
|---------|------|------|
| `.env.example` | テンプレート | 設定項目の例（APIキーなし） |
| `.env.development` | 開発環境 | 開発用設定（APIキー設定済み） |
| `.env.tablet` | タブレット環境 | タブレット用設定（軽量・タッチ対応） |
| `.env.production` | 本番環境 | 本番用設定（環境変数参照） |
| `.env` | 実行時設定 | 実際に使用される設定ファイル |

### GitHub連携時の注意事項
- `.env`ファイルは`.gitignore`に含まれており、Gitにコミットされません
- APIキーは必ず環境変数ファイルで管理し、コードに直接記述しないでください
- 本番環境では、GitHub Secretsを使用してAPIキーを管理してください
- タブレット共有時は、ネットワークセキュリティに注意してください

## 🐳 Docker環境でのセットアップ

### 前提条件
- Docker と Docker Compose がインストールされていること
- Google Gemini API キーを取得済みであること
- PostgreSQL 用の pgvector 拡張が利用可能であること
  - 本リポジトリの `docker-compose.common.yml` では `pgvector/pgvector:pg16` イメージを使用し拡張を自動で有効化
  - 既存のデータベースを利用する場合は `CREATE EXTENSION IF NOT EXISTS vector;` を実行して拡張を有効化してください

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

#### 全環境用
```bash
# 全環境用イメージをビルド
make build

# デフォルト環境（デスクトップVM用）を起動
make dev
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

### 4. 環境別の特徴

#### デスクトップVM用
- **リソース**: メモリ2GB、CPU1.0コア
- **機能**: デバッグモード、開発ツール、詳細ログ
- **用途**: メイン開発環境

#### WSL用
- **リソース**: メモリ1GB、CPU0.5コア
- **機能**: 軽量設定、最小限のツール
- **用途**: タブレットでの開発・テスト

#### タブレット用
- **リソース**: メモリ1GB、CPU0.5コア
- **機能**: 軽量設定、タッチ対応、ネットワーク共有
- **用途**: タブレットでの使用・共有

### 5. 便利なコマンド

```bash
# ヘルプ表示
make help

# 環境設定
make setup-env      # 開発環境設定
make setup-env-dev  # 開発環境設定
make setup-env-prod # 本番環境設定
make setup-env-tablet # タブレット環境設定

# ビルド関連
make build-common    # 共通イメージのみ
make build-desktop   # デスクトップVM用
make build-wsl       # WSL用
make build-tablet    # タブレット用

# 環境別起動
make dev-desktop     # デスクトップVM用
make dev-wsl         # WSL用
make dev-tablet      # タブレット用

# サービスの状態確認
make status

# ログの表示
make logs            # デフォルト環境
make logs-desktop    # デスクトップVM用
make logs-wsl        # WSL用
make logs-tablet     # タブレット用

# 特定のサービスのログ
make logs-backend
make logs-frontend
make logs-postgres

# コンテナのシェルに接続
make backend-shell
make frontend-shell
make db-shell

# データベースのリセット
make db-reset

# 全サービスを停止
make down

# クリーンアップ（コンテナとボリュームを削除）
make clean
```

## 🌐 GitHub連携とCI/CD

### GitHub Actions設定
プロジェクトには以下のCI/CDパイプラインが含まれています：

1. **テスト実行**: プルリクエスト時に自動テスト
2. **Dockerイメージビルド**: メインブランチにマージ時に自動ビルド
3. **コンテナレジストリプッシュ**: GitHub Container Registryに自動プッシュ

### GitHub Secrets設定
本番環境では以下のSecretsを設定してください：

- `GEMINI_API_KEY`: Google Gemini APIキー
- `DATABASE_URL`: 本番データベースURL
- `REDIS_URL`: 本番Redis URL
- `SECRET_KEY`: アプリケーションシークレットキー
- `JWT_SECRET_KEY`: JWT署名用シークレットキー

### デプロイメント
```bash
# ローカルでのテスト
make test

# GitHubにプッシュ（自動デプロイ）
git add .
git commit -m "Update feature"
git push origin main
```

## 📱 タブレット共有設定

### ネットワーク設定
タブレットからアクセスする場合：

1. **IPアドレスの確認**
   ```bash
   # ホストのIPアドレスを確認
   ip addr show
   ```

2. **ファイアウォール設定**
   ```bash
   # 必要なポートを開放
   sudo ufw allow 3000
   sudo ufw allow 8000
   sudo ufw allow 5173
   ```

3. **CORS設定の調整**
   `.env.tablet`ファイルでCORS設定を調整：
   ```
   CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://192.168.1.100:3000
   ```

### タブレット最適化
- **タッチ操作**: タッチフレンドリーなUI
- **軽量化**: メモリ使用量を最小限に抑制
- **レスポンシブ**: タブレット画面に最適化
- **オフライン対応**: 基本的な機能はオフラインでも動作

## 🛠️ 手動セットアップ（Docker不使用）

### 前提条件
- Node.js 18+ と npm
- Python 3.11+
- PostgreSQL 16+ (pgvector拡張対応)
- Redis 7+
- Google Gemini API キー

#### pgvector拡張のインストール

PostgreSQL を手動でセットアップする場合は、pgvector 拡張をインストールした上で次のコマンドを実行してください:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Alembic マイグレーションは拡張が有効であることを前提に実行されます。

### 1. 環境変数の設定

```bash
# バックエンドの環境変数設定
cd backend
cp .env.example .env
# .envファイルを編集してGEMINI_API_KEYを設定
```

### 2. 依存関係のインストール

```bash
# バックエンド
cd backend
pip install -e .

# フロントエンド
cd frontend
npm install
```

### 3. 開発サーバーの起動

```bash
# バックエンド
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# フロントエンド
cd frontend
npm run dev
```

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

## 🔧 トラブルシューティング

### よくある問題

1. **APIキーが設定されていない場合**
   ```bash
   # 環境設定を実行
   make setup-env
   
   # APIキーが正しく設定されているか確認
   grep GEMINI_API_KEY .env
   ```

2. **ポートが既に使用されている場合**
   ```bash
   # 使用中のポートを確認
   lsof -i :8000
   lsof -i :3000
   lsof -i :5173
   
   # 必要に応じてプロセスを停止
   kill -9 <PID>
   ```

3. **Dockerイメージのビルドエラー**
   ```bash
   # キャッシュをクリアして再ビルド
   docker-compose build --no-cache
   ```

4. **データベース接続エラー**
   ```bash
   # データベースをリセット
   make db-reset
   ```

5. **環境変数が読み込まれない**
   ```bash
   # .envファイルが正しく配置されているか確認
   ls -la .env
   
   # 環境設定を再実行
   make setup-env
   ```

6. **WSL環境でのパフォーマンス問題**
   ```bash
   # WSL用の軽量設定を使用
   make dev-wsl
   ```

7. **タブレットからのアクセスエラー**
   ```bash
   # ネットワーク設定を確認
   ip addr show
   
   # ファイアウォール設定を確認
   sudo ufw status
   
   # タブレット用環境を起動
   make dev-tablet
   ```

## 🗒️ 更新履歴

- **2025-09-15**: PostgreSQL に pgvector 拡張を導入し、関連ドキュメントを更新

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

## Environment files policy
- 機密を含む `.env*` は **コミット禁止**。Gitに残すのは `*.example` のみ。
- ローカルは `make setup-env` で `.env` を生成して使う（各自端末のみ保持）。
- CI/本番は **GitHub Secrets や環境変数**で注入し、ファイルは置かない。
- フロント側は `VITE_` 変数のみ（=公開情報）。秘密はバックエンドに置く。
## Quick Checks

- Smoke (API):
  - `docker compose -f docker-compose.yml up -d --build postgres redis backend`
  - `MSYS_NO_PATHCONV=1 docker compose -f docker-compose.yml exec backend sh -lc 'cd /app && ./scripts/smoke.sh'`

- E2E (Playwright):
  - CI 同等（専用ネットワークで実行）:
    - `docker compose -f docker-compose.yml up -d --build postgres redis backend frontend`
    - `docker compose -f docker-compose.ci.yml build e2e`
    - `docker compose -f docker-compose.ci.yml run --rm --no-deps e2e`
  - ローカル既存スタックのネットワークを再利用（より実稼働に近い）:
    - `docker compose -f docker-compose.yml up -d postgres redis backend frontend`
    - `docker compose -f docker-compose.ci.yml -f docker-compose.e2e.local.yml build e2e`
    - `docker compose -f docker-compose.ci.yml -f docker-compose.e2e.local.yml run --rm --no-deps e2e`

Notes:
- Alembic runs at startup via `/app/entrypoint.sh` and will stop the container on failure.
- Git Bash users: prefer the `MSYS_NO_PATHCONV=1` prefix when exec-ing absolute paths.
