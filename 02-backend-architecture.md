# AI秘書チーム・プラットフォーム - バックエンドアーキテクチャ

**作成日**: 2025年8月17日  
**作成者**: 中野五月（Claude Code）  
**バージョン**: 1.0

## 🏗️ アーキテクチャ概要

### 技術スタック
- **フレームワーク**: FastAPI 0.104.1
- **言語**: Python 3.12
- **データベース**: PostgreSQL 16 + Redis 7
- **AI統合**: Google Gemini API
- **ORM**: SQLAlchemy 2.0.23
- **マイグレーション**: Alembic 1.12.1

### アーキテクチャパターン
- **レイヤードアーキテクチャ**
- **依存性注入**
- **非同期処理**
- **マイクロサービス志向**

## 📁 ディレクトリ構造

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # アプリケーションエントリーポイント
│   ├── api/                    # API層
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── api.py          # APIルーター統合
│   │       └── endpoints/      # エンドポイント定義
│   │           ├── assistants.py
│   │           └── routing.py
│   ├── core/                   # コア設定
│   │   ├── config.py          # 設定管理
│   │   └── database.py        # データベース接続
│   ├── models/                 # データモデル層
│   │   ├── __init__.py
│   │   ├── models.py          # 基本モデル
│   │   └── phase2_models.py   # Phase 2拡張モデル
│   ├── schemas/                # スキーマ定義
│   │   ├── assistant.py       # アシスタントスキーマ
│   │   └── routing.py         # ルーティングスキーマ
│   └── services/               # ビジネスロジック層
│       ├── __init__.py
│       └── routing/           # ルーティングサービス
│           ├── orchestrator.py
│           ├── core/
│           │   ├── agent_selector.py
│           │   ├── llm_router.py
│           │   ├── skill_matcher.py
│           │   └── task_analyzer.py
│           └── models/
│               └── routing_models.py
├── alembic/                    # データベースマイグレーション
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── tests/                      # テストファイル
│   ├── __init__.py
│   ├── conftest.py
│   └── api/
├── requirements.txt            # Python依存関係
├── alembic.ini                # Alembic設定
└── Dockerfile*                # Docker設定
```

## 🔧 コアコンポーネント

### 1. アプリケーションエントリーポイント (main.py)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.v1.api import api_router
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # アプリケーション起動時に実行される処理
    print("アプリケーションを起動します...")
    
    # NOTE: データベースの初期化はAlembicマイグレーションで管理します
    # 開発環境では: alembic upgrade head
    # 本番環境では: CI/CDパイプラインでマイグレーションを実行
    
    yield
    # アプリケーション終了時に実行される処理
    print("アプリケーションを終了します...")

app = FastAPI(
    title="AI秘書チーム・プラットフォーム",
    description="AI秘書チームによる統合的なプロジェクト管理・ワークフロー・知識管理プラットフォーム",
    version="1.0.0",
    lifespan=lifespan
)

# CORS設定（環境変数から読み込み）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy"}
```

### 2. 設定管理 (core/config.py)

```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # データベース設定
    database_url: str = "postgresql+asyncpg://ai_secretary_user:ai_secretary_password@localhost:5432/ai_secretary"
    redis_url: str = "redis://localhost:6379"
    
    # API設定
    gemini_api_key: str
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    # 環境設定
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 3. データベース接続 (core/database.py)

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 非同期エンジンの作成
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True
)

# セッションファクトリーの作成
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_async_db():
    """データベースセッションの依存性注入"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

## 🗄️ データモデル

### 1. 基本モデル (models/models.py)

```python
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey
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
    personality_template_id = Column(UUID(as_uuid=True), index=True)
    voice_id = Column(UUID(as_uuid=True), index=True)
    avatar_id = Column(UUID(as_uuid=True), index=True)
    default_llm_model = Column(String(100), default="gemini-pro")
    custom_system_prompt = Column(Text)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    is_public = Column(Boolean, nullable=False, default=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="assistants")
```

### 2. Phase 2拡張モデル (models/phase2_models.py)

```python
# Phase 2: インテリジェント・ルーティング基盤のためのモデル定義
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, JSON, Integer, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from .models import Base

class SkillDefinition(Base):
    """スキル定義モデル"""
    __tablename__ = "skill_definitions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    skill_code = Column(String(10), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    skill_type = Column(String(50), nullable=False)
    configuration = Column(JSONB, nullable=False)
    is_public = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    
    assistant_skills = relationship("AssistantSkill", back_populates="skill_definition", cascade="all, delete-orphan")

class Conversation(Base):
    """会話セッションモデル"""
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    assistant_id = Column(UUID(as_uuid=True), ForeignKey("assistants.id"))
    title = Column(String(200))
    conversation_type = Column(String(50))
    status = Column(String(50))
    voice_enabled = Column(Boolean, default=False)
    voice_id = Column(UUID(as_uuid=True), ForeignKey("voices.id"))
    conversation_metadata = Column('metadata', JSONB)
    started_at = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))
    
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    """メッセージ履歴モデル"""
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False)
    content = Column(Text)
    content_type = Column(String(50))
    parent_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"))
    message_metadata = Column('metadata', JSONB)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    conversation = relationship("Conversation", back_populates="messages")
```

## 🔌 APIエンドポイント

### 1. アシスタント管理 (api/v1/endpoints/assistants.py)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
import uuid

from app.core.database import get_async_db
from app.models.models import AIAssistant, User
from app.schemas.assistant import AssistantCreate, AssistantResponse, AssistantUpdateFinal

router = APIRouter()

@router.post("/", response_model=AssistantResponse, status_code=status.HTTP_201_CREATED)
async def create_assistant(
    *,
    db: AsyncSession = Depends(get_async_db),
    assistant_in: AssistantCreate
):
    """新しいAIアシスタント（キャラクター）を作成します。"""
    # シングルユーザー環境を前提とし、最初のユーザーを取得して紐づけます
    user_result = await db.execute(select(User).limit(1))
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Default user not found")

    db_assistant = AIAssistant(
        user_id=user.id,
        **assistant_in.dict()
    )
    db.add(db_assistant)
    await db.commit()
    await db.refresh(db_assistant)
    return db_assistant

@router.get("/", response_model=List[AssistantResponse])
async def read_assistants(
    db: AsyncSession = Depends(get_async_db),
    skip: int = 0,
    limit: int = 100
):
    """AIアシスタントのリストを取得します。"""
    result = await db.execute(select(AIAssistant).offset(skip).limit(limit))
    assistants = result.scalars().all()
    return assistants

@router.get("/{assistant_id}", response_model=AssistantResponse)
async def read_assistant(
    *,
    db: AsyncSession = Depends(get_async_db),
    assistant_id: uuid.UUID
):
    """指定されたIDのAIアシスタントを取得します。"""
    result = await db.execute(select(AIAssistant).filter(AIAssistant.id == assistant_id))
    assistant = result.scalars().first()
    if not assistant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assistant not found")
    return assistant

@router.put("/{assistant_id}", response_model=AssistantResponse)
async def update_assistant(
    *,
    db: AsyncSession = Depends(get_async_db),
    assistant_id: uuid.UUID,
    assistant_in: AssistantUpdateFinal
):
    """AIアシスタントの情報を部分的に更新します。"""
    result = await db.execute(select(AIAssistant).filter(AIAssistant.id == assistant_id))
    assistant = result.scalars().first()
    if not assistant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assistant not found")
    
    update_data = assistant_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(assistant, key, value)
        
    db.add(assistant)
    await db.commit()
    await db.refresh(assistant)
    return assistant

@router.delete("/{assistant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assistant(
    *,
    db: AsyncSession = Depends(get_async_db),
    assistant_id: uuid.UUID
):
    """AIアシスタントを削除します。"""
    result = await db.execute(select(AIAssistant).filter(AIAssistant.id == assistant_id))
    assistant = result.scalars().first()
    if not assistant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assistant not found")
    
    await db.delete(assistant)
    await db.commit()
    return None
```

### 2. ルーティング機能 (api/v1/endpoints/routing.py)

```python
from fastapi import APIRouter, Depends
from app.schemas.routing import RoutingRequest
from app.services.routing.orchestrator import RoutingOrchestrator

router = APIRouter()

@router.post("/route")
async def route_request(
    request: RoutingRequest,
    orchestrator: RoutingOrchestrator = Depends()
):
    """リクエストを適切なAI秘書にルーティングします。"""
    result = await orchestrator.route_request(request.prompt, request.assistant_id)
    return result
```

## 🔄 サービス層

### 1. ルーティングオーケストレーター (services/routing/orchestrator.py)

```python
from app.services.routing.core.task_analyzer import TaskAnalyzer
from app.services.routing.core.skill_matcher import SkillMatcher
from app.services.routing.core.agent_selector import AgentSelector
from app.services.routing.core.llm_router import LLMRouter

class RoutingOrchestrator:
    """AI秘書へのルーティングを統括するオーケストレーター"""
    
    def __init__(self):
        self.task_analyzer = TaskAnalyzer()
        self.skill_matcher = SkillMatcher()
        self.agent_selector = AgentSelector()
        self.llm_router = LLMRouter()
    
    async def route_request(self, prompt: str, assistant_id: str = None):
        """リクエストを適切なAI秘書にルーティング"""
        # 1. タスクの分析
        task_analysis = await self.task_analyzer.analyze(prompt)
        
        # 2. スキルのマッチング
        required_skills = await self.skill_matcher.match_skills(task_analysis)
        
        # 3. エージェントの選択
        selected_agent = await self.agent_selector.select_agent(
            required_skills, assistant_id
        )
        
        # 4. LLMルーティング
        response = await self.llm_router.route_to_agent(
            prompt, selected_agent, task_analysis
        )
        
        return response
```

## 🧪 テスト戦略

### 1. テスト構造

```
tests/
├── __init__.py
├── conftest.py              # テスト設定
├── api/                     # APIテスト
│   ├── test_assistants.py
│   └── test_routing.py
├── models/                  # モデルテスト
│   └── test_models.py
└── services/                # サービステスト
    └── test_routing.py
```

### 2. テスト設定 (conftest.py)

```python
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.models import Base
from app.core.database import get_async_db

# テスト用データベース
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

@pytest.fixture(scope="session")
def event_loop():
    """テスト用のイベントループ"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_db():
    """テスト用データベースセッション"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    TestingSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with TestingSessionLocal() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
```

## 🚀 デプロイメント

### 1. Docker設定

```dockerfile
# backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# 依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# アプリケーションの起動
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. 環境変数

```bash
# .env
DATABASE_URL=postgresql+asyncpg://ai_secretary_user:ai_secretary_password@postgres:5432/ai_secretary
REDIS_URL=redis://redis:6379
GEMINI_API_KEY=your_gemini_api_key_here
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
DEBUG=true
LOG_LEVEL=DEBUG
```

## 📊 パフォーマンス最適化

### 1. データベース最適化
- インデックスの適切な設定
- クエリの最適化
- 接続プールの設定

### 2. キャッシュ戦略
- Redis を使用したレスポンスキャッシュ
- セッション情報のキャッシュ
- 頻繁にアクセスされるデータのキャッシュ

### 3. 非同期処理
- FastAPIの非同期機能を活用
- データベース操作の非同期化
- 外部API呼び出しの非同期化

## 🔒 セキュリティ

### 1. 認証・認可
- JWT トークンによる認証（将来実装）
- ロールベースのアクセス制御
- API キーの安全な管理

### 2. データ保護
- パスワードのハッシュ化
- 機密情報の暗号化
- SQL インジェクション対策

### 3. 入力検証
- Pydantic スキーマによる入力検証
- ファイルアップロードの検証
- レート制限の実装

## 📈 監視・ログ

### 1. ログ設定
- 構造化ログの実装
- ログレベルの動的変更
- ログの外部送信

### 2. メトリクス
- レスポンス時間の監視
- エラー率の追跡
- リソース使用量の監視

### 3. ヘルスチェック
- データベース接続の確認
- 外部サービス依存関係の確認
- アプリケーション状態の報告
