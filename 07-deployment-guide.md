# AI秘書チーム・プラットフォーム - デプロイメントガイド

**作成日**: 2025年8月17日  
**作成者**: 中野五月（Claude Code）  
**バージョン**: 1.0

## 🚀 デプロイメント概要

### デプロイメント環境
- **開発環境**: ローカルDocker環境
- **ステージング環境**: クラウド仮想マシン
- **本番環境**: クラウド仮想マシン + CDN

### デプロイメント戦略
- **Blue-Green デプロイメント**: ダウンタイムゼロ
- **自動ロールバック**: 問題発生時の自動復旧
- **ヘルスチェック**: デプロイメント後の自動検証

## 🏗️ インフラ構成

### 開発環境
```
┌─────────────────────────────────────────┐
│           ローカルPC                    │
│  ┌─────────────┐  ┌─────────────────┐  │
│  │   Frontend  │  │    Backend      │  │
│  │   (React)   │  │   (FastAPI)     │  │
│  │   Port:3000 │  │   Port:8000     │  │
│  └─────────────┘  └─────────────────┘  │
│  ┌─────────────┐  ┌─────────────────┐  │
│  │ PostgreSQL  │  │     Redis       │  │
│  │   Port:5432 │  │   Port:6379     │  │
│  └─────────────┘  └─────────────────┘  │
└─────────────────────────────────────────┘
```

### 本番環境
```
┌─────────────────────────────────────────────────────────────┐
│                    Cloud Provider                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐    │
│  │   CDN       │  │   Load      │  │   Application   │    │
│  │  (CloudFlare)│  │  Balancer   │  │    Servers      │    │
│  └─────────────┘  └─────────────┘  └─────────────────┘    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐    │
│  │   Database  │  │   Cache     │  │   File Storage  │    │
│  │ (PostgreSQL)│  │   (Redis)   │  │    (S3/OSS)     │    │
│  └─────────────┘  └─────────────┘  └─────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## 📋 デプロイメント手順

### 1. 開発環境デプロイ

#### 前提条件
- Docker 20.10+
- Docker Compose 2.0+
- Git 2.30+

#### セットアップ手順
```bash
# 1. リポジトリのクローン
git clone https://github.com/your-org/ai-secretary-team.git
cd ai-secretary-team

# 2. 環境変数の設定
cp .env.example .env
# .envファイルを編集してAPIキーを設定

# 3. 開発環境の起動
make dev-desktop

# 4. アクセス確認
curl http://localhost:8000/health
open http://localhost:3000
```

#### 環境別起動コマンド
```bash
# デスクトップVM用（推奨）
make dev-desktop

# WSL用（軽量）
make dev-wsl

# タブレット用（共有対応）
make dev-tablet
```

### 2. ステージング環境デプロイ

#### 前提条件
- クラウドプロバイダーアカウント
- Terraform 1.0+
- Ansible 2.9+

#### インフラ構築
```bash
# 1. インフラの構築
cd infrastructure/terraform
terraform init
terraform plan -var-file=staging.tfvars
terraform apply -var-file=staging.tfvars

# 2. アプリケーションのデプロイ
cd ../ansible
ansible-playbook -i staging/inventory deploy.yml
```

#### ステージング環境設定
```yaml
# infrastructure/ansible/staging/group_vars/all.yml
environment: staging
domain: staging.ai-secretary.local
database_url: postgresql://user:pass@staging-db:5432/ai_secretary
redis_url: redis://staging-redis:6379
gemini_api_key: "{{ vault_gemini_api_key }}"
```

### 3. 本番環境デプロイ

#### 前提条件
- ステージング環境での動作確認完了
- 本番用ドメインの準備
- SSL証明書の取得

#### 本番デプロイ手順
```bash
# 1. 本番環境の構築
cd infrastructure/terraform
terraform plan -var-file=production.tfvars
terraform apply -var-file=production.tfvars

# 2. アプリケーションのデプロイ
cd ../ansible
ansible-playbook -i production/inventory deploy.yml

