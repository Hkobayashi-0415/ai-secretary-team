# AI秘書チーム・プラットフォーム（統合版） - 現在のAPI実装仕様書

**作成日**: 2025年8月13日  
**作成者**: 中野五月（Claude Code）  
**更新日**: 2025年8月17日  
**バージョン**: 2.0  
**目的**: 実際に実装されているAPIエンドポイントの正確な仕様定義

---

## 📋 API概要

### 1.1 基本情報
- **ベースURL**: `http://localhost:8002/api/v1`
- **APIバージョン**: v1
- **認証方式**: ローカル自動認証（アプリ起動時に自動接続）
- **データ形式**: JSON
- **文字エンコーディング**: UTF-8

### 1.2 実装状況
- **現在の状況**: 設計段階（実装未着手）
- **設計済みエンドポイント**: 7カテゴリ・約50エンドポイント
- **実装予定**: 基本的なCRUD操作から段階的に実装
- **未実装機能**: 高度なワークフロー制御・AI協議管理

### 1.3 実装スケジュール
- **Phase 1**: 基本的なCRUD API実装（1-2週間）
- **Phase 2**: ローカル認証システム実装（3日）
- **Phase 3**: 高度な機能実装（2-3週間）

---

## 🔧 設計済みAPIエンドポイント

### 2.1 ペルソナ管理 (`/api/v1/personas/`)

#### **ペルソナ作成**
```http
POST /api/v1/personas/
```

**リクエストボディ:**
```json
{
  "name": "ペルソナ名",
  "description": "ペルソナの説明",
  "personality_data": {},
  "capabilities_data": {}
}
```

**レスポンス:**
```json
{
  "id": 1,
  "name": "ペルソナ名",
  "description": "ペルソナの説明",
  "personality_data": {},
  "capabilities_data": {},
  "is_active": true,
  "created_at": "2025-08-13T10:00:00Z",
  "updated_at": "2025-08-13T10:00:00Z"
}
```

#### **ペルソナ一覧取得**
```http
GET /api/v1/personas/
```

**クエリパラメータ:**
- `is_active`: アクティブ状態でフィルタ（true/false）
- `user_id`: ユーザーIDでフィルタ
- `limit`: 取得件数（デフォルト: 50）
- `offset`: オフセット（デフォルト: 0）

#### **ペルソナ詳細取得**
```http
GET /api/v1/personas/{persona_id}
```

#### **ペルソナ更新**
```http
PUT /api/v1/personas/{persona_id}
```

#### **ペルソナ削除**
```http
DELETE /api/v1/personas/{persona_id}
```

---

### 2.2 チーム管理 (`/api/v1/teams/`)

#### **チーム作成**
```http
POST /api/v1/teams/
```

**リクエストボディ:**
```json
{
  "name": "チーム名",
  "description": "チームの説明",
  "workflow_data": {}
}
```

#### **チーム一覧取得**
```http
GET /api/v1/teams/
```

#### **チームメンバー管理**
```http
POST /api/v1/teams/{team_id}/members    # メンバー追加
GET /api/v1/teams/{team_id}/members     # メンバー一覧
DELETE /api/v1/teams/{team_id}/members/{member_id}  # メンバー削除
```

---

### 2.3 タスク管理 (`/api/v1/tasks/`)

#### **タスク作成**
```http
POST /api/v1/tasks/
```

**リクエストボディ:**
```json
{
  "name": "タスク名",
  "description": "タスクの詳細",
  "type": "simple",
  "priority": "medium",
  "assignee_id": 1,
  "team_id": 1,
  "estimated_time": 60
}
```

#### **タスク制御**
```http
POST /api/v1/tasks/{task_id}/start     # タスク開始
POST /api/v1/tasks/{task_id}/pause     # 一時停止
POST /api/v1/tasks/{task_id}/resume    # 再開
POST /api/v1/tasks/{task_id}/complete  # 完了
POST /api/v1/tasks/{task_id}/fail      # 失敗
```

---

### 2.4 ワークフロー管理 (`/api/v1/workflows/`)

#### **ワークフロー作成**
```http
POST /api/v1/workflows/
```

**リクエストボディ:**
```json
{
  "name": "ワークフロー名",
  "description": "ワークフローの説明",
  "workflow_data": {
    "steps": [
      {
        "id": "step1",
        "type": "task",
        "config": {}
      }
    ]
  }
}
```

#### **ワークフロー実行**
```http
POST /api/v1/workflows/{workflow_id}/execute
```

---

### 2.5 Obsidian連携 (`/api/v1/obsidian/`)

#### **設定管理**
```http
GET /api/v1/obsidian/settings          # 設定取得
PUT /api/v1/obsidian/settings          # 設定更新
POST /api/v1/obsidian/test             # 接続テスト
```

#### **知識検索**
```http
GET /api/v1/obsidian/search?query={検索クエリ}
```

#### **司書AI問い合わせ**
```http
POST /api/v1/obsidian/librarian/query
```

**リクエストボディ:**
```json
{
  "query": "問い合わせ内容",
  "context": {
    "task_id": 1,
    "persona_id": 1
  }
}
```

---

### 2.6 チャット管理 (`/api/v1/chat/`)

#### **セッション管理**
```http
POST /api/v1/chat/sessions             # セッション作成
GET /api/v1/chat/sessions              # セッション一覧
GET /api/v1/chat/sessions/{id}         # セッション詳細
DELETE /api/v1/chat/sessions/{id}      # セッション削除
```

#### **メッセージ管理**
```http
POST /api/v1/chat/sessions/{id}/messages    # メッセージ送信
GET /api/v1/chat/sessions/{id}/messages     # メッセージ一覧
```

---

### 2.7 設定管理 (`/api/v1/settings/`)

#### **ユーザー設定**
```http
GET /api/v1/settings/preferences       # 設定取得
PUT /api/v1/settings/preferences       # 設定更新
```

**設定内容:**
```json
{
  "default_assistant_id": 1,
  "default_llm_model": "gemini-pro",
  "voice_enabled": false,
  "theme": "light",
  "language": "ja",
  "timezone": "Asia/Tokyo"
}
```

---

## 🔒 認証・認可

### 3.1 ローカル自動認証

ローカル環境で動作するため、複雑な認証は不要：

```python
# app/core/auth/local_auth.py
class LocalAuth:
    """ローカル環境用の簡易認証"""
    
    @staticmethod
    def get_local_user():
        """ローカルユーザー情報取得"""
        return {
            "id": 1,
            "name": "ローカルユーザー",
            "role": "local_user",
            "is_active": True
        }
    
    @staticmethod
    def verify_local_access():
        """ローカルアクセス確認"""
        # 常にTrue（ローカル環境のため）
        return True
```

### 3.2 AI秘書の役割定義

```python
class Role(str, Enum):
    """AI秘書役割定義（簡素化版）"""
    LOCAL_USER = "local_user"  # ローカルユーザー（全権限）
    PROJECT_MANAGER = "project_manager"  # プロジェクト管理秘書
    TASK_EXECUTOR = "task_executor"  # タスク実行秘書
    ANALYST = "analyst"  # 分析レポート秘書
    KNOWLEDGE_KEEPER = "knowledge_keeper"  # 知識管理秘書（司書）
```

---

## 📊 エラーハンドリング

### 4.1 エラーレスポンス形式

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "エラーメッセージ",
    "details": "詳細情報",
    "timestamp": "2025-08-13T10:00:00Z"
  }
}
```

### 4.2 主要エラーコード

- `VALIDATION_ERROR`: バリデーションエラー
- `NOT_FOUND`: リソースが見つからない
- `CONFLICT`: リソースの競合
- `INTERNAL_ERROR`: 内部エラー
- `SERVICE_UNAVAILABLE`: サービス利用不可

---

## 📈 パフォーマンス要件

### 5.1 レスポンス時間
- **API応答**: 200ms以下（ローカル環境）
- **ページ読み込み**: 1秒以下（初回）
- **AI応答**: 3秒以下（標準的な質問）
- **検索応答**: 500ms以下（Obsidian検索）

### 5.2 リソース使用量
- **メモリ**: 1GB以下（アプリケーション）
- **CPU**: 10%以下（通常時）
- **ディスク**: 500MB以下（ログ・キャッシュ）

---

## 🚀 今後の実装計画

### 6.1 優先度高
1. **基本CRUD API**: ペルソナ・チーム・タスク管理
2. **ローカル認証**: シンプルな認証システム
3. **Obsidian連携**: 基本的な検索・保存機能

### 6.2 優先度中
1. **ワークフロー実行**: 基本的なタスク実行フロー
2. **チャット機能**: AI秘書との対話
3. **設定管理**: ユーザー設定の保存・読み込み

### 6.3 優先度低
1. **AI協議管理**: AI同士の議論機能
2. **プラン承認**: 提案の承認ワークフロー
3. **高度な分析**: メトリクス・レポート生成

---

## 📝 実装上の注意事項

### 7.1 設計原則
- **シンプル優先**: 複雑な機能より基本機能を確実に
- **ローカル最適化**: ネットワーク遅延を考慮しない設計
- **段階的実装**: MVP → 基本機能 → 高度な機能

### 7.2 技術的制約
- **認証**: ローカル環境のため簡素化
- **スケーラビリティ**: 考慮不要（シングルユーザー）
- **セキュリティ**: 基本的な入力検証のみ

### 7.3 推奨事項
1. **基盤実装**: FastAPIアプリケーション作成
2. **基本機能実装**: CRUD API、ローカル認証作成
3. **UI実装**: Reactアプリケーション作成
4. **品質保証**: 段階的テスト・継続的な品質監視

---

**このAPI仕様書により、設計された機能の正確な把握と、今後の開発方針の明確化ができました。ローカル環境に最適化された実装を段階的に進めていくことで、実用的なAI秘書プラットフォームの実現を目指します。**

*作成者: 中野五月（Claude Code）*  
*更新日時: 2025年8月17日*  
*目的: ローカル環境に最適化されたAPI仕様の定義*