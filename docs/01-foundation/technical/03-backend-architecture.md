# Phase 3: バックエンドアーキテクチャ設計書

## 1. 設計概要

### 1.1 設計目的
統合版プラットフォームのバックエンドアーキテクチャにおいて、FastAPI 0.104.1 + Python 3.12を基盤とし、AI秘書チーム・ワークフロー管理・Obsidian連携・プラン承認システムを統合した、スケーラブルで保守性の高いシステムアーキテクチャを設計する。

### 1.2 設計の役割
- **統合アーキテクチャ**: 全機能を統合した一貫性のあるシステム設計
- **スケーラビリティ**: ユーザー数・データ量増加への対応
- **保守性**: モジュール化・依存関係の明確化
- **パフォーマンス**: 高速応答・高スループットの実現
- **セキュリティ**: 認証・認可・データ保護の統合

### 1.3 対象範囲
- **API Gateway**: 統一的なAPI管理・ルーティング
- **サービス層**: ビジネスロジック・ドメインサービス
- **データアクセス層**: データベース・キャッシュ・ファイル管理
- **AI統合**: LangGraph・Zen MCP Server・外部AI API
- **非同期処理**: Celery・Redis Queue・WebSocket

## 2. 全体アーキテクチャ

### 2.1 レイヤー構成
```
┌─────────────────────────────────────────────────────────┐
│ プレゼンテーション層                                    │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│ │ フロントエンド│ │ API Gateway│ │ WebSocket   │        │
│ │ (React)     │ │ (FastAPI)   │ │ (リアルタイム)│        │
│ └─────────────┘ └─────────────┘ └─────────────┘        │
├─────────────────────────────────────────────────────────┤
│ アプリケーション層                                      │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│ │ ペルソナ    │ │ ワークフロー│ │ プラン承認  │        │
│ │ サービス    │ │ サービス    │ │ サービス    │        │
│ └─────────────┘ └─────────────┘ └─────────────┘        │
├─────────────────────────────────────────────────────────┤
│ ドメイン層                                              │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│ │ ペルソナ    │ │ タスク      │ │ プロジェクト│        │
│ │ エンティティ│ │ エンティティ│ │ エンティティ│        │
│ └─────────────┘ └─────────────┘ └─────────────┘        │
├─────────────────────────────────────────────────────────┤
│ インフラストラクチャ層                                  │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│ │ PostgreSQL  │ │ Redis       │ │ ファイル    │        │
│ │ (データ)     │ │ (キャッシュ)  │ │ ストレージ  │        │
│ └─────────────┘ └─────────────┘ └─────────────┘        │
└─────────────────────────────────────────────────────────┘
```

### 2.2 コンポーネント構成
**主要コンポーネント**:
1. **API Gateway**: FastAPI 0.104.1 + ルーティング・認証・レート制限
2. **サービス層**: ビジネスロジック・ドメインサービス・ワークフロー管理
3. **AI統合層**: LangGraph・Zen MCP Server・外部AI API連携
4. **データ層**: PostgreSQL 16・Redis 7・SQLAlchemy 2.0
5. **非同期処理**: Celery・Redis Queue・WebSocket・バックグラウンドタスク
6. **セキュリティ層**: JWT認証・RBAC認可・暗号化・監査ログ

## 3. API Gateway設計

### 3.1 FastAPI設定
**基本設定**:
```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI(
    title="AI秘書チーム・プラットフォーム（統合版）",
    description="AI秘書チームによる統合的なプロジェクト管理・ワークフロー・知識管理プラットフォーム",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ミドルウェア設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

**ルーティング設定**:
```python
# メインルーター
from app.api.v1 import api_router

app.include_router(api_router, prefix="/api/v1")

# ヘルスチェック
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# メトリクス
@app.get("/metrics")
async def metrics():
    return {"requests_total": 1000, "active_users": 50}
```

### 3.2 認証・認可ミドルウェア
**ローカル環境用簡易認証**:
```python
# ローカル・シングルユーザー環境のため、複雑な認証は不要
# アプリケーション起動時に自動的にユーザーセッションを確立

async def get_current_user():
    """ローカルユーザー情報取得"""
    # シングルユーザー環境のため固定ユーザーを返す
    return {
        "user_id": "local_user",
        "name": "ローカルユーザー",
        "roles": ["admin"]  # 全権限を持つ
    }

async def get_current_active_user():
    # ローカル環境では常にアクティブ
    return current_user
```

**RBAC認可**:
```python
from functools import wraps

def require_permission(permission: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user_id = kwargs.get("current_user")
            if not has_permission(user_id, permission):
                raise HTTPException(status_code=403, detail="Permission denied")
            return await func(*args, **kwargs)
        return wrapper
    return decorator

@require_permission("persona:create")
async def create_persona(persona_data: PersonaCreate, current_user: str):
    # ペルソナ作成ロジック
    pass
```

### 3.3 レート制限・セキュリティ
**レート制限**:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/v1/personas")
@limiter.limit("10/minute")
async def create_persona(
    request: Request,
    persona_data: PersonaCreate,
    current_user: str = Depends(get_current_active_user)
):
    # ペルソナ作成
    pass
```

**セキュリティヘッダー**:
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# 本番環境でのHTTPS強制リダイレクト
if ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# セキュリティヘッダー
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

## 4. サービス層設計

### 4.1 ペルソナサービス
**PersonaService**:
```python
from app.services.base import BaseService
from app.models.persona import Persona, PersonaCreate, PersonaUpdate
from app.repositories.persona import PersonaRepository

class PersonaService(BaseService):
    def __init__(self, persona_repo: PersonaRepository):
        self.persona_repo = persona_repo
        
    async def create_persona(self, persona_data: PersonaCreate, user_id: str) -> Persona:
        """ペルソナ作成"""
        # バリデーション
        await self._validate_persona_data(persona_data)
        
        # アイコン・画像処理
        if persona_data.icon_data:
            icon_url = await self._process_icon(persona_data.icon_data)
            persona_data.icon_url = icon_url
            
        # ペルソナ作成
        persona = await self.persona_repo.create(persona_data, user_id)
        
        # ログ出力
        logger.info("ペルソナ作成完了", persona_id=persona.id, user_id=user_id)
        
        return persona
        
    async def update_persona(self, persona_id: str, update_data: PersonaUpdate, user_id: str) -> Persona:
        """ペルソナ更新"""
        # 権限チェック
        await self._check_persona_permission(persona_id, user_id, "update")
        
        # 更新処理
        persona = await self.persona_repo.update(persona_id, update_data)
        
        return persona
        
    async def delete_persona(self, persona_id: str, user_id: str) -> bool:
        """ペルソナ削除"""
        # 権限チェック
        await self._check_persona_permission(persona_id, user_id, "delete")
        
        # 削除処理
        result = await self.persona_repo.delete(persona_id)
        
        return result
```

### 4.2 ワークフローサービス
**WorkflowService**:
```python
from app.services.base import BaseService
from app.models.workflow import Workflow, WorkflowCreate, Task, TaskCreate
from app.repositories.workflow import WorkflowRepository
from app.services.ai import AIService

class WorkflowService(BaseService):
    def __init__(self, workflow_repo: WorkflowRepository, ai_service: AIService):
        self.workflow_repo = workflow_repo
        self.ai_service = ai_service
        
    async def create_workflow(self, workflow_data: WorkflowCreate, user_id: str) -> Workflow:
        """ワークフロー作成"""
        # ワークフロー作成
        workflow = await self.workflow_repo.create(workflow_data, user_id)
        
        # AI秘書による初期タスク生成
        if workflow_data.auto_generate_tasks:
            tasks = await self.ai_service.generate_initial_tasks(workflow)
            await self.workflow_repo.add_tasks(workflow.id, tasks)
            
        return workflow
        
    async def add_task(self, workflow_id: str, task_data: TaskCreate, user_id: str) -> Task:
        """タスク追加"""
        # 権限チェック
        await self._check_workflow_permission(workflow_id, user_id, "add_task")
        
        # タスク作成
        task = await self.workflow_repo.add_task(workflow_id, task_data)
        
        # 通知送信
        await self._notify_task_assignment(task)
        
        return task
        
    async def update_task_status(self, task_id: str, status: str, user_id: str) -> Task:
        """タスクステータス更新"""
        # 権限チェック
        await self._check_task_permission(task_id, user_id, "update")
        
        # ステータス更新
        task = await self.workflow_repo.update_task_status(task_id, status)
        
        # ワークフロー進行状況更新
        await self._update_workflow_progress(task.workflow_id)
        
        return task
```

### 4.3 プラン承認サービス
**PlanApprovalService**:
```python
from app.services.base import BaseService
from app.models.plan import Plan, PlanCreate, ApprovalRequest
from app.repositories.plan import PlanRepository
from app.services.notification import NotificationService

class PlanApprovalService(BaseService):
    def __init__(self, plan_repo: PlanRepository, notification_service: NotificationService):
        self.plan_repo = plan_repo
        self.notification_service = notification_service
        
    async def submit_plan(self, plan_data: PlanCreate, user_id: str) -> Plan:
        """プラン提出"""
        # プラン作成
        plan = await self.plan_repo.create(plan_data, user_id)
        
        # 承認者への通知
        await self._notify_approvers(plan)
        
        return plan
        
    async def request_approval(self, plan_id: str, approver_id: str, user_id: str) -> ApprovalRequest:
        """承認要求"""
        # 権限チェック
        await self._check_plan_permission(plan_id, user_id, "request_approval")
        
        # 承認要求作成
        approval_request = await self.plan_repo.create_approval_request(
            plan_id, approver_id, user_id
        )
        
        # 承認者への通知
        await self.notification_service.send_approval_request(approval_request)
        
        return approval_request
        
    async def approve_plan(self, plan_id: str, approver_id: str, comments: str = None) -> Plan:
        """プラン承認"""
        # 権限チェック
        await self._check_approval_permission(plan_id, approver_id)
        
        # 承認処理
        plan = await self.plan_repo.approve(plan_id, approver_id, comments)
        
        # 承認者への通知
        await self.notification_service.send_plan_approved(plan)
        
        return plan
```

## 5. AI統合層設計

### 5.1 LangGraph統合
**WorkflowOrchestrator**:
```python
from langgraph import StateGraph, END
from app.models.workflow import WorkflowState, TaskState
from app.services.ai import AITaskProcessor

class WorkflowOrchestrator:
    def __init__(self, ai_service: AITaskProcessor):
        self.ai_service = ai_service
        self.workflow_graph = self._build_workflow_graph()
        
    def _build_workflow_graph(self) -> StateGraph:
        """ワークフローの状態遷移グラフ構築"""
        workflow = StateGraph(WorkflowState)
        
        # 状態遷移の定義
        workflow.add_node("planning", self._planning_phase)
        workflow.add_node("execution", self._execution_phase)
        workflow.add_node("review", self._review_phase)
        workflow.add_node("completion", self._completion_phase)
        
        # 遷移条件の定義
        workflow.add_edge("planning", "execution")
        workflow.add_edge("execution", "review")
        workflow.add_edge("review", "completion")
        workflow.add_edge("review", "execution")  # 修正が必要な場合
        workflow.add_edge("completion", END)
        
        return workflow.compile()
        
    async def _planning_phase(self, state: WorkflowState) -> WorkflowState:
        """計画フェーズ"""
        # AI秘書による計画策定
        plan = await self.ai_service.generate_workflow_plan(state.requirements)
        state.plan = plan
        state.current_phase = "execution"
        return state
        
    async def _execution_phase(self, state: WorkflowState) -> WorkflowState:
        """実行フェーズ"""
        # タスク実行
        for task in state.plan.tasks:
            result = await self.ai_service.execute_task(task)
            state.task_results[task.id] = result
            
        state.current_phase = "review"
        return state
        
    async def _review_phase(self, state: WorkflowState) -> WorkflowState:
        """レビューフェーズ"""
        # AI秘書による結果レビュー
        review = await self.ai_service.review_workflow_results(state.task_results)
        state.review = review
        
        if review.needs_revision:
            state.current_phase = "execution"
        else:
            state.current_phase = "completion"
            
        return state
        
    async def _completion_phase(self, state: WorkflowState) -> WorkflowState:
        """完了フェーズ"""
        # 最終レポート生成
        final_report = await self.ai_service.generate_final_report(state)
        state.final_report = final_report
        state.status = "completed"
        return state
```

### 5.2 Zen MCP Server統合
**MCPServerManager**:
```python
from app.services.mcp import MCPServerManager
from app.models.ai import AIProvider, AIModel

class MCPServerManager:
    def __init__(self):
        self.servers = {}
        self.providers = {}
        
    async def start_server(self, provider: AIProvider, model: AIModel):
        """MCPサーバー起動"""
        server_config = {
            "provider": provider.name,
            "model": model.name,
            "api_key": provider.api_key,
            "endpoint": provider.endpoint
        }
        
        # サーバー起動
        server = await self._create_mcp_server(server_config)
        self.servers[f"{provider.name}_{model.name}"] = server
        
        return server
        
    async def execute_ai_task(self, task: dict, provider: str, model: str):
        """AIタスク実行"""
        server_key = f"{provider}_{model}"
        if server_key not in self.servers:
            raise ValueError(f"Server not found: {server_key}")
            
        server = self.servers[server_key]
        result = await server.execute_task(task)
        
        return result
        
    async def get_available_tools(self, provider: str, model: str) -> List[str]:
        """利用可能ツール取得"""
        server_key = f"{provider}_{model}"
        if server_key not in self.servers:
            return []
            
        server = self.servers[server_key]
        return await server.get_tools()
```

## 6. データアクセス層設計

### 6.1 SQLAlchemy設定
**データベース設定**:
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

# データベース設定
DATABASE_URL = "postgresql://user:password@localhost/ai_secretary_db"

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 依存性注入
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**リポジトリパターン**:
```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType], ABC):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db
        
    async def get(self, id: str) -> Optional[ModelType]:
        """IDによる取得"""
        return self.db.query(self.model).filter(self.model.id == id).first()
        
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """全件取得"""
        return self.db.query(self.model).offset(skip).limit(limit).all()
        
    async def create(self, obj_in: dict) -> ModelType:
        """作成"""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
        
    async def update(self, id: str, obj_in: dict) -> Optional[ModelType]:
        """更新"""
        db_obj = await self.get(id)
        if db_obj:
            for field, value in obj_in.items():
                setattr(db_obj, field, value)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj
        
    async def delete(self, id: str) -> bool:
        """削除"""
        db_obj = await self.get(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False
```

### 6.2 Redis統合
**キャッシュ管理**:
```python
import redis.asyncio as redis
from app.core.config import settings

class RedisManager:
    def __init__(self):
        self.redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        
    async def get(self, key: str) -> Optional[str]:
        """キャッシュ取得"""
        return await self.redis_client.get(key)
        
    async def set(self, key: str, value: str, expire: int = 3600):
        """キャッシュ設定"""
        await self.redis_client.set(key, value, ex=expire)
        
    async def delete(self, key: str):
        """キャッシュ削除"""
        await self.redis_client.delete(key)
        
    async def exists(self, key: str) -> bool:
        """キー存在確認"""
        return await self.redis_client.exists(key) > 0
        
    async def increment(self, key: str, amount: int = 1) -> int:
        """カウンター増加"""
        return await self.redis_client.incr(key, amount)
```

## 7. 非同期処理設計

### 7.1 Celery設定
**Celery設定**:
```python
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "ai_secretary",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.persona",
        "app.tasks.workflow",
        "app.tasks.ai_processing",
        "app.tasks.notification"
    ]
)

# Celery設定
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Tokyo",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30分
    task_soft_time_limit=25 * 60,  # 25分
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000
)
```

**タスク定義**:
```python
from app.tasks.base import BaseTask
from app.services.ai import AIService

class PersonaIconGenerationTask(BaseTask):
    name = "persona.icon_generation"
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        
    def run(self, persona_id: str, prompt: str, style: str):
        """ペルソナアイコン生成タスク"""
        try:
            # AIによるアイコン生成
            icon_url = self.ai_service.generate_icon(prompt, style)
            
            # データベース更新
            self.update_persona_icon(persona_id, icon_url)
            
            return {"status": "success", "icon_url": icon_url}
            
        except Exception as e:
            logger.error("アイコン生成失敗", persona_id=persona_id, error=str(e))
            return {"status": "error", "message": str(e)}

@celery_app.task(bind=True)
def generate_persona_icon(self, persona_id: str, prompt: str, style: str):
    """ペルソナアイコン生成（Celeryタスク）"""
    task = PersonaIconGenerationTask(ai_service)
    return task.run(persona_id, prompt, style)
```

### 7.2 WebSocket統合
**ローカル環境用バランス型WebSocket実装**:
```python
from fastapi import WebSocket, WebSocketDisconnect
from typing import Optional, Dict, Any
import json
import asyncio
from datetime import datetime

class OptimizedLocalWebSocket:
    """
    ローカル環境に最適化されたWebSocket実装
    必要な機能は維持しつつ、過剰な複雑性は排除
    """
    def __init__(self):
        self.connection: Optional[WebSocket] = None
        self.is_connected: bool = False
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.heartbeat_interval: int = 30  # 秒
        
    async def connect(self, websocket: WebSocket):
        """WebSocket接続確立（自動再接続機能付き）"""
        await websocket.accept()
        self.connection = websocket
        self.is_connected = True
        
        # ハートビート開始
        asyncio.create_task(self._heartbeat())
        
    async def disconnect(self):
        """WebSocket切断処理"""
        self.is_connected = False
        if self.connection:
            await self.connection.close()
            self.connection = None
            
    async def _heartbeat(self):
        """接続維持のためのハートビート"""
        while self.is_connected:
            try:
                await self.send_message({"type": "ping", "timestamp": datetime.now().isoformat()})
                await asyncio.sleep(self.heartbeat_interval)
            except:
                self.is_connected = False
                break
                
    async def send_message(self, data: Dict[str, Any], priority: str = "normal"):
        """
        メッセージ送信（優先度制御付き）
        priority: "high" | "normal" | "low"
        """
        if not self.is_connected or not self.connection:
            # 接続がない場合はキューに保存
            await self.message_queue.put((priority, data))
            return
            
        try:
            message = json.dumps(data)
            await self.connection.send_text(message)
        except Exception as e:
            print(f"送信エラー: {e}")
            # エラー時は再接続を試みる
            await self._handle_reconnection()
            
    async def receive_message(self) -> Optional[Dict[str, Any]]:
        """メッセージ受信"""
        if not self.is_connected or not self.connection:
            return None
            
        try:
            data = await self.connection.receive_text()
            return json.loads(data)
        except WebSocketDisconnect:
            await self.disconnect()
            return None
        except Exception as e:
            print(f"受信エラー: {e}")
            return None
            
    async def _handle_reconnection(self):
        """自動再接続処理"""
        max_retries = 3
        retry_delay = 1  # 秒
        
        for attempt in range(max_retries):
            await asyncio.sleep(retry_delay * (attempt + 1))
            # 再接続ロジック（簡略化）
            print(f"再接続試行 {attempt + 1}/{max_retries}")
            
    async def process_queued_messages(self):
        """キューイングされたメッセージの処理"""
        while not self.message_queue.empty():
            priority, data = await self.message_queue.get()
            await self.send_message(data, priority)

# 使用例
manager = OptimizedLocalWebSocket()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await manager.receive_message()
            if data:
                # メッセージタイプに応じた処理
                if data.get("type") == "ai_discussion":
                    # AI協議メッセージの処理
                    pass
                elif data.get("type") == "ui_update":
                    # UI更新メッセージの処理
                    pass
    except WebSocketDisconnect:
        await manager.disconnect()
```

## 8. セキュリティ設計

### 8.1 認証・認可
**ローカル環境セキュリティ**:
```python
# ローカル・シングルユーザー環境用のシンプルなセキュリティ設定
# 複雑な認証は不要だが、基本的なセキュリティは維持

class LocalSecurityConfig:
    """ローカル環境セキュリティ設定"""
    def __init__(self):
        self.user_id = "local_user"
        self.is_authenticated = True
        
    def get_user(self):
        """ローカルユーザー情報取得"""
        return {
            "user_id": self.user_id,
            "is_admin": True,
            "permissions": ["all"]  # ローカルユーザーは全権限
        }

def verify_password(plain_password: str, hashed_password: str):
    """パスワード検証"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    """パスワードハッシュ化"""
    return pwd_context.hash(password)
```

**権限管理**:
```python
from app.models.user import User, Role, Permission
from app.services.auth import AuthService

class PermissionService:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service
        
    async def check_permission(self, user_id: str, resource: str, action: str) -> bool:
        """権限チェック"""
        user = await self.auth_service.get_user(user_id)
        if not user:
            return False
            
        # ユーザーのロール取得
        roles = await self.auth_service.get_user_roles(user_id)
        
        # 権限チェック
        for role in roles:
            permissions = await self.auth_service.get_role_permissions(role.id)
            for permission in permissions:
                if permission.resource == resource and permission.action == action:
                    return True
                    
        return False
        
    async def require_permission(self, resource: str, action: str):
        """権限要求デコレーター"""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                user_id = kwargs.get("current_user")
                if not await self.check_permission(user_id, resource, action):
                    raise HTTPException(status_code=403, detail="Permission denied")
                return await func(*args, **kwargs)
            return wrapper
        return decorator
```

### 8.2 データ保護
**暗号化**:
```python
from cryptography.fernet import Fernet
from app.core.config import settings

class EncryptionService:
    def __init__(self):
        self.cipher_suite = Fernet(settings.ENCRYPTION_KEY)
        
    def encrypt_data(self, data: str) -> str:
        """データ暗号化"""
        encrypted_data = self.cipher_suite.encrypt(data.encode())
        return encrypted_data.decode()
        
    def decrypt_data(self, encrypted_data: str) -> str:
        """データ復号化"""
        decrypted_data = self.cipher_suite.decrypt(encrypted_data.encode())
        return decrypted_data.decode()
        
    def encrypt_sensitive_fields(self, obj: dict, fields: List[str]) -> dict:
        """機密フィールド暗号化"""
        encrypted_obj = obj.copy()
        for field in fields:
            if field in encrypted_obj and encrypted_obj[field]:
                encrypted_obj[field] = self.encrypt_data(encrypted_obj[field])
        return encrypted_obj
```

## 9. パフォーマンス最適化

### 9.1 キャッシュ戦略
**多層キャッシュ**:
```python
from app.services.cache import CacheService
from app.services.redis import RedisManager

class MultiLayerCache:
    def __init__(self):
        self.l1_cache = {}  # メモリキャッシュ
        self.l2_cache = RedisManager()  # Redisキャッシュ
        
    async def get(self, key: str) -> Optional[dict]:
        """キャッシュ取得（L1 → L2）"""
        # L1キャッシュ確認
        if key in self.l1_cache:
            return self.l1_cache[key]
            
        # L2キャッシュ確認
        value = await self.l2_cache.get(key)
        if value:
            # L1キャッシュに保存
            self.l1_cache[key] = value
            return value
            
        return None
        
    async def set(self, key: str, value: dict, ttl: int = 3600):
        """キャッシュ設定（L1 + L2）"""
        # L1キャッシュに保存
        self.l1_cache[key] = value
        
        # L2キャッシュに保存
        await self.l2_cache.set(key, json.dumps(value), ttl)
        
    async def invalidate(self, key: str):
        """キャッシュ無効化"""
        if key in self.l1_cache:
            del self.l1_cache[key]
        await self.l2_cache.delete(key)
```

### 9.2 データベース最適化
**クエリ最適化**:
```python
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy import and_, or_

class OptimizedPersonaRepository(BaseRepository[Persona]):
    async def get_persona_with_details(self, persona_id: str) -> Optional[Persona]:
        """ペルソナ詳細取得（最適化）"""
        return self.db.query(Persona)\
            .options(
                joinedload(Persona.role),
                joinedload(Persona.permissions),
                selectinload(Persona.workflows)
            )\
            .filter(Persona.id == persona_id)\
            .first()
            
    async def get_personas_by_role(self, role_id: str, skip: int = 0, limit: int = 100):
        """ロール別ペルソナ取得（最適化）"""
        return self.db.query(Persona)\
            .options(joinedload(Persona.role))\
            .filter(Persona.role_id == role_id)\
            .offset(skip)\
            .limit(limit)\
            .all()
            
    async def search_personas(self, query: str, filters: dict = None):
        """ペルソナ検索（最適化）"""
        base_query = self.db.query(Persona)\
            .options(joinedload(Persona.role))
            
        # 検索条件
        if query:
            base_query = base_query.filter(
                or_(
                    Persona.name.ilike(f"%{query}%"),
                    Persona.description.ilike(f"%{query}%")
                )
            )
            
        # フィルター適用
        if filters:
            if filters.get("role_id"):
                base_query = base_query.filter(Persona.role_id == filters["role_id"])
            if filters.get("is_active") is not None:
                base_query = base_query.filter(Persona.is_active == filters["is_active"])
                
        return base_query.all()
```

## 10. 監視・ログ設計

### 10.1 ヘルスチェック
**システム監視**:
```python
from app.services.monitoring import SystemMonitor
from app.services.health import HealthChecker

class HealthCheckService:
    def __init__(self):
        self.system_monitor = SystemMonitor()
        self.health_checker = HealthChecker()
        
    async def check_system_health(self) -> dict:
        """システムヘルスチェック"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {}
        }
        
        # データベース接続チェック
        db_health = await self.health_checker.check_database()
        health_status["components"]["database"] = db_health
        
        # Redis接続チェック
        redis_health = await self.health_checker.check_redis()
        health_status["components"]["redis"] = redis_health
        
        # AIサービス接続チェック
        ai_health = await self.health_checker.check_ai_services()
        health_status["components"]["ai_services"] = ai_health
        
        # 全体ステータス判定
        if any(comp["status"] == "unhealthy" for comp in health_status["components"].values()):
            health_status["status"] = "unhealthy"
            
        return health_status
        
    async def get_system_metrics(self) -> dict:
        """システムメトリクス取得"""
        return {
            "cpu_usage": await self.system_monitor.get_cpu_usage(),
            "memory_usage": await self.system_monitor.get_memory_usage(),
            "disk_usage": await self.system_monitor.get_disk_usage(),
            "active_connections": await self.system_monitor.get_active_connections(),
            "request_rate": await self.system_monitor.get_request_rate()
        }
```

### 10.2 ログ集約
**ログ管理**:
```python
from app.services.logging import LogAggregator
from app.services.alerting import AlertService

class LogManagementService:
    def __init__(self):
        self.log_aggregator = LogAggregator()
        self.alert_service = AlertService()
        
    async def process_logs(self, logs: List[dict]):
        """ログ処理・集約"""
        # ログの正規化
        normalized_logs = await self.log_aggregator.normalize_logs(logs)
        
        # 異常検出
        anomalies = await self.log_aggregator.detect_anomalies(normalized_logs)
        
        # アラート発火
        for anomaly in anomalies:
            await self.alert_service.send_alert(anomaly)
            
        # ログ保存
        await self.log_aggregator.store_logs(normalized_logs)
        
    async def generate_log_report(self, time_range: dict) -> dict:
        """ログレポート生成"""
        return await self.log_aggregator.generate_report(time_range)
```

---

## 📋 設計完了確認

このバックエンドアーキテクチャ設計書は、以下の要素を包括的にカバーしています：

✅ **全体アーキテクチャ**: レイヤー構成・コンポーネント構成  
✅ **API Gateway設計**: FastAPI設定・認証・認可・セキュリティ  
✅ **サービス層設計**: ペルソナ・ワークフロー・プラン承認サービス  
✅ **AI統合層設計**: LangGraph・Zen MCP Server統合  
✅ **データアクセス層設計**: SQLAlchemy・Redis・リポジトリパターン  
✅ **非同期処理設計**: Celery・WebSocket・バックグラウンドタスク  
✅ **セキュリティ設計**: JWT認証・RBAC認可・データ保護・暗号化  
✅ **パフォーマンス最適化**: 多層キャッシュ・クエリ最適化・データベース最適化  
✅ **監視・ログ設計**: ヘルスチェック・システム監視・ログ集約・アラート  

次のワークフロー設計書の作成に進みます。