# 3. ヘルスチェック
curl https://api.ai-secretary.local/health
```

## 🔧 CI/CDパイプライン

### GitHub Actions設定

#### メインワークフロー (.github/workflows/main.yml)
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ai-secretary-team

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        cd backend
        pytest tests/
    
    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install frontend dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Run frontend tests
      run: |
        cd frontend
        npm run test
    
    - name: Build frontend
      run: |
        cd frontend
        npm run build

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Login to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Build and push backend image
      uses: docker/build-push-action@v5
      with:
        context: ./backend
        push: true
        tags: |
          ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/backend:latest
          ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/backend:${{ github.sha }}
    
    - name: Build and push frontend image
      uses: docker/build-push-action@v5
      with:
        context: ./frontend
        push: true
        tags: |
          ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/frontend:latest
          ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/frontend:${{ github.sha }}

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to staging
      uses: appleboy/ssh-action@v1.0.0
      with:
        host: ${{ secrets.STAGING_HOST }}
        username: ${{ secrets.STAGING_USER }}
        key: ${{ secrets.STAGING_SSH_KEY }}
        script: |
          cd /opt/ai-secretary-team
          git pull origin develop
          docker-compose -f docker-compose.staging.yml pull
          docker-compose -f docker-compose.staging.yml up -d
          docker system prune -f

  deploy-production:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to production
      uses: appleboy/ssh-action@v1.0.0
      with:
        host: ${{ secrets.PRODUCTION_HOST }}
        username: ${{ secrets.PRODUCTION_USER }}
        key: ${{ secrets.PRODUCTION_SSH_KEY }}
        script: |
          cd /opt/ai-secretary-team
          git pull origin main
          docker-compose -f docker-compose.production.yml pull
          docker-compose -f docker-compose.production.yml up -d
          docker system prune -f
```

### デプロイメント設定ファイル

#### ステージング環境 (docker-compose.staging.yml)
```yaml
version: '3.8'

services:
  backend:
    image: ghcr.io/ai-secretary-team/backend:latest
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - ENVIRONMENT=staging
      - CORS_ORIGINS=https://staging.ai-secretary.local
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  frontend:
    image: ghcr.io/ai-secretary-team/frontend:latest
    environment:
      - VITE_API_URL=https://api-staging.ai-secretary.local
    ports:
      - "3000:3000"
    depends_on:
      - backend
    restart: unless-stopped

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=ai_secretary
      - POSTGRES_USER=ai_secretary_user
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

#### 本番環境 (docker-compose.production.yml)
```yaml
version: '3.8'

services:
  backend:
    image: ghcr.io/ai-secretary-team/backend:latest
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - ENVIRONMENT=production
      - CORS_ORIGINS=https://ai-secretary.local
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'

  frontend:
    image: ghcr.io/ai-secretary-team/frontend:latest
    environment:
      - VITE_API_URL=https://api.ai-secretary.local
    ports:
      - "3000:3000"
    depends_on:
      - backend
    restart: unless-stopped
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 512M
          cpus: '0.25'
        reservations:
          memory: 256M
          cpus: '0.1'

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=ai_secretary
      - POSTGRES_USER=ai_secretary_user
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.25'
        reservations:
          memory: 256M
          cpus: '0.1'

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

## 🔒 セキュリティ設定

### SSL/TLS設定

#### Nginx設定 (nginx.conf)
```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }
    
    upstream frontend {
        server frontend:3000;
    }
    
    server {
        listen 80;
        server_name ai-secretary.local;
        return 301 https://$server_name$request_uri;
    }
    
    server {
        listen 443 ssl http2;
        server_name ai-secretary.local;
        
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
        ssl_prefer_server_ciphers off;
        
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### 環境変数管理

#### シークレット管理
```bash
# 本番環境用シークレット
export DATABASE_URL="postgresql://user:pass@prod-db:5432/ai_secretary"
export REDIS_URL="redis://prod-redis:6379"
export GEMINI_API_KEY="your_production_gemini_api_key"
export JWT_SECRET_KEY="your_jwt_secret_key"
export ENCRYPTION_KEY="your_encryption_key"
```

#### Vault設定
```yaml
# vault/secrets/production.yml
database_url: "postgresql://user:pass@prod-db:5432/ai_secretary"
redis_url: "redis://prod-redis:6379"
gemini_api_key: "your_production_gemini_api_key"
jwt_secret_key: "your_jwt_secret_key"
encryption_key: "your_encryption_key"
```

## 📊 監視・ログ

### 監視設定

#### Prometheus設定 (monitoring/prometheus.yml)
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ai-secretary-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'ai-secretary-frontend'
    static_configs:
      - targets: ['frontend:3000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    scrape_interval: 30s
```

#### Grafanaダッシュボード設定
```json
{
  "dashboard": {
    "title": "AI Secretary Team Platform",
    "panels": [
      {
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])"
          }
        ]
      },
      {
        "title": "Database Connections",
        "type": "graph",
        "targets": [
          {
            "expr": "pg_stat_database_numbackends"
          }
        ]
      }
    ]
  }
}
```

### ログ管理

#### ログ設定 (logging/logback.xml)
```xml
<configuration>
    <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>%d{HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>
    
    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>logs/ai-secretary.log</file>
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>logs/ai-secretary.%d{yyyy-MM-dd}.log</fileNamePattern>
            <maxHistory>30</maxHistory>
        </rollingPolicy>
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>
    
    <root level="INFO">
        <appender-ref ref="STDOUT" />
        <appender-ref ref="FILE" />
    </root>
</configuration>
```

## 🔄 バックアップ・復旧

### データベースバックアップ

#### 自動バックアップスクリプト (scripts/backup.sh)
```bash
#!/bin/bash

# データベースバックアップスクリプト
BACKUP_DIR="/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="ai_secretary"
RETENTION_DAYS=30

# バックアップディレクトリの作成
mkdir -p $BACKUP_DIR

# フルバックアップ
pg_dump -h localhost -U ai_secretary_user -d $DB_NAME \
    --format=custom --compress=9 \
    --file="$BACKUP_DIR/ai_secretary_$DATE.dump"

# バックアップの検証
if [ $? -eq 0 ]; then
    echo "バックアップが正常に完了しました: $BACKUP_DIR/ai_secretary_$DATE.dump"
else
    echo "バックアップに失敗しました"
    exit 1
fi

# 古いバックアップの削除
find $BACKUP_DIR -name "*.dump" -mtime +$RETENTION_DAYS -delete

# S3へのアップロード（オプション）
if [ -n "$S3_BUCKET" ]; then
    aws s3 cp "$BACKUP_DIR/ai_secretary_$DATE.dump" "s3://$S3_BUCKET/backups/"
fi
```

#### 復旧手順
```bash
# 1. バックアップファイルの確認
ls -la /backups/postgresql/

# 2. データベースの復旧
pg_restore -h localhost -U ai_secretary_user -d ai_secretary \
    --clean --if-exists \
    /backups/postgresql/ai_secretary_20250817_103000.dump

# 3. 復旧の確認
psql -h localhost -U ai_secretary_user -d ai_secretary -c "SELECT COUNT(*) FROM users;"
```

### アプリケーションデータバックアップ

#### ファイルバックアップスクリプト
```bash
#!/bin/bash

# アプリケーションデータバックアップ
APP_DATA_DIR="/opt/ai-secretary-team/data"
BACKUP_DIR="/backups/app-data"
DATE=$(date +%Y%m%d_%H%M%S)

# バックアップの作成
tar -czf "$BACKUP_DIR/app-data_$DATE.tar.gz" -C $APP_DATA_DIR .

# 古いバックアップの削除（30日以上）
find $BACKUP_DIR -name "app-data_*.tar.gz" -mtime +30 -delete
```

## 🚨 障害対応

### ヘルスチェック

#### ヘルスチェックスクリプト (scripts/health-check.sh)
```bash
#!/bin/bash

# ヘルスチェックスクリプト
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

### 自動復旧

#### 自動復旧スクリプト (scripts/auto-recovery.sh)
```bash
#!/bin/bash

# 自動復旧スクリプト
LOG_FILE="/var/log/ai-secretary-recovery.log"

# ログ関数
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> $LOG_FILE
}

# サービス再起動
restart_services() {
    log "Restarting services..."
    cd /opt/ai-secretary-team
    docker-compose -f docker-compose.production.yml restart
    log "Services restarted"
}

# メイン処理
log "Starting health check and recovery process"

# ヘルスチェック実行
if ! ./scripts/health-check.sh; then
    log "Health check failed, attempting recovery"
    restart_services
    
    # 復旧確認
    sleep 30
    if ./scripts/health-check.sh; then
        log "Recovery successful"
    else
        log "Recovery failed, manual intervention required"
        # 管理者に通知
        echo "AI Secretary Platform requires manual intervention" | \
            mail -s "CRITICAL: AI Secretary Platform Down" admin@ai-secretary.local
    fi
else
    log "All services are healthy"
fi
```

## 📈 パフォーマンス最適化

### データベース最適化

#### インデックス最適化
```sql
-- パフォーマンス監視用クエリ
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- 未使用インデックスの特定
SELECT 
    schemaname,
    tablename,
    indexname
FROM pg_stat_user_indexes
WHERE idx_scan = 0;
```

#### クエリ最適化
```sql
-- スロークエリの特定
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### アプリケーション最適化

#### キャッシュ戦略
```python
# Redis キャッシュ設定
CACHE_CONFIG = {
    "default_ttl": 3600,  # 1時間
    "max_connections": 100,
    "retry_on_timeout": True,
    "socket_keepalive": True,
    "socket_keepalive_options": {}
}

# キャッシュキーの命名規則
CACHE_KEY_PREFIX = "ai_secretary"
CACHE_KEYS = {
    "user": f"{CACHE_KEY_PREFIX}:user:{{user_id}}",
    "assistant": f"{CACHE_KEY_PREFIX}:assistant:{{assistant_id}}",
    "conversation": f"{CACHE_KEY_PREFIX}:conversation:{{conversation_id}}"
}
```

## 🔄 ロールバック手順

### 自動ロールバック

#### ロールバックスクリプト (scripts/rollback.sh)
```bash
#!/bin/bash

# ロールバックスクリプト
PREVIOUS_VERSION=$1
CURRENT_DIR="/opt/ai-secretary-team"
BACKUP_DIR="/backups/rollback"

if [ -z "$PREVIOUS_VERSION" ]; then
    echo "使用方法: $0 <previous_version>"
    echo "利用可能なバージョン:"
    ls -la $BACKUP_DIR/
    exit 1
fi

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log "Starting rollback to version $PREVIOUS_VERSION"

# 現在のバージョンのバックアップ
log "Creating backup of current version"
cd $CURRENT_DIR
docker-compose -f docker-compose.production.yml down
tar -czf "$BACKUP_DIR/current_$(date +%Y%m%d_%H%M%S).tar.gz" .

# 前のバージョンにロールバック
log "Rolling back to version $PREVIOUS_VERSION"
rm -rf $CURRENT_DIR/*
tar -xzf "$BACKUP_DIR/$PREVIOUS_VERSION.tar.gz" -C $CURRENT_DIR

# サービス再起動
log "Restarting services"
cd $CURRENT_DIR
docker-compose -f docker-compose.production.yml up -d

# ヘルスチェック
log "Performing health check"
sleep 30
if ./scripts/health-check.sh; then
    log "Rollback successful"
else
    log "Rollback failed, manual intervention required"
    exit 1
fi
```

このデプロイメントガイドにより、安全で効率的なデプロイメントが実現できます。
