# 技術仕様書統合 実装計画書

**作成日**: 2025年8月17日  
**作成者**: 中野五月（Claude Code）  
**CLAUDE.md準拠**: フェーズ1 - 理解と計画

---

## 1. 現状分析

### 1.1 ファイル詳細
| ファイル | requirements版 | technical版 |
|---------|--------------|------------|
| パス | 01-foundation/requirements/04-*.md | 01-foundation/technical/04-*.md |
| 行数 | 677行 | 約300行（データベース設計なし） |
| Python | 3.11+ | 3.12 |
| ビルドツール | 記載なし | Vite明記 |
| AI統合 | 記載なし | LangGraph + Zen MCP Server |
| Redis | Redis 7 | Redis 7（キャッシュ専用） |
| 前提条件 | リスト形式 | 階層的・体系的 |
| データベース設計 | あり（詳細） | なし |

### 1.2 主要な相違点

#### **technical版の優位点**
1. **技術スタック最新化**
   - Python 3.12（具体的バージョン）
   - Vite明記（高速ビルド）
   - LangGraph + Zen MCP Server（AI統合）
   - AI Collaboration Engine追加

2. **前提条件の体系化**
   - 階層的な記述（設計レベル、動作環境、技術制約、運用・保守、設計思想）
   - より明確な分類

3. **簡素化反映済み**
   - Redis（キャッシュ専用）
   - ローカル認証

#### **requirements版の有用な情報**
1. **データベース設計（約200行）**
   - CREATE TABLE文
   - インデックス設計
   - ユーザー管理系テーブル
   - AI秘書管理系テーブル
   - ワークフロー管理系テーブル
   - Obsidian連携系テーブル
   - セッション・ログ系テーブル

2. **API設計（約150行）**
   - エンドポイント一覧
   - 認証・認可
   - エラーレスポンス形式

3. **配布パッケージ化（約50行）**
   - PyInstaller設定
   - インストーラー機能

## 2. 統合方針

### 2.1 基本方針
- **technical版を正式版として採用**
- requirements版から有用な情報を移植
- 重複する内容は最新版（technical版）を優先

### 2.2 統合内容

#### **technical版に追加する内容**
1. データベース設計セクション（修正版）
   - ローカル環境に適した設計に修正
   - email、password_hashを削除
   - app_stateテーブルに変更済み

2. API設計の詳細
   - エンドポイント一覧
   - エラーレスポンス形式

3. 配布パッケージ化の詳細

#### **削除・修正する内容**
1. JWT認証関連の記述
2. セッション管理関連
3. Python 3.11+ → 3.12に統一

## 3. 作業手順

### Step 1: バックアップ作成
```bash
cp docs/01-foundation/requirements/04-technical-specification.md \
   docs/01-foundation/requirements/04-technical-specification-backup.md
```

### Step 2: technical版への情報移植
1. データベース設計セクションを追加（修正版）
2. API設計の詳細を追加
3. 配布パッケージ化の詳細を追加

### Step 3: requirements版のリネーム
```bash
mv docs/01-foundation/requirements/04-technical-specification.md \
   docs/01-foundation/requirements/04-technical-specification-reference.md
```

### Step 4: 参照更新
- 他のドキュメントからの参照を確認・更新

## 4. リスク評価

| リスク | 影響度 | 対策 |
|--------|-------|------|
| 情報の欠落 | 中 | 詳細な差分確認 |
| 参照エラー | 小 | grep検索で確認 |
| バージョン不整合 | 小 | Python 3.12で統一 |

## 5. 成功基準

- [ ] technical版に必要な情報が統合される
- [ ] requirements版がreferenceとして保存される
- [ ] 参照エラーが発生しない
- [ ] ローカル環境に適した内容になる

## 6. 予想作業時間

- バックアップ: 1分
- 情報移植: 30分
- 確認・テスト: 10分
- 合計: 約40分

---

**この計画により、技術仕様書を適切に統合します。**

*作成者: 中野五月（Claude Code）*