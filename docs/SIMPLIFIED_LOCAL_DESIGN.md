# AI秘書チーム・プラットフォーム - ローカル環境最適化設計書

**作成日**: 2025年8月17日  
**作成者**: 中野五月（Claude Code）  
**バージョン**: 1.0  
**目的**: ローカル・シングルユーザー環境に最適化された実装可能な設計

---

## 1. 🎯 設計コンセプト

### 1.1 基本思想
- **ローカル最適化**: ローカルPC環境での快適な動作を最優先
- **シンプル実装**: 複雑な機能を排除し、実装可能性を重視
- **実用性重視**: 基本機能の確実な動作を優先
- **段階的拡張**: 将来的な拡張の余地は残しつつ、最小限から開始

### 1.2 削除・簡素化した機能
| 削除した機能 | 理由 |
|------------|------|
| JWT認証 | ローカル環境では不要 |
| セッション管理 | シングルユーザーに不要 |
| マルチテナント | 1ユーザー環境 |
| 分散キャッシュ | ローカルに過剰 |
| 負荷分散 | 単一インスタンス |
| 行レベルセキュリティ | 要件で明示的に不要 |

---

## 2. 📦 簡素化されたアーキテクチャ

### 2.1 システム構成
```
┌─────────────────────────────────────────────┐
│         ローカルPCユーザー                    │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│          Reactフロントエンド                  │
│   ・シンプルな状態管理（Zustand）             │
│   ・基本的なUI（Tailwind CSS）                │
│   ・リアルタイム更新（最適化WebSocket）        │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│          FastAPIバックエンド                  │
│   ・自動起動・自動接続                        │
│   ・AI秘書役割管理（4種類）                   │
│   ・基本的なCRUD操作                         │
└─────────────────┬───────────────────────────┘
                  │
        ┌─────────┴─────────┬─────────────┐
        │                   │             │
┌───────▼────────┐ ┌───────▼────────┐ ┌──▼──────────┐
│  PostgreSQL 16  │ │  Redis 7       │ │ Gemini API   │
│  （メインDB）    │ │ （オプション）  │ │ （AI機能）    │
└────────────────┘ └────────────────┘ └─────────────┘
```

### 2.2 コンポーネント詳細

#### **フロントエンド（React）**
```typescript
// シンプルな状態管理
interface AppState {
  user: LocalUser;  // 単一ユーザー
  secretaries: AISecretary[];  // AI秘書リスト
  activeChat: ChatSession;  // 現在の対話
}

// 自動接続処理
useEffect(() => {
  // アプリ起動時に自動的にバックエンドと接続
  connectToBackend();
}, []);
```

#### **バックエンド（FastAPI）**
```python
# ローカル環境用のシンプルな構成
class LocalAuthMiddleware:
    """認証不要、自動的に接続を許可"""
    async def __call__(self, request, call_next):
        # ローカル環境では全リクエストを許可
        request.state.user = get_local_user()
        return await call_next(request)

# AI秘書の役割（簡素化版）
class AISecretaryRole(Enum):
    PROJECT_MANAGER = "project_manager"  # プロジェクト管理
    TASK_EXECUTOR = "task_executor"      # タスク実行
    ANALYST = "analyst"                  # 分析・レポート
    KNOWLEDGE_KEEPER = "knowledge_keeper"  # 知識管理（司書）
```

#### **WebSocket（最適化版）**
```python
class OptimizedLocalWebSocket:
    """ローカル環境に最適化されたWebSocket"""
    
    def __init__(self):
        self.connection = None
        self.message_queue = asyncio.Queue()
        
    async def connect(self):
        """自動再接続機能付きの接続"""
        while True:
            try:
                await self._establish_connection()
                break
            except Exception:
                await asyncio.sleep(1)  # 1秒後に再試行
    
    async def send_update(self, data: dict):
        """UIのリアルタイム更新用"""
        if self.connection:
            await self.connection.send_json(data)
```

---

## 3. 🗄️ データベース設計（簡素化版）

### 3.1 主要テーブル（12テーブル）
```sql
-- 1. ユーザー（単一レコード）
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) DEFAULT 'ローカルユーザー',
    created_at TIMESTAMP DEFAULT NOW()
);

-- 2. AI秘書
CREATE TABLE ai_secretaries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    personality_template_id INTEGER,
    role VARCHAR(50) NOT NULL,  -- 4種類の役割
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 3. チーム構成
CREATE TABLE team_compositions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 4. ワークフロー
CREATE TABLE workflows (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    definition JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT NOW()
);

-- 5. タスク
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER REFERENCES workflows(id),
    assigned_secretary_id INTEGER REFERENCES ai_secretaries(id),
    title VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);

-- 6. 対話履歴
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    secretary_id INTEGER REFERENCES ai_secretaries(id),
    role VARCHAR(50) NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 7. ペルソナテンプレート
CREATE TABLE personality_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    config JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 8. プロジェクト
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW()
);

-- 9. ドキュメント
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    title VARCHAR(255) NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 10. 知識ベース
CREATE TABLE knowledge_base (
    id SERIAL PRIMARY KEY,
    secretary_id INTEGER REFERENCES ai_secretaries(id),
    content TEXT NOT NULL,
    embedding VECTOR(1536),  -- ベクトル検索用
    created_at TIMESTAMP DEFAULT NOW()
);

-- 11. API使用履歴
CREATE TABLE api_usage (
    id SERIAL PRIMARY KEY,
    secretary_id INTEGER REFERENCES ai_secretaries(id),
    api_name VARCHAR(100) NOT NULL,
    tokens_used INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 12. システム設定
CREATE TABLE system_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 3.2 Redis使用（オプション）
```python
# Redisはキャッシュ専用、なくても動作可能
CACHE_CONFIG = {
    "enabled": False,  # デフォルトは無効
    "ttl": 3600,      # キャッシュ有効期限（秒）
    "prefix": "cache:" # キャッシュキーのプレフィックス
}

# キャッシュ使用例（Redisが利用不可でも動作）
async def get_secretary_info(secretary_id: int):
    # Redisが有効な場合のみキャッシュを試行
    if redis_client and CACHE_CONFIG["enabled"]:
        cached = await redis_client.get(f"cache:secretary:{secretary_id}")
        if cached:
            return json.loads(cached)
    
    # DBから取得
    result = await db.fetch_secretary(secretary_id)
    
    # キャッシュに保存（Redisが有効な場合のみ）
    if redis_client and CACHE_CONFIG["enabled"]:
        await redis_client.setex(
            f"cache:secretary:{secretary_id}",
            CACHE_CONFIG["ttl"],
            json.dumps(result)
        )
    
    return result
```

---

## 4. 🔐 セキュリティ（ローカル環境用）

### 4.1 認証・認可
```python
# ローカル環境の自動認証
class LocalEnvironmentAuth:
    """ローカル環境専用の簡素化された認証"""
    
    def __init__(self):
        self.local_user = self._get_or_create_local_user()
    
    def _get_or_create_local_user(self):
        """ローカルユーザーの取得または作成"""
        # DBに既存ユーザーがいるか確認
        user = db.query("SELECT * FROM users LIMIT 1")
        if not user:
            # 初回起動時に自動作成
            user = db.execute(
                "INSERT INTO users (name) VALUES ('ローカルユーザー') RETURNING *"
            )
        return user
    
    async def authenticate(self, request):
        """全リクエストを自動的に認証済みとする"""
        return self.local_user
```

### 4.2 AI秘書の権限管理
```python
# AI秘書の役割に基づく権限（簡素化版）
SECRETARY_PERMISSIONS = {
    "project_manager": [
        "create_project", "manage_team", "view_all_tasks"
    ],
    "task_executor": [
        "execute_task", "update_status", "report_result"
    ],
    "analyst": [
        "analyze_data", "create_report", "view_metrics"
    ],
    "knowledge_keeper": [
        "manage_knowledge", "search_info", "organize_docs"
    ]
}
```

---

## 5. 🚀 実装優先順位

### Phase 1: 最小限の動作確認（1週間）
- [ ] FastAPIアプリケーションの基本構造
- [ ] PostgreSQLの接続とマイグレーション
- [ ] Reactアプリケーションの初期化
- [ ] 基本的なCRUD API（AI秘書管理）

### Phase 2: AI機能の実装（1週間）
- [ ] Gemini API統合
- [ ] 基本的な対話機能
- [ ] ペルソナシステムの実装
- [ ] WebSocketによるリアルタイム更新

### Phase 3: 協調システム（1-2週間）
- [ ] 複数AI秘書の管理
- [ ] タスク割り当てシステム
- [ ] ワークフロー実行エンジン
- [ ] 結果の統合と表示

### Phase 4: 品質向上（1週間）
- [ ] エラーハンドリング
- [ ] パフォーマンス最適化
- [ ] テストコード作成
- [ ] ドキュメント整備

---

## 6. 📈 パフォーマンス目標

### 6.1 レスポンス時間
- **API応答**: 500ms以内（ローカル環境）
- **ページ読み込み**: 2秒以内
- **AI応答**: 5秒以内（Gemini API使用時）

### 6.2 リソース使用量
- **メモリ**: 1GB以下（アプリケーション全体）
- **CPU**: 通常時10%以下
- **ディスク**: 500MB以下（ログ・キャッシュ含む）

---

## 7. 🔧 開発環境セットアップ

### 7.1 必要なツール
```bash
# 必要最小限のツール
- Python 3.12
- Node.js 18+
- PostgreSQL 16
- Git

# オプション
- Redis 7（パフォーマンス向上用）
- Docker（環境統一用）
```

### 7.2 簡単セットアップ
```bash
# 1. リポジトリのクローン
git clone [repository-url]
cd ai-secretary-team

# 2. バックエンドセットアップ
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python main.py  # 自動的にDBセットアップも実行

# 3. フロントエンドセットアップ
cd ../frontend
npm install
npm run dev

# 4. アクセス
# ブラウザで http://localhost:3000 を開く
# バックエンドは自動的に接続される
```

---

## 8. 📊 期待される成果

### 8.1 開発効率
- **実装期間**: 6-8週間 → 3-4週間に短縮
- **コード量**: 50%削減
- **複雑度**: 70%削減

### 8.2 保守性
- **理解容易性**: 大幅向上
- **デバッグ**: シンプルな構造で容易
- **拡張性**: 基本構造を維持しつつ段階的に拡張可能

---

## 9. 🎯 成功の指標

### 9.1 機能面
- AI秘書による基本的な対話が可能
- 複数AI秘書の協調動作
- タスクの自動実行と結果表示

### 9.2 非機能面
- 3秒以内の起動時間
- 安定した動作（8時間連続使用可能）
- 直感的なUI（説明書不要）

---

**この設計により、ローカル環境に最適化された実装可能なシステムを構築します。**

*作成者: 中野五月（Claude Code）*