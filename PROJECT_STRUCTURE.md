# 🏗️ AI秘書チーム・プラットフォーム - プロジェクト構造

**最終更新**: 2025年8月17日
**作成者**: 中野五月（Claude Code）

## ⚠️ プロジェクトステータス

**重要**: このプロジェクトは設計・計画段階が完了し、実装開始前の状態です。
- ✅ 詳細設計書完備
- ✅ インフラ設定準備済み
- ❌ **ソースコード未実装**

## 📂 ディレクトリ構造

```
ai-secretary-team/                    # プロジェクトルート
│
├── 📋 管理・運用層
│   ├── work-logs/                   # 作業記録（時系列）
│   ├── session-handover/            # セッション引継ぎ
│   ├── CLAUDE.md                    # AI行動規範
│   ├── SESSION_HANDOVER_*.md        # 引継ぎドキュメント
│   └── README.md                    # プロジェクト概要
│
├── 💻 実装層（GitHubと同期）
│   ├── backend/                     # FastAPIバックエンド
│   │   ├── Dockerfile*              # Docker設定
│   │   ├── requirements.txt         # Python依存関係
│   │   └── database/                # DB初期化SQL
│   ├── frontend/                    # Reactフロントエンド
│   │   ├── Dockerfile*              # Docker設定
│   │   └── package.json             # Node依存関係
│   ├── database/                    # データベース設定
│   │   └── init/                    # 初期化スクリプト
│   ├── scripts/                     # セットアップスクリプト
│   ├── ai_secretary_core/           # AIコアモジュール
│   │   ├── collaboration/           # 協調機能
│   │   ├── knowledge_management/    # 知識管理
│   │   ├── personas/                # ペルソナ定義
│   │   └── workflows/               # ワークフロー
│   ├── docker-compose*.yml          # Docker Compose設定
│   ├── Makefile                     # ビルド自動化
│   └── build.sh                     # ビルドスクリプト
│
├── 📚 ドキュメント層
│   └── docs/
│       ├── 01-foundation/           # 基礎設計フェーズ
│       │   ├── requirements/        # 要件定義
│       │   ├── database/            # DB設計
│       │   ├── technical/           # 技術設計
│       │   └── ui-ux/               # UI/UX設計
│       ├── 02-implementation/       # 実装フェーズ
│       │   ├── api/                 # API仕様
│       │   ├── guides/              # 実装ガイド
│       │   ├── testing/             # テスト戦略
│       │   ├── deployment/          # デプロイ手順
│       │   ├── integration/         # 統合戦略
│       │   └── maintenance/         # 保守手順
│       ├── 03-github-original/      # GitHub由来文書
│       │   ├── README.md            # プロジェクト概要
│       │   ├── AIエージェントチーム_仕様.txt
│       │   ├── database_design.md   # DB設計
│       │   ├── table_columns.md     # カラム定義
│       │   ├── table_definitions.md # テーブル定義
│       │   └── table_overview.md    # 概要
│       ├── 04-templates/            # テンプレート
│       │   ├── CHANGELOG_TEMPLATE.md
│       │   ├── HANDOVER_DOCUMENT.md
│       │   └── QUALITY_CHECKLIST.md
│       ├── 05-archives/             # アーカイブ
│       └── README.md                # ナビゲーション
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

## 🎯 各層の役割

### 1. 管理・運用層
- **目的**: プロジェクトの状況把握と引継ぎ
- **対象**: 新規参加者、AI、プロジェクト管理者
- **特徴**: ルートレベルで即座にアクセス可能

### 2. 実装層
- **目的**: アプリケーションの実装コード
- **対象**: 開発者、CI/CD
- **特徴**: GitHubリポジトリと完全同期

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

## 🔄 構造変更履歴

### 2025年8月17日 - 大規模再構築
- ai-secretary-team-main/の内容をルートに移動
- agents/をtools/studio-agents/に再配置
- GitHubドキュメントをdocs/03-github-original/に統合
- 作業ログと引継ぎ資料をルートレベルに配置
- 不要なディレクトリとバックアップを削除

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

*このドキュメントは、プロジェクト構造の最適化作業（2025年8月17日）の一環として作成されました。*