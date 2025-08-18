# API設計書

## 1. 概要

### 1.1 目的
AI Secretary PlatformのAPI設計書。新機能（AI協議管理・プラン承認システム）を含む包括的なAPI仕様を定義する。

**設計レベル**: ローカル・シングルユーザー級（エンタープライズ級・大規模システム対応は不要）
**対象規模**: 1ユーザー、1万-10万レコード
**機能範囲**: 基本機能に集中（高度な監査・セキュリティ・パフォーマンス最適化は不要）

### 1.2 対象読者
- フロントエンド開発者
- バックエンド開発者
- システム統合担当者
- テスト担当者

### 1.3 技術スタック
- **バックエンド**: FastAPI (Python)
- **データベース**: PostgreSQL（ローカル環境）
- **認証**: 基本認証（JWT Token）
- **API仕様**: OpenAPI 3.0
- **データ形式**: JSON

### 1.4 システム特性・前提条件

#### **設計レベル**
- **設計レベル**: ローカル・シングルユーザー級（エンタープライズ級・大規模システム対応は不要）
- **対象規模**: 1ユーザー、1万-10万レコード
- **機能範囲**: 基本機能に集中（高度な監査・セキュリティ・パフォーマンス最適化は不要）

#### **動作環境**
- **動作環境**: ローカルPC（Windows 10/11）での単独動作
- **同時接続**: 想定なし（シングルユーザー・ローカル環境）
- **配布方式**: 各自のPCで動作するハイブリッドアプリ（デスクトップ + Web技術）
- **カスタマイズ**: 各自のPCで独自にカスタマイズ可能

#### **技術制約**
- **ネットワーク**: LLM API使用時のインターネット接続のみ（ローカルネットワーク不要）
- **外部連携**: 外部システム連携なし（ローカル完結型）
- **データ処理**: 大規模データ処理・分散処理・クラスタリングは不要
- **パフォーマンス**: ローカル環境での動作に最適化（高負荷・高可用性は不要）

#### **運用・保守**
- **運用**: 開発者による基本運用で十分（24/7監視・専門運用チーム不要）
- **保守**: 基本的なメンテナンス・バックアップで十分
- **スケーラビリティ**: 将来的な機能拡張の準備は維持（段階的実装）
- **セキュリティ**: 基本的なセキュリティ対策で十分（行レベルセキュリティ等の複雑機能は不要）

#### **設計思想**
- **実用性優先**: 実装可能な機能から段階的に構築
- **品質重視**: 基本機能の確実な動作・保守性の向上
- **ローカル最適化**: ローカル環境での動作に最適化された設計
- **将来拡張準備**: 基本的な拡張性は維持（過剰設計は排除）

## 2. API基本仕様

### 2.1 基本URL
```
開発環境: http://localhost:8000
本番環境: ローカル環境のみ（外部公開なし）
```

### 2.2 共通仕様
- **Content-Type**: `application/json`
- **文字エンコーディング**: UTF-8
- **日時形式**: ISO 8601 (YYYY-MM-DDTHH:MM:SSZ)
- **タイムゾーン**: UTC

### 2.3 認証・認可
```http
Authorization: Bearer <JWT_TOKEN>
```
**認証レベル**: 基本認証（複雑なRBAC・多層認証は不要）

### 2.4 エラーレスポンス形式
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "エラーメッセージ",
    "details": "詳細情報（オプション）"
  },
  "timestamp": "2025-08-13T10:00:00Z"
}
```

### 2.5 共通HTTPステータスコード
- `200`: 成功
- `201`: 作成成功
- `400`: リクエストエラー
- `401`: 認証エラー
- `403`: 権限エラー
- `404`: リソース未発見
- `422`: バリデーションエラー
- `500`: サーバーエラー

## 3. エンドポイント一覧

### 3.1 認証・ユーザー管理
| メソッド | エンドポイント | 説明 |
|---------|---------------|------|
| POST | `/api/v1/auth/login` | ログイン |
| POST | `/api/v1/auth/register` | ユーザー登録 |
| POST | `/api/v1/auth/refresh` | トークン更新 |
| POST | `/api/v1/auth/logout` | ログアウト |
| GET | `/api/v1/auth/profile` | プロフィール取得 |
| PUT | `/api/v1/auth/profile` | プロフィール更新 |

### 3.2 AI秘書管理
| メソッド | エンドポイント | 説明 |
|---------|---------------|------|
| GET | `/api/v1/assistants` | AI秘書一覧取得 |
| POST | `/api/v1/assistants` | AI秘書作成 |
| GET | `/api/v1/assistants/{id}` | AI秘書詳細取得 |
| PUT | `/api/v1/assistants/{id}` | AI秘書更新 |
| DELETE | `/api/v1/assistants/{id}` | AI秘書削除 |
| POST | `/api/v1/assistants/{id}/activate` | AI秘書有効化 |
| POST | `/api/v1/assistants/{id}/deactivate` | AI秘書無効化 |

### 3.3 ペルソナ管理
| メソッド | エンドポイント | 説明 |
|---------|---------------|------|
| GET | `/api/v1/personas` | ペルソナ一覧取得 |
| POST | `/api/v1/personas` | ペルソナ作成 |
| GET | `/api/v1/personas/{id}` | ペルソナ詳細取得 |
| PUT | `/api/v1/personas/{id}` | ペルソナ更新 |
| DELETE | `/api/v1/personas/{id}` | ペルソナ削除 |
| GET | `/api/v1/personas/{id}/assistants` | ペルソナ適用AI秘書一覧 |

#### 3.3.1 ペルソナアイコン・画像管理（基本機能のみ）
| メソッド | エンドポイント | 説明 |
|---------|---------------|------|
| POST | `/api/v1/personas/{id}/icon` | ペルソナアイコン設定 |
| POST | `/api/v1/personas/{id}/image` | ペルソナ画像設定 |
| GET | `/api/v1/personas/icons/presets` | プリセットアイコン一覧取得 |
| DELETE | `/api/v1/personas/{id}/icon` | ペルソナアイコン削除 |
| DELETE | `/api/v1/personas/{id}/image` | ペルソナ画像削除 |

### 3.4 チーム管理（基本機能のみ）
| メソッド | エンドポイント | 説明 |
|---------|---------------|------|
| GET | `/api/v1/teams` | チーム一覧取得 |
| POST | `/api/v1/teams` | チーム作成 |
| GET | `/api/v1/teams/{id}` | チーム詳細取得 |
| PUT | `/api/v1/teams/{id}` | チーム更新 |
| DELETE | `/api/v1/teams/{id}` | チーム削除 |
| POST | `/api/v1/teams/{id}/members` | チームメンバー追加 |
| DELETE | `/api/v1/teams/{id}/members/{member_id}` | チームメンバー削除 |

### 3.5 役割管理（基本機能のみ）
| メソッド | エンドポイント | 説明 |
|---------|---------------|------|
| GET | `/api/v1/roles` | 役割一覧取得 |
| POST | `/api/v1/roles` | 役割作成 |
| GET | `/api/v1/roles/{id}` | 役割詳細取得 |
| PUT | `/api/v1/roles/{id}` | 役割更新 |
| DELETE | `/api/v1/roles/{id}` | 役割削除 |

### 3.6 ワークフロー管理（基本機能のみ）
| メソッド | エンドポイント | 説明 |
|---------|---------------|------|
| GET | `/api/v1/workflows` | ワークフロー一覧取得 |
| POST | `/api/v1/workflows` | ワークフロー作成 |
| GET | `/api/v1/workflows/{id}` | ワークフロー詳細取得 |
| PUT | `/api/v1/workflows/{id}` | ワークフロー更新 |
| DELETE | `/api/v1/workflows/{id}` | ワークフロー削除 |
| POST | `/api/v1/workflows/{id}/start` | ワークフロー開始 |
| POST | `/api/v1/workflows/{id}/complete` | ワークフロー完了 |

### 3.7 タスク管理（基本機能のみ）
| メソッド | エンドポイント | 説明 |
|---------|---------------|------|
| GET | `/api/v1/tasks` | タスク一覧取得 |
| POST | `/api/v1/tasks` | タスク作成 |
| GET | `/api/v1/tasks/{id}` | タスク詳細取得 |
| PUT | `/api/v1/tasks/{id}` | タスク更新 |
| DELETE | `/api/v1/tasks/{id}` | タスク削除 |
| POST | `/api/v1/tasks/{id}/assign` | タスク割り当て |
| POST | `/api/v1/tasks/{id}/complete` | タスク完了 |

### 3.8 会話管理（基本機能のみ）
| メソッド | エンドポイント | 説明 |
|---------|---------------|------|
| GET | `/api/v1/conversations` | 会話一覧取得 |
| POST | `/api/v1/conversations` | 会話作成 |
| GET | `/api/v1/conversations/{id}` | 会話詳細取得 |
| DELETE | `/api/v1/conversations/{id}` | 会話削除 |
| GET | `/api/v1/conversations/{id}/messages` | メッセージ一覧取得 |
| POST | `/api/v1/conversations/{id}/messages` | メッセージ送信 |

### 3.9 Obsidian連携（基本機能のみ）
| メソッド | エンドポイント | 説明 |
|---------|---------------|------|
| GET | `/api/v1/obsidian/status` | Obsidian連携状態確認 |
| POST | `/api/v1/obsidian/connect` | Obsidian連携設定 |
| PUT | `/api/v1/obsidian/settings` | Obsidian設定更新 |
| GET | `/api/v1/obsidian/search` | Obsidian内検索 |
| POST | `/api/v1/obsidian/notes` | ノート作成 |
| PUT | `/api/v1/obsidian/notes/{note_id}` | ノート更新 |
| DELETE | `/api/v1/obsidian/notes/{note_id}` | ノート削除 |

### 3.10 司書AI管理（基本機能のみ）
| メソッド | エンドポイント | 説明 |
|---------|---------------|------|
| GET | `/api/v1/librarian/status` | 司書AI状態確認 |
| POST | `/api/v1/librarian/query` | 司書AIへの問い合わせ |
| GET | `/api/v1/librarian/knowledge` | 知識ベース一覧取得 |
| POST | `/api/v1/librarian/knowledge` | 知識ベース追加 |
| PUT | `/api/v1/librarian/knowledge/{id}` | 知識ベース更新 |
| DELETE | `/api/v1/librarian/knowledge/{id}` | 知識ベース削除 |

### 3.11 AI協議管理（基本機能のみ）
| メソッド | エンドポイント | 説明 |
|---------|---------------|------|
| GET | `/api/v1/discussions` | AI協議一覧取得 |
| POST | `/api/v1/discussions` | AI協議開始 |
| GET | `/api/v1/discussions/{id}` | AI協議詳細取得 |
| PUT | `/api/v1/discussions/{id}` | AI協議更新 |
| DELETE | `/api/v1/discussions/{id}` | AI協議削除 |
| POST | `/api/v1/discussions/{id}/join` | AI協議参加 |
| POST | `/api/v1/discussions/{id}/leave` | AI協議退出 |
| GET | `/api/v1/discussions/{id}/messages` | 協議メッセージ一覧取得 |
| POST | `/api/v1/discussions/{id}/messages` | 協議メッセージ送信 |

### 3.12 プラン承認システム（基本機能のみ）
| メソッド | エンドポイント | 説明 |
|---------|---------------|------|
| GET | `/api/v1/plans` | プラン一覧取得 |
| POST | `/api/v1/plans` | プラン作成 |
| GET | `/api/v1/plans/{id}` | プラン詳細取得 |
| PUT | `/api/v1/plans/{id}` | プラン更新 |
| DELETE | `/api/v1/plans/{id}` | プラン削除 |
| POST | `/api/v1/plans/{id}/submit` | プラン提出 |
| POST | `/api/v1/plans/{id}/approve` | プラン承認 |
| POST | `/api/v1/plans/{id}/reject` | プラン却下 |

**エンドポイント総数**: 約60個（エンタープライズ級の100個以上から削減）

## 4. 詳細API仕様

### 4.1 認証・ユーザー管理

#### 4.1.1 ログイン
```http
POST /api/v1/auth/login
```

**リクエストボディ:**
```json
{
  "username": "string",
  "password": "string"
}
```

**レスポンス:**
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "username": "string",
    "email": "string",
    "full_name": "string",
    "role": "string",
    "created_at": "2025-08-13T10:00:00Z"
  }
}
```

#### 4.1.2 ユーザー登録
```http
POST /api/v1/auth/register
```

**リクエストボディ:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "full_name": "string"
}
```

**レスポンス:**
```json
{
  "id": 1,
  "username": "string",
  "email": "string",
  "full_name": "string",
  "created_at": "2025-08-13T10:00:00Z"
}
```

### 4.2 AI秘書管理

#### 4.2.1 AI秘書作成
```http
POST /api/v1/assistants
```

**リクエストボディ:**
```json
{
  "name": "string",
  "description": "string",
  "ai_provider": "openai|claude|gemini",
  "model": "string",
  "api_key": "string",
  "persona_id": 1,
  "team_id": 1,
  "is_active": true,
  "settings": {
    "temperature": 0.7,
    "max_tokens": 1000,
    "system_prompt": "string"
  }
}
```

**レスポンス:**
```json
{
  "id": 1,
  "name": "string",
  "description": "string",
  "ai_provider": "string",
  "model": "string",
  "persona_id": 1,
  "team_id": 1,
  "is_active": true,
  "created_at": "2025-08-13T10:00:00Z",
  "updated_at": "2025-08-13T10:00:00Z"
}
```

### 4.3 ペルソナ管理

#### 4.3.1 ペルソナ作成
```http
POST /api/v1/personas
```

**リクエストボディ:**
```json
{
  "name": "string",
  "description": "string",
  "personality": "string",
  "role_id": 1,
  "is_default": false,
  "metadata": {
    "voice_tone": "string",
    "response_style": "string",
    "specialization": "string"
  }
}
```

**レスポンス:**
```json
{
  "id": 1,
  "name": "string",
  "description": "string",
  "personality": "string",
  "role_id": 1,
  "is_default": false,
  "created_at": "2025-08-13T10:00:00Z",
  "updated_at": "2025-08-13T10:00:00Z"
}
```

### 4.4 AI協議管理（基本機能のみ）

#### 4.4.1 AI協議開始
```http
POST /api/v1/discussions
```

**リクエストボディ:**
```json
{
  "title": "string",
  "description": "string",
  "topic": "string",
  "participant_assistant_ids": [1, 2, 3],
  "max_participants": 5,
  "discussion_type": "collaborative|debate|brainstorming"
}
```

**レスポンス:**
```json
{
  "id": 1,
  "title": "string",
  "description": "string",
  "topic": "string",
  "status": "active",
  "discussion_type": "string",
  "created_at": "2025-08-13T10:00:00Z",
  "started_at": "2025-08-13T10:00:00Z",
  "participants": [
    {
      "assistant_id": 1,
      "assistant_name": "string",
      "joined_at": "2025-08-13T10:00:00Z"
    }
  ]
}
```

### 4.5 ペルソナアイコン・画像管理（基本機能のみ）

#### 4.5.1 ペルソナアイコン設定
```http
POST /api/v1/personas/{id}/icon
```

**リクエストボディ:**
```json
{
  "icon_type": "preset|upload",
  "icon_data": {
    "preset_name": "string", // icon_typeがpresetの場合
    "upload_file": "file"    // icon_typeがuploadの場合
  }
}
```

**レスポンス:**
```json
{
  "id": 1,
  "icon_url": "string",
  "icon_type": "string",
  "updated_at": "2025-08-13T10:00:00Z"
}
```

#### 4.5.2 ペルソナ画像設定
```http
POST /api/v1/personas/{id}/image
```

**リクエストボディ:**
```http
Content-Type: multipart/form-data

{
  "image_file": "file"
}
```

**レスポンス:**
```json
{
  "id": 1,
  "image_url": "string",
  "updated_at": "2025-08-13T10:00:00Z"
}
```

#### 4.5.3 プリセットアイコン一覧取得
```http
GET /api/v1/personas/icons/presets
```

**クエリパラメータ:**
- `category`: 専門性カテゴリ（development, design, marketing, sales, management）
- `limit`: 取得件数（デフォルト: 20）

**レスポンス:**
```json
{
  "presets": [
    {
      "id": "string",
      "name": "string",
      "category": "string",
      "icon_url": "string",
      "tags": ["string"]
    }
  ],
  "total_count": 50
}
```

### 4.6 プラン承認システム（基本機能のみ）

#### 4.6.1 プラン作成
```http
POST /api/v1/plans
```

**リクエストボディ:**
```json
{
  "title": "string",
  "description": "string",
  "objective": "string",
  "scope": "string",
  "timeline": {
    "estimated_start": "2025-08-13T10:00:00Z",
    "estimated_end": "2025-08-20T10:00:00Z"
  },
  "resources": {
    "required_assistants": [1, 2],
    "estimated_cost": 0
  },
  "assistant_id": 1
}
```

**レスポンス:**
```json
{
  "id": 1,
  "title": "string",
  "description": "string",
  "objective": "string",
  "status": "draft",
  "version": 1,
  "assistant_id": 1,
  "created_at": "2025-08-13T10:00:00Z",
  "submitted_at": null,
  "approved_at": null
}
```

#### 4.6.2 プラン承認
```http
POST /api/v1/plans/{id}/approve
```

**リクエストボディ:**
```json
{
  "approved": true,
  "comments": "string"
}
```

**レスポンス:**
```json
{
  "id": 1,
  "plan_id": 1,
  "approved": true,
  "comments": "string",
  "approved_by": "string",
  "approval_date": "2025-08-13T10:00:00Z",
  "status": "approved"
}
```

## 5. データモデル

### 5.1 共通フィールド
```json
{
  "id": "integer (Primary Key)",
  "created_at": "datetime",
  "updated_at": "datetime",
  "deleted_at": "datetime (Soft Delete)"
}
```

### 5.2 エンティティ関係図（簡素化版）
```
User (1) ←→ (N) Assistant
User (1) ←→ (N) Team
Team (1) ←→ (N) Assistant
Persona (1) ←→ (N) Assistant
Role (1) ←→ (N) Persona
Assistant (1) ←→ (N) Task
Workflow (1) ←→ (N) Task
Conversation (1) ←→ (N) Message
Discussion (1) ←→ (N) DiscussionParticipant
Discussion (1) ←→ (N) DiscussionMessage
Plan (1) ←→ (N) PlanApproval
```

## 6. エラーハンドリング（基本機能のみ）

### 6.1 共通エラーコード
| コード | 説明 | HTTPステータス |
|--------|------|---------------|
| `AUTH_001` | 認証トークン無効 | 401 |
| `AUTH_002` | 認証トークン期限切れ | 401 |
| `VAL_001` | バリデーションエラー | 422 |
| `NOT_FOUND_001` | リソース未発見 | 404 |
| `CONFLICT_001` | リソース競合 | 409 |

### 6.2 エラーレスポンス例
```json
{
  "error": {
    "code": "VAL_001",
    "message": "バリデーションエラー",
    "details": {
      "field": "email",
      "message": "有効なメールアドレスを入力してください"
    }
  },
  "timestamp": "2025-08-13T10:00:00Z"
}
```

## 7. レート制限（基本設定のみ）

### 7.1 制限設定
- **認証エンドポイント**: 10回/分
- **一般API**: 200回/分
- **検索API**: 100回/分
- **ファイルアップロード**: 20回/分

### 7.2 レート制限ヘッダー
```http
X-RateLimit-Limit: 200
X-RateLimit-Remaining: 180
X-RateLimit-Reset: 1640995200
```

## 8. セキュリティ（基本機能のみ）

### 8.1 認証・認可
- JWT Token認証
- 基本認証（複雑なRBACは不要）
- API Key管理（AI秘書用）

### 8.2 データ保護
- HTTPS通信必須
- 機密データの暗号化
- SQL Injection対策
- XSS対策

### 8.3 監査ログ（基本機能のみ）
- API呼び出しログ
- 認証・認可ログ
- データ変更ログ

## 9. パフォーマンス（ローカル環境最適化）

### 9.1 レスポンス時間目標
- **単純なCRUD操作**: < 200ms
- **検索・集計**: < 1000ms
- **複雑な処理**: < 3秒

### 9.2 最適化戦略
- データベースクエリ最適化
- 基本キャッシュ機能
- ページネーション
- 非同期処理（基本レベル）

## 10. テスト（基本機能のみ）

### 10.1 テスト戦略
- Unit Test (Pytest)
- Integration Test
- API Test (Postman/Newman)

### 10.2 テスト環境
- 開発環境: テスト用データベース
- ローカル環境: 基本テスト実行

## 11. ドキュメント・ツール

### 11.1 API仕様書
- OpenAPI 3.0 (Swagger)
- ReDoc
- Postman Collection

### 11.2 開発ツール
- FastAPI自動生成ドキュメント
- インタラクティブAPIテスト
- スキーマ検証

## 12. バージョニング

### 12.1 バージョン管理
- URLパス: `/api/v1/`
- 後方互換性維持

### 12.2 非推奨・廃止
- 非推奨通知: 3ヶ月前
- 廃止通知: 1ヶ月前
- 移行ガイド提供

## 13. 監視・運用（基本機能のみ）

### 13.1 監視項目
- API応答時間
- エラー率
- 基本リソース使用量

### 13.2 アラート設定
- エラー率 > 10%
- 応答時間 > 3秒
- 可用性 < 95%

## 14. 今後の拡張予定（段階的実装）

### 14.1 短期（3ヶ月以内）
- 基本WebSocket対応
- ファイルアップロード機能
- 基本バッチ処理API

### 14.2 中期（6ヶ月以内）
- 基本GraphQL対応
- 基本マイクロサービス化

### 14.3 長期（1年以内）
- 基本gRPC対応
- 基本イベント駆動アーキテクチャ

---

**作成日**: 2025-08-13  
**作成者**: AI Assistant  
**バージョン**: 2.0（ローカル・シングルユーザー級対応版）  
**次回更新予定**: 2025-08-20  
**設計レベル**: ローカル・シングルユーザー級（エンタープライズ級から調整完了） 