# 🏗️ AI秘書チーム・プラットフォーム - プロジェクト構造

**最終更新**: 2025年9月17日
**作成者**: 中野五月（Claude Code）

## ⚠️ プロジェクトステータス

**現状**: バックエンドとフロントエンドのMVPが稼働しており、Phase 2機能を段階的に開発中です。

- ✅ **バックエンド（FastAPI）**: `app/` 配下にAPIルーター、DB接続、Pydanticスキーマ、サービス層を実装。`/api/v1/assistants` 経由でAI秘書のCRUD操作が可能。
- ✅ **フロントエンド（React + Vite）**: `src/` にページ、UIコンポーネント、APIクライアント、状態管理を配置。チャットUIと基本操作フローが整備済み。
- ✅ **開発環境**: Docker Compose、Makefile、共通スクリプトでローカル/デスクトップ/WSL/タブレット向け環境を提供。
- 🚧 **Phase 2 進行中**: マルチAI秘書切り替え、音声I/O、拡張ワークフローの整備を推進中。
- ⏳ **今後の重点項目**: 認証・ユーザー管理、LangGraphベースの高度なオーケストレーション、ベクトルDB統合。

**進捗目安**（Phase 2完了を100%とした場合）

| 領域 | 進捗率 | 補足 |
| --- | --- | --- |
| バックエンド | 約60% | 核となるエンドポイントとDBスキーマが揃い、認証/権限・高度AI連携が未着手。 |
| フロントエンド | 約55% | チャット画面・レイアウトは実装済み。マルチエージェントUIと音声操作が未実装。 |
| 全体 | 約50% | READMEが示すPhase 1完了、Phase 2開発中の状態と整合。 |

**直近の残タスク**
1. FastAPIベースの認証・ユーザー管理機構の導入
2. フロントエンドでのAI秘書切替とマルチタブUIの実装
3. LangGraphワークフローの接続とエージェント協調ロジックの実装
4. ベクトルDB（pgvector）連携と知識検索APIの公開

## 📂 ディレクトリ構造

```
ai-secretary-team/                    # プロジェクトルート
│
├── 📋 管理・運用層
│   ├── work-logs/                   # 作業記録（時系列）
│   ├── SESSION_HANDOVER_*.md        # セッション引継ぎドキュメント
│   ├── PROJECT_COMPLETE_OVERVIEW*.md # 進捗ハイライト
│   ├── README.md                    # プロジェクト概要
│   └── CLAUDE.md                    # AI行動規範
│
├── 💻 実装層（GitHubと同期）
│   ├── backend/                     # FastAPIバックエンド
│   │   ├── app/                     # API・設定・ドメインロジック
│   │   │   ├── api/v1/              # バージョン管理されたルーター
│   │   │   ├── core/                # 設定・DB接続・セキュリティ
│   │   │   ├── models/              # SQLAlchemyモデル
│   │   │   ├── schemas/             # Pydanticスキーマ
│   │   │   └── services/            # ビジネスロジック
│   │   ├── alembic/                 # マイグレーション設定
│   │   ├── scripts/                 # メンテナンススクリプト
│   │   ├── database/                # DBシード・初期化SQL
│   │   └── Dockerfile*              # 環境別Docker設定
│   ├── frontend/                    # React + Viteフロントエンド
│   │   ├── src/                     # アプリ本体
│   │   │   ├── pages/               # 画面コンポーネント
│   │   │   ├── components/          # 再利用UI
│   │   │   ├── api/                 # APIクライアント
│   │   │   ├── types/               # 型定義
│   │   │   └── assets/              # 画像・スタイル
│   │   ├── public/                  # 静的アセット（ビルド出力対象）
│   │   └── Dockerfile*              # 環境別Docker設定
│   ├── database/                    # 共有DBリソース（Docker起動時に使用）
│   │   └── init/                    # PostgreSQL初期化スクリプト
│   ├── scripts/                     # セットアップ・メンテナンススクリプト
│   ├── .github/workflows/           # CI/CD設定
│   ├── docker-compose*.yml          # Docker Compose構成
│   ├── Makefile                     # ビルド・起動コマンド
│   └── build.sh                     # 環境別ビルドスクリプト
│
├── 📚 ドキュメント層
│   ├── docs/                        # 詳細設計・実装ガイド
│   │   ├── 01-foundation/           # 基礎設計フェーズ
│   │   ├── 02-implementation/       # 実装ガイド・テスト計画
│   │   ├── 03-github-original/      # 参考資料・仕様書
│   │   ├── 04-templates/            # 標準テンプレート
│   │   └── 05-archives/             # アーカイブ
│   └── docs-backup/                 # ドキュメントバックアップ
│
└── 🛠️ ツール層
    └── tools/
        ├── cipher-mcp/              # Cipher記憶システム
        │   ├── src/                 # ソースコード
        │   ├── data/                # データストレージ
        │   ├── memAgent/            # メモリエージェント
        │   └── package.json         # 依存関係
        └── studio-agents/           # Contains Studioエージェント
            ├── engineering/         # 開発系
            ├── product/             # プロダクト系
            ├── marketing/           # マーケティング系
            ├── design/              # デザイン系
            ├── project-management/  # PM系
            ├── studio-operations/   # 運営系
            ├── testing/             # テスト系
            ├── bonus/               # ボーナス
            └── README.md            # エージェント概要
```

