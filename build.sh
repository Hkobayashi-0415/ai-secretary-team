#!/bin/bash

# AI秘書チーム・プラットフォーム ビルドスクリプト
# 使用方法: ./build.sh [common|desktop|wsl|tablet|all]

set -e

echo "AI秘書チーム・プラットフォーム ビルドスクリプト"
echo "=============================================="

# 共通イメージのビルド
build_common() {
    echo "共通イメージをビルド中..."
    
    # バックエンド共通イメージ
    docker build -f backend/Dockerfile.common -t ai-secretary-backend:common ./backend
    echo "✓ バックエンド共通イメージをビルドしました"
    
    # フロントエンド共通イメージ
    docker build -f frontend/Dockerfile.common -t ai-secretary-frontend:common ./frontend
    echo "✓ フロントエンド共通イメージをビルドしました"
}

# デスクトップVM用イメージのビルド
build_desktop() {
    echo "デスクトップVM用イメージをビルド中..."
    
    # バックエンドデスクトップ用イメージ
    docker build -f backend/Dockerfile.desktop -t ai-secretary-backend:desktop ./backend
    echo "✓ バックエンドデスクトップ用イメージをビルドしました"
    
    # フロントエンドデスクトップ用イメージ
    docker build -f frontend/Dockerfile.desktop -t ai-secretary-frontend:desktop ./frontend
    echo "✓ フロントエンドデスクトップ用イメージをビルドしました"
}

# WSL用イメージのビルド
build_wsl() {
    echo "WSL用イメージをビルド中..."
    
    # バックエンドWSL用イメージ
    docker build -f backend/Dockerfile.wsl -t ai-secretary-backend:wsl ./backend
    echo "✓ バックエンドWSL用イメージをビルドしました"
    
    # フロントエンドWSL用イメージ
    docker build -f frontend/Dockerfile.wsl -t ai-secretary-frontend:wsl ./frontend
    echo "✓ フロントエンドWSL用イメージをビルドしました"
}

# タブレット用イメージのビルド
build_tablet() {
    echo "タブレット用イメージをビルド中..."
    
    # バックエンドタブレット用イメージ（WSL設定を流用）
    docker build -f backend/Dockerfile.wsl -t ai-secretary-backend:tablet ./backend
    echo "✓ バックエンドタブレット用イメージをビルドしました"
    
    # フロントエンドタブレット用イメージ（WSL設定を流用）
    docker build -f frontend/Dockerfile.wsl -t ai-secretary-frontend:tablet ./frontend
    echo "✓ フロントエンドタブレット用イメージをビルドしました"
}

# 全イメージのビルド
build_all() {
    echo "全イメージをビルド中..."
    build_common
    build_desktop
    build_wsl
    build_tablet
    echo "✓ 全イメージのビルドが完了しました"
}

# メイン処理
case "$1" in
    "common")
        build_common
        ;;
    "desktop")
        build_common
        build_desktop
        ;;
    "wsl")
        build_common
        build_wsl
        ;;
    "tablet")
        build_common
        build_tablet
        ;;
    "all")
        build_all
        ;;
    *)
        echo "使用方法: $0 [common|desktop|wsl|tablet|all]"
        echo ""
        echo "オプション:"
        echo "  common   - 共通イメージのみビルド"
        echo "  desktop  - デスクトップVM用イメージをビルド"
        echo "  wsl      - WSL用イメージをビルド"
        echo "  tablet   - タブレット用イメージをビルド"
        echo "  all      - 全イメージをビルド"
        exit 1
        ;;
esac

echo ""
echo "ビルド完了！"
echo "次のコマンドで環境を起動できます："
echo "  make dev-desktop  # デスクトップVM用"
echo "  make dev-wsl      # WSL用"
echo "  make dev-tablet   # タブレット用" 