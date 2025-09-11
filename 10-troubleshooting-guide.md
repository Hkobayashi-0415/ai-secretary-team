# AI秘書チーム・プラットフォーム - トラブルシューティングガイド

**作成日**: 2025年8月17日  
**作成者**: 中野五月（Claude Code）  
**バージョン**: 1.0

## 🚨 トラブルシューティング概要

### 問題分類
- **🔴 Critical**: システム全体が停止
- **🟡 Warning**: 機能制限があるが動作
- **🟢 Info**: 軽微な問題

### 対応優先度
1. **Critical** → 即座に対応
2. **Warning** → 24時間以内に対応
3. **Info** → 次回リリースで対応

## 🔧 よくある問題と解決方法

### 1. 環境関連の問題

#### 問題: Dockerコンテナが起動しない
**症状**: `docker-compose up`でコンテナが起動しない

**原因と解決方法**:
```bash
# 1. ポートの競合確認
lsof -i :8000
lsof -i :3000
lsof -i :5432

# 2. 競合するプロセスを停止
kill -9 <PID>

# 3. Dockerの状態確認
docker ps -a
docker-compose ps

# 4. ログの確認
docker-compose logs backend
docker-compose logs frontend

# 5. コンテナの再作成
docker-compose down
docker-compose up --build
```

#### 問題: 環境変数が読み込まれない
**症状**: APIキーが設定されているのに認証エラー

**原因と解決方法**:
```bash
# 1. .envファイルの存在確認
ls -la .env

# 2. 環境変数の内容確認
cat .env | grep GEMINI_API_KEY

# 3. 環境変数の再読み込み
source .env
# または
make setup-env

# 4. コンテナの再起動
docker-compose restart backend
```

#### 問題: データベース接続エラー
**症状**: `database connection failed`エラー

**原因と解決方法**:
```bash
# 1. PostgreSQLの状態確認
docker-compose ps postgres

# 2. データベースログの確認
docker-compose logs postgres

# 3. 接続テスト
docker-compose exec postgres psql -U ai_secretary_user -d ai_secretary -c "SELECT 1;"

# 4. データベースの再起動
docker-compose restart postgres

# 5. データベースのリセット（データが失われます）
make db-reset
```

### 2. バックエンド関連の問題

#### 問題: FastAPIアプリケーションが起動しない
**症状**: `uvicorn`でアプリケーションが起動しない

**原因と解決方法**:
```bash
# 1. Python依存関係の確認
cd backend
pip list | grep fastapi

# 2. 依存関係の再インストール
pip install -r requirements.txt

# 3. アプリケーションの直接起動
python -m uvicorn app.main:app --reload

# 4. エラーログの確認
python -c "from app.main import app; print('App loaded successfully')"
```

#### 問題: データベースマイグレーションエラー
**症状**: `alembic upgrade head`でエラー

**原因と解決方法**:
```bash
# 1. マイグレーション状態の確認
docker-compose exec backend alembic current

# 2. マイグレーション履歴の確認
docker-compose exec backend alembic history

# 3. 特定のマイグレーションまで戻す
docker-compose exec backend alembic downgrade -1

# 4. マイグレーションの再実行
docker-compose exec backend alembic upgrade head

# 5. マイグレーションファイルの確認
ls -la backend/alembic/versions/
```

#### 問題: APIエンドポイントが404エラー
**症状**: API呼び出しで404 Not Found

**原因と解決方法**:
```bash
# 1. ルーターの登録確認
grep -r "include_router" backend/app/

# 2. エンドポイントの確認
curl http://localhost:8000/docs

# 3. アプリケーションの再起動
docker-compose restart backend

# 4. ログの確認
docker-compose logs backend | grep -i error
```

### 3. フロントエンド関連の問題

#### 問題: Reactアプリケーションがビルドできない
**症状**: `npm run build`でエラー

**原因と解決方法**:
```bash
# 1. Node.jsバージョンの確認
node --version
npm --version

# 2. 依存関係の確認
cd frontend
npm list

# 3. node_modulesの削除と再インストール
rm -rf node_modules package-lock.json
npm install

# 4. TypeScriptエラーの確認
npm run type-check

# 5. ビルドの詳細ログ
npm run build -- --verbose
```

#### 問題: ホットリロードが動作しない
**症状**: ファイル変更しても画面が更新されない

**原因と解決方法**:
```bash
# 1. ファイル監視の確認
ls -la frontend/src/

# 2. Vite設定の確認
cat frontend/vite.config.ts

# 3. 開発サーバーの再起動
docker-compose restart frontend-dev

# 4. ブラウザキャッシュのクリア
# ブラウザでCtrl+Shift+R

# 5. ポートの確認
netstat -tulpn | grep :5173
```

#### 問題: API通信エラー
**症状**: フロントエンドからAPIにアクセスできない