### backend/app/ の主構成

- `api/v1/` - FastAPIルーターとエンドポイント群。`assistants.py` でAI秘書CRUDを提供し、`routing.py`が共通処理を担う。
- `core/` - 設定値（環境変数）、DBセッション管理、CORSなどアプリ基盤設定を集約。
- `models/` - SQLAlchemyモデル定義。`models.py` にユーザー・AI秘書などの永続化構造を実装。
- `schemas/` - Pydanticスキーマ群。リクエスト/レスポンス契約を型安全に定義。
- `services/` - ルーティングやオーケストレーションなどのドメインロジックを段階的に分離中。
- `main.py` - アプリケーションエントリーポイント。CORSやライフサイクル管理を統括。

### frontend/src/ の主構成

- `pages/` - チャット体験や設定画面など、ルーティング対象の画面コンポーネントを格納。
- `components/` - レイアウト、フォーム、チャットメッセージなど再利用可能なUI部品を集約。
- `api/` - AxiosベースのAPIクライアントと型安全なエンドポイント呼び出しラッパー。
- `types/` - サーバーとのインターフェースに合わせたTypeScript型定義。
- `assets/` - 画像やスタイルシートなど静的リソース。
- `main.tsx` / `App.tsx` - アプリケーションのエントリーポイントとルーティング設定。

## 🎯 各層の役割

### 1. 管理・運用層
- **目的**: プロジェクトの状況把握と引継ぎ
- **対象**: 新規参加者、AI、プロジェクト管理者
- **特徴**: ルートレベルで即座にアクセス可能

### 2. 実装層
- **目的**: アプリケーションの実装コード
- **対象**: 開発者、CI/CD
- **特徴**: バックエンド/フロントエンドの実装と自動化スクリプトを集約

### 3. ドキュメント層
- **目的**: 設計書と実装ガイド
- **対象**: 開発者、設計者、レビュアー
- **特徴**: フェーズ別に整理された包括的文書

### 4. ツール層
- **目的**: 開発支援ツールとエージェント
- **対象**: AI開発者、自動化ツール
- **特徴**: プロジェクト本体から独立した拡張機能

## 🚀 クイックスタート

### 開発環境セットアップ
```bash
# 環境変数設定
cp .env.example .env
# 編集して必要な値を設定

# Docker環境起動
make dev-desktop

# フロントエンド開発サーバー
http://localhost:5173

# バックエンドAPI
http://localhost:8000
```

### Git操作
```bash
# 変更をコミット
git add .
git commit -m "feat: プロジェクト構造を最適化"

# GitHubへプッシュ
git push origin main
```

## 📖 重要ドキュメント

1. **CLAUDE.md** - AI開発者の行動規範
2. **work-logs/** - 日々の作業記録
3. **docs/01-foundation/** - 基礎設計書
4. **docs/02-implementation/** - 実装ガイド
5. **README.md / README_v2.md** - 進捗および利用方法の最新概要

## 🔄 構造変更履歴

### 2025年8月17日 - 大規模再構築
- ai-secretary-team-main/の内容をルートに移動
- agents/をtools/studio-agents/に再配置
- GitHubドキュメントをdocs/03-github-original/に統合
- 作業ログと引継ぎ資料をルートレベルに配置
- 不要なディレクトリとバックアップを削除

## 更新履歴

- **2025年9月17日** - バックエンド/フロントエンド実装状況を反映し、ステータス・ディレクトリ説明・残タスクを更新。

## 📝 注意事項

- **バックアップ**: docs-backup/とai-secretary-team-main-docs-backup/は一時保存
- **Git同期**: backend/, frontend/, database/はGitHubと同期
- **機密情報**: .envファイルは絶対にコミットしない
- **エージェント**: tools/studio-agents/にContains Studio定義

## 🤝 貢献ガイドライン

1. 新機能はfeatureブランチで開発
2. ドキュメントは同時に更新
3. work-logs/に作業記録を残す
4. CLAUDE.mdの規範に従う

---

*このドキュメントは、プロジェクト構造の最適化作業（2025年8月17日）を起点に作成され、2025年9月17日に実装状況を反映する更新を行いました。*
