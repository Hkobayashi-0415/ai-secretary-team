# AI Secretary Team — DB & Test TODO（ステータス更新 2025-10-20）

## 完了
- AlembicをSSOTに統一し、正規化（013）を適用（conversations/messages/assistant_skills）
- backend起動時のlembic upgrade headをエントリポイントで強制
- E2EをCIに統合（Playwright 6/6）
- UnitをCIに統合し、coverage gate（≥75%）を導入
- テストDB初期化をAlembic経由で統一（create_all/drop_all排除）

## 次のアクション
- 旧ENUM message_role の未使用確認とDROP（安全確認後）
- インデックス/制約の微調整（運用実測に基づく）
- 本番ロールアウトRunbookの運用反映

## ✅ 一度だけやる（初期整備）

- [ ] **Compose の共通エイリアスを定義**
  ```bash
  export DC="docker compose -f docker-compose.yml -f docker-compose.ci.yml"
 Postgres イメージタグを固定（pg16-alpine は存在しない）

pgvector/pgvector:pg16

 init SQL は拡張だけにする（テーブルは Alembic に一本化）

./database/init/01-init.sql:

sql
コードをコピーする
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
 CORS_ORIGINS の重複を削除（backend の env で1か所だけに）

 pytest 用保険：tests/conftest.py で拡張を念のため有効化

py
コードをコピーする
await conn.exec_driver_sql('CREATE EXTENSION IF NOT EXISTS "vector";')
 テスト DB 切替：DOCKERIZED=1 のときはコンテナ内 PG を使う分岐を維持

🔁 毎回の開発フロー
 クリーン起動

bash
コードをコピーする
$DC down -v
$DC up -d postgres redis backend
 backend 起動確認（/health が 200）

bash
コードをコピーする
$DC logs -f backend   # Ctrl-C で抜け
 pgvector の有無確認（Windows/Git Bash は -T 推奨）

bash
コードをコピーする
$DC exec -T postgres psql -U ai_secretary_user -d ai_secretary -c "\dx"
 テスト実行（Docker ネットワーク上）

bash
コードをコピーする
$DC run --rm -e DOCKERIZED=1 backend pytest -q
🧭 Alembic（移行）運用ルール
 テーブル作成は Alembic のみ（init SQL は拡張だけにする）

 既存 DB に手作業のテーブルが残っている場合

破棄して再作成：

bash
コードをコピーする
$DC down -v && $DC up -d postgres redis backend
既存を尊重して合わせる（自己責任）：

bash
コードをコピーする
$DC exec backend alembic stamp head
$DC exec backend alembic upgrade head
🚑 トラブル時のクイックリファレンス
 type "vector" does not exist

画像：pgvector/pgvector:pg16 を使っているか

拡張：\dx に vector が表示されるか

tests/conftest.py に CREATE EXTENSION IF NOT EXISTS "vector"; があるか

 DuplicateTableError（例：relation "users" already exists）

init SQL に テーブル作成が残っていないか（削除）

一時回避：alembic stamp head → alembic upgrade head

 Windows の docker exec が落ちる（Git Bash のシェル問題）

-T を付けるか、PowerShell を使用
例：$DC exec -T postgres psql -U ... -c "\dx"

 どの DB に向いているか不安

テスト時は必ず DOCKERIZED=1 をセット

もしくは TEST_DATABASE_URL を明示

🧪 CI の要点
 Postgres サービスは pgvector/pgvector:pg16 を使用

 pytest は DOCKERIZED=1 で実行

 backend 起動コマンドに alembic upgrade head を含める
（init SQL は拡張のみが流れる前提）

📝 便利コマンド（抜粋）
bash
コードをコピーする
# 状態確認
$DC ps

# backend ログ（追尾）
$DC logs -f backend

# Postgres ログ
$DC logs postgres --tail=200

# 拡張一覧（pgvector が入っているか）
$DC exec -T postgres psql -U ai_secretary_user -d ai_secretary -c "\dx"
makefile
コードをコピーする
::contentReference[oaicite:0]{index=0}
