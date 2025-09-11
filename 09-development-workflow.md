# AI秘書チーム・プラットフォーム - 開発ワークフロー

**作成日**: 2025年8月17日  
**作成者**: 中野五月（Claude Code）  
**バージョン**: 1.0

## 🔄 開発ワークフロー概要

### 開発フロー
```
Feature Request → Planning → Development → Testing → Review → Deploy
      ↓              ↓           ↓          ↓        ↓        ↓
   Issue作成    設計・実装計画   コーディング   テスト    PR作成   本番デプロイ
```

### ブランチ戦略
- **main**: 本番環境用（安定版）
- **develop**: 開発環境用（統合ブランチ）
- **feature/**: 機能開発用
- **hotfix/**: 緊急修正用
- **release/**: リリース準備用

## 🛠️ 開発環境セットアップ

### 前提条件
- Docker 20.10+
- Docker Compose 2.0+
- Git 2.30+
- Node.js 18+（ローカル開発用）
- Python 3.12+（ローカル開発用）

### 初期セットアップ
```bash
# 1. リポジトリのクローン
git clone https://github.com/your-org/ai-secretary-team.git
cd ai-secretary-team

# 2. 環境変数の設定
cp .env.example .env
# .envファイルを編集してAPIキーを設定

# 3. 開発環境の起動
make dev-desktop

# 4. 依存関係のインストール（ローカル開発用）
cd backend && pip install -r requirements.txt
cd ../frontend && npm install
```

## 📋 開発プロセス

### 1. 機能開発フロー

#### ステップ1: イシュー作成
```markdown
# イシューテンプレート
## 機能概要
- 機能名: [機能名]
- 優先度: [High/Medium/Low]
- 見積もり: [1-8時間]

## 詳細
### 要件
- [ ] 要件1
- [ ] 要件2

### 受け入れ基準
- [ ] 基準1
- [ ] 基準2

### 技術的考慮事項
- 影響範囲
- 依存関係
- リスク

### テスト計画
- [ ] ユニットテスト
- [ ] 統合テスト
- [ ] E2Eテスト
```

#### ステップ2: ブランチ作成
```bash
# 機能ブランチの作成
git checkout develop
git pull origin develop
git checkout -b feature/assistant-voice-settings

# ブランチの命名規則
# feature/機能名
# hotfix/修正内容
# release/バージョン番号
```

#### ステップ3: 開発
```bash
# 開発開始
git checkout feature/assistant-voice-settings

# 定期的なコミット
git add .
git commit -m "feat: add voice settings to assistant model"

# コミットメッセージの規則
# feat: 新機能
# fix: バグ修正
# docs: ドキュメント更新
# style: コードスタイル修正
# refactor: リファクタリング
# test: テスト追加
# chore: その他の変更
```

#### ステップ4: テスト
```bash
# バックエンドテスト
cd backend
pytest tests/ -v --cov=app

# フロントエンドテスト
cd frontend
npm run test

# E2Eテスト
npm run test:e2e

# 全テスト実行
make test
```

#### ステップ5: プルリクエスト作成
```markdown
# PRテンプレート
## 変更内容
- [ ] 変更1
- [ ] 変更2

## テスト
- [ ] ユニットテスト追加
- [ ] 統合テスト追加
- [ ] E2Eテスト追加
- [ ] 手動テスト実施

## チェックリスト
- [ ] コードレビュー依頼
- [ ] ドキュメント更新
- [ ] 破壊的変更なし
- [ ] パフォーマンス影響なし
```

### 2. コードレビュープロセス

#### レビュー観点
```markdown
## コード品質
- [ ] 可読性
- [ ] 保守性
- [ ] パフォーマンス
- [ ] セキュリティ

## テスト
- [ ] テストカバレッジ
- [ ] テストの品質
- [ ] エッジケースの考慮

## ドキュメント
- [ ] コメントの適切性
- [ ] README更新
- [ ] API仕様書更新
```

#### レビューコメント例
```markdown
# 良い例
@username この関数は複雑すぎるので、小さな関数に分割することを検討してください。

# 改善案
```python
def process_user_data(user_data):
    validated_data = validate_user_data(user_data)
    processed_data = transform_user_data(validated_data)
    return save_user_data(processed_data)
```

# 悪い例
@username このコードは良くない
```

### 3. デプロイメントフロー

#### 開発環境デプロイ
```bash
# 自動デプロイ（developブランチへのマージ時）
git checkout develop
git pull origin develop
git merge feature/assistant-voice-settings
git push origin develop

# 手動デプロイ
make deploy-staging
```

#### 本番環境デプロイ
```bash
# リリースブランチ作成
git checkout develop
git checkout -b release/v1.2.0
git push origin release/v1.2.0

# リリース準備
# - バージョン番号更新
# - CHANGELOG更新
# - 最終テスト

# 本番デプロイ
git checkout main
git merge release/v1.2.0
git tag v1.2.0
git push origin main --tags
```

## 🔧 開発ツール

### エディター設定

#### VSCode設定 (.vscode/settings.json)
```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true,
    "source.organizeImports": true
  },
  "python.defaultInterpreterPath": "./backend/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "typescript.preferences.importModuleSpecifier": "relative",
  "eslint.workingDirectories": ["frontend"],
  "files.associations": {
    "*.md": "markdown"
  }
}
```

#### VSCode拡張機能 (.vscode/extensions.json)
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.pylint",
    "ms-python.black-formatter",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next",
    "ms-playwright.playwright",
    "ms-vscode.test-adapter-converter"
  ]
}
```

### 開発用スクリプト

#### package.jsonスクリプト
```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "lint:fix": "eslint . --ext ts,tsx --fix",
    "type-check": "tsc --noEmit"
  }
}
```

#### Makefileコマンド
```makefile
# 開発用コマンド
dev-setup: setup-env build-desktop up
dev-logs: logs-desktop
dev-shell-backend: backend-shell
dev-shell-frontend: frontend-shell
dev-shell-db: db-shell

# テスト用コマンド
test: test-backend test-frontend
test-backend:
	cd backend && pytest tests/ -v --cov=app
test-frontend:
	cd frontend && npm run test
test-e2e:
	cd frontend && npm run test:e2e

# 品質チェック
lint: lint-backend lint-frontend
lint-backend:
	cd backend && black . && isort . && flake8 .
lint-frontend:
	cd frontend && npm run lint:fix

# データベース操作
db-migrate:
	docker-compose exec backend alembic upgrade head
db-reset: down
	docker volume rm ai-secretary-team_ai-secretary-postgres-data || true
	$(MAKE) up
db-seed:
	docker-compose exec backend python scripts/seed_data.py
```

## 📊 品質管理

### コード品質チェック

#### バックエンド品質チェック
```bash
# コードフォーマット
black backend/
isort backend/

# リント
flake8 backend/

# 型チェック
mypy backend/

# セキュリティチェック
bandit -r backend/
```

#### フロントエンド品質チェック
```bash
# リント
npm run lint

# 型チェック
npm run type-check

# ビルドチェック
npm run build
```

### パフォーマンス監視

#### バックエンドパフォーマンス
```python
# パフォーマンステスト
import time
import asyncio
from app.services.routing.orchestrator import RoutingOrchestrator

async def performance_test():
    orchestrator = RoutingOrchestrator()
    
    start_time = time.time()
    result = await orchestrator.route_request("Test prompt")
    end_time = time.time()
    
    print(f"Response time: {end_time - start_time:.2f}s")
    assert end_time - start_time < 5.0  # 5秒以内
```

#### フロントエンドパフォーマンス
```typescript
// パフォーマンステスト
import { performance } from 'perf_hooks';

describe('Performance Tests', () => {
  it('should load assistants within 2 seconds', async () => {
    const start = performance.now();
    
    const { result } = renderHook(() => useAssistants());
    
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });
    
    const end = performance.now();
    expect(end - start).toBeLessThan(2000);
  });
});
```

## 🐛 デバッグ

### バックエンドデバッグ

#### ログ設定
```python
# app/core/logging.py
import logging
import structlog

# 構造化ログの設定
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()
```

#### デバッグ用エンドポイント
```python
# app/api/v1/endpoints/debug.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_db

router = APIRouter()

@router.get("/debug/health")
async def debug_health():
    """デバッグ用ヘルスチェック"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@router.get("/debug/db-status")
async def debug_db_status(db: AsyncSession = Depends(get_async_db)):
    """データベース接続状態確認"""
    try:
        result = await db.execute("SELECT 1")
        return {"database": "connected", "result": result.scalar()}
    except Exception as e:
        return {"database": "error", "error": str(e)}
```

### フロントエンドデバッグ

#### デバッグツール
```typescript
// src/utils/debug.ts
export const debug = {
  log: (message: string, data?: any) => {
    if (process.env.NODE_ENV === 'development') {
      console.log(`[DEBUG] ${message}`, data);
    }
  },
  
  error: (message: string, error?: Error) => {
    if (process.env.NODE_ENV === 'development') {
      console.error(`[ERROR] ${message}`, error);
    }
  },
  
  api: (url: string, method: string, data?: any) => {
    if (process.env.NODE_ENV === 'development') {
      console.log(`[API] ${method} ${url}`, data);
    }
  }
};
```

#### React Developer Tools
```typescript
// src/components/DebugPanel.tsx
import React from 'react';
import { useQuery } from '@tanstack/react-query';

export const DebugPanel: React.FC = () => {
  const { data: assistants, isLoading, error } = useQuery({
    queryKey: ['assistants'],
    queryFn: getAssistants
  });

  if (process.env.NODE_ENV !== 'development') {
    return null;
  }

  return (
    <div className="debug-panel">
      <h3>Debug Panel</h3>
      <div>
        <strong>Assistants:</strong> {isLoading ? 'Loading...' : assistants?.length || 0}
      </div>
      {error && (
        <div>
          <strong>Error:</strong> {error.message}
        </div>
      )}
    </div>
  );
};
```

## 📚 ドキュメント管理

### ドキュメント更新フロー

#### 自動ドキュメント生成
```python
# docs/generate_api_docs.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
import json

def generate_openapi_schema(app: FastAPI):
    """OpenAPIスキーマを生成"""
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    with open("docs/api/openapi.json", "w") as f:
        json.dump(openapi_schema, f, indent=2)

# 実行
if __name__ == "__main__":
    from app.main import app
    generate_openapi_schema(app)
```

#### ドキュメントテンプレート
```markdown
<!-- docs/templates/feature_template.md -->
# [機能名] - 実装ガイド

## 概要
[機能の概要]

## 実装詳細
### バックエンド
- [ ] モデル定義
- [ ] APIエンドポイント
- [ ] ビジネスロジック
- [ ] テスト

### フロントエンド
- [ ] コンポーネント
- [ ] 状態管理
- [ ] API統合
- [ ] テスト

## 使用方法
[使用方法の説明]

## 注意事項
[注意事項]

## 関連ファイル
- [ファイルパス1]
- [ファイルパス2]
```

## 🔄 継続的インテグレーション

### GitHub Actions設定

#### 開発ワークフロー
```yaml
# .github/workflows/development.yml
name: Development Workflow

on:
  push:
    branches: [ develop, feature/* ]
  pull_request:
    branches: [ develop ]

jobs:
  code-quality:
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
    
    - name: Run linting
      run: |
        cd backend
        black --check .
        isort --check-only .
        flake8 .
    
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
    
    - name: Run frontend linting
      run: |
        cd frontend
        npm run lint
        npm run type-check

  tests:
    runs-on: ubuntu-latest
    needs: code-quality
    steps:
    - uses: actions/checkout@v4
    
    - name: Run backend tests
      run: |
        cd backend
        pip install -r requirements.txt
        pytest tests/ --cov=app --cov-report=xml
    
    - name: Run frontend tests
      run: |
        cd frontend
        npm ci
        npm run test:coverage
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## 🚀 リリース管理

### バージョニング戦略

#### セマンティックバージョニング
```
MAJOR.MINOR.PATCH
1.2.3

MAJOR: 破壊的変更
MINOR: 新機能追加（後方互換性あり）
PATCH: バグ修正（後方互換性あり）
```

#### リリースノート生成
```bash
# 自動リリースノート生成
git log --oneline v1.1.0..HEAD --grep="feat:" --grep="fix:" --grep="docs:" > CHANGELOG.md
```

### リリースプロセス

#### リリース準備
```bash
# 1. リリースブランチ作成
git checkout develop
git checkout -b release/v1.2.0

# 2. バージョン更新
# package.json, pyproject.toml等のバージョン更新

# 3. CHANGELOG更新
# 変更内容をCHANGELOG.mdに追加

# 4. 最終テスト
make test
make test-e2e

# 5. リリースブランチプッシュ
git add .
git commit -m "chore: prepare release v1.2.0"
git push origin release/v1.2.0
```

#### 本番リリース
```bash
# 1. mainブランチにマージ
git checkout main
git merge release/v1.2.0

# 2. タグ作成
git tag v1.2.0
git push origin main --tags

# 3. 本番デプロイ
make deploy-production

# 4. リリースブランチ削除
git branch -d release/v1.2.0
git push origin --delete release/v1.2.0
```

この開発ワークフローにより、効率的で品質の高い開発が実現できます。
