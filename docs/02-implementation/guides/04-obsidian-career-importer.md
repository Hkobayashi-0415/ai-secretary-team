# Obsidian 連携キャリアインポータ（Phase 2 器だけの範囲）

## 目的と範囲
- Obsidian をキャリア情報のマスターデータベースにするための “ツール枠” を `tools/career_profile_importer/` に追加する。
- Phase 2 ではチャット基盤を優先するため、**スケルトン＋設定雛形＋CLIインターフェース** までを実装範囲とする（AI呼び出しは Gemini 固定）。
- 将来（Phase 3+）は OpenAI/Claude 追加や backend からの統合を想定し、AIModelClient 抽象を前提とした設計にする。

## ディレクトリ構成（予定）
```
tools/
  career_profile_importer/
    __init__.py
    config.py            # config.toml を読み込む設定ラッパー
    ai_client.py         # AIModelClient 抽象 + Gemini 実装
    parser_llm.py        # 入力txt/md -> LLMで構造化JSONに変換
    markdown_builder.py  # JSON -> Obsidian向けMarkdown生成
    cli.py               # CLIエントリポイント（デフォルト設定 + 引数上書き）
    config.toml.sample   # Vault/サブディレクトリ/モデル設定の雛形
```

## Vault とデフォルト設定（暫定）
- キャリア用 Vault（暫定パス）: `C:\Users\sugar\OneDrive\デスクトップ\Obsidian`
- Vault はカテゴリ別に分割する方針: `vaults.career` / `vaults.code` を設定ファイルで切替。
- `config.toml.sample` の例:
```toml
[defaults]
vault = "career"
input_dir = "./input"
model = "gemini-pro"

[vaults.career]
path = "C:\\Users\\sugar\\OneDrive\\デスクトップ\\Obsidian"
projects_subdir = "projects"
skills_subdir = "skills"

[vaults.code]
path = "C:\\Users\\sugar\\OneDrive\\デスクトップ\\Obsidian"  # 後で別Vaultに差し替え
projects_subdir = "projects"
skills_subdir = "skills"
```

## Markdown フロントマター（v1）
必須フィールド: `type=project`, `title`, `period`, `role`, `client_industry`, `team_size`, `environment`, `tags`

```md
---
type: project
title: 〇〇システム刷新プロジェクト
period: 2023-04 ~ 2024-03
role: PM
client_industry: 製薬
client_type: 事業会社        # 任意
employment_type: 副業         # 任意
work_style: フルリモート       # 任意
team_size: 10
environment:
  - AWS
  - Python
  - FastAPI
responsibilities:
  - 要件定義〜リリースまでのプロジェクトマネジメント
achievements:
  - 工数◯◯%削減
  - 新規案件××件の受注に貢献
tags:
  - #project
  - #role/PM
  - #industry/製造DX
  - #skill/生成AI
---
### 概要
（2〜3行）

### 担当業務
- …

### 実績・工夫
- …
```

## CLI の利用イメージ（Phase 2）
- 設定デフォルトを使う: `poetry run python -m tools.career_profile_importer.cli`
- Vault を切替: `... cli --vault code`
- 特定ファイルを指定: `... cli --vault career --input-file ./input/job_history_2024.txt`
- 入出力ポリシー:
  - 入力: `.txt` / `.md`（v1）。将来 PDF/Docx を検討。
  - 出力: `<vault>/projects/PJ_YYYY-YYYY_案件名.md` などを生成。

## プライバシー/LLMポリシー
- キャリア情報は API 経由のみ送信（学習利用なしのポリシーで呼び出す）。
- Web版UIやクラウドログを残すツールには送らない。
- 環境変数で API キーを渡し、キーは config.toml には直書きしない。

## Phase 2 の完了条件（ツール枠）
- config 読み込み＋CLIエントリが動作し、Vault/入力パスを指定できる。
- Gemini クライアントを通じてダミー/モック応答で JSON スキーマを返せる状態。
- Markdownビルダーが front matter を正しく組み立ててファイルを保存できる（プロジェクトノート単位）。
