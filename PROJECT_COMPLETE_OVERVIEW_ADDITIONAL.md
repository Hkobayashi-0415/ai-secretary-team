# AI Secretary Team - 追加詳細情報

## 🚀 バックエンド詳細（FastAPI）

### APIエンドポイント実装

#### backend/app/api/v1/endpoints/assistants.py
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from sqlalchemy import select
from typing import List

from app.schemas.assistant import Assistant, AssistantCreate
from app.core.database import get_async_db
from app.models.models import AIAssistant

router = APIRouter()

@router.get("/", response_model=List[Assistant])
async def read_assistants(db: AsyncSession = Depends(get_async_db)):
    """
    AIアシスタントの一覧を取得します。
    """
    result = await db.execute(select(AIAssistant))
    assistants = result.scalars().all()
    return assistants

@router.post("/", response_model=Assistant)
async def create_assistant(assistant_in: AssistantCreate, db: AsyncSession = Depends(get_async_db)):
    """
    新しいAIアシスタントを作成します。
    """
    # 仮の固定ユーザーIDを生成します（将来的には認証情報から取得します）
    mock_user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    
    # 受け取ったデータと仮のユーザーIDでAIAssistantオブジェクトを作成
    db_assistant = AIAssistant(
        **assistant_in.model_dump(), 
        user_id=mock_user_id
    )
    
    # データベースセッションに追加してコミット
    db.add(db_assistant)
    await db.commit()
    await db.refresh(db_assistant)
    return db_assistant
```

#### backend/app/schemas/assistant.py
```python
import uuid
from pydantic import BaseModel, Field
from typing import Optional

class AssistantBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    default_llm_model: Optional[str] = Field("gemini-pro", max_length=100)

class AssistantCreate(AssistantBase):
    pass

class AssistantUpdate(AssistantBase):
    name: Optional[str] = Field(None, max_length=100)

class Assistant(AssistantBase):
    id: uuid.UUID
    user_id: uuid.UUID
    
    class Config:
        from_attributes = True
```

### テスト設定

#### backend/pytest.ini
```ini
[pytest]
asyncio_mode = auto
python_files = tests/**/test_*.py
addopts = -v --cov=app --cov-report=term-missing
```

#### backend/tests/conftest.py
```python
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import get_async_db
from app.models.models import Base

# テスト用のデータベースURL
TEST_DATABASE_URL = "postgresql+asyncpg://ai_secretary_user:ai_secretary_password@postgres_test:5432/ai_secretary_test"

engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

# --- Fixtureの再構築 ---

@pytest.fixture(scope="session")
def event_loop(request) -> Generator:
    """テストセッション全体で一つのイベントループを作成する"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def db() -> AsyncGenerator[AsyncSession, None]:
    """
    テストごとに、まっさらなデータベースとセッションを提供するFixture
    """
    # テストの前に、すべてのテーブルを作成
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # テストにDBセッションを渡す
    async with TestingSessionLocal() as session:
        yield session

    # テストの後に、すべてのテーブルを削除
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    テスト用のAPIクライアントを提供するFixture
    """
    # アプリケーションのDB接続を、テスト用DBに向ける
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db

    app.dependency_overrides[get_async_db] = override_get_db

    # テスト用のクライアントを生成
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # テストが終わったらオーバーライドを元に戻す
    app.dependency_overrides.clear()
```

#### backend/tests/api/v1/test_assistants.py
```python
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import get_async_db
from app.models.models import Base

# テスト用のデータベースURL
TEST_DATABASE_URL = "postgresql+asyncpg://ai_secretary_user:ai_secretary_password@postgres_test:5432/ai_secretary_test"

engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

# --- Fixtureの再構築 ---

@pytest.fixture(scope="session")
def event_loop(request) -> Generator:
    """テストセッション全体で一つのイベントループを作成する"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def db() -> AsyncGenerator[AsyncSession, None]:
    """
    テストごとに、まっさらなデータベースとセッションを提供するFixture
    """
    # テストの前に、すべてのテーブルを作成
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # テストにDBセッションを渡す
    async with TestingSessionLocal() as session:
        yield session

    # テストの後に、すべてのテーブルを削除
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    テスト用のAPIクライアントを提供するFixture
    """
    # アプリケーションのDB接続を、テスト用DBに向ける
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db

    app.dependency_overrides[get_async_db] = override_get_db

    # テスト用のクライアントを生成
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # テストが終わったらオーバーライドを元に戻す
    app.dependency_overrides.clear()


# --- 実際のテストケース ---

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """ヘルスチェックエンドポイントのテスト"""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
```

### データベースマイグレーション

#### backend/alembic/env.py
```python
# backend/alembic/env.py
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from app.models.models import Base
target_metadata = Base.metadata

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """マイグレーションを実行するためのヘルパー関数"""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # connectableを非同期で作成します
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # 非同期で接続し、同期的なマイグレーション関数を呼び出します
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    # 非同期関数をasyncioで実行します
    asyncio.run(run_migrations_online())
```

#### backend/alembic.ini
```ini
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os

sqlalchemy.url = postgresql+asyncpg://ai_secretary_user:ai_secretary_password@postgres/ai_secretary

[post_write_hooks]
hooks = black
black.type = console_scripts
black.entrypoint = black
black.options = -l 79 REVISION_SCRIPT_FILENAME

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

#### backend/alembic/versions/21953cb59bd8_create_users_and_assistants_tables.py
```python
"""Create users and assistants tables

Revision ID: 21953cb59bd8
Revises: 
Create Date: 2025-08-18 12:37:48.661844

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '21953cb59bd8'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('first_name', sa.String(length=100), nullable=True),
    sa.Column('last_name', sa.String(length=100), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_is_active'), 'users', ['is_active'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('assistants',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('personality_template_id', sa.UUID(), nullable=True),
    sa.Column('voice_id', sa.UUID(), nullable=True),
    sa.Column('avatar_id', sa.UUID(), nullable=True),
    sa.Column('default_llm_model', sa.String(length=100), nullable=True),
    sa.Column('custom_system_prompt', sa.Text(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_public', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assistants_avatar_id'), 'assistants', ['avatar_id'], unique=False)
    op.create_index(op.f('ix_assistants_is_active'), 'assistants', ['is_active'], unique=False)
    op.create_index(op.f('ix_assistants_is_public'), 'assistants', ['is_public'], unique=False)
    op.create_index(op.f('ix_assistants_personality_template_id'), 'assistants', ['personality_template_id'], unique=False)
    op.create_index(op.f('ix_assistants_user_id'), 'assistants', ['user_id'], unique=False)
    op.create_index(op.f('ix_assistants_voice_id'), 'assistants', ['voice_id'], unique=False)
    # ### end Alembic commands ###

def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_assistants_voice_id'), table_name='assistants')
    op.drop_index(op.f('ix_assistants_user_id'), table_name='assistants')
    op.drop_index(op.f('ix_assistants_personality_template_id'), table_name='assistants')
    op.drop_index(op.f('ix_assistants_is_public'), table_name='assistants')
    op.drop_index(op.f('ix_assistants_is_active'), table_name='assistants')
    op.drop_index(op.f('ix_assistants_avatar_id'), table_name='assistants')
    op.drop_table('assistants')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_is_active'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
```

## ⚛️ フロントエンド詳細（React + Vite）

### ページコンポーネント

#### frontend/src/pages/AssistantsPage.tsx
```tsx
import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getAssistants, createAssistant } from '../api/assistants';
import type { AssistantCreate } from '../types/assistant';

const AssistantsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');

  const { data: assistants, isLoading, error } = useQuery({
    queryKey: ['assistants'],
    queryFn: getAssistants,
  });

  const createMutation = useMutation({
    mutationFn: createAssistant,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assistants'] });
      setName('');
      setDescription('');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const newAssistant: AssistantCreate = { name, description };
    createMutation.mutate(newAssistant);
  };

  return (
    <div>
      <h2>AI Assistants Management</h2>
      
      <form onSubmit={handleSubmit} style={{ marginBottom: '2rem' }}>
        <h3>Create New Assistant</h3>
        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor="name">Name: </label>
          <input
            id="name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor="description">Description: </label>
          <input
            id="description"
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>
        <button type="submit" disabled={createMutation.isPending}>
          {createMutation.isPending ? 'Creating...' : 'Create Assistant'}
        </button>
        {createMutation.isError && <p>Error creating assistant.</p>}
      </form>

      <h3>Existing Assistants</h3>
      {isLoading && <p>Loading assistants...</p>}
      {error && <p>Error fetching assistants.</p>}
      <ul>
        {assistants?.map((assistant) => (
          <li key={assistant.id}>
            <strong>{assistant.name}</strong>: {assistant.description || 'No description'}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default AssistantsPage;
```

### APIクライアント

#### frontend/src/api/assistants.ts
```typescript
import apiClient from './client';
import type { Assistant, AssistantCreate } from '../types/assistant';

export const getAssistants = async (): Promise<Assistant[]> => {
  const response = await apiClient.get<Assistant[]>('/assistants');
  return response.data;
};

export const createAssistant = async (data: AssistantCreate): Promise<Assistant> => {
  const response = await apiClient.post<Assistant>('/assistants', data);
  return response.data;
};
```

### TypeScript設定

#### frontend/tsconfig.app.json
```json
{
  "compilerOptions": {
    "tsBuildInfoFile": "./node_modules/.tmp/tsconfig.app.tsbuildinfo",
    "target": "ES2022",
    "useDefineForClassFields": true,
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "verbatimModuleSyntax": true,
    "moduleDetection": "force",
    "noEmit": true,
    "jsx": "react-jsx",

    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "erasableSyntaxOnly": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedSideEffectImports": true
  },
  "include": ["src"]
}
```

#### frontend/tsconfig.node.json
```json
{
  "compilerOptions": {
    "tsBuildInfoFile": "./node_modules/.tmp/tsconfig.node.tsbuildinfo",
    "target": "ES2023",
    "lib": ["ES2023"],
    "module": "ESNext",
    "skipLibCheck": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "verbatimModuleSyntax": true,
    "moduleDetection": "force",
    "noEmit": true,

    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "erasableSyntaxOnly": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedSideEffectImports": true
  },
  "include": ["vite.config.ts"]
}
```

### スタイル設定

#### frontend/src/App.css
```css
/* Layout Styles */
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.header {
  height: 64px;
  background-color: #1a1a1a;
  border-bottom: 1px solid #333;
  display: flex;
  align-items: center;
  padding: 0 24px;
  flex-shrink: 0;
}

.logo {
  font-weight: bold;
  font-size: 1.2rem;
  margin-right: 48px;
}

.navigation {
  display: flex;
  gap: 24px;
  flex-grow: 1;
}

.user-menu {
  margin-left: auto;
}

.main-wrapper {
  display: flex;
  flex-grow: 1;
  overflow: hidden;
}

.sidebar {
  width: 280px;
  background-color: #1e1e1e;
  border-right: 1px solid #333;
  padding: 24px;
  flex-shrink: 0;
}

.main-content {
  flex-grow: 1;
  padding: 24px;
  overflow-y: auto;
}
```

### 本番環境設定

#### frontend/Dockerfile.production
```dockerfile
# Production Dockerfile for AI Secretary Frontend
FROM node:20-alpine AS builder

# Set work directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create non-root user for security
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Change ownership of the app directory
RUN chown -R nextjs:nodejs /usr/share/nginx/html && \
    chown -R nextjs:nodejs /var/cache/nginx && \
    chown -R nextjs:nodejs /var/log/nginx && \
    chown -R nextjs:nodejs /etc/nginx/conf.d

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

#### frontend/nginx.conf
```nginx
# frontend/nginx.conf
server {
    listen 3000;
    server_name localhost;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # APIリクエストをバックエンドに転送するための設定（今後のための準備）
    # location /api/ {
    #     proxy_pass http://backend:8000;
    #     proxy_set_header Host $host;
    #     proxy_set_header X-Real-IP $remote_addr;
    #     proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    #     proxy_set_header X-Forwarded-Proto $scheme;
    # }
}
```

### ESLint設定

#### frontend/eslint.config.js
```javascript
import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import tseslint from 'typescript-eslint'
import { globalIgnores } from 'eslint/config'

export default tseslint.config([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      js.configs.recommended,
      tseslint.configs.recommended,
      reactHooks.configs['recommended-latest'],
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
  },
])
```

#### frontend/index.html
```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Vite + React + TS</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

## 🔧 開発環境詳細

### テスト環境
- **Python**: pytest + pytest-asyncio + カバレッジ
- **フロントエンド**: ESLint + TypeScript strict mode
- **データベース**: PostgreSQL + Alembic
- **キャッシュ**: Redis

### コード品質
- **Python**: Black + isort + flake8
- **TypeScript**: strict mode + noUnusedLocals + noUnusedParameters
- **React**: ESLint + React Hooks rules

### 依存関係管理
- **Python**: requirements.txt + pip
- **Node.js**: package.json + npm
- **Docker**: マルチステージビルド

### 本番環境設定
- **フロントエンド**: Nginx + Node.js 20 Alpine
- **セキュリティ**: 非rootユーザー実行
- **パフォーマンス**: マルチステージビルド
- **スケーラビリティ**: 静的ファイル配信

## 📊 現在の実装状況

### 完了済み機能
- ✅ 基本的なAPI設計（FastAPI + SQLAlchemy）
- ✅ データベースモデル（User + AIAssistant）
- ✅ APIエンドポイント（アシスタント管理）
- ✅ フロントエンド基盤（React + Vite）
- ✅ ページコンポーネント（アシスタント管理）
- ✅ APIクライアント（Axios + React Query）
- ✅ 型安全性（Zod + TypeScript）
- ✅ テスト環境（pytest + カバレッジ）
- ✅ データベースマイグレーション（Alembic）
- ✅ 本番環境設定（Nginx + Docker）
- ✅ コード品質管理（ESLint + TypeScript strict）

### 進行中機能
- 🔄 ユーザー認証システム
- 🔄 AI機能統合（LangChain + LangGraph）
- 🔄 リアルタイム通信
- 🔄 高度なUI/UX

### 今後の計画
- 📋 モバイルアプリ対応
- 📋 クラウドデプロイ
- 📋 スケーラビリティ向上
- 📋 セキュリティ強化

## 🚀 開発・テスト・デプロイフロー

### 開発フロー
1. **コード作成**: TypeScript strict mode + ESLint
2. **テスト実行**: pytest + カバレッジ
3. **コード品質**: Black + isort + flake8
4. **データベース**: Alembic マイグレーション

### テストフロー
1. **ユニットテスト**: pytest + pytest-asyncio
2. **統合テスト**: FastAPI TestClient
3. **カバレッジ**: --cov=app --cov-report=term-missing
4. **データベース**: テスト用DB + 自動クリーンアップ

### デプロイフロー
1. **開発環境**: Docker Compose + ホットリロード
2. **本番環境**: マルチステージDocker + Nginx
3. **セキュリティ**: 非rootユーザー + 最小権限
4. **スケーラビリティ**: 静的ファイル配信 + API プロキシ

---

**最終更新**: 2025-08-19
**バージョン**: 1.0.0
**ステータス**: Phase 1 完了 + 詳細実装 + 本番環境準備
**技術スタック**: FastAPI + React + Vite + PostgreSQL + Redis
**テスト環境**: pytest + pytest-asyncio + カバレッジ
**フロントエンド**: React Query + Zod + Axios + TypeScript strict mode
**本番環境**: Nginx + Docker + セキュリティ設定
**データベース**: Alembic + 非同期SQLAlchemy + インデックス最適化
