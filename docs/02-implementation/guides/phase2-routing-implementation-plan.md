# Phase 2: インテリジェント・ルーティング基盤 実装計画書

## 1. 設計方針

### 1.1 基本方針
**既存の正規化されたDB設計を最大限活用し、適応的LLMルーティング・アーキテクチャを実現する**

参考: Avengers-Pro (https://github.com/ZhangYiqun018/AvengersPro)

### 1.2 既存DB構造の活用方針

#### 活用するテーブル
- `skill_definitions`: スキル定義とLLMルーティングルール
- `assistant_skills`: アシスタントとスキルの関連付け  
- `agents`: エージェント定義とベクトル検索
- `assistants`: AIアシスタント基本情報

## 2. 実装計画

### 2.1 スキル管理機能の実装

#### DB拡張不要（既存構造を活用）
```python
# skill_definitions.configuration の活用例
{
  "skill_category": "analysis",  # 分析、リサーチ、創造など
  "llm_routing": {
    "preferred": "gemini-pro",
    "fallback": ["gpt-3.5-turbo", "claude-instant"],
    "cost_weight": 0.3,
    "performance_weight": 0.7
  },
  "capabilities": ["data_analysis", "chart_generation", "insight_extraction"]
}
```

#### 実装タスク
1. SkillDefinitionモデルの実装
2. AssistantSkillモデルの実装  
3. スキルCRUD APIの実装
4. スキル選択UIコンポーネントの実装

### 2.2 LLMルーティング・エンジンの実装

#### アーキテクチャ
```
User Request
    ↓
Task Analyzer (タスク内容を解析)
    ↓
Skill Matcher (必要なスキルを特定)
    ↓
LLM Router (最適なLLMを選択)
    ↓
Agent Selector (エージェントを選択)
    ↓
Execution
```

#### 実装タスク
1. `backend/app/services/routing/`ディレクトリ作成
2. `LLMRouter`クラスの実装
3. `SkillMatcher`クラスの実装
4. `AgentSelector`クラスの実装

### 2.3 エージェント管理機能の実装

#### ディレクトリ構造
```
backend/app/agents/
├── system/           # システム提供エージェント
│   ├── data-analysis.md
│   ├── research.md
│   └── creative-writing.md
└── user/            # ユーザー定義エージェント
    └── {user_id}/
        └── custom-agent.md
```

#### agentsテーブルの活用
```python
# 既存のagentsテーブルを活用
class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(UUID)
    name = Column(String)
    description = Column(Text)
    file_path = Column(String)  # agents/ディレクトリのパス
    vector = Column(Vector(768))  # ベクトル検索用
```

### 2.4 チャット機能の実装

#### 既存テーブルの活用
- `conversations`: 会話セッション管理
- `messages`: メッセージ履歴

#### WebSocket実装
```python
# backend/app/api/v1/websocket/chat.py
@router.websocket("/ws/chat/{conversation_id}")
async def chat_endpoint(websocket: WebSocket, conversation_id: str):
    # 1. タスク解析
    # 2. スキルマッチング
    # 3. LLMルーティング
    # 4. エージェント選択
    # 5. 実行とストリーミング応答
```

## 3. 実装スケジュール

### Week 1: 基盤整備
- [ ] 既存テーブルのモデル化完了
- [ ] ルーティングエンジンの基本実装
- [ ] エージェントディレクトリ構造の整備

### Week 2: API実装
- [ ] スキル管理API完成
- [ ] LLMルーティングAPI完成  
- [ ] エージェント選択API完成

### Week 3: 統合とUI
- [ ] WebSocket通信の実装
- [ ] チャットUIの実装
- [ ] エンドツーエンドテスト

## 4. 成功指標

- [ ] スキルベースでLLMが自動選択される
- [ ] エージェントが動的に選択される
- [ ] レスポンスタイム2秒以内
- [ ] テストカバレッジ85%以上

## 5. 技術的決定事項

### なぜ既存DB設計を維持するか

1. **正規化の利点**
   - スキル定義の重複を防ぐ
   - 更新異常を回避
   - データ整合性を保証

2. **拡張性**
   - スキルごとの詳細設定が可能
   - 将来的な機能追加が容易

3. **パフォーマンス**
   - インデックスが既に最適化済み
   - JOINによる効率的なデータ取得

4. **既存実装との互換性**
   - Phase 1の成果を無駄にしない
   - 段階的な機能追加が可能

## 6. 次のステップ

1. この計画書の承認を得る
2. 既存テーブルのSQLAlchemyモデルを実装
3. ルーティングエンジンのプロトタイプを作成
4. 段階的に機能を追加していく

---

*この実装計画は既存のDB構造を最大限活用し、かつ新しい要件を満たすように設計されています。*