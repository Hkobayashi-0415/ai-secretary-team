# AI Secretary Team - Backend起動スクリプト (PowerShell版)
# 起動待機とヘルスチェックを自動化

param(
    [switch]$SkipBuild = $false
)

Write-Host "🚀 AI Secretary Team Backend 起動中..." -ForegroundColor Green

try {
    # バックエンドをビルド＆起動
    if (-not $SkipBuild) {
        Write-Host "📦 バックエンドコンテナをビルド・起動中..." -ForegroundColor Yellow
        docker compose -f docker-compose.yml up -d --build backend
    } else {
        Write-Host "📦 バックエンドコンテナを起動中..." -ForegroundColor Yellow
        docker compose -f docker-compose.yml up -d backend
    }

    # 起動完了まで待機
    Write-Host "⏳ バックエンドの起動完了を待機中..." -ForegroundColor Yellow
    docker compose -f docker-compose.yml wait backend

    # ヘルスチェック実行
    Write-Host "🔍 ヘルスチェック実行中..." -ForegroundColor Yellow
    
    $maxRetries = 10
    $retryCount = 0
    $isHealthy = $false
    
    while ($retryCount -lt $maxRetries -and -not $isHealthy) {
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
            if ($response.status -eq "healthy") {
                $isHealthy = $true
            }
        } catch {
            $retryCount++
            if ($retryCount -lt $maxRetries) {
                Write-Host "⏳ ヘルスチェック再試行中... ($retryCount/$maxRetries)" -ForegroundColor Yellow
                Start-Sleep -Seconds 3
            }
        }
    }
    
    if ($isHealthy) {
        Write-Host "✅ バックエンドが正常に起動しました！" -ForegroundColor Green
        Write-Host "🌐 API URL: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "📊 ヘルスチェック: http://localhost:8000/health" -ForegroundColor Cyan
        
        # ヘルスチェック結果を表示
        Write-Host ""
        Write-Host "📋 ヘルスチェック結果:" -ForegroundColor White
        $healthResponse = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
        $healthResponse | ConvertTo-Json -Depth 3
    } else {
        Write-Host "❌ ヘルスチェックに失敗しました" -ForegroundColor Red
        Write-Host "📋 コンテナログを確認してください:" -ForegroundColor Yellow
        Write-Host "   docker compose -f docker-compose.yml logs backend" -ForegroundColor Gray
        exit 1
    }
} catch {
    Write-Host "❌ エラーが発生しました: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "📋 コンテナログを確認してください:" -ForegroundColor Yellow
    Write-Host "   docker compose -f docker-compose.yml logs backend" -ForegroundColor Gray
    exit 1
}
