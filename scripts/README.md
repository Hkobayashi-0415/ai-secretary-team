# AI Secretary Team - バックエンド管理スクリプト

## 概要
バックエンドの起動、再起動、状態確認を自動化するスクリプト群です。
起動タイミングの問題を解決し、確実なヘルスチェックを提供します。

## スクリプト一覧

### 1. 起動スクリプト

#### `start-backend.ps1` (PowerShell版 - 推奨)
```powershell
# 通常の起動（ビルド込み）
.\scripts\start-backend.ps1

# ビルドをスキップして起動のみ
.\scripts\start-backend.ps1 -SkipBuild
```

#### `start-backend.sh` (Bash版)
```bash
# Linux/WSL環境で使用
./scripts/start-backend.sh
```

### 2. 再起動スクリプト

#### `restart-backend.ps1`
```powershell
# 完全な再起動（コンテナ削除→再ビルド→起動）
.\scripts\restart-backend.ps1
```

### 3. 状態確認スクリプト

#### `check-backend.ps1`
```powershell
# バックエンドの状態を詳細確認
.\scripts\check-backend.ps1
```

## 機能詳細

### 起動スクリプトの機能
- ✅ バックエンドコンテナのビルド・起動
- ✅ 起動完了まで自動待機
- ✅ ヘルスチェックの自動実行
- ✅ エラー時の詳細ログ表示
- ✅ 再試行機能（最大10回）

### 再起動スクリプトの機能
- ✅ 既存コンテナの完全停止・削除
- ✅ イメージの再ビルド（キャッシュなし）
- ✅ 新規コンテナの起動
- ✅ 起動完了まで自動待機
- ✅ ヘルスチェックの自動実行
- ✅ 再試行機能（最大15回）

### 状態確認スクリプトの機能
- ✅ コンテナ状態の表示
- ✅ バックエンドログの表示（最新10行）
- ✅ ヘルスチェック状況の確認
- ✅ ネットワーク接続テスト
- ✅ ポート使用状況の確認

## 使用方法

### 初回起動
```powershell
# 1. プロジェクトディレクトリに移動
cd C:\Users\sugar\OneDrive\デスクトップ\ai-secretary-team

# 2. バックエンドを起動
.\scripts\start-backend.ps1
```

### 日常的な使用
```powershell
# 状態確認
.\scripts\check-backend.ps1

# 問題がある場合の再起動
.\scripts\restart-backend.ps1
```

### トラブルシューティング
```powershell
# 1. 状態確認
.\scripts\check-backend.ps1

# 2. ログ確認
docker compose -f docker-compose.yml logs backend

# 3. 完全再起動
.\scripts\restart-backend.ps1
```

## 設定変更

### Docker Compose設定の改善
- ヘルスチェック間隔: 30s → 10s
- タイムアウト: 10s → 5s
- リトライ回数: 3回 → 5回
- 起動待機時間: 40s → 60s

## エラー対処

### よくあるエラーと対処法

1. **ポート8000が使用中**
   ```powershell
   # ポート使用状況確認
   netstat -an | Select-String ":8000"
   
   # プロセス終了
   taskkill /F /PID <プロセスID>
   ```

2. **コンテナが起動しない**
   ```powershell
   # ログ確認
   docker compose -f docker-compose.yml logs backend
   
   # 完全再起動
   .\scripts\restart-backend.ps1
   ```

3. **ヘルスチェックが失敗**
   ```powershell
   # 状態確認
   .\scripts\check-backend.ps1
   
   # データベース接続確認
   docker compose -f docker-compose.yml logs postgres
   ```

## 注意事項

- PowerShellスクリプトの実行ポリシーが制限されている場合は、以下を実行：
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

- 初回実行時は、Dockerイメージのダウンロードに時間がかかる場合があります。

- ネットワーク環境によっては、ヘルスチェックに時間がかかる場合があります。
