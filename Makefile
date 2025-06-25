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