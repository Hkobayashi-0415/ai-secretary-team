# AI秘書チーム・プラットフォーム - Docker設定

**作成日**: 2025年8月17日  
**作成者**: 中野五月（Claude Code）  
**バージョン**: 1.0

## 🐳 Docker概要

### 環境別構成
- **共通設定**: `docker-compose.common.yml` - データベース・Redis等の共通サービス
- **デスクトップVM用**: `docker-compose.desktop.yml` - メイン開発環境
- **WSL用**: `docker-compose.wsl.yml` - 軽量環境
- **タブレット用**: `docker-compose.tablet.yml` - 共有・デモ環境

### 技術スタック
- **PostgreSQL 16**: メインデータベース
- **Redis 7**: キャッシュ・セッション管理
- **FastAPI**: Pythonバックエンド
- **React**: フロントエンド
- **pgAdmin**: データベース管理

## 📁 Dockerfile構成

### バックエンドDockerfile

#### 共通Dockerfile (Dockerfile.common)
```dockerfile
# backend/Dockerfile.common
FROM python:3.12-slim

# 作業ディレクトリの設定
WORKDIR /app

# システムパッケージのインストール
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# ポートの公開
EXPOSE 8000

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# アプリケーションの起動
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### デスクトップVM用 (Dockerfile.desktop)
```dockerfile
# backend/Dockerfile.desktop
FROM ai-secretary-backend:common

# 開発用の追加パッケージ
RUN pip install --no-cache-dir \
    debugpy \
    pytest \
    pytest-asyncio \
    black \
    isort \
    flake8

# 開発用の環境変数
ENV DEBUG=true
ENV LOG_LEVEL=DEBUG
ENV PYTHONPATH=/app

# デバッグポートの公開
EXPOSE 5678

# 開発用の起動コマンド
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"]
```

#### WSL用 (Dockerfile.wsl)
```dockerfile
# backend/Dockerfile.wsl
FROM ai-secretary-backend:common

# 軽量設定
ENV DEBUG=false
ENV LOG_LEVEL=INFO
ENV WORKERS=1

# 軽量起動コマンド
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
```

### フロントエンドDockerfile

#### 共通Dockerfile (Dockerfile.common)
```dockerfile
# frontend/Dockerfile.common
FROM node:18-alpine

# 作業ディレクトリの設定
WORKDIR /app

# package.jsonとpackage-lock.jsonをコピー
COPY package*.json ./

# 依存関係のインストール
RUN npm ci --only=production

# アプリケーションコードのコピー
COPY . .

# ビルド
RUN npm run build

# ポートの公開
EXPOSE 3000

# アプリケーションの起動
CMD ["npm", "start"]
```

#### 開発用 (Dockerfile.dev)
```dockerfile
# frontend/Dockerfile.dev
FROM node:18-alpine

# 作業ディレクトリの設定
WORKDIR /app

# package.jsonとpackage-lock.jsonをコピー
COPY package*.json ./

# 依存関係のインストール（開発用）
RUN npm ci

# アプリケーションコードのコピー
COPY . .

# 開発サーバーの起動
CMD ["npm", "run", "dev"]
```

#### デスクトップVM用 (Dockerfile.desktop)
```dockerfile
# frontend/Dockerfile.desktop
FROM ai-secretary-frontend:common

# 開発用の追加パッケージ
RUN npm install --save-dev \
    @types/node \
    @types/react \
    @types/react-dom \
    typescript \
    vite

# 開発用の環境変数
ENV NODE_ENV=development
ENV CHOKIDAR_USEPOLLING=true

# 開発サーバーの起動
CMD ["npm", "run", "dev"]
```

## 🔧 Docker Compose設定

### 共通設定 (docker-compose.common.yml)
```yaml
version: '3.8'

volumes:
  ai-secretary-postgres-data:
    driver: local
  ai-secretary-redis-data:
    driver: local

