# AI Secretary Team - プロジェクト完全概要

## 📋 プロジェクト概要
AI Secretary Teamは、AIアシスタントチームによる効率的なタスク管理とコラボレーションを実現するシステムです。

## 🏗️ プロジェクト構造

### ルートディレクトリ
```
ai-secretary-team/
├── .git/                          # Gitリポジトリ
├── .github/                       # GitHub Actions設定
├── .cursor/                       # Cursor IDE設定
├── .claude/                       # Claude設定
├── ai_secretary_core/            # AI秘書コア機能
├── ai-secretary-team-main-docs-backup/  # ドキュメントバックアップ
├── backend/                       # バックエンド（FastAPI）
├── frontend/                      # フロントエンド（React + Vite）
├── tools/                         # 開発ツール
├── docs/                          # プロジェクトドキュメント
├── database/                      # データベース設定
├── scripts/                       # スクリプト
├── work-logs/                     # 作業ログ
├── logs/                          # ログファイル
├── temp-archive/                  # 一時アーカイブ
└── session-handover/              # セッション引き継ぎ
```

## 🐳 Docker環境設定

### docker-compose.common.yml
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ai_secretary
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  pgadmin:
    image: dpage/pgadmin4
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@example.com
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "5050:80"
    depends_on:
      postgres:
        condition: service_healthy

volumes:
  postgres_data:
```

### docker-compose.desktop.yml
```yaml
version: '3.8'
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.desktop
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/ai_secretary
      - REDIS_URL=redis://redis:6379
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
      - ./logs:/app/logs

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.desktop
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend

  frontend-dev:
    build:
      context: ./frontend
      dockerfile: Dockerfile.desktop
    ports:
      - "3001:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
    depends_on:
      - backend
```

## 🚀 バックエンド（FastAPI）

### ディレクトリ構造
```
backend/
├── alembic/                       # データベースマイグレーション
├── app/                           # アプリケーションコード
│   ├── api/                       # APIルーター
│   │   └── v1/                    # API v1
│   │       ├── endpoints/         # APIエンドポイント
│   │       │   └── assistants.py  # アシスタント管理API
│   │       └── api.py             # APIルーター統合
│   ├── core/                      # コア設定
│   ├── models/                    # データモデル
│   ├── schemas/                   # Pydanticスキーマ
│   │   └── assistant.py           # アシスタントスキーマ
│   └── main.py                    # メインアプリケーション
├── database/                      # データベース初期化
├── Dockerfile                     # Docker設定
├── Dockerfile.desktop            # デスクトップ用Docker設定
├── requirements.txt               # Python依存関係
└── pytest.ini                    # テスト設定
```

### 主要ファイル

#### backend/app/main.py
```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.v1.api import api_router
from app.core.database import engine
from app.models import models

@asynccontextmanager
async def lifespan(app: FastAPI):
    # アプリケーション起動時に実行される処理
    async with engine.begin() as conn:
        # development用: テーブルを（もしなければ）作成する
        # productionではAlembicで管理するので不要
        await conn.run_sync(models.Base.metadata.create_all)
    yield
    # アプリケーション終了時に実行される処理

app = FastAPI(
    title="AI秘書チーム・プラットフォーム",
    description="AI秘書チームによる統合的なプロジェクト管理・ワークフロー・知識管理プラットフォーム",
    version="1.0.0",
    lifespan=lifespan
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy"}
```

#### backend/app/api/v1/api.py
```python
# backend/app/api/v1/api.py
from fastapi import APIRouter
from app.api.v1.endpoints import assistants 

api_router = APIRouter()
api_router.include_router(assistants.router, prefix="/assistants", tags=["Assistants"])
```

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
# backend/app/schemas/assistant.py
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

#### backend/app/core/config.py
```python
# backend/app/core/config.py
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# .envファイルから環境変数を読み込みます
load_dotenv()

class Settings(BaseSettings):
    """
    アプリケーションの設定を管理するクラスです。
    環境変数から値を読み込みます。
    """
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_default_secret_key")

    class Config:
        case_sensitive = True

settings = Settings()
```

#### backend/app/core/database.py
```python
# backend/app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True
)

AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_async_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

#### backend/app/models/models.py
```python
# backend/app/models/models.py
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
import uuid
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    last_login_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    assistants = relationship("AIAssistant", back_populates="user")


class AIAssistant(Base):
    __tablename__ = "assistants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    personality_template_id = Column(UUID(as_uuid=True), index=True) # 外部キー制約は後で追加
    voice_id = Column(UUID(as_uuid=True), index=True) # 外部キー制約は後で追加
    avatar_id = Column(UUID(as_uuid=True), index=True) # 外部キー制約は後で追加
    default_llm_model = Column(String(100), default="gemini-pro")
    custom_system_prompt = Column(Text)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    is_public = Column(Boolean, nullable=False, default=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="assistants")
```

#### backend/requirements.txt
```txt
# FastAPI and web framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
asyncpg==0.29.0

# Redis
redis==5.0.1
aioredis==2.0.1

# AI and LangGraph
langgraph==0.0.20
langchain==0.0.350
langchain-google-genai==0.0.5
google-generativeai==0.3.2

# Vector database
pgvector==0.2.4

# Environment and configuration
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Authentication and security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# File handling
aiofiles==23.2.1
Pillow==10.1.0

# HTTP client
httpx==0.25.2
aiohttp==3.9.1

# Utilities
python-dateutil==2.8.2
pytz==2023.3

# Development and testing
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.11.0
isort==5.12.0
flake8==6.1.0

# Monitoring and logging
structlog==23.2.0
```

#### backend/pytest.ini
```ini
[pytest]
asyncio_mode = auto
python_files = tests/**/test_*.py
addopts = -v --cov=app --cov-report=term-missing
```

### Dockerfile設定

#### backend/Dockerfile.desktop
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# システム依存関係のインストール
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# ポート8000を公開
EXPOSE 8000

# アプリケーション起動
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"]
```

## ⚛️ フロントエンド（React + TypeScript + Vite）

### ディレクトリ構造
```
frontend/
├── public/                        # 静的ファイル
├── src/                           # ソースコード
│   ├── api/                       # APIクライアント
│   │   ├── client.ts              # 基本APIクライアント
│   │   └── assistants.ts          # アシスタントAPI
│   ├── components/                # Reactコンポーネント
│   │   ├── Layout.tsx             # レイアウトコンポーネント
│   │   ├── Header.tsx             # ヘッダーコンポーネント
│   │   └── Sidebar.tsx            # サイドバーコンポーネント
│   ├── pages/                     # ページコンポーネント
│   │   └── AssistantsPage.tsx     # アシスタント管理ページ
│   ├── types/                     # TypeScript型定義
│   │   └── assistant.ts           # アシスタント型定義
│   ├── assets/                    # アセットファイル
│   ├── App.tsx                    # メインアプリケーション
│   ├── main.tsx                   # エントリーポイント
│   ├── App.css                    # アプリケーションスタイル
│   └── index.css                  # グローバルスタイル
├── Dockerfile                     # Docker設定
├── Dockerfile.desktop            # デスクトップ用Docker設定
├── package.json                   # Node.js依存関係
├── tsconfig.json                  # TypeScript設定（メイン）
├── tsconfig.app.json             # TypeScript設定（アプリ）
├── tsconfig.node.json            # TypeScript設定（Node）
├── vite.config.ts                 # Vite設定
└── .eslintrc.json                # ESLint設定
```

### 主要ファイル

#### frontend/package.json
```json
{
  "name": "frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "lint": "eslint .",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.6.2",
    "clsx": "^2.0.0",
    "date-fns": "^2.30.0",
    "lucide-react": "^0.294.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-hook-form": "^7.48.2",
    "react-hot-toast": "^2.4.1",
    "react-router-dom": "^6.20.1",
    "@hookform/resolvers": "^3.3.2",
    "@tanstack/react-query": "^5.8.4",
    "tailwind-merge": "^2.0.0",
    "zod": "^3.22.4",
    "react-dropzone": "^14.2.3",
    "zustand": "^4.4.7"
  },
  "devDependencies": {
    "@eslint/js": "^9.33.0",
    "@types/react": "^19.1.10",
    "@types/react-dom": "^19.1.7",
    "@vitejs/plugin-react": "^5.0.0",
    "eslint": "^9.33.0",
    "eslint-plugin-react-hooks": "^5.2.0",
    "eslint-plugin-react-refresh": "^0.4.20",
    "globals": "^16.3.0",
    "typescript": "~5.8.3",
    "typescript-eslint": "^8.39.1",
    "vite": "^7.1.2"
  }
}
```

#### frontend/src/App.tsx
```tsx
// frontend/src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/Layout';
import AssistantsPage from './pages/AssistantsPage';

const queryClient = new QueryClient();

const HomePage: React.FC = () => (
  <div>
    <h1>Welcome to AI Secretary Team Platform!</h1>
    <p>This is the main content area.</p>
  </div>
);

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/assistants" element={<AssistantsPage />} />
          </Routes>
        </Layout>
      </Router>
    </QueryClientProvider>
  );
};

export default App;
```

#### frontend/src/main.tsx
```tsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

#### frontend/src/components/Layout.tsx
```tsx
// frontend/src/components/Layout.tsx
import React from 'react';
import Header from './Header';
import Sidebar from './Sidebar';

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="app-container">
      <Header />
      <div className="main-wrapper">
        <Sidebar />
        <main className="main-content">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
```

#### frontend/src/components/Header.tsx
```tsx
// frontend/src/components/Header.tsx
import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="header">
      <div className="logo">AI Secretary Team</div>
      <nav className="navigation">
        <a href="#dashboard">Dashboard</a>
        <a href="#projects">Projects</a>
        <a href="#workflows">Workflows</a>
      </nav>
      <div className="user-menu">
        <span>User</span>
      </div>
    </header>
  );
};

export default Header;
```

#### frontend/src/components/Sidebar.tsx
```tsx
// frontend/src/components/Sidebar.tsx
import React from 'react';

const Sidebar: React.FC = () => {
  return (
    <aside className="sidebar">
      <div className="sidebar-menu">
        <p>Menu</p>
        <ul>
          <li>Dashboard</li>
          <li>Projects</li>
          <li>Workflows</li>
          <li>AI Assistants</li>
          <li>Settings</li>
        </ul>
      </div>
    </aside>
  );
};

export default Sidebar;
```

#### frontend/src/pages/AssistantsPage.tsx
```tsx
// frontend/src/pages/AssistantsPage.tsx
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

#### frontend/src/types/assistant.ts
```typescript
// frontend/src/types/assistant.ts
import { z } from 'zod';

// Zodスキーマでバリデーションルールを定義
export const AssistantSchema = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),
  name: z.string().min(1, "名前は必須です").max(100),
  description: z.string().optional(),
  default_llm_model: z.string().optional(),
});

export const AssistantCreateSchema = AssistantSchema.omit({ id: true, user_id: true });

// TypeScriptの型を生成
export type Assistant = z.infer<typeof AssistantSchema>;
export type AssistantCreate = z.infer<typeof AssistantCreateSchema>;
```

#### frontend/src/api/client.ts
```typescript
// frontend/src/api/client.ts
import axios from 'axios';

// バックエンドAPIのベースURLを設定します。
// .envファイルなどから読み込むのが理想ですが、まずは直接記述します。
const API_BASE_URL = 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// リクエストインターセプター（今後の拡張用）
// ここに、リクエストが送信される前にトークンをヘッダーに付与する処理などを追加できます。
apiClient.interceptors.request.use(
  (config) => {
    // const token = localStorage.getItem('accessToken');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// レスポンスインターセプター（今後の拡張用）
// ここに、エラーレスポンスを共通でハンドリングする処理などを追加できます。
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // 例えば、401 Unauthorizedエラーの場合はログインページにリダイレクトするなど
    return Promise.reject(error);
  }
);

export default apiClient;
```

#### frontend/src/api/assistants.ts
```typescript
// frontend/src/api/assistants.ts
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

#### frontend/vite.config.ts
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
})
```

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

#### frontend/src/App.css
```css
/* frontend/src/App.css */
:root {
  font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
  line-height: 1.5;
  font-weight: 400;
  color-scheme: light dark;
  color: rgba(255, 255, 255, 0.87);
  background-color: #242424;
}

body {
  margin: 0;
  display: flex;
  min-width: 320px;
  min-height: 100vh;
}

#root {
  width: 100%;
}

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

### Dockerfile設定

#### frontend/Dockerfile.desktop
```dockerfile
FROM node:18-alpine

WORKDIR /app

# 依存関係のインストール
COPY package*.json ./
RUN npm ci --only=production

# アプリケーションコードのコピー
COPY . .

# ポート3000を公開
EXPOSE 3000

# 開発サーバー起動
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
```

## 🛠️ 開発ツール

### tools/cipher-mcp/
Cipher MCPサーバーによる高度なAI機能

#### tools/cipher-mcp/src/core/brain/
- **embedding/**: ベクトル埋め込み機能
- **llm/**: 大規模言語モデル統合
- **memAgent/**: メモリエージェント
- **reasoning/**: 推論機能
- **systemPrompt/**: システムプロンプト管理
- **tools/**: ツール統合

#### tools/cipher-mcp/src/core/storage/
- **backend/**: ストレージバックエンド
- **memory-history/**: メモリ履歴管理
- **vector_storage/**: ベクトルストレージ

### studio-agents/
AI開発チームの役割定義

#### エンジニアリングチーム
- **ai-engineer.md**: AIエンジニア
- **backend-architect.md**: バックエンドアーキテクト
- **devops-automator.md**: DevOps自動化
- **frontend-developer.md**: フロントエンド開発者
- **mobile-app-builder.md**: モバイルアプリ開発者
- **rapid-prototyper.md**: ラピッドプロトタイピング
- **test-writer-fixer.md**: テスト作成・修正

#### デザインチーム
- **ui-designer.md**: UIデザイナー
- **ux-researcher.md**: UXリサーチャー
- **visual-storyteller.md**: ビジュアルストーリーテラー
- **whimsy-injector.md**: ウィムシー注入者

#### プロダクトチーム
- **feedback-synthesizer.md**: フィードバック統合者
- **sprint-prioritizer.md**: スプリント優先順位付け
- **trend-researcher.md**: トレンドリサーチャー

## 📚 ドキュメント

### docs/01-foundation/
- **requirements/**: 要件定義
- **database/**: データベース設計
- **technical/**: 技術仕様
- **ui-ux/**: UI/UX設計

### docs/02-implementation/
- **api/**: API設計
- **deployment/**: デプロイメント
- **guides/**: 実装ガイド
- **integration/**: 統合戦略
- **maintenance/**: 保守
- **testing/**: テスト戦略

## 🔧 スクリプト

### scripts/setup-env.sh
```bash
#!/bin/bash

# 環境設定スクリプト
echo "Setting up AI Secretary Team environment..."

# 必要なディレクトリの作成
mkdir -p logs
mkdir -p temp
mkdir -p data

# 環境変数ファイルの作成
if [ ! -f .env ]; then
    cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_secretary
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Frontend Configuration
FRONTEND_HOST=0.0.0.0
FRONTEND_PORT=3000
EOF
    echo "Created .env file"
fi

echo "Environment setup complete!"
```

### build.sh
```bash
#!/bin/bash

# ビルドスクリプト
echo "Building AI Secretary Team..."

# バックエンドのビルド
echo "Building backend..."
cd backend
docker build -f Dockerfile.desktop -t ai-secretary-backend:latest .
cd ..

# フロントエンドのビルド
echo "Building frontend..."
cd frontend
docker build -f Dockerfile.desktop -t ai-secretary-frontend:latest .
cd ..

echo "Build complete!"
```

## 🚀 起動方法

### 1. 環境準備
```bash
# 依存関係のインストール
npm install
pip install -r backend/requirements.txt

# 環境設定
chmod +x scripts/setup-env.sh
./scripts/setup-env.sh
```

### 2. Docker環境起動
```bash
# 開発環境起動
docker-compose -f docker-compose.common.yml -f docker-compose.desktop.yml up -d

# ログ確認
docker-compose -f docker-compose.common.yml -f docker-compose.desktop.yml logs -f
```

### 3. 個別サービス起動
```bash
# バックエンドのみ
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# フロントエンドのみ
cd frontend
npm run dev
```

## 📊 システム構成図

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (React+Vite)  │◄──►│   (FastAPI)     │◄──►│   (PostgreSQL)  │
│   Port: 5173    │    │   Port: 8000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Redis Cache   │    │   PgAdmin       │    │   Logs          │
│   Port: 6379    │    │   Port: 5050    │    │   /logs/        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔍 監視・ログ

### ログディレクトリ
- **logs/**: アプリケーションログ
- **work-logs/**: 開発作業ログ
- **session-handover/**: セッション引き継ぎ記録

### ヘルスチェック
- **バックエンド**: `http://localhost:8000/health`
- **フロントエンド**: `http://localhost:5173` (Vite開発サーバー)
- **PgAdmin**: `http://localhost:5050`

## 📝 開発ガイドライン

### コーディング規約
- **ESLint + Prettier**: Airbnbベース + 独自ルール
- **インデント**: スペース2
- **セミコロン**: 必須
- **import順序**: 標準→外部→内部

### 命名規則
- **変数・関数**: camelCase
- **クラス**: PascalCase
- **定数**: SNAKE_CASE

### テスト
- **ユニットテスト**: Jest/Mocha必須
- **E2Eテスト**: 推奨
- **テストファイル**: `tests/`配下に配置
- **Pythonテスト**: pytest + pytest-asyncio + カバレッジ

## 🚨 トラブルシューティング

### よくある問題

#### 1. バックエンド起動エラー
```
ERROR: Error loading ASGI app. Could not import module "main"
```
**解決方法**: 作業ディレクトリとインポートパスの確認

#### 2. データベース接続エラー
```
Connection refused to postgres:5432
```
**解決方法**: PostgreSQLコンテナの起動確認

#### 3. フロントエンドビルドエラー
```
Module not found: Can't resolve './components/Layout'
```
**解決方法**: ファイルパスとimport文の確認

## 📈 今後の開発計画

### Phase 1 (完了)
- ✅ Docker環境構築
- ✅ 基本的なAPI設計
- ✅ フロントエンド基盤（React + Vite）
- ✅ データベース設計（PostgreSQL + UUID）
- ✅ 非同期データベース対応
- ✅ APIエンドポイント実装（アシスタント管理）
- ✅ フロントエンドページ実装（アシスタント管理）
- ✅ テスト環境構築（pytest + カバレッジ）

### Phase 2 (計画中)
- 🔄 AI機能の統合（LangChain, LangGraph）
- 🔄 ユーザー認証システム
- 🔄 リアルタイム通信
- 🔄 高度なUI/UX（Tailwind CSS）

### Phase 3 (将来)
- 📋 モバイルアプリ対応
- 📋 クラウドデプロイ
- 📋 スケーラビリティ向上
- 📋 セキュリティ強化

---

**最終更新**: 2025-08-19
**バージョン**: 1.0.0
**ステータス**: Phase 1 完了
**技術スタック**: FastAPI + React + Vite + PostgreSQL + Redis
**テスト環境**: pytest + pytest-asyncio + カバレッジ
**フロントエンド**: React Query + Zod + Axios