**原因と解決方法**:
```bash
# 1. API URLの確認
grep -r "VITE_API_URL" frontend/

# 2. ネットワーク接続の確認
curl http://localhost:8000/health

# 3. CORS設定の確認
grep -r "CORS_ORIGINS" backend/

# 4. ブラウザの開発者ツールでネットワークタブを確認
# F12 → Network → エラーの詳細を確認
```

### 4. データベース関連の問題

#### 問題: データベース接続タイムアウト
**症状**: データベース接続がタイムアウトする

**原因と解決方法**:
```bash
# 1. PostgreSQLの状態確認
docker-compose ps postgres

# 2. 接続数の確認
docker-compose exec postgres psql -U ai_secretary_user -d ai_secretary -c "SELECT count(*) FROM pg_stat_activity;"

# 3. 接続プール設定の確認
grep -r "pool_size" backend/

# 4. データベースの再起動
docker-compose restart postgres

# 5. 接続プールの調整
# backend/app/core/database.pyでpool_sizeを調整
```

#### 問題: データベースのデータが表示されない
**症状**: アプリケーションは起動するがデータが表示されない

**原因と解決方法**:
```bash
# 1. テーブルの存在確認
docker-compose exec postgres psql -U ai_secretary_user -d ai_secretary -c "\dt"

# 2. データの確認
docker-compose exec postgres psql -U ai_secretary_user -d ai_secretary -c "SELECT COUNT(*) FROM users;"

# 3. マイグレーションの確認
docker-compose exec backend alembic current

# 4. 初期データの投入
docker-compose exec backend python scripts/seed_data.py

# 5. データベースのリセット
make db-reset
```

### 5. パフォーマンス関連の問題

#### 問題: アプリケーションが遅い
**症状**: ページの読み込みが遅い

**原因と解決方法**:
```bash
# 1. リソース使用量の確認
docker stats

# 2. データベースクエリの確認
docker-compose exec postgres psql -U ai_secretary_user -d ai_secretary -c "SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 5;"

# 3. ログの確認
docker-compose logs backend | grep -i "slow"

# 4. インデックスの確認
docker-compose exec postgres psql -U ai_secretary_user -d ai_secretary -c "\di"

# 5. キャッシュの確認
docker-compose exec redis redis-cli info memory
```

#### 問題: メモリ使用量が高い
**症状**: メモリ使用量が異常に高い

**原因と解決方法**:
```bash
# 1. メモリ使用量の確認
docker stats --no-stream

# 2. プロセスの確認
docker-compose exec backend ps aux --sort=-%mem

# 3. メモリリークの確認
docker-compose exec backend python -c "import gc; print(gc.get_count())"

# 4. コンテナの再起動
docker-compose restart backend frontend

# 5. リソース制限の調整
# docker-compose.ymlでmemory制限を調整
```

## 🔍 デバッグツール

### 1. ログ監視

#### リアルタイムログ監視
```bash
# 全サービスのログ
docker-compose logs -f

# 特定のサービスのログ
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# エラーログのみ
docker-compose logs -f backend | grep -i error

# 特定の時間範囲のログ
docker-compose logs --since="2025-08-17T10:00:00" backend
```

#### ログファイルの確認
```bash
# ログファイルの場所
ls -la logs/

# ログファイルの内容確認
tail -f logs/backend.log
tail -f logs/frontend.log

# ログの検索
grep -r "ERROR" logs/
grep -r "Exception" logs/
```

### 2. データベースデバッグ

#### データベース接続テスト
```bash
# 接続テスト
docker-compose exec postgres psql -U ai_secretary_user -d ai_secretary -c "SELECT version();"

# テーブル一覧
docker-compose exec postgres psql -U ai_secretary_user -d ai_secretary -c "\dt"

# テーブル構造
docker-compose exec postgres psql -U ai_secretary_user -d ai_secretary -c "\d users"

# データの確認
docker-compose exec postgres psql -U ai_secretary_user -d ai_secretary -c "SELECT * FROM users LIMIT 5;"
```

#### パフォーマンス分析
```sql
-- スロークエリの確認
SELECT query, calls, total_time, mean_time, rows
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- インデックス使用状況
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- 接続数
SELECT count(*) as active_connections
FROM pg_stat_activity
WHERE state = 'active';
```

### 3. ネットワークデバッグ

#### ネットワーク接続テスト
```bash
# ポートの確認
netstat -tulpn | grep -E ":(3000|8000|5432|6379)"

# 接続テスト
curl -v http://localhost:8000/health
curl -v http://localhost:3000

# ネットワーク診断
docker network ls
docker network inspect ai-secretary-team_ai-secretary-network
```

#### APIテスト
```bash
# ヘルスチェック
curl http://localhost:8000/health

# APIエンドポイントテスト
curl -X GET http://localhost:8000/api/v1/assistants/
curl -X POST http://localhost:8000/api/v1/assistants/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Assistant", "description": "Test Description"}'

# 認証テスト
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpassword"}'
```

## 🚨 緊急時対応

### 1. システム全体が停止した場合

#### 緊急復旧手順
```bash
# 1. 全サービスの停止
docker-compose down

# 2. リソースの確認
docker system df
docker system prune -f

# 3. 設定ファイルの確認
cat .env
cat docker-compose.yml

# 4. 段階的起動
docker-compose up -d postgres redis
sleep 10
docker-compose up -d backend
sleep 10
docker-compose up -d frontend

# 5. ヘルスチェック
curl http://localhost:8000/health
curl http://localhost:3000
```

#### データベースの緊急復旧
```bash
# 1. データベースのバックアップ
docker-compose exec postgres pg_dump -U ai_secretary_user ai_secretary > backup.sql

# 2. データベースのリセット
make db-reset

# 3. バックアップからの復旧
docker-compose exec -T postgres psql -U ai_secretary_user -d ai_secretary < backup.sql

# 4. データの確認
docker-compose exec postgres psql -U ai_secretary_user -d ai_secretary -c "SELECT COUNT(*) FROM users;"
```

### 2. セキュリティインシデント

#### 緊急対応手順
```bash
# 1. 全サービスの停止
docker-compose down

# 2. ログの保存
docker-compose logs > security_incident_logs.txt

# 3. 設定ファイルの確認
grep -r "password\|secret\|key" .env
grep -r "password\|secret\|key" backend/
grep -r "password\|secret\|key" frontend/

# 4. アクセスログの確認
grep -r "unauthorized\|forbidden\|error" logs/

# 5. システムの再構築
make clean
make dev-desktop
```

## 📊 監視・アラート

### 1. ヘルスチェック

#### 自動ヘルスチェックスクリプト
```bash
#!/bin/bash
# scripts/health_check.sh

API_URL="http://localhost:8000/health"
FRONTEND_URL="http://localhost:3000"
ALERT_EMAIL="admin@ai-secretary.local"

# APIヘルスチェック
api_status=$(curl -s -o /dev/null -w "%{http_code}" $API_URL)
if [ $api_status -ne 200 ]; then
    echo "API is down (HTTP $api_status)" | mail -s "AI Secretary Alert" $ALERT_EMAIL
    exit 1
fi

# フロントエンドヘルスチェック
frontend_status=$(curl -s -o /dev/null -w "%{http_code}" $FRONTEND_URL)
if [ $frontend_status -ne 200 ]; then
    echo "Frontend is down (HTTP $frontend_status)" | mail -s "AI Secretary Alert" $ALERT_EMAIL
    exit 1
fi

echo "All services are healthy"
```

#### 定期的なヘルスチェック
```bash
# crontabに追加
# 5分ごとにヘルスチェック
*/5 * * * * /path/to/scripts/health_check.sh

# 毎日午前2時にログローテーション
0 2 * * * docker-compose exec backend find /app/logs -name "*.log" -mtime +7 -delete
```

### 2. パフォーマンス監視

#### リソース監視スクリプト
```bash
#!/bin/bash
# scripts/monitor_resources.sh

# CPU使用率
cpu_usage=$(docker stats --no-stream --format "table {{.CPUPerc}}" | tail -n +2 | sed 's/%//')

# メモリ使用率
memory_usage=$(docker stats --no-stream --format "table {{.MemPerc}}" | tail -n +2 | sed 's/%//')

# ディスク使用率
disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')

echo "CPU: ${cpu_usage}%, Memory: ${memory_usage}%, Disk: ${disk_usage}%"

# 閾値チェック
if [ $cpu_usage -gt 80 ]; then
    echo "High CPU usage: ${cpu_usage}%" | mail -s "AI Secretary Alert" admin@ai-secretary.local
fi

if [ $memory_usage -gt 80 ]; then
    echo "High memory usage: ${memory_usage}%" | mail -s "AI Secretary Alert" admin@ai-secretary.local
fi

if [ $disk_usage -gt 90 ]; then
    echo "High disk usage: ${disk_usage}%" | mail -s "AI Secretary Alert" admin@ai-secretary.local
fi
```

## 📞 サポート連絡先

### 内部サポート
- **開発チーム**: dev@ai-secretary.local
- **インフラチーム**: infra@ai-secretary.local
- **緊急時**: +81-90-1234-5678

### 外部サポート
- **Docker**: https://docs.docker.com/
- **PostgreSQL**: https://www.postgresql.org/docs/
- **FastAPI**: https://fastapi.tiangolo.com/
- **React**: https://reactjs.org/docs/

### ドキュメント
- **プロジェクトドキュメント**: `docs/`
- **API仕様書**: `docs/api/`
- **開発ガイド**: `docs/development/`

このトラブルシューティングガイドにより、問題の迅速な解決が可能になります。