services:
  # PostgreSQL Database
  postgres:
    image: postgres:16-alpine
    container_name: ai-secretary-postgres
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: ai_secretary
      POSTGRES_USER: ai_secretary_user
      POSTGRES_PASSWORD: ai_secretary_password
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --lc-collate=C --lc-ctype=C"
    volumes:
      - ai-secretary-postgres-data:/var/lib/postgresql/data
      - ./database/init:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ai_secretary_user -d ai_secretary"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    networks:
      - ai-secretary-network

  # Redis for caching and session management
  redis:
    image: redis:7-alpine
    container_name: ai-secretary-redis
    ports:
      - "6379:6379"
    volumes:
      - ai-secretary-redis-data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - ai-secretary-network

  # pgAdmin (Database management)
  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: ai-secretary-pgadmin
    ports:
      - "5050:80"
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@ai-secretary.local
      - PGADMIN_DEFAULT_PASSWORD=admin123
      - PGADMIN_CONFIG_SERVER_MODE=False
    volumes:
      - ./database/pgadmin:/var/lib/pgadmin
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - ai-secretary-network

networks:
  ai-secretary-network:
    driver: bridge
```

### デスクトップVM用設定 (docker-compose.desktop.yml)
```yaml
version: '3.8'

services:
  # Backend API (FastAPI + LangGraph) - デスクトップVM用
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.desktop
    container_name: ai-secretary-backend-desktop
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://ai_secretary_user:ai_secretary_password@postgres:5432/ai_secretary
      - REDIS_URL=redis://redis:6379
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - ENVIRONMENT=development
      - CORS_ORIGINS=http://localhost:3000,http://localhost:5173
      - DEBUG=true
      - LOG_LEVEL=DEBUG
      - DB_HOST=postgres
      - DB_USER=ai_secretary_user
      - DB_NAME=ai_secretary
      - POSTGRES_PASSWORD=ai_secretary_password
    volumes:
      - ./backend:/app
      - /app/__pycache__
      - ./logs:/app/logs
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: >
      sh -c "
        echo 'Waiting for database...' &&
        sleep 5 &&
        cd /app &&
        alembic upgrade head &&
        uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
      "
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - ai-secretary-network
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'

  # Frontend (React + Vite) - デスクトップVM用
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.desktop
    container_name: ai-secretary-frontend-desktop
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000
      - NODE_ENV=development
      - CHOKIDAR_USEPOLLING=true
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
    networks:
      - ai-secretary-network
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'

  # Development frontend (for hot reload) - デスクトップVM用
  frontend-dev:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    container_name: ai-secretary-frontend-dev-desktop
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000
      - NODE_ENV=development
      - CHOKIDAR_USEPOLLING=true
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
    networks:
      - ai-secretary-network
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'

networks:
  ai-secretary-network:
    driver: bridge
```

### WSL用設定 (docker-compose.wsl.yml)
```yaml
version: '3.8'

services:
  # Backend API (FastAPI + LangGraph) - WSL用（軽量）
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.wsl
    container_name: ai-secretary-backend-wsl
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://ai_secretary_user:ai_secretary_password@postgres:5432/ai_secretary
      - REDIS_URL=redis://redis:6379
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - ENVIRONMENT=development
      - CORS_ORIGINS=http://localhost:3000,http://localhost:5173
      - DEBUG=false
      - LOG_LEVEL=INFO
    volumes:
      - ./backend:/app
      - /app/__pycache__
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 60s
      timeout: 15s
      retries: 2
      start_period: 60s
    networks:
      - ai-secretary-network
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'

  # Frontend (React + Vite) - WSL用（軽量）
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.wsl
    container_name: ai-secretary-frontend-wsl
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000
      - NODE_ENV=development
      - CHOKIDAR_USEPOLLING=true
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
    networks:
      - ai-secretary-network
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.25'
        reservations:
          memory: 256M
          cpus: '0.1'

  # Development frontend (for hot reload) - WSL用（軽量）
  frontend-dev:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    container_name: ai-secretary-frontend-dev-wsl
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000
      - NODE_ENV=development
      - CHOKIDAR_USEPOLLING=true
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
    networks:
      - ai-secretary-network
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.25'
        reservations:
          memory: 256M
          cpus: '0.1'

networks:
  ai-secretary-network:
    driver: bridge
```

### タブレット用設定 (docker-compose.tablet.yml)
```yaml
version: '3.8'

