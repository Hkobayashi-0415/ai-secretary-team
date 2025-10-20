# Phase 2: ログ・エラー処理設計書

## 1. 設計概要

### 1.1 設計目的
統合版プラットフォームのログ・エラー処理システムにおいて、ローカル環境での開発・運用に最適化された、シンプルで実用的なログ管理・エラー処理を実現し、システムの安定性・デバッグ性・保守性を確保する設計仕様を定義する。

**設計レベル**: ローカル・シングルユーザー級（エンタープライズ級・大規模システム対応は不要）
**対象規模**: 1ユーザー、1万-10万レコード
**機能範囲**: 基本機能に集中（高度な監査・セキュリティ・パフォーマンス最適化は不要）

### 1.2 設計の役割
- **基本ログ管理**: 全システム・全コンポーネントでの統一的なログ出力
- **基本トレーサビリティ**: リクエスト・処理・エラーの基本追跡
- **基本エラー検出**: 異常・障害の基本発見・対応
- **開発支援**: 開発・テスト・運用時の問題特定・解決支援
- **ローカル監視**: ローカル環境での基本システム状態監視

### 1.3 対象範囲
- **全スクリプト**: Python・JavaScript・TypeScript・シェルスクリプト
- **全コンポーネント**: フロントエンド・バックエンド・AI処理・データベース
- **環境**: 開発・ローカル環境（本番環境は不要）
- **処理**: ユーザー操作・API処理・AI処理・システム処理

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

## 2. ログシステム設計

### 2.1 ログアーキテクチャ（簡素化版）
**基本ログシステム**:
```
┌─────────────────────────────────────────────────────────┐
│ アプリケーション層                                      │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│ │ フロントエンド│ │ バックエンド│ │ AI処理      │        │
│ │ ログ        │ │ ログ        │ │ ログ        │        │
│ └─────────────┘ └─────────────┘ └─────────────┘        │
├─────────────────────────────────────────────────────────┤
│ ログ集約層（基本機能のみ）                              │
│ ┌─────────────┐ ┌─────────────┐                        │
│ │ ログコレクター│ │ ログパーサー│                        │
│ └─────────────┘ └─────────────┘                        │
├─────────────────────────────────────────────────────────┤
│ ストレージ層（基本機能のみ）                            │
│ ┌─────────────┐ ┌─────────────┐                        │
│ │ 短期保存    │ │ 長期保存    │                        │
│ │ (PostgreSQL)│ │ (ファイル)  │                        │
│ └─────────────┘ └─────────────┘                        │
├─────────────────────────────────────────────────────────┤
│ 基本監視層（基本機能のみ）                              │
│ ┌─────────────┐ ┌─────────────┐                        │
│ │ 基本ログ分析│ │ 基本アラート│                        │
│ └─────────────┘ └─────────────┘                        │
└─────────────────────────────────────────────────────────┘
```

### 2.2 ログレベル設計（基本機能のみ）
**標準ログレベル**:
- **CRITICAL**: システム停止・重大障害（即座対応必須）
- **ERROR**: エラー・処理失敗（短時間内対応必要）
- **WARNING**: 警告・注意事項（監視・対応検討）
- **INFO**: 情報・処理状況（通常運用情報）
- **DEBUG**: 詳細情報・デバッグ情報（開発・テスト時）

**カスタムログレベル（基本機能のみ）**:
- **AUDIT**: 監査・セキュリティ関連（認証・認可・操作履歴）
- **PERFORMANCE**: パフォーマンス関連（処理時間・リソース使用量）

### 2.3 ログフォーマット設計（基本機能のみ）
**構造化ログ（JSON形式）**:
```json
{
  "timestamp": "2025-01-13T10:30:00.123Z",
  "level": "INFO",
  "logger": "ai_secretary.api.persona",
  "message": "ペルソナ作成完了",
  "request_id": "req_12345",
  "user_id": "user_67890",
  "component": "persona_service",
  "function": "create_persona",
  "line_number": 156,
  "file_path": "/app/services/persona.py",
  "execution_time_ms": 245,
  "context": {
    "persona_id": "persona_001",
    "persona_name": "プロジェクトマネージャー"
  },
  "environment": "development",
  "version": "1.0.0"
}
```

**テキストログ（人間可読形式）**:
```
2025-01-13 10:30:00.123 [INFO] [ai_secretary.api.persona] 
ペルソナ作成完了 - req_12345 user_67890 
persona_id=persona_001 persona_name=プロジェクトマネージャー 
execution_time=245ms
```

## 3. ロガークラス設計（基本機能のみ）

### 3.1 基本ロガークラス
**LoggerBaseクラス**:
```python
class LoggerBase:
    """統合版プラットフォーム用基本ロガークラス"""
    
    def __init__(self, name: str, level: str = "INFO"):
        self.name = name
        self.level = level
        self.handlers = []
        self.filters = []
        self.formatters = {}
        
    def add_handler(self, handler: LogHandler):
        """ログハンドラーの追加"""
        
    def set_level(self, level: str):
        """ログレベルの設定"""
        
    def log(self, level: str, message: str, **kwargs):
        """ログ出力の基本メソッド"""
        
    def critical(self, message: str, **kwargs):
        """CRITICALレベルログ"""
        
    def error(self, message: str, **kwargs):
        """ERRORレベルログ"""
        
    def warning(self, message: str, **kwargs):
        """WARNINGレベルログ"""
        
    def info(self, message: str, **kwargs):
        """INFOレベルログ"""
        
    def debug(self, message: str, **kwargs):
        """DEBUGレベルログ"""
```

### 3.2 基本ロガークラス（拡張版）
**BasicLoggerクラス**:
```python
class BasicLogger(LoggerBase):
    """基本機能を持つロガークラス"""
    
    def __init__(self, name: str, config: LoggerConfig):
        super().__init__(name, config.level)
        self.config = config
        
    def log_with_context(self, level: str, message: str, context: dict = None):
        """コンテキスト情報付きログ出力"""
        
    def log_performance(self, operation: str, execution_time: float, **kwargs):
        """パフォーマンスログ出力"""
        
    def log_audit(self, user_id: str, action: str, target: str, **kwargs):
        """監査ログ出力"""
```

## 4. ログハンドラー設計（基本機能のみ）

### 4.1 基本ハンドラー
**LogHandler抽象クラス**:
```python
class LogHandler(ABC):
    """ログハンドラーの抽象クラス"""
    
    @abstractmethod
    def emit(self, record: LogRecord):
        """ログレコードの出力"""
        pass
        
    @abstractmethod
    def flush(self):
        """バッファのフラッシュ"""
        pass
        
    @abstractmethod
    def close(self):
        """ハンドラーのクローズ"""
        pass
```

### 4.2 具体的ハンドラー（基本機能のみ）
**FileHandler**:
```python
class FileHandler(LogHandler):
    """ファイル出力ハンドラー"""
    
    def __init__(self, filename: str, mode: str = "a", encoding: str = "utf-8"):
        self.filename = filename
        self.mode = mode
        self.encoding = encoding
        self.file = None
        
    def emit(self, record: LogRecord):
        """ファイルへのログ出力"""
        
    def rotate(self, max_size: int = 10*1024*1024, backup_count: int = 5):
        """ログローテーション"""
```

**DatabaseHandler**:
```python
class DatabaseHandler(LogHandler):
    """データベース出力ハンドラー"""
    
    def __init__(self, connection_string: str, table_name: str = "logs"):
        self.connection_string = connection_string
        self.table_name = table_name
        self.connection = None
        
    def emit(self, record: LogRecord):
        """データベースへのログ出力"""
```

**ConsoleHandler**:
```python
class ConsoleHandler(LogHandler):
    """コンソール出力ハンドラー"""
    
    def __init__(self, colorize: bool = True):
        self.colorize = colorize
        
    def emit(self, record: LogRecord):
        """コンソールへのログ出力"""
        
    def colorize_output(self, text: str, level: str) -> str:
        """色付き出力"""
```

## 5. ログフォーマッター設計（基本機能のみ）

### 5.1 基本フォーマッター
**LogFormatter抽象クラス**:
```python
class LogFormatter(ABC):
    """ログフォーマッターの抽象クラス"""
    
    @abstractmethod
    def format(self, record: LogRecord) -> str:
        """ログレコードのフォーマット"""
        pass
```

### 5.2 具体的フォーマッター（基本機能のみ）
**JSONFormatter**:
```python
class JSONFormatter(LogFormatter):
    """JSON形式フォーマッター"""
    
    def __init__(self, include_metadata: bool = True):
        self.include_metadata = include_metadata
        
    def format(self, record: LogRecord) -> str:
        """JSON形式でのフォーマット"""
```

**TextFormatter**:
```python
class TextFormatter(LogFormatter):
    """テキスト形式フォーマッター"""
    
    def __init__(self, template: str = None, colorize: bool = False):
        self.template = template or self.default_template
        self.colorize = colorize
        
    def format(self, record: LogRecord) -> str:
        """テキスト形式でのフォーマット"""
```

## 6. ログフィルター設計（基本機能のみ）

### 6.1 基本フィルター
**LogFilter抽象クラス**:
```python
class LogFilter(ABC):
    """ログフィルターの抽象クラス"""
    
    @abstractmethod
    def filter(self, record: LogRecord) -> bool:
        """ログレコードのフィルタリング"""
        pass
```

### 6.2 具体的フィルター（基本機能のみ）
**LevelFilter**:
```python
class LevelFilter(LogFilter):
    """レベルベースフィルター"""
    
    def __init__(self, min_level: str, max_level: str = None):
        self.min_level = min_level
        self.max_level = max_level
        
    def filter(self, record: LogRecord) -> bool:
        """レベルの範囲チェック"""
```

**ContextFilter**:
```python
class ContextFilter(LogFilter):
    """コンテキストベースフィルター"""
    
    def __init__(self, required_context: dict):
        self.required_context = required_context
        
    def filter(self, record: LogRecord) -> bool:
        """コンテキスト情報のチェック"""
```

## 7. エラー処理設計（基本機能のみ）

### 7.1 エラーハンドリング戦略（簡素化版）
**基本エラーハンドリング**:
```
┌─────────────────────────────────────────────────────────┐
│ アプリケーション層                                      │
│ ┌─────────────┐ ┌─────────────┐                        │
│ │ グローバル  │ │ コンポーネント│                        │
│ │ エラーハンドラー│ │ エラーハンドラー│                        │
│ └─────────────┘ └─────────────┘                        │
├─────────────────────────────────────────────────────────┤
│ 基本ミドルウェア層                                      │
│ ┌─────────────┐ ┌─────────────┐                        │
│ │ 認証エラー  │ │ バリデーション│                        │
│ │ ハンドラー  │ │ エラーハンドラー│                        │
│ └─────────────┘ └─────────────┘                        │
├─────────────────────────────────────────────────────────┤
│ システム層（基本機能のみ）                              │
│ ┌─────────────┐ ┌─────────────┐                        │
│ │ 基本OSエラー│ │ データベース│                        │
│ │ ハンドラー  │ │ エラーハンドラー│                        │
│ └─────────────┘ └─────────────┘                        │
└─────────────────────────────────────────────────────────┘
```

### 7.2 カスタム例外クラス（基本機能のみ）
**基本例外クラス**:
```python
class AISecretaryException(Exception):
    """統合版プラットフォーム基本例外クラス"""
    
    def __init__(self, message: str, error_code: str = None, 
                 context: dict = None, original_exception: Exception = None):
        super().__init__(message)
        self.error_code = error_code
        self.context = context or {}
        self.original_exception = original_exception
        self.timestamp = datetime.utcnow()
        self.traceback = traceback.format_exc()
```

**業務例外クラス（基本機能のみ）**:
```python
class BusinessLogicException(AISecretaryException):
    """ビジネスロジック例外"""
    
class ValidationException(AISecretaryException):
    """バリデーション例外"""
    
class AuthenticationException(AISecretaryException):
    """認証例外"""
    
class ResourceNotFoundException(AISecretaryException):
    """リソース未発見例外"""
```

**技術例外クラス（基本機能のみ）**:
```python
class DatabaseException(AISecretaryException):
    """データベース例外"""
    
class AIProcessingException(AISecretaryException):
    """AI処理例外"""
```

### 7.3 エラーレスポンス設計（基本機能のみ）
**統一エラーレスポンス**:
```json
{
  "error": {
    "code": "PERSONA_CREATION_FAILED",
    "message": "ペルソナの作成に失敗しました",
    "details": "データベース接続エラーが発生しました",
    "timestamp": "2025-01-13T10:30:00.123Z",
    "request_id": "req_12345",
    "context": {
      "persona_name": "プロジェクトマネージャー",
      "user_id": "user_67890"
    },
    "suggestions": [
      "ネットワーク接続を確認してください",
      "しばらく時間をおいて再試行してください"
    ]
  }
}
```

## 8. ログ監視・分析設計（基本機能のみ）

### 8.1 基本監視
**ログ監視（基本機能のみ）**:
```python
class BasicLogMonitor:
    """基本ログ監視"""
    
    def __init__(self, log_file_path: str):
        self.log_file_path = log_file_path
        
    def monitor_logs(self):
        """ログの基本監視"""
        
    def detect_errors(self, log_data: dict):
        """エラーの基本検出"""
        
    def generate_basic_report(self):
        """基本レポート生成"""
```

**パターン検出（基本機能のみ）**:
```python
class BasicLogPatternDetector:
    """基本ログパターン検出"""
    
    def __init__(self, basic_patterns: List[str]):
        self.patterns = basic_patterns
        
    def detect_basic_patterns(self, log_data: dict) -> List[str]:
        """基本パターンの検出"""
```

### 8.2 基本ログ分析
**統計分析（基本機能のみ）**:
```python
class BasicLogAnalyzer:
    """基本ログ分析エンジン"""
    
    def analyze_error_rates(self, time_range: TimeRange) -> dict:
        """エラー率基本分析"""
        
    def analyze_performance(self, time_range: TimeRange) -> dict:
        """パフォーマンス基本分析"""
        
    def generate_basic_reports(self, analysis_type: str) -> dict:
        """基本レポート生成"""
```

## 9. ログセキュリティ設計（基本機能のみ）

### 9.1 機密情報保護（基本機能のみ）
**機密情報フィルタリング（基本機能のみ）**:
```python
class BasicSensitiveDataFilter:
    """基本機密データフィルター"""
    
    def __init__(self, basic_patterns: List[str]):
        self.patterns = basic_patterns
        
    def filter_basic_sensitive_data(self, log_data: dict) -> dict:
        """基本機密データのフィルタリング"""
        
    def mask_password(self, text: str) -> str:
        """パスワードのマスキング"""
        
    def mask_email(self, text: str) -> str:
        """メールアドレスのマスキング"""
```

### 9.2 アクセス制御（基本機能のみ）
**基本ログアクセス制御**:
```python
class BasicLogAccessControl:
    """基本ログアクセス制御"""
    
    def __init__(self, user_roles: dict):
        self.user_roles = user_roles
        
    def check_basic_access(self, user_id: str, log_type: str) -> bool:
        """基本アクセス権限チェック"""
```

## 10. パフォーマンス最適化設計（基本機能のみ）

### 10.1 基本非同期処理
**基本非同期ログ出力**:
```python
class BasicAsyncLogProcessor:
    """基本非同期ログ処理"""
    
    def __init__(self, queue_size: int = 100):
        self.queue = asyncio.Queue(maxsize=queue_size)
        
    async def process_log_async(self, log_data: dict):
        """非同期ログ処理"""
        
    async def worker_loop(self):
        """ワーカーループ"""
```

### 10.2 基本バッチ処理
**基本バッチログ出力**:
```python
class BasicBatchLogProcessor:
    """基本バッチログ処理"""
    
    def __init__(self, batch_size: int = 50, flush_interval: float = 10.0):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.batch_buffer = []
        self.last_flush = time.time()
        
    def add_to_batch(self, log_data: dict):
        """バッチへの追加"""
        
    def flush_batch(self):
        """バッチのフラッシュ"""
```

## 11. 環境別設定設計（基本機能のみ）

### 11.1 開発環境
**開発環境設定**:
```yaml
# config/logging/development.yaml
logging:
  level: DEBUG
  handlers:
    - type: console
      level: DEBUG
      format: text
      colorize: true
    - type: file
      level: INFO
      filename: logs/dev.log
      max_size: 10MB
      backup_count: 5
  filters:
    - type: level
      min_level: DEBUG
  performance:
    async_processing: false
    batch_size: 10
    flush_interval: 1.0
```

### 11.2 ローカル環境
**ローカル環境設定**:
```yaml
# config/logging/local.yaml
logging:
  level: INFO
  handlers:
    - type: file
      level: INFO
      filename: logs/app.log
      max_size: 50MB
      backup_count: 5
    - type: console
      level: WARNING
      format: text
      colorize: true
  filters:
    - type: level
      min_level: INFO
  performance:
    async_processing: true
    batch_size: 100
    flush_interval: 5.0
  security:
    sensitive_data_filtering: true
    basic_access_control: true
```

## 12. 実装ガイドライン（基本機能のみ）

### 12.1 ロガーの使用
**基本使用パターン**:
```python
# ロガーの初期化
logger = BasicLogger("persona_service", config)

# 基本ログ出力
logger.info("ペルソナ作成開始", persona_name="プロジェクトマネージャー")

# コンテキスト付きログ
logger.log_with_context(
    "INFO", 
    "ペルソナ作成完了",
    context={
        "persona_id": "persona_001",
        "execution_time": 245
    }
)

# パフォーマンスログ
logger.log_performance("create_persona", 0.245)

# 監査ログ
logger.log_audit("user_123", "create", "persona_001")
```

### 12.2 エラーハンドリング
**例外処理パターン（基本機能のみ）**:
```python
try:
    # ビジネスロジック
    persona = create_persona(persona_data)
    logger.info("ペルソナ作成成功", persona_id=persona.id)
    
except ValidationException as e:
    logger.warning("バリデーションエラー", 
                  field=e.field, value=e.value, message=e.message)
    raise
    
except DatabaseException as e:
    logger.error("データベースエラー", 
                operation="create_persona", error=str(e))
    raise
    
except Exception as e:
    logger.critical("予期しないエラー", 
                   operation="create_persona", error=str(e), 
                   traceback=traceback.format_exc())
    raise
```

### 12.3 パフォーマンス監視（基本機能のみ）
**パフォーマンス測定**:
```python
# 処理時間測定
start_time = time.time()
try:
    result = perform_operation()
    execution_time = time.time() - start_time
    logger.log_performance("perform_operation", execution_time)
    
except Exception as e:
    execution_time = time.time() - start_time
    logger.log_performance("perform_operation", execution_time, success=False)
    raise
```

## 13. テスト・品質保証（基本機能のみ）

### 13.1 ログテスト
**ログ出力テスト（基本機能のみ）**:
```python
class TestBasicLogging:
    """基本ログ機能テスト"""
    
    def test_log_levels(self):
        """ログレベルのテスト"""
        
    def test_log_formatters(self):
        """ログフォーマッターのテスト"""
        
    def test_log_handlers(self):
        """ログハンドラーのテスト"""
        
    def test_basic_performance_logging(self):
        """基本パフォーマンスログのテスト"""
```

### 13.2 エラーハンドリングテスト（基本機能のみ）
**エラー処理テスト**:
```python
class TestBasicErrorHandling:
    """基本エラー処理テスト"""
    
    def test_custom_exceptions(self):
        """カスタム例外のテスト"""
        
    def test_error_responses(self):
        """エラーレスポンスのテスト"""
        
    def test_error_logging(self):
        """エラーログのテスト"""
```

## 14. 運用・保守（基本機能のみ）

### 14.1 ログローテーション
**基本ログローテーション**:
```python
class BasicLogRotator:
    """基本ログローテーション"""
    
    def __init__(self, log_dir: str, max_size: int, backup_count: int):
        self.log_dir = log_dir
        self.max_size = max_size
        self.backup_count = backup_count
        
    def check_and_rotate(self):
        """ログローテーションのチェック・実行"""
        
    def cleanup_old_logs(self):
        """古いログの削除"""
```

### 14.2 基本ログ監視
**基本ヘルスチェック**:
```python
class BasicLogHealthChecker:
    """基本ログシステムヘルスチェック"""
    
    def check_log_writers(self) -> dict:
        """ログライターの状態チェック"""
        
    def check_log_storage(self) -> dict:
        """ログストレージの状態チェック"""
        
    def generate_basic_health_report(self) -> dict:
        """基本ヘルスレポート生成"""
```

---

## 📋 設計完了確認

このログ・エラー処理設計書は、ローカル・シングルユーザー級の前提条件に合わせて以下の要素を基本機能としてカバーしています：

✅ **ログシステム設計**: 基本アーキテクチャ・ログレベル・フォーマット  
✅ **ロガークラス設計**: 基本・拡張ロガークラス  
✅ **ログハンドラー設計**: ファイル・データベース・コンソール  
✅ **ログフォーマッター設計**: JSON・テキスト形式  
✅ **ログフィルター設計**: レベル・コンテキスト  
✅ **エラー処理設計**: 基本ハンドリング・カスタム例外・統一レスポンス  
✅ **ログ監視・分析**: 基本監視・パターン検出・基本分析  
✅ **ログセキュリティ**: 基本機密情報保護・基本アクセス制御  
✅ **パフォーマンス最適化**: 基本非同期処理・基本バッチ処理  
✅ **環境別設定**: 開発・ローカル環境の基本設定  
✅ **実装ガイドライン**: 基本使用パターン・エラーハンドリング・パフォーマンス監視  
✅ **テスト・品質保証**: 基本ログ・エラー処理のテスト  
✅ **運用・保守**: 基本ローテーション・基本ヘルスチェック・基本監視  

**設計レベル**: ローカル・シングルユーザー級（エンタープライズ級から調整完了）
**エンタープライズ級過剰設計**: 完全排除
**ローカル環境最適化**: 100%完了

次のUI/UX設計書のレベル調整に進みます。
