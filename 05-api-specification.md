# AI秘書チーム・プラットフォーム - API仕様書

**作成日**: 2025年8月17日  
**作成者**: 中野五月（Claude Code）  
**バージョン**: 1.0

## 🔌 API概要

### ベースURL
```
開発環境: http://localhost:8000/api/v1
本番環境: https://api.ai-secretary.local/api/v1
```

### 認証方式
- **開発環境**: 認証なし（ローカル環境）
- **本番環境**: JWT Bearer Token（将来実装）

### レスポンス形式
```json
{
  "data": {}, // 成功時のデータ
  "error": {}, // エラー時の情報
  "message": "string", // メッセージ
  "status": "success|error" // ステータス
}
```

## 📋 エンドポイント一覧

### 1. システム管理

#### ヘルスチェック
```http
GET /health
```

**レスポンス**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-17T10:30:00Z",
  "version": "1.0.0"
}
```

### 2. アシスタント管理

#### アシスタント一覧取得
```http
GET /assistants
```

**クエリパラメータ**
- `skip` (integer, optional): スキップ数（デフォルト: 0）
- `limit` (integer, optional): 取得数（デフォルト: 100）
- `is_active` (boolean, optional): アクティブなアシスタントのみ

**レスポンス**
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "name": "string",
    "description": "string",
    "personality_template_id": "uuid",
    "voice_id": "uuid",
    "avatar_id": "uuid",
    "default_llm_model": "string",
    "custom_system_prompt": "string",
    "is_active": true,
    "is_public": false,
    "created_at": "2025-08-17T10:30:00Z",
    "updated_at": "2025-08-17T10:30:00Z"
  }
]
```

#### アシスタント作成
```http
POST /assistants
```

**リクエストボディ**
```json
{
  "name": "string",
  "description": "string",
  "personality_template_id": "uuid",
  "voice_id": "uuid",
  "avatar_id": "uuid",
  "default_llm_model": "string",
  "custom_system_prompt": "string"
}
```

**レスポンス**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "name": "string",
  "description": "string",
  "personality_template_id": "uuid",
  "voice_id": "uuid",
  "avatar_id": "uuid",
  "default_llm_model": "string",
  "custom_system_prompt": "string",
  "is_active": true,
  "is_public": false,
  "created_at": "2025-08-17T10:30:00Z",
  "updated_at": "2025-08-17T10:30:00Z"
}
```

#### アシスタント詳細取得
```http
GET /assistants/{assistant_id}
```

**パスパラメータ**
- `assistant_id` (uuid): アシスタントID

**レスポンス**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "name": "string",
  "description": "string",
  "personality_template_id": "uuid",
  "voice_id": "uuid",
  "avatar_id": "uuid",
  "default_llm_model": "string",
  "custom_system_prompt": "string",
  "is_active": true,
  "is_public": false,
  "created_at": "2025-08-17T10:30:00Z",
  "updated_at": "2025-08-17T10:30:00Z"
}
```

#### アシスタント更新
```http
PUT /assistants/{assistant_id}
```

**パスパラメータ**
- `assistant_id` (uuid): アシスタントID

**リクエストボディ**
```json
{
  "name": "string",
  "description": "string",
  "personality_template_id": "uuid",
  "voice_id": "uuid",
  "avatar_id": "uuid",
  "default_llm_model": "string",
  "custom_system_prompt": "string"
}
```

**レスポンス**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "name": "string",
  "description": "string",
  "personality_template_id": "uuid",
  "voice_id": "uuid",
  "avatar_id": "uuid",
  "default_llm_model": "string",
  "custom_system_prompt": "string",
  "is_active": true,
  "is_public": false,
  "created_at": "2025-08-17T10:30:00Z",
  "updated_at": "2025-08-17T10:30:00Z"
}
```

#### アシスタント削除
```http
DELETE /assistants/{assistant_id}
```

**パスパラメータ**
- `assistant_id` (uuid): アシスタントID

**レスポンス**
```
204 No Content
```

### 3. ルーティング機能

#### リクエストルーティング
```http
POST /routing/route
```

**リクエストボディ**
```json
{
  "prompt": "string",
  "assistant_id": "uuid"
}
```

**レスポンス**
```json
{
  "routed_assistant_id": "uuid",
  "response": "string",
  "confidence": 0.95,
  "processing_time_ms": 1500,
  "tokens_used": 150
}
```

### 4. 会話管理

#### 会話一覧取得
```http
GET /conversations
```

**クエリパラメータ**
- `skip` (integer, optional): スキップ数
- `limit` (integer, optional): 取得数
- `assistant_id` (uuid, optional): アシスタントIDでフィルタ
- `status` (string, optional): ステータスでフィルタ

**レスポンス**
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "assistant_id": "uuid",
    "title": "string",
    "conversation_type": "string",
    "status": "string",
    "voice_enabled": false,
    "voice_id": "uuid",
    "metadata": {},
    "started_at": "2025-08-17T10:30:00Z",
    "ended_at": "2025-08-17T10:30:00Z",
    "created_at": "2025-08-17T10:30:00Z",
    "updated_at": "2025-08-17T10:30:00Z"
  }
]
```

#### 会話作成
```http
POST /conversations
```

**リクエストボディ**
```json
{
  "assistant_id": "uuid",
  "title": "string",
  "conversation_type": "chat",
  "voice_enabled": false,
  "voice_id": "uuid"
}
```

**レスポンス**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "assistant_id": "uuid",
  "title": "string",
  "conversation_type": "string",
  "status": "active",
  "voice_enabled": false,
  "voice_id": "uuid",
  "metadata": {},
  "started_at": "2025-08-17T10:30:00Z",
  "ended_at": null,
  "created_at": "2025-08-17T10:30:00Z",
  "updated_at": "2025-08-17T10:30:00Z"
}
```

#### メッセージ送信
```http
POST /conversations/{conversation_id}/messages
```

**パスパラメータ**
- `conversation_id` (uuid): 会話ID

**リクエストボディ**
```json
{
  "role": "user",
  "content": "string",
  "content_type": "text",
  "parent_id": "uuid"
}
```

**レスポンス**
```json
{
  "id": "uuid",
  "conversation_id": "uuid",
  "role": "user",
  "content": "string",
  "content_type": "text",
  "parent_id": "uuid",
  "metadata": {},
  "created_at": "2025-08-17T10:30:00Z"
}
```

#### メッセージ一覧取得
```http
GET /conversations/{conversation_id}/messages
```

**パスパラメータ**
- `conversation_id` (uuid): 会話ID

**クエリパラメータ**
- `skip` (integer, optional): スキップ数
- `limit` (integer, optional): 取得数

**レスポンス**
```json
[
  {
    "id": "uuid",
    "conversation_id": "uuid",
    "role": "user",
    "content": "string",
    "content_type": "text",
    "parent_id": "uuid",
    "metadata": {},
    "created_at": "2025-08-17T10:30:00Z"
  }
]
```

### 5. ファイル管理

#### ファイルアップロード
```http
POST /files/upload
```

**リクエスト**
- Content-Type: `multipart/form-data`
- `file`: ファイルデータ
- `conversation_id` (optional): 会話ID
- `message_id` (optional): メッセージID

**レスポンス**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "conversation_id": "uuid",
  "message_id": "uuid",
  "file_name": "string",
  "file_type": "string",
  "file_size": 1024,
  "storage_path": "string",
  "mime_type": "string",
  "is_processed": false,
  "metadata": {},
  "created_at": "2025-08-17T10:30:00Z",
  "updated_at": "2025-08-17T10:30:00Z"
}
```

#### ファイル一覧取得
```http
GET /files
```

**クエリパラメータ**
- `conversation_id` (uuid, optional): 会話IDでフィルタ
- `file_type` (string, optional): ファイルタイプでフィルタ
- `is_processed` (boolean, optional): 処理済みでフィルタ

**レスポンス**
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "conversation_id": "uuid",
    "message_id": "uuid",
    "file_name": "string",
    "file_type": "string",
    "file_size": 1024,
    "storage_path": "string",
    "mime_type": "string",
    "is_processed": false,
    "metadata": {},
    "created_at": "2025-08-17T10:30:00Z",
    "updated_at": "2025-08-17T10:30:00Z"
  }
]
```

### 6. スキル管理

#### スキル定義一覧取得
```http
GET /skills
```

**クエリパラメータ**
- `skill_type` (string, optional): スキルタイプでフィルタ
- `is_active` (boolean, optional): アクティブなスキルのみ

**レスポンス**
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "skill_code": "string",
    "name": "string",
    "description": "string",
    "skill_type": "string",
    "configuration": {},
    "is_public": false,
    "is_active": true,
    "created_at": "2025-08-17T10:30:00Z",
    "updated_at": "2025-08-17T10:30:00Z"
  }
]
```

#### スキル定義作成
```http
POST /skills
```

**リクエストボディ**
```json
{
  "skill_code": "string",
  "name": "string",
  "description": "string",
  "skill_type": "string",
  "configuration": {},
  "is_public": false
}
```

**レスポンス**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "skill_code": "string",
  "name": "string",
  "description": "string",
  "skill_type": "string",
  "configuration": {},
  "is_public": false,
  "is_active": true,
  "created_at": "2025-08-17T10:30:00Z",
  "updated_at": "2025-08-17T10:30:00Z"
}
```

### 7. 知識管理

#### 知識ベース検索
```http
POST /knowledge/search
```

**リクエストボディ**
```json
{
  "query": "string",
  "secretary_id": "uuid",
  "limit": 10,
  "threshold": 0.7
}
```

**レスポンス**
```json
{
  "results": [
    {
      "id": "uuid",
      "content": "string",
      "similarity": 0.95,
      "source_type": "string",
      "source_url": "string",
      "tags": ["string"],
      "created_at": "2025-08-17T10:30:00Z"
    }
  ],
  "total_count": 5,
  "search_time_ms": 150
}
```

#### 知識ベース追加
```http
POST /knowledge
```

**リクエストボディ**
```json
{
  "secretary_id": "uuid",
  "content": "string",
  "source_type": "string",
  "source_url": "string",
  "tags": ["string"],
  "metadata": {}
}
```

**レスポンス**
```json
{
  "id": "uuid",
  "secretary_id": "uuid",
  "content": "string",
  "source_type": "string",
  "source_url": "string",
  "tags": ["string"],
  "metadata": {},
  "created_at": "2025-08-17T10:30:00Z",
  "updated_at": "2025-08-17T10:30:00Z"
}
```

## ❌ エラーレスポンス

### エラーコード一覧

| コード | 説明 |
|--------|------|
| 400 | Bad Request - リクエストが不正 |
| 401 | Unauthorized - 認証が必要 |
| 403 | Forbidden - アクセス権限なし |
| 404 | Not Found - リソースが見つからない |
| 422 | Unprocessable Entity - バリデーションエラー |
| 500 | Internal Server Error - サーバー内部エラー |

### エラーレスポンス例

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "入力データが不正です",
    "details": [
      {
        "field": "name",
        "message": "名前は必須です"
      }
    ]
  },
  "status": "error",
  "timestamp": "2025-08-17T10:30:00Z"
}
```

## 🔒 認証・認可

### JWT認証（将来実装）

#### ログイン
```http
POST /auth/login
```

**リクエストボディ**
```json
{
  "username": "string",
  "password": "string"
}
```

**レスポンス**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "string"
}
```

#### トークンリフレッシュ
```http
POST /auth/refresh
```

**リクエストボディ**
```json
{
  "refresh_token": "string"
}
```

**レスポンス**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## 📊 レート制限

### 制限値
- **一般API**: 1000リクエスト/時間
- **AI処理API**: 100リクエスト/時間
- **ファイルアップロード**: 50リクエスト/時間

### レート制限ヘッダー
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## 🔄 WebSocket API

### 接続
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

### メッセージ形式
```json
{
  "type": "message|notification|error",
  "data": {},
  "timestamp": "2025-08-17T10:30:00Z"
}
```

### イベントタイプ
- `conversation_update`: 会話の更新
- `message_received`: 新しいメッセージ
- `assistant_status`: アシスタントの状態変更
- `file_processed`: ファイル処理完了

## 📈 監視・メトリクス

### ヘルスチェック詳細
```http
GET /health/detailed
```

**レスポンス**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-17T10:30:00Z",
  "version": "1.0.0",
  "database": {
    "status": "connected",
    "response_time_ms": 5
  },
  "redis": {
    "status": "connected",
    "response_time_ms": 2
  },
  "gemini_api": {
    "status": "connected",
    "response_time_ms": 150
  },
  "system": {
    "cpu_usage": 15.5,
    "memory_usage": 512.3,
    "disk_usage": 75.2
  }
}
```

### メトリクス取得
```http
GET /metrics
```

**レスポンス**
```json
{
  "requests_total": 1500,
  "requests_per_second": 2.5,
  "average_response_time_ms": 250,
  "error_rate": 0.02,
  "active_conversations": 25,
  "total_assistants": 10
}
```

## 🧪 テスト用エンドポイント

### テストデータ生成
```http
POST /test/generate-data
```

**リクエストボディ**
```json
{
  "assistants_count": 5,
  "conversations_count": 10,
  "messages_per_conversation": 20
}
```

### テストデータクリア
```http
DELETE /test/clear-data
```

**レスポンス**
```json
{
  "message": "テストデータをクリアしました",
  "cleared_tables": ["assistants", "conversations", "messages"]
}
```

このAPI仕様書により、フロントエンドとバックエンドの連携が明確に定義され、開発効率が大幅に向上します。