services:
  # Backend API (FastAPI + LangGraph) - タブレット用
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.wsl  # 軽量設定を使用
    container_name: ai-secretary-backend-tablet
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://ai_secretary_user:ai_secretary_password@postgres:5432/ai_secretary
      - REDIS_URL=redis://redis:6379
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - ENVIRONMENT=development
      - CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://192.168.1.100:3000
      - DEBUG=false
      - LOG_LEVEL=INFO
      - TABLET_MODE=true
      - TOUCH_OPTIMIZED=true
    volumes:
      - ./backend:/app
      - /app/__pycache__
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 60s
      timeout: 15s
      retries: 2
      start_period: 60s
    networks:
      - ai-secretary-network
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'

  # Frontend (React + Vite) - タブレット用
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.wsl  # 軽量設定を使用
    container_name: ai-secretary-frontend-tablet
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000
      - NODE_ENV=development
      - CHOKIDAR_USEPOLLING=true
      - TABLET_MODE=true
      - TOUCH_OPTIMIZED=true
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
    networks:
      - ai-secretary-network
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.25'
        reservations:
          memory: 256M
          cpus: '0.1'

  # Development frontend (for hot reload) - タブレット用
  frontend-dev:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    container_name: ai-secretary-frontend-dev-tablet
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000
      - NODE_ENV=development
      - CHOKIDAR_USEPOLLING=true
      - TABLET_MODE=true
      - TOUCH_OPTIMIZED=true
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
    networks:
      - ai-secretary-network
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.25'
        reservations:
          memory: 256M
          cpus: '0.1'

networks:
  ai-secretary-network:
    driver: bridge
```

## 🚀 ビルド・実行スクリプト

### ビルドスクリプト (build.sh)
```bash
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
```

### Makefile
```makefile
.PHONY: help build build-common build-desktop build-wsl build-tablet up down logs clean dev dev-desktop dev-wsl dev-tablet db-reset setup-env

# デフォルトターゲット
help:
	@echo "AI秘書チーム・プラットフォーム 管理コマンド"
	@echo ""
	@echo "基本コマンド:"
	@echo "  make build          - 全Dockerイメージをビルド"
	@echo "  make build-common   - 共通イメージのみビルド"
	@echo "  make build-desktop  - デスクトップVM用イメージをビルド"
	@echo "  make build-wsl      - WSL用イメージをビルド"
	@echo "  make build-tablet   - タブレット用イメージをビルド"
	@echo "  make up             - 全サービスを起動"
	@echo "  make down           - 全サービスを停止"
	@echo "  make logs           - ログを表示"
	@echo "  make clean          - コンテナとボリュームを削除"
	@echo ""
	@echo "環境設定コマンド:"
	@echo "  make setup-env      - 開発環境の設定"
	@echo "  make setup-env-dev  - 開発環境の設定"
	@echo "  make setup-env-prod - 本番環境の設定"
	@echo "  make setup-env-tablet - タブレット環境の設定"
	@echo ""
	@echo "開発コマンド:"
	@echo "  make dev            - 開発環境を起動（デフォルト）"
	@echo "  make dev-desktop    - デスクトップVM用開発環境を起動"
	@echo "  make dev-wsl        - WSL用開発環境を起動"
	@echo "  make dev-tablet     - タブレット用開発環境を起動"
	@echo ""
	@echo "データベースコマンド:"
	@echo "  make db-reset       - データベースをリセット"
	@echo "  make db-migrate     - データベースマイグレーション実行"
	@echo ""
	@echo "アクセスURL:"
	@echo "  フロントエンド: http://localhost:3000"
	@echo "  開発フロントエンド: http://localhost:5173"
	@echo "  バックエンドAPI: http://localhost:8000"
	@echo "  pgAdmin: http://localhost:5050 (admin@ai-secretary.local / admin123)"

# 環境設定コマンド
setup-env:
	@echo "開発環境の設定を行います..."
	@chmod +x scripts/setup-env.sh
	@./scripts/setup-env.sh development

setup-env-dev:
	@echo "開発環境の設定を行います..."
	@chmod +x scripts/setup-env.sh
	@./scripts/setup-env.sh development

setup-env-prod:
	@echo "本番環境の設定を行います..."
	@chmod +x scripts/setup-env.sh
	@./scripts/setup-env.sh production

setup-env-tablet:
	@echo "タブレット環境の設定を行います..."
	@cp .env.tablet .env
	@echo "✓ タブレット環境設定が完了しました"
	@echo "  .envファイルを編集してAPIキーを設定してください"

# Dockerイメージをビルド
build:
	@echo "全Dockerイメージをビルド中..."
	chmod +x build.sh
	./build.sh all

# 共通イメージをビルド
build-common:
	@echo "共通イメージをビルド中..."
	chmod +x build.sh
	./build.sh common

# デスクトップVM用イメージをビルド
build-desktop:
	@echo "デスクトップVM用イメージをビルド中..."
	chmod +x build.sh
	./build.sh desktop

# WSL用イメージをビルド
build-wsl:
	@echo "WSL用イメージをビルド中..."
	chmod +x build.sh
	./build.sh wsl

# タブレット用イメージをビルド
build-tablet:
	@echo "タブレット用イメージをビルド中..."
	chmod +x build.sh
	./build.sh tablet

# 全サービスを起動（デフォルト）
up:
	@echo "全サービスを起動中..."
	docker-compose -f docker-compose.common.yml -f docker-compose.desktop.yml up -d

# 全サービスを停止
down:
	@echo "全サービスを停止中..."
	docker-compose -f docker-compose.common.yml -f docker-compose.desktop.yml down

# ログを表示
logs:
	@echo "ログを表示中..."
	docker-compose -f docker-compose.common.yml -f docker-compose.desktop.yml logs -f

# コンテナとボリュームを削除
clean:
	@echo "コンテナとボリュームを削除中..."
	docker-compose -f docker-compose.common.yml -f docker-compose.desktop.yml down -v --remove-orphans
	docker system prune -f

# 開発環境を起動（デフォルト：デスクトップVM用）
dev: setup-env build-desktop up
	@echo "デスクトップVM用開発環境を起動中..."
	@echo "フロントエンド: http://localhost:3000"
	@echo "開発フロントエンド: http://localhost:5173"
	@echo "バックエンドAPI: http://localhost:8000"
	@echo "pgAdmin: http://localhost:5050"

# デスクトップVM用開発環境を起動
dev-desktop: setup-env build-desktop
	@echo "デスクトップVM用開発環境を起動中..."
	docker-compose -f docker-compose.common.yml -f docker-compose.desktop.yml up -d
	@echo "フロントエンド: http://localhost:3000"
	@echo "開発フロントエンド: http://localhost:5173"
	@echo "バックエンドAPI: http://localhost:8000"
	@echo "pgAdmin: http://localhost:5050"

# WSL用開発環境を起動
dev-wsl: setup-env build-wsl
	@echo "WSL用開発環境を起動中..."
	docker-compose -f docker-compose.common.yml -f docker-compose.wsl.yml up -d
	@echo "フロントエンド: http://localhost:3000"
	@echo "開発フロントエンド: http://localhost:5173"
	@echo "バックエンドAPI: http://localhost:8000"
	@echo "pgAdmin: http://localhost:5050"

# タブレット用開発環境を起動
dev-tablet: setup-env-tablet build-tablet
	@echo "タブレット用開発環境を起動中..."
	docker-compose -f docker-compose.common.yml -f docker-compose.tablet.yml up -d
	@echo "フロントエンド: http://localhost:3000"
	@echo "開発フロントエンド: http://localhost:5173"
	@echo "バックエンドAPI: http://localhost:8000"
	@echo "pgAdmin: http://localhost:5050"
	@echo ""
	@echo "タブレットからアクセスする場合:"
	@echo "  フロントエンド: http://192.168.1.100:3000"
	@echo "  バックエンドAPI: http://192.168.1.100:8000"

# データベースをリセット
db-reset:
	@echo "データベースをリセット中..."
	docker-compose -f docker-compose.common.yml down
	docker volume rm ai-secretary-team_ai-secretary-postgres-data || true
	docker-compose -f docker-compose.common.yml up -d postgres
	@echo "PostgreSQLが起動するまで待機中..."
	@sleep 10
	@echo "データベースリセット完了"

# データベースマイグレーション実行
db-migrate:
	@echo "データベースマイグレーションを実行中..."
	docker-compose -f docker-compose.common.yml -f docker-compose.desktop.yml exec backend alembic upgrade head

# サービスの状態確認
status:
	@echo "サービスの状態を確認中..."
	docker-compose -f docker-compose.common.yml -f docker-compose.desktop.yml ps

# バックエンドのシェルに接続
backend-shell:
	@echo "バックエンドコンテナのシェルに接続中..."
	docker-compose -f docker-compose.common.yml -f docker-compose.desktop.yml exec backend bash

# フロントエンドのシェルに接続
frontend-shell:
	@echo "フロントエンドコンテナのシェルに接続中..."
	docker-compose -f docker-compose.common.yml -f docker-compose.desktop.yml exec frontend-dev sh

# データベースのシェルに接続
db-shell:
	@echo "PostgreSQLコンテナのシェルに接続中..."
	docker-compose -f docker-compose.common.yml exec postgres psql -U ai_secretary_user -d ai_secretary

# ログの確認（特定のサービス）
logs-backend:
	docker-compose -f docker-compose.common.yml -f docker-compose.desktop.yml logs -f backend

logs-frontend:
	docker-compose -f docker-compose.common.yml -f docker-compose.desktop.yml logs -f frontend-dev

logs-postgres:
	docker-compose -f docker-compose.common.yml logs -f postgres

logs-redis:
	docker-compose -f docker-compose.common.yml logs -f redis

# 環境別のログ確認
logs-desktop:
	docker-compose -f docker-compose.common.yml -f docker-compose.desktop.yml logs -f

logs-wsl:
	docker-compose -f docker-compose.common.yml -f docker-compose.wsl.yml logs -f

logs-tablet:
	docker-compose -f docker-compose.common.yml -f docker-compose.tablet.yml logs -f
```

## 🔧 環境変数設定

### 環境設定スクリプト (scripts/setup-env.sh)
```bash
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

# テンプレートファイルが存在するか確認
if [ ! -f ".env.example" ]; then
    echo "エラー: テンプレートファイル .env.example が見つかりません"
    exit 1
fi

# 環境ごとの設定ファイルが存在しない場合、テンプレートからコピーする
if [ ! -f "$ENV_FILE" ]; then
    echo "情報: $ENV_FILE が存在しないため、.env.example からコピーします"
    cp ".env.example" "$ENV_FILE"
fi

# .envファイルの作成
echo "環境変数ファイルを設定中..."
cp "$ENV_FILE" .env

# APIキーの設定確認
echo ""
echo "API設定の確認:"
echo "=============="

# Gemini APIキーの確認
if grep -q "your_gemini_api_key_here" .env; then
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
```

## 📊 パフォーマンス最適化

### 1. リソース制限
```yaml
# デスクトップVM用（高リソース）
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '1.0'
    reservations:
      memory: 1G
      cpus: '0.5'

# WSL用（中リソース）
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '0.5'
    reservations:
      memory: 512M
      cpus: '0.25'

# タブレット用（低リソース）
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '0.25'
    reservations:
      memory: 256M
      cpus: '0.1'
```

### 2. ヘルスチェック設定
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### 3. ボリューム最適化
```yaml
volumes:
  # 開発用：ホストマウント
  - ./backend:/app
  - /app/__pycache__  # Pythonキャッシュ除外
  
  # 本番用：名前付きボリューム
  - ai-secretary-postgres-data:/var/lib/postgresql/data
  - ai-secretary-redis-data:/data
```

## 🔒 セキュリティ設定

### 1. ネットワーク分離
```yaml
networks:
  ai-secretary-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### 2. 環境変数の管理
```bash
# .env.example
DATABASE_URL=postgresql+asyncpg://ai_secretary_user:ai_secretary_password@postgres:5432/ai_secretary
REDIS_URL=redis://redis:6379
GEMINI_API_KEY=your_gemini_api_key_here
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
DEBUG=true
LOG_LEVEL=DEBUG
```

### 3. シークレット管理
```yaml
# docker-compose.override.yml（本番環境用）
services:
  backend:
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    secrets:
      - gemini_api_key
    configs:
      - app_config

secrets:
  gemini_api_key:
    external: true

configs:
  app_config:
    file: ./config/production.yml
```

このDocker設定により、環境別に最適化された開発・本番環境を構築できます。
