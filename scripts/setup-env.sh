#!/bin/bash

# AI秘書チーム・プラットフォーム 環境設定スクリプト
# 使用方法: ./scripts/setup-env.sh [development|production]

set -e

echo "AI秘書チーム・プラットフォーム 環境設定スクリプト"
echo "=============================================="

# 環境の選択
ENVIRONMENT=${1:-development}

case "$ENVIRONMENT" in
    "development")
        echo "開発環境の設定を行います..."
        ENV_FILE=".env.development"
        ;;
    "production")
        echo "本番環境の設定を行います..."
        ENV_FILE=".env.production"
        ;;
    *)
        echo "エラー: 無効な環境が指定されました"
        echo "使用方法: $0 [development|production]"
        exit 1
        ;;
esac

# 環境変数ファイルの存在確認
if [ ! -f "$ENV_FILE" ]; then
    echo "エラー: $ENV_FILE が見つかりません"
    exit 1
fi

# .envファイルの作成
echo "環境変数ファイルを設定中..."
cp "$ENV_FILE" .env

# APIキーの設定確認
echo ""
echo "API設定の確認:"
echo "=============="

# Gemini APIキーの確認
if grep -q "your_actual_gemini_api_key_here" .env; then
    echo "⚠️  警告: Gemini APIキーが設定されていません"
    echo "   .envファイルを編集してGEMINI_API_KEYを設定してください"
    echo ""
    echo "   例:"
    echo "   GEMINI_API_KEY=AIzaSyBth1NEer2qiMH9niE4GqsCJhsRQBDqFuc"
    echo ""
else
    echo "✓ Gemini APIキーが設定されています"
fi

# その他のAPIキーの確認
if grep -q "your_google_search_api_key_here" .env; then
    echo "ℹ️  情報: Google Search APIキーはオプションです"
fi

if grep -q "your_openai_api_key_here" .env; then
    echo "ℹ️  情報: OpenAI APIキーはオプションです"
fi

echo ""
echo "環境設定が完了しました！"
echo "=========================="
echo "環境: $ENVIRONMENT"
echo "設定ファイル: .env"
echo ""
echo "次のコマンドで開発環境を起動できます："
echo "  make dev-desktop  # デスクトップVM用"
echo "  make dev-wsl      # WSL用"
echo ""
echo "注意: APIキーが正しく設定されていることを確認してください" 