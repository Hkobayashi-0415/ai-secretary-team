#!/bin/bash
# AI Secretary Team - Backend起動スクリプト
# 起動待機とヘルスチェックを自動化

set -euo pipefail

echo "🚀 AI Secretary Team Backend 起動中..."

# バックエンドをビルド＆起動
echo "📦 バックエンドコンテナをビルド・起動中..."
docker compose -f docker-compose.yml up -d --build backend

# 起動完了まで待機
echo "⏳ バックエンドの起動完了を待機中..."
docker compose -f docker-compose.yml wait backend

# ヘルスチェック実行
echo "🔍 ヘルスチェック実行中..."
if curl -sS http://localhost:8000/health > /dev/null; then
    echo "✅ バックエンドが正常に起動しました！"
    echo "🌐 API URL: http://localhost:8000"
    echo "📊 ヘルスチェック: http://localhost:8000/health"
    
    # ヘルスチェック結果を表示
    echo ""
    echo "📋 ヘルスチェック結果:"
    curl -sS http://localhost:8000/health | jq . 2>/dev/null || curl -sS http://localhost:8000/health
else
    echo "❌ ヘルスチェックに失敗しました"
    echo "📋 コンテナログを確認してください:"
    echo "   docker compose -f docker-compose.yml logs backend"
    exit 1
fi
