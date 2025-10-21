# 作業ログ: エンタープライズ級安定化と正規化対応 (2025-10-20)

## 目的/要件
- Alembicを唯一のSSOTに統一（テーブル/インデックス/データ移行）
- 起動前に必ずAlembicマイグレーション完了
- 参照整合（users → assistants → conversations → messages）
- 冪等seed・可観測性（Alembic/Healthログ）
- CIのE2E（chat-flow含む）とUnitをグリーン化

## 実施サマリ
- 正規化リビジョン追加: `backend/alembic/versions/013_normalize_phase2.py:1`
  - conversations/messagesの列・型・制約・インデックスの正規化
  - messages.role を VARCHAR + CHECK に統一（ENUM撤廃）
  - assistant_skills を `(assistant_id, skill_id)` に一本化しデータ移行
- 起動経路の統一: `backend/entrypoint.sh:1`
  - DB準備 → Alembic版管理表確認 → `upgrade head` 実行 → アプリ起動
- 競合排除と観測: `.github/workflows/e2e.yml:45` 近辺
  - ワークフロー側は `alembic current` の表示のみ（アップグレードはbackend側）
  - UnitをCIに追加、`--cov-fail-under=75` のゲート導入
- テスト初期化の統一: `backend/tests/conftest.py:1`
  - create_all/drop_allを廃止、Alembicでheadまで上げてTRUNCATEでデータのみリセット
  - WSテストでもAlembicを使用: `backend/tests/api/v1/test_chat_ws.py:1`, `backend/tests/api/v1/test_chat_ws_edgecases.py:1`
- ドキュメント整備
  - 正規化の方針: `docs/01-foundation/database/02-migration-normalization.md:1`
  - テストDBの方針: `docs/01-foundation/testing/01-testing-db.md:1`
  - ブランチ保護Runbook: `docs/01-foundation/operations/01-branch-protection.md:1`
  - 本番DBロールアウトRunbook: `docs/01-foundation/operations/02-db-rollout.md:1`
  - リリースノート: `RELEASE_NOTES.md:1`
- 旧資料の物理移動（棚卸し第1弾）
  - `archive/docs-backup/` と `archive/ai-secretary-team-main-docs-backup/` へ移動、参照更新: `archive/README.md:1`

## 実行・検証結果
- Alembic: `alembic current` = `013_normalize_phase2 (head)`
- Backend起動: `/health` 200 OK
- E2E: 6/6 Green（Playwright）
- Unit: 31/31 pass, coverage ~77%（coverage gate ≥75%）

## リスク評価とフォローアップ
- 旧ENUM `message_role` がDBに残る場合は後日DROP（依存確認後）
- 追加のインデックス/制約は運用実測に基づき微調整
- 長寿命DBへ適用する際は、必ず事前バックアップ（Runbook参照）

## リンク/参照
- エントリポイント: backend/entrypoint.sh:1
- 正規化リビジョン: backend/alembic/versions/013_normalize_phase2.py:1
- CIワークフロー: .github/workflows/e2e.yml:45
- テスト初期化: backend/tests/conftest.py:1
- リリースノート: RELEASE_NOTES.md:1
- 運用Runbook: docs/01-foundation/operations/02-db-rollout.md:1
- ブランチ保護: docs/01-foundation/operations/01-branch-protection.md:1

