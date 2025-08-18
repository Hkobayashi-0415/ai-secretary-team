# 古いデータベース設計ファイル削除 実装計画書

**作成日**: 2025年8月17日  
**作成者**: 中野五月（Claude Code）  
**CLAUDE.md準拠**: フェーズ1完了

---

## 1. タスク概要

古い設計（マルチテナント、PostgreSQL 15）のデータベース設計ファイルを削除し、ドキュメント構造を整理する。

## 2. 削除対象ファイル

```bash
docs/database_design.md         # 385行、マルチテナント設計
docs/table_columns.md           # テーブルカラム定義
docs/table_definitions.md       # テーブル定義
docs/table_overview.md          # テーブル概要
docs/AIエージェントチーム_仕様.txt  # v5.0仕様書
```

## 3. 事前確認完了事項

- ✅ MD5ハッシュ値で03-github-originalと完全一致確認
- ✅ 他ドキュメントからの参照なし確認
- ✅ 正式版は`docs/01-foundation/database/01-database-design.md`
- ✅ Gitによるバックアップ可能

## 4. 作業手順

### Step 1: 削除前の最終確認
```bash
# ファイル存在確認
ls -la docs/database_design.md docs/table_*.md docs/AIエージェント*.txt

# バックアップ確認
ls -la docs/03-github-original/
```

### Step 2: ファイル削除実行
```bash
# 削除実行
rm docs/database_design.md
rm docs/table_columns.md
rm docs/table_definitions.md
rm docs/table_overview.md
rm docs/AIエージェントチーム_仕様.txt
```

### Step 3: 削除確認
```bash
# 削除確認
ls docs/*.md | grep -E "database|table"
```

## 5. リスク対策

| リスク | 対策 | 状態 |
|--------|------|------|
| 誤削除 | 03-github-originalにバックアップ | ✅ |
| 参照エラー | grep検索で確認済み | ✅ |
| 復元必要性 | Git管理で復元可能 | ✅ |

## 6. 成功基準

- [ ] 5ファイルが削除される
- [ ] エラーメッセージなし
- [ ] 削除後の確認で存在しない

---

**この計画により、安全に古いファイルを削除します。**