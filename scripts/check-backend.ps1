# AI Secretary Team - バックエンド状態確認スクリプト
# トラブルシューティング用

Write-Host "🔍 AI Secretary Team Backend 状態確認" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# 1. コンテナ状態確認
Write-Host "`n📋 コンテナ状態:" -ForegroundColor Yellow
docker compose -f docker-compose.yml ps

# 2. バックエンドログ確認（最新10行）
Write-Host "`n📋 バックエンドログ（最新10行）:" -ForegroundColor Yellow
docker compose -f docker-compose.yml logs --tail=10 backend

# 3. ヘルスチェック状況確認
Write-Host "`n📋 ヘルスチェック状況:" -ForegroundColor Yellow
$backendStatus = docker compose -f docker-compose.yml ps --format "json" | ConvertFrom-Json | Where-Object { $_.Service -eq "backend" }
if ($backendStatus) {
    Write-Host "   サービス名: $($backendStatus.Service)" -ForegroundColor White
    Write-Host "   状態: $($backendStatus.State)" -ForegroundColor White
    Write-Host "   ヘルス: $($backendStatus.Health)" -ForegroundColor White
    Write-Host "   ポート: $($backendStatus.Ports)" -ForegroundColor White
} else {
    Write-Host "   ❌ バックエンドコンテナが見つかりません" -ForegroundColor Red
}

# 4. ネットワーク接続テスト
Write-Host "`n📋 ネットワーク接続テスト:" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
    Write-Host "   ✅ ヘルスチェック成功: $($response | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ ヘルスチェック失敗: $($_.Exception.Message)" -ForegroundColor Red
}

# 5. ポート使用状況確認
Write-Host "`n📋 ポート8000使用状況:" -ForegroundColor Yellow
$port8000 = netstat -an | Select-String ":8000"
if ($port8000) {
    Write-Host "   $port8000" -ForegroundColor White
} else {
    Write-Host "   ❌ ポート8000でリスニングしているプロセスが見つかりません" -ForegroundColor Red
}

Write-Host "`n=================================" -ForegroundColor Green
Write-Host "✅ 状態確認完了" -ForegroundColor Green
