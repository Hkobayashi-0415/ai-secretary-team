# AI秘書チーム・プラットフォーム（統合版） - 現在のAPI実装仕様書

**作成日**: 2025年8月13日  
**作成者**: 中野五月（Claude Code）  
**バージョン**: 1.0  
**目的**: 実際に実装されているAPIエンドポイントの正確な仕様定義

---

## 📋 API概要

### 1.1 基本情報
- **ベースURL**: `http://localhost:8002/api/v1`
- **APIバージョン**: v1
- **認証方式**: 現在は未実装（今後の実装予定）
- **データ形式**: JSON
- **文字エンコーディング**: UTF-8

### 1.2 実装状況
- **実装済みエンドポイント**: 7カテゴリ・約50エンドポイント
- **実装状況**: 基本的なCRUD操作完了
- **未実装機能**: 認証・認可・高度なワークフロー制御

---

## 🔧 実装済みAPIエンドポイント

### 2.1 プロジェクト管理 (`/api/v1/projects/`)

#### **プロジェクト作成**
```http
POST /api/v1/projects/
```

**リクエストボディ:**
```json
{
  "name": "プロジェクト名",
  "description": "プロジェクトの説明",
  "supervisor_mode": "hierarchical",
  "created_by_persona_id": 1
}
```

**レスポンス:**
```json
{
  "id": 1,
  "name": "プロジェクト名",
  "description": "プロジェクトの説明",
  "supervisor_mode": "hierarchical",
  "created_by_persona_id": 1,
  "created_at": "2025-08-13T00:00:00Z",
  "updated_at": "2025-08-13T00:00:00Z"
}
```

#### **プロジェクト一覧取得**
```http
GET /api/v1/projects/
```

**クエリパラメータ:**
- `supervisor_mode`: 監督者モードでフィルタ
- `created_by_persona_id`: 作成者ペルソナIDでフィルタ

**レスポンス:**
```json
[
  {
    "id": 1,
    "name": "プロジェクト名",
    "description": "プロジェクトの説明",
    "supervisor_mode": "hierarchical",
    "created_by_persona_id": 1,
    "created_at": "2025-08-13T00:00:00Z",
    "updated_at": "2025-08-13T00:00:00Z"
  }
]
```

#### **プロジェクト詳細取得**
```http
GET /api/v1/projects/{id}
```

**レスポンス:**
```json
{
  "id": 1,
  "name": "プロジェクト名",
  "description": "プロジェクトの説明",
  "supervisor_mode": "hierarchical",
  "created_by_persona_id": 1,
  "created_at": "2025-08-13T00:00:00Z",
  "updated_at": "2025-08-13T00:00:00Z"
}
```

#### **プロジェクト更新**
```http
PUT /api/v1/projects/{id}
```

**リクエストボディ:**
```json
{
  "name": "更新されたプロジェクト名",
  "description": "更新された説明"
}
```

#### **プロジェクト削除**
```http
DELETE /api/v1/projects/{id}
```

**レスポンス:**
```json
{
  "success": true,
  "message": "プロジェクトが削除されました"
}
```

### 2.2 ペルソナ管理 (`/api/v1/personas/`)

#### **ペルソナテンプレート作成**
```http
POST /api/v1/personas/templates/
```

**リクエストボディ:**
```json
{
  "name": "ペルソナ名",
  "character_name": "キャラクター名",
  "character_description": "キャラクターの説明",
  "personality_traits": {
    "traits": ["真面目", "努力家", "責任感"]
  },
  "communication_style": {
    "style": "丁寧語",
    "tone": "親しみやすい"
  },
  "specialization": "開発・品質管理",
  "is_active": true
}
```

**レスポンス:**
```json
{
  "id": 1,
  "name": "ペルソナ名",
  "character_name": "キャラクター名",
  "character_description": "キャラクターの説明",
  "personality_traits": {
    "traits": ["真面目", "努力家", "責任感"]
  },
  "communication_style": {
    "style": "丁寧語",
    "tone": "親しみやすい"
  },
  "specialization": "開発・品質管理",
  "is_active": true,
  "created_at": "2025-08-13T00:00:00Z",
  "updated_at": "2025-08-13T00:00:00Z"
}
```

#### **ペルソナテンプレート一覧取得**
```http
GET /api/v1/personas/templates/
```

**クエリパラメータ:**
- `is_active`: アクティブフラグでフィルタ
- `specialization`: 専門分野でフィルタ

#### **ペルソナテンプレート詳細取得**
```http
GET /api/v1/personas/templates/{id}
```

#### **ペルソナテンプレート更新**
```http
PUT /api/v1/personas/templates/{id}
```

#### **ペルソナテンプレート削除**
```http
DELETE /api/v1/personas/templates/{id}
```

#### **AIアシスタント作成**
```http
POST /api/v1/personas/assistants/
```

**リクエストボディ:**
```json
{
  "personality_template_id": 1,
  "name": "アシスタント名",
  "description": "アシスタントの説明",
  "capabilities": [
    {
      "skill_name": "Python開発",
      "skill_level": "expert",
      "description": "Pythonでの開発支援"
    }
  ],
  "is_active": true
}
```

#### **AIアシスタント一覧取得**
```http
GET /api/v1/personas/assistants/
```

**クエリパラメータ:**
- `personality_template_id`: ペルソナテンプレートIDでフィルタ
- `is_active`: アクティブフラグでフィルタ

#### **AIアシスタント詳細取得**
```http
GET /api/v1/personas/assistants/{id}
```

#### **AIアシスタント更新**
```http
PUT /api/v1/personas/assistants/{id}
```

#### **AIアシスタント削除**
```http
DELETE /api/v1/personas/assistants/{id}
```

### 2.3 チーム管理 (`/api/v1/teams/`)

#### **チーム作成**
```http
POST /api/v1/teams/
```

**リクエストボディ:**
```json
{
  "name": "チーム名",
  "description": "チームの説明",
  "team_type": "development",
  "project_id": 1,
  "created_by_persona_id": 1
}
```

**レスポンス:**
```json
{
  "id": 1,
  "name": "チーム名",
  "description": "チームの説明",
  "team_type": "development",
  "project_id": 1,
  "created_by_persona_id": 1,
  "created_at": "2025-08-13T00:00:00Z",
  "updated_at": "2025-08-13T00:00:00Z"
}
```

#### **チーム一覧取得**
```http
GET /api/v1/teams/
```

**クエリパラメータ:**
- `project_id`: プロジェクトIDでフィルタ
- `team_type`: チームタイプでフィルタ

#### **チーム詳細取得**
```http
GET /api/v1/teams/{id}
```

#### **チーム更新**
```http
PUT /api/v1/teams/{id}
```

#### **チーム削除**
```http
DELETE /api/v1/teams/{id}
```

#### **チームメンバー追加**
```http
POST /api/v1/teams/{id}/members
```

**リクエストボディ:**
```json
{
  "persona_id": 1,
  "role": "developer",
  "permissions": ["read", "write"]
}
```

#### **チームメンバー一覧取得**
```http
GET /api/v1/teams/{id}/members
```

**レスポンス:**
```json
[
  {
    "id": 1,
    "team_id": 1,
    "persona_id": 1,
    "role": "developer",
    "permissions": ["read", "write"],
    "joined_at": "2025-08-13T00:00:00Z"
  }
]
```

#### **チームメンバー更新**
```http
PUT /api/v1/teams/{id}/members/{member_id}
```

#### **チームメンバー削除**
```http
DELETE /api/v1/teams/{id}/members/{member_id}
```

### 2.4 ワークスペース管理 (`/api/v1/workspaces/`)

#### **ワークスペース設定作成**
```http
POST /api/v1/workspaces/
```

**リクエストボディ:**
```json
{
  "workspace_name": "workspace_name",
  "workspace_type": "persona",
  "persona_id": 1,
  "project_id": 1,
  "config": {
    "environment": "development",
    "tools": ["claude", "gemini"]
  }
}
```

**レスポンス:**
```json
{
  "id": 1,
  "workspace_name": "workspace_name",
  "workspace_type": "persona",
  "persona_id": 1,
  "project_id": 1,
  "config": {
    "environment": "development",
    "tools": ["claude", "gemini"]
  },
  "created_at": "2025-08-13T00:00:00Z",
  "updated_at": "2025-08-13T00:00:00Z"
}
```

#### **ワークスペース設定一覧取得**
```http
GET /api/v1/workspaces/
```

**クエリパラメータ:**
- `workspace_type`: ワークスペースタイプでフィルタ
- `persona_id`: ペルソナIDでフィルタ
- `project_id`: プロジェクトIDでフィルタ

#### **ワークスペース設定詳細取得**
```http
GET /api/v1/workspaces/{id}
```

#### **ワークスペース設定更新**
```http
PUT /api/v1/workspaces/{id}
```

#### **ワークスペース設定削除**
```http
DELETE /api/v1/workspaces/{id}
```

#### **ワークスペース実行**
```http
POST /api/v1/workspaces/{id}/execute
```

**リクエストボディ:**
```json
{
  "command": "execute_workflow",
  "parameters": {
    "workflow_id": 1
  }
}
```

**レスポンス:**
```json
{
  "execution_id": "exec_123",
  "status": "running",
  "workspace_id": 1,
  "command": "execute_workflow",
  "start_time": "2025-08-13T00:00:00Z"
}
```

#### **ワークスペース実行状況取得**
```http
GET /api/v1/workspaces/{id}/status
```

**レスポンス:**
```json
{
  "workspace_config_id": 1,
  "status": "running",
  "last_execution": {
    "execution_id": "exec_123",
    "start_time": "2025-08-13T00:00:00Z",
    "command": "execute_workflow"
  },
  "statistics": {
    "total_executions": 5,
    "successful_executions": 4,
    "success_rate": 80.0
  }
}
```

### 2.5 監督者管理 (`/api/v1/supervisors/`)

#### **監督者作成**
```http
POST /api/v1/supervisors/
```

**リクエストボディ:**
```json
{
  "persona_id": 1,
  "project_id": 1,
  "permission_level": "admin",
  "supervision_scope": "quality",
  "is_active": true
}
```

**レスポンス:**
```json
{
  "id": 1,
  "persona_id": 1,
  "project_id": 1,
  "permission_level": "admin",
  "supervision_scope": "quality",
  "is_active": true,
  "created_at": "2025-08-13T00:00:00Z",
  "updated_at": "2025-08-13T00:00:00Z"
}
```

#### **監督者一覧取得**
```http
GET /api/v1/supervisors/
```

**クエリパラメータ:**
- `project_id`: プロジェクトIDでフィルタ
- `permission_level`: 権限レベルでフィルタ
- `supervision_scope`: 監督範囲でフィルタ

#### **監督者詳細取得**
```http
GET /api/v1/supervisors/{id}
```

#### **監督者更新**
```http
PUT /api/v1/supervisors/{id}
```

#### **監督者削除**
```http
DELETE /api/v1/supervisors/{id}
```

#### **監督者アクション記録**
```http
POST /api/v1/supervisors/{id}/actions
```

**リクエストボディ:**
```json
{
  "action_type": "quality_review",
  "description": "コード品質レビュー実施",
  "decision": "approved",
  "details": {
    "review_target": "workflow_123",
    "quality_score": 85
  }
}
```

### 2.6 ペルソナルール管理 (`/api/v1/persona-rules/`)

#### **ペルソナルール作成**
```http
POST /api/v1/persona-rules/
```

**リクエストボディ:**
```json
{
  "persona_id": 1,
  "rule_type": "behavior",
  "rule_content": "常に品質を最優先に考える",
  "priority": 1,
  "scope": "global",
  "is_active": true
}
```

**レスポンス:**
```json
{
  "id": 1,
  "persona_id": 1,
  "rule_type": "behavior",
  "rule_content": "常に品質を最優先に考える",
  "priority": 1,
  "scope": "global",
  "is_active": true,
  "created_at": "2025-08-13T00:00:00Z",
  "updated_at": "2025-08-13T00:00:00Z"
}
```

#### **ペルソナルール一覧取得**
```http
GET /api/v1/persona-rules/
```

**クエリパラメータ:**
- `persona_id`: ペルソナIDでフィルタ
- `rule_type`: ルールタイプでフィルタ
- `priority`: 優先度でフィルタ
- `scope`: 適用範囲でフィルタ

#### **ペルソナルール詳細取得**
```http
GET /api/v1/persona-rules/{id}
```

#### **ペルソナルール更新**
```http
PUT /api/v1/persona-rules/{id}
```

#### **ペルソナルール削除**
```http
DELETE /api/v1/persona-rules/{id}
```

#### **ルールオーバーライド作成**
```http
POST /api/v1/persona-rules/{id}/overrides
```

**リクエストボディ:**
```json
{
  "override_type": "temporary",
  "reason": "緊急対応のため",
  "new_content": "一時的に品質を犠牲にして速度を優先",
  "expires_at": "2025-08-20T00:00:00Z"
}
```

### 2.7 ワークフロー管理 (`/api/v1/workflows/`)

#### **ワークフロー作成**
```http
POST /api/v1/workflows/
```

**リクエストボディ:**
```json
{
  "name": "ワークフロー名",
  "description": "ワークフローの説明",
  "execution_type": "parallel",
  "project_id": 1,
  "team_id": 1,
  "created_by_persona_id": 1,
  "config": {
    "timeout_seconds": 3600,
    "max_retries": 3
  },
  "steps": [
    {
      "step_order": 1,
      "name": "ステップ1",
      "description": "ステップ1の説明",
      "ai_model_type": "claude",
      "persona_id": 1,
      "task_type": "code_review",
      "task_prompt": "コードレビューを実施してください"
    }
  ]
}
```

**レスポンス:**
```json
{
  "id": 1,
  "name": "ワークフロー名",
  "description": "ワークフローの説明",
  "execution_type": "parallel",
  "project_id": 1,
  "team_id": 1,
  "created_by_persona_id": 1,
  "status": "draft",
  "total_steps": 1,
  "created_at": "2025-08-13T00:00:00Z",
  "updated_at": "2025-08-13T00:00:00Z"
}
```

#### **ワークフロー一覧取得**
```http
GET /api/v1/workflows/
```

**クエリパラメータ:**
- `project_id`: プロジェクトIDでフィルタ
- `team_id`: チームIDでフィルタ
- `status`: ステータスでフィルタ
- `execution_type`: 実行タイプでフィルタ

#### **ワークフロー詳細取得**
```http
GET /api/v1/workflows/{id}
```

**クエリパラメータ:**
- `include_steps`: ステップ情報を含めるかどうか（デフォルト: true）

#### **ワークフロー更新**
```http
PUT /api/v1/workflows/{id}
```

#### **ワークフロー削除**
```http
DELETE /api/v1/workflows/{id}
```

#### **ワークフロー実行**
```http
POST /api/v1/workflows/{id}/execute
```

**リクエストボディ:**
```json
{
  "execution_context": {
    "environment": "development",
    "parameters": {
      "input_file": "input.txt"
    }
  }
}
```

**レスポンス:**
```json
{
  "execution_id": "exec_123",
  "workflow_id": 1,
  "status": "running",
  "start_time": "2025-08-13T00:00:00Z",
  "execution_context": {
    "environment": "development",
    "parameters": {
      "input_file": "input.txt"
    }
  }
}
```

#### **ワークフロー進捗取得**
```http
GET /api/v1/workflows/{id}/progress
```

**レスポンス:**
```json
{
  "workflow_id": 1,
  "execution_id": "exec_123",
  "status": "running",
  "progress_percentage": 50,
  "completed_steps": 1,
  "total_steps": 2,
  "current_step": {
    "id": 2,
    "name": "ステップ2",
    "status": "running"
  },
  "last_updated": "2025-08-13T00:00:00Z"
}
```

#### **ワークフロー実行制御**
```http
PUT /api/v1/workflows/{id}/control
```

**リクエストボディ:**
```json
{
  "action": "pause"
}
```

**利用可能なアクション**: `pause`, `resume`, `cancel`, `retry`

#### **ステータス別ワークフロー取得**
```http
GET /api/v1/workflows/status/{status}
```

**利用可能なステータス**: `draft`, `ready`, `running`, `completed`, `failed`, `cancelled`

---

## 🚨 現在の制限事項

### 3.1 未実装機能

#### **認証・認可システム**
- ユーザー認証・セッション管理
- 権限チェック・アクセス制御
- API Key管理

#### **高度なワークフロー機能**
- 条件分岐・ループ処理
- エラーハンドリング・リトライ機能
- ワークフロー履歴・ログ

#### **AI統合実行**
- Claude Code/Gemini CLIの実際の呼び出し
- AI実行結果の取得・処理
- 複数AIモデルの並列実行

### 3.2 技術的制約

#### **データベース**
- PostgreSQL 16使用による高パフォーマンス・高可用性
- 大規模データ処理の制限
- 分散環境での制約

#### **パフォーマンス**
- 大量データ処理時の応答時間
- リアルタイム更新の制限
- キャッシュ機能の未実装

---

## 📋 今後の実装予定

### 4.1 短期実装（1-2週間）

#### **認証システム**
- JWT認証の実装
- ユーザー管理・ログイン機能
- 基本的な権限管理

#### **エラーハンドリング強化**
- 統一されたエラーレスポンス形式
- バリデーションエラーの詳細化
- ログ出力の改善

### 4.2 中期実装（1ヶ月）

#### **AI統合実行**
- Claude Code/Gemini CLI統合
- 基本的なワークフロー実行
- 結果取得・表示機能

#### **ワークフロー機能強化**
- 条件分岐・ループ処理
- エラーハンドリング・リトライ機能
- ワークフロー履歴・ログ

### 4.3 長期実装（3ヶ月）

#### **高度な機能**
- 複数AIモデルの並列実行
- 合意形成・品質評価
- リアルタイム協調状況表示

#### **スケーラビリティ**
- PostgreSQL移行
- キャッシュシステム導入
- 負荷分散・スケーリング

---

## 🔧 開発・テスト方法

### 5.1 開発環境セットアップ

#### **バックエンド起動**
```bash
# 統一起動システムを使用（推奨）
npm run backend:unified

# または直接実行
node scripts/run-backend-unified.js
```

#### **フロントエンド起動**
```bash
npm run frontend:dev
```

### 5.2 APIテスト

#### **Swagger UI**
- URL: `http://localhost:8002/docs`
- 機能: インタラクティブなAPIテスト・ドキュメント確認

#### **ReDoc**
- URL: `http://localhost:8002/redoc`
- 機能: 読みやすいAPIドキュメント

#### **OpenAPI Spec**
- URL: `http://localhost:8002/openapi.json`
- 機能: 機械可読なAPI仕様

### 5.3 データベース確認

#### **PostgreSQL 16データベース**
```bash
# データベースファイル
backend/ai_secretary_platform.db

# 確認ツール
psql -h localhost -U postgres -d ai_secretary_platform
.tables
.schema table_name
```

---

## 📋 まとめ

### 6.1 現在の実装状況
- **基本CRUD操作**: 7カテゴリ・約50エンドポイント完了
- **データベース設計**: 17テーブル・正常動作
- **API基盤**: FastAPI + Pydantic + SQLAlchemy完了

### 6.2 今後の方向性
- **現実主義**: 実装可能な機能から段階的に構築
- **品質優先**: テスト駆動開発・継続的な品質向上
- **段階的改善**: 基盤問題解決→機能実装→高度化

### 6.3 推奨事項
1. **基盤問題解決**: WorkflowService非同期セッション管理修正
2. **UI問題解決**: Phase 3.3 Workspace分離システム完成
3. **機能実装**: Phase 3.4 進捗管理カンバンUI実装
4. **品質保証**: 段階的テスト・継続的な品質監視

---

**このAPI仕様書により、現在実装されている機能の正確な把握と、今後の開発方針の明確化ができました。実装済み機能を活用しながら、段階的に機能を拡張していくことで、成功するAI協調プラットフォームの実現を目指します。**

*作成者: 中野五月（Claude Code）*  
*作成日時: 2025年8月13日*  
*目的: 現在のAPI実装に準拠した正確な仕様定義・今後の開発方針策定* 

## 16. 統合版プラットフォーム API設計詳細

### 16.1 認証・認可システム設計

#### 16.1.1 JWT認証システム
```python
# app/core/auth/jwt_handler.py
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# JWT設定
SECRET_KEY = "your-secret-key-here"  # 環境変数から取得
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# パスワードハッシュ化
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

class JWTHandler:
    """JWT認証・認可ハンドラー"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """パスワード検証"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """パスワードハッシュ化"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """アクセストークン作成"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """リフレッシュトークン作成"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """トークン検証"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

# 依存性注入
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """現在のユーザー取得"""
    token = credentials.credentials
    payload = JWTHandler.verify_token(token)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """現在のアクティブユーザー取得"""
    if not current_user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user
```

#### 16.1.2 ロールベースアクセス制御（RBAC）
```python
# app/core/auth/rbac.py
from typing import List, Optional
from fastapi import HTTPException, status, Depends
from enum import Enum

class Permission(str, Enum):
    """権限定義"""
    # ユーザー管理
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"
    
    # AI秘書管理
    AI_ASSISTANT_READ = "ai_assistant:read"
    AI_ASSISTANT_WRITE = "ai_assistant:write"
    AI_ASSISTANT_DELETE = "ai_assistant:delete"
    
    # ワークフロー管理
    WORKFLOW_READ = "workflow:read"
    WORKFLOW_WRITE = "workflow:write"
    WORKFLOW_DELETE = "workflow:delete"
    WORKFLOW_EXECUTE = "workflow:execute"
    
    # AI協議管理
    AI_DISCUSSION_READ = "ai_discussion:read"
    AI_DISCUSSION_WRITE = "ai_discussion:write"
    AI_DISCUSSION_MODERATE = "ai_discussion:moderate"
    
    # プラン承認
    PLAN_READ = "plan:read"
    PLAN_WRITE = "plan:write"
    PLAN_APPROVE = "plan:approve"
    
    # システム管理
    SYSTEM_ADMIN = "system:admin"

class Role(str, Enum):
    """役割定義"""
    ADMIN = "admin"
    USER = "user"
    AI_ASSISTANT = "ai_assistant"
    TEAM_LEADER = "team_leader"
    WORKFLOW_MANAGER = "workflow_manager"

# 役割別権限マッピング
ROLE_PERMISSIONS = {
    Role.ADMIN: [
        Permission.USER_READ, Permission.USER_WRITE, Permission.USER_DELETE,
        Permission.AI_ASSISTANT_READ, Permission.AI_ASSISTANT_WRITE, Permission.AI_ASSISTANT_DELETE,
        Permission.WORKFLOW_READ, Permission.WORKFLOW_WRITE, Permission.WORKFLOW_DELETE, Permission.WORKFLOW_EXECUTE,
        Permission.AI_DISCUSSION_READ, Permission.AI_DISCUSSION_WRITE, Permission.AI_DISCUSSION_MODERATE,
        Permission.PLAN_READ, Permission.PLAN_WRITE, Permission.PLAN_APPROVE,
        Permission.SYSTEM_ADMIN
    ],
    Role.USER: [
        Permission.USER_READ,
        Permission.AI_ASSISTANT_READ,
        Permission.WORKFLOW_READ, Permission.WORKFLOW_WRITE,
        Permission.AI_DISCUSSION_READ, Permission.AI_DISCUSSION_WRITE,
        Permission.PLAN_READ, Permission.PLAN_WRITE
    ],
    Role.AI_ASSISTANT: [
        Permission.AI_ASSISTANT_READ,
        Permission.WORKFLOW_READ, Permission.WORKFLOW_EXECUTE,
        Permission.AI_DISCUSSION_READ, Permission.AI_DISCUSSION_WRITE,
        Permission.PLAN_READ, Permission.PLAN_WRITE
    ],
    Role.TEAM_LEADER: [
        Permission.USER_READ,
        Permission.AI_ASSISTANT_READ, Permission.AI_ASSISTANT_WRITE,
        Permission.WORKFLOW_READ, Permission.WORKFLOW_WRITE, Permission.WORKFLOW_EXECUTE,
        Permission.AI_DISCUSSION_READ, Permission.AI_DISCUSSION_WRITE, Permission.AI_DISCUSSION_MODERATE,
        Permission.PLAN_READ, Permission.PLAN_WRITE, Permission.PLAN_APPROVE
    ],
    Role.WORKFLOW_MANAGER: [
        Permission.WORKFLOW_READ, Permission.WORKFLOW_WRITE, Permission.WORKFLOW_DELETE, Permission.WORKFLOW_EXECUTE,
        Permission.AI_DISCUSSION_READ, Permission.AI_DISCUSSION_WRITE,
        Permission.PLAN_READ, Permission.PLAN_WRITE
    ]
}

def require_permission(permission: Permission):
    """権限チェックデコレーター"""
    def permission_checker(current_user: Dict[str, Any] = Depends(get_current_active_user)):
        user_role = current_user.get("role", Role.USER)
        user_permissions = ROLE_PERMISSIONS.get(user_role, [])
        
        if permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission}"
            )
        return current_user
    
    return permission_checker

# 権限チェック例
async def get_users_with_permission(current_user: Dict[str, Any] = Depends(require_permission(Permission.USER_READ))):
    """ユーザー一覧取得（権限チェック付き）"""
    # ユーザー一覧取得処理
    pass

async def create_user_with_permission(current_user: Dict[str, Any] = Depends(require_permission(Permission.USER_WRITE))):
    """ユーザー作成（権限チェック付き）"""
    # ユーザー作成処理
    pass
```

### 16.2 新機能API設計

#### 16.2.1 AI協議管理API
```python
# app/api/v1/ai_discussions.py
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from typing import List, Optional
from app.core.auth.rbac import require_permission, Permission
from app.schemas.ai_discussion import (
    AIDiscussionCreate, AIDiscussionUpdate, AIDiscussionResponse,
    DiscussionParticipantCreate, DiscussionMessageCreate
)

router = APIRouter(prefix="/ai-discussions", tags=["AI協議管理"])

@router.post("/", response_model=AIDiscussionResponse)
async def create_ai_discussion(
    discussion: AIDiscussionCreate,
    current_user: Dict[str, Any] = Depends(require_permission(Permission.AI_DISCUSSION_WRITE))
):
    """AI協議作成"""
    # AI協議作成処理
    pass

@router.get("/", response_model=List[AIDiscussionResponse])
async def get_ai_discussions(
    status: Optional[str] = None,
    discussion_type: Optional[str] = None,
    topic: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(require_permission(Permission.AI_DISCUSSION_READ))
):
    """AI協議一覧取得"""
    # AI協議一覧取得処理
    pass

@router.get("/{discussion_id}", response_model=AIDiscussionResponse)
async def get_ai_discussion(
    discussion_id: int,
    current_user: Dict[str, Any] = Depends(require_permission(Permission.AI_DISCUSSION_READ))
):
    """AI協議詳細取得"""
    # AI協議詳細取得処理
    pass

@router.put("/{discussion_id}", response_model=AIDiscussionResponse)
async def update_ai_discussion(
    discussion_id: int,
    discussion: AIDiscussionUpdate,
    current_user: Dict[str, Any] = Depends(require_permission(Permission.AI_DISCUSSION_WRITE))
):
    """AI協議更新"""
    # AI協議更新処理
    pass

@router.delete("/{discussion_id}")
async def delete_ai_discussion(
    discussion_id: int,
    current_user: Dict[str, Any] = Depends(require_permission(Permission.AI_DISCUSSION_WRITE))
):
    """AI協議削除"""
    # AI協議削除処理
    pass

@router.post("/{discussion_id}/participants")
async def add_discussion_participant(
    discussion_id: int,
    participant: DiscussionParticipantCreate,
    current_user: Dict[str, Any] = Depends(require_permission(Permission.AI_DISCUSSION_WRITE))
):
    """AI協議参加者追加"""
    # 参加者追加処理
    pass

@router.post("/{discussion_id}/messages")
async def add_discussion_message(
    discussion_id: int,
    message: DiscussionMessageCreate,
    current_user: Dict[str, Any] = Depends(require_permission(Permission.AI_DISCUSSION_WRITE))
):
    """AI協議メッセージ追加"""
    # メッセージ追加処理
    pass

@router.post("/{discussion_id}/interrupt")
async def interrupt_discussion(
    discussion_id: int,
    interruption_type: str,
    message: str,
    current_user: Dict[str, Any] = Depends(require_permission(Permission.AI_DISCUSSION_MODERATE))
):
    """AI協議割込み"""
    # 協議割込み処理
    pass
```

#### 16.2.2 プラン承認システムAPI
```python
# app/api/v1/plans.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.core.auth.rbac import require_permission, Permission
from app.schemas.plan import (
    PlanCreate, PlanUpdate, PlanResponse,
    PlanApprovalCreate, PlanVersionCreate
)

router = APIRouter(prefix="/plans", tags=["プラン承認システム"])

@router.post("/", response_model=PlanResponse)
async def create_plan(
    plan: PlanCreate,
    current_user: Dict[str, Any] = Depends(require_permission(Permission.PLAN_WRITE))
):
    """プラン作成"""
    # プラン作成処理
    pass

@router.get("/", response_model=List[PlanResponse])
async def get_plans(
    status: Optional[str] = None,
    assistant_id: Optional[int] = None,
    workflow_id: Optional[int] = None,
    current_user: Dict[str, Any] = Depends(require_permission(Permission.PLAN_READ))
):
    """プラン一覧取得"""
    # プラン一覧取得処理
    pass

@router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: int,
    current_user: Dict[str, Any] = Depends(require_permission(Permission.PLAN_READ))
):
    """プラン詳細取得"""
    # プラン詳細取得処理
    pass

@router.put("/{plan_id}", response_model=PlanResponse)
async def update_plan(
    plan_id: int,
    plan: PlanUpdate,
    current_user: Dict[str, Any] = Depends(require_permission(Permission.PLAN_WRITE))
):
    """プラン更新"""
    # プラン更新処理
    pass

@router.delete("/{plan_id}")
async def delete_plan(
    plan_id: int,
    current_user: Dict[str, Any] = Depends(require_permission(Permission.PLAN_WRITE))
):
    """プラン削除"""
    # プラン削除処理
    pass

@router.post("/{plan_id}/submit")
async def submit_plan(
    plan_id: int,
    current_user: Dict[str, Any] = Depends(require_permission(Permission.PLAN_WRITE))
):
    """プラン提出"""
    # プラン提出処理
    pass

@router.post("/{plan_id}/approve")
async def approve_plan(
    plan_id: int,
    approval: PlanApprovalCreate,
    current_user: Dict[str, Any] = Depends(require_permission(Permission.PLAN_APPROVE))
):
    """プラン承認"""
    # プラン承認処理
    pass

@router.post("/{plan_id}/reject")
async def reject_plan(
    plan_id: int,
    rejection_reason: str,
    current_user: Dict[str, Any] = Depends(require_permission(Permission.PLAN_APPROVE))
):
    """プラン却下"""
    # プラン却下処理
    pass

@router.post("/{plan_id}/request-revision")
async def request_plan_revision(
    plan_id: int,
    revision_notes: str,
    current_user: Dict[str, Any] = Depends(require_permission(Permission.PLAN_APPROVE))
):
    """プラン修正要求"""
    # プラン修正要求処理
    pass

@router.post("/{plan_id}/versions")
async def create_plan_version(
    plan_id: int,
    version: PlanVersionCreate,
    current_user: Dict[str, Any] = Depends(require_permission(Permission.PLAN_WRITE))
):
    """プランバージョン作成"""
    # プランバージョン作成処理
    pass
```

### 16.3 WebSocket API設計

#### 16.3.1 WebSocket接続管理
```python
# app/api/websocket/connection_manager.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
import asyncio
from datetime import datetime

class ConnectionManager:
    """WebSocket接続管理"""
    
    def __init__(self):
        # 接続管理
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_subscriptions: Dict[str, Set[str]] = {}
        self.room_connections: Dict[str, Set[str]] = {}
        
        # 接続情報
        self.connection_info: Dict[str, Dict] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str, client_info: Dict):
        """WebSocket接続確立"""
        await websocket.accept()
        
        # 接続情報記録
        self.active_connections[user_id] = websocket
        self.connection_info[user_id] = {
            "connected_at": datetime.utcnow().isoformat(),
            "client_info": client_info,
            "last_heartbeat": datetime.utcnow().isoformat()
        }
        
        # 接続確認メッセージ送信
        await self.send_personal_message(
            user_id,
            {
                "type": "connection_established",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        print(f"User {user_id} connected")
    
    async def disconnect(self, user_id: str):
        """WebSocket接続切断"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        if user_id in self.connection_info:
            del self.connection_info[user_id]
        
        # サブスクリプション削除
        if user_id in self.user_subscriptions:
            del self.user_subscriptions[user_id]
        
        # ルーム接続削除
        for room_id, connections in self.room_connections.items():
            if user_id in connections:
                connections.remove(user_id)
        
        print(f"User {user_id} disconnected")
    
    async def send_personal_message(self, user_id: str, message: Dict):
        """個人メッセージ送信"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
            except Exception as e:
                print(f"Error sending message to user {user_id}: {e}")
                await self.disconnect(user_id)
    
    async def broadcast_to_subscribers(self, topic: str, message: Dict):
        """トピック購読者へのブロードキャスト"""
        if topic in self.room_connections:
            disconnected_users = []
            
            for user_id in self.room_connections[topic]:
                try:
                    await self.send_personal_message(user_id, message)
                except Exception as e:
                    print(f"Error broadcasting to user {user_id}: {e}")
                    disconnected_users.append(user_id)
            
            # 切断されたユーザーを削除
            for user_id in disconnected_users:
                await self.disconnect(user_id)
    
    async def subscribe_to_topic(self, user_id: str, topic: str):
        """トピック購読"""
        if topic not in self.room_connections:
            self.room_connections[topic] = set()
        
        self.room_connections[topic].add(user_id)
        
        if user_id not in self.user_subscriptions:
            self.user_subscriptions[user_id] = set()
        
        self.user_subscriptions[user_id].add(topic)
        
        # 購読確認メッセージ送信
        await self.send_personal_message(
            user_id,
            {
                "type": "subscription_confirmed",
                "topic": topic,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    async def unsubscribe_from_topic(self, user_id: str, topic: str):
        """トピック購読解除"""
        if topic in self.room_connections and user_id in self.room_connections[topic]:
            self.room_connections[topic].remove(user_id)
        
        if user_id in self.user_subscriptions and topic in self.user_subscriptions[user_id]:
            self.user_subscriptions[user_id].remove(topic)
        
        # 購読解除確認メッセージ送信
        await self.send_personal_message(
            user_id,
            {
                "type": "unsubscription_confirmed",
                "topic": topic,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    async def handle_heartbeat(self, user_id: str):
        """ハートビート処理"""
        if user_id in self.connection_info:
            self.connection_info[user_id]["last_heartbeat"] = datetime.utcnow().isoformat()
    
    def get_connection_stats(self) -> Dict:
        """接続統計情報取得"""
        return {
            "total_connections": len(self.active_connections),
            "total_subscriptions": len(self.room_connections),
            "connection_info": self.connection_info
        }

# グローバル接続マネージャー
manager = ConnectionManager()
```

#### 16.3.2 WebSocketエンドポイント
```python
# app/api/websocket/endpoints.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.api.websocket.connection_manager import manager
from app.core.auth.jwt_handler import get_current_user
import json
from typing import Dict, Any

router = APIRouter()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    token: str = None
):
    """WebSocket接続エンドポイント"""
    
    # 認証チェック（トークンがある場合）
    if token:
        try:
            # JWTトークン検証
            payload = JWTHandler.verify_token(token)
            if payload.get("sub") != user_id:
                await websocket.close(code=4001, reason="Invalid user")
                return
        except Exception:
            await websocket.close(code=4001, reason="Invalid token")
            return
    
    # クライアント情報取得
    client_info = {
        "ip_address": websocket.client.host,
        "user_agent": websocket.headers.get("user-agent", ""),
        "platform": "web"
    }
    
    # 接続確立
    await manager.connect(websocket, user_id, client_info)
    
    try:
        while True:
            # メッセージ受信
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # メッセージタイプ別処理
            await handle_websocket_message(user_id, message)
            
    except WebSocketDisconnect:
        await manager.disconnect(user_id)
    except Exception as e:
        print(f"WebSocket error for user {user_id}: {e}")
        await manager.disconnect(user_id)

async def handle_websocket_message(user_id: str, message: Dict[str, Any]):
    """WebSocketメッセージ処理"""
    message_type = message.get("type")
    
    if message_type == "subscribe":
        # トピック購読
        topic = message.get("topic")
        if topic:
            await manager.subscribe_to_topic(user_id, topic)
    
    elif message_type == "unsubscribe":
        # トピック購読解除
        topic = message.get("topic")
        if topic:
            await manager.unsubscribe_from_topic(user_id, topic)
    
    elif message_type == "heartbeat":
        # ハートビート処理
        await manager.handle_heartbeat(user_id)
    
    elif message_type == "chat_message":
        # チャットメッセージ処理
        await handle_chat_message(user_id, message)
    
    elif message_type == "workflow_update":
        # ワークフロー更新通知
        await handle_workflow_update(user_id, message)
    
    elif message_type == "ai_discussion_update":
        # AI協議更新通知
        await handle_ai_discussion_update(user_id, message)
    
    elif message_type == "plan_approval_update":
        # プラン承認更新通知
        await handle_plan_approval_update(user_id, message)
    
    else:
        # 不明なメッセージタイプ
        await manager.send_personal_message(
            user_id,
            {
                "type": "error",
                "message": f"Unknown message type: {message_type}",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

async def handle_chat_message(user_id: str, message: Dict[str, Any]):
    """チャットメッセージ処理"""
    # チャットメッセージの処理
    pass

async def handle_workflow_update(user_id: str, message: Dict[str, Any]):
    """ワークフロー更新処理"""
    # ワークフロー更新の処理
    pass

async def handle_ai_discussion_update(user_id: str, message: Dict[str, Any]):
    """AI協議更新処理"""
    # AI協議更新の処理
    pass

async def handle_plan_approval_update(user_id: str, message: Dict[str, Any]):
    """プラン承認更新処理"""
    # プラン承認更新の処理
    pass

@router.get("/ws/stats")
async def get_websocket_stats():
    """WebSocket統計情報取得"""
    return manager.get_connection_stats()
```

### 16.4 OpenAPI 3.0仕様書

#### 16.4.1 OpenAPI設定
```python
# app/main.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.api.v1 import (
    users, ai_assistants, personas, teams, workflows, tasks,
    conversations, obsidian, ai_discussions, plans
)
from app.api.websocket import endpoints

app = FastAPI(
    title="AI秘書チーム・プラットフォーム（統合版）",
    description="AI秘書チームの協調作業プラットフォーム",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# APIルーター登録
app.include_router(users.router, prefix="/api/v1")
app.include_router(ai_assistants.router, prefix="/api/v1")
app.include_router(personas.router, prefix="/api/v1")
app.include_router(teams.router, prefix="/api/v1")
app.include_router(workflows.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(conversations.router, prefix="/api/v1")
app.include_router(obsidian.router, prefix="/api/v1")
app.include_router(ai_discussions.router, prefix="/api/v1")
app.include_router(plans.router, prefix="/api/v1")

# WebSocketルーター登録
app.include_router(endpoints.router, prefix="/ws")

def custom_openapi():
    """カスタムOpenAPI仕様書生成"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="AI秘書チーム・プラットフォーム（統合版）",
        version="1.0.0",
        description="""
        ## 概要
        
        AI秘書チーム・プラットフォーム（統合版）は、AI秘書の協調作業を支援する包括的なプラットフォームです。
        
        ## 主要機能
        
        * **ユーザー管理**: ユーザー認証・認可・プロフィール管理
        * **AI秘書管理**: AI秘書の作成・設定・スキル管理
        * **ペルソナ管理**: AI秘書の個性・専門性管理
        * **チーム管理**: チーム構成・メンバー管理
        * **ワークフロー管理**: タスク・プロジェクト管理
        * **AI協議管理**: AI同士の議論・合意形成
        * **プラン承認システム**: AI提案プランの承認ワークフロー
        * **Obsidian連携**: 知識管理・司書AI機能
        
        ## 認証
        
        このAPIはJWT（JSON Web Token）による認証を使用します。
        
        ## 権限
        
        ロールベースアクセス制御（RBAC）により、ユーザーの役割に応じた権限が付与されます。
        
        ## WebSocket
        
        リアルタイム通信にはWebSocketを使用し、以下の機能を提供します：
        
        * リアルタイム通知
        * チャット機能
        * ワークフロー更新通知
        * AI協議進行状況
        * プラン承認状況
        """,
        routes=app.routes,
    )
    
    # セキュリティスキーマ追加
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    # セキュリティ要件追加
    openapi_schema["security"] = [{"BearerAuth": []}]
    
    # タグ情報追加
    openapi_schema["tags"] = [
        {
            "name": "認証・認可",
            "description": "ユーザー認証・セッション管理・権限管理"
        },
        {
            "name": "ユーザー管理",
            "description": "ユーザー情報・プロフィール・設定管理"
        },
        {
            "name": "AI秘書管理",
            "description": "AI秘書の作成・設定・スキル管理"
        },
        {
            "name": "ペルソナ管理",
            "description": "AI秘書の個性・専門性・役割管理"
        },
        {
            "name": "チーム管理",
            "description": "チーム構成・メンバー・権限管理"
        },
        {
            "name": "ワークフロー管理",
            "description": "タスク・プロジェクト・進捗管理"
        },
        {
            "name": "会話管理",
            "description": "チャット・メッセージ・履歴管理"
        },
        {
            "name": "Obsidian連携",
            "description": "Obsidian知識管理・司書AI機能"
        },
        {
            "name": "AI協議管理",
            "description": "AI同士の議論・合意形成・割込み制御"
        },
        {
            "name": "プラン承認システム",
            "description": "AI提案プランの承認・却下・修正要求"
        },
        {
            "name": "WebSocket",
            "description": "リアルタイム通信・通知・更新"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

#### 16.4.2 APIレスポンス形式標準化
```python
# app/schemas/common.py
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List
from datetime import datetime
from enum import Enum

class ResponseStatus(str, Enum):
    """レスポンスステータス"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"

class BaseResponse(BaseModel):
    """基本レスポンス形式"""
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS)
    message: Optional[str] = Field(default=None, description="レスポンスメッセージ")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Optional[Any] = Field(default=None, description="レスポンスデータ")

class SuccessResponse(BaseResponse):
    """成功レスポンス"""
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS)
    data: Any = Field(..., description="レスポンスデータ")

class ErrorResponse(BaseResponse):
    """エラーレスポンス"""
    status: ResponseStatus = Field(default=ResponseStatus.ERROR)
    error_code: str = Field(..., description="エラーコード")
    error_details: Optional[Dict[str, Any]] = Field(default=None, description="エラー詳細")

class PaginatedResponse(BaseResponse):
    """ページネーション付きレスポンス"""
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS)
    data: List[Any] = Field(..., description="データリスト")
    pagination: Dict[str, Any] = Field(..., description="ページネーション情報")
    total_count: int = Field(..., description="総件数")
    page: int = Field(..., description="現在のページ")
    page_size: int = Field(..., description="ページサイズ")
    total_pages: int = Field(..., description="総ページ数")

# エラーコード定義
class ErrorCode(str, Enum):
    """エラーコード定義"""
    # 認証・認可エラー
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INVALID_TOKEN = "INVALID_TOKEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    
    # バリデーションエラー
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    
    # データベースエラー
    DATABASE_ERROR = "DATABASE_ERROR"
    RECORD_NOT_FOUND = "RECORD_NOT_FOUND"
    DUPLICATE_RECORD = "DUPLICATE_RECORD"
    CONSTRAINT_VIOLATION = "CONSTRAINT_VIOLATION"
    
    # ビジネスロジックエラー
    BUSINESS_LOGIC_ERROR = "BUSINESS_LOGIC_ERROR"
    INVALID_STATE_TRANSITION = "INVALID_STATE_TRANSITION"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    
    # 外部サービスエラー
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    API_RATE_LIMIT_EXCEEDED = "API_RATE_LIMIT_EXCEEDED"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    
    # システムエラー
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
```

---

**作成日**: 2025-08-13  
**作成者**: AI Assistant  
**バージョン**: 1.0  
**次回更新予定**: 2025-08-20 