# デプロイメントガイド

## 1. 概要

### 1.1 目的
AI Secretary Platformのデプロイメントガイド。非エンジニアでも簡単にインストール・起動できる配布パッケージの作成、環境構築、運用準備を定義する。

### 1.2 デプロイメント方針
- **簡単インストール**: ワンクリックインストーラー
- **Docker非依存**: スタンドアロン実行可能ファイル
- **自動環境構築**: 必要な依存関係の自動インストール
- **クロスプラットフォーム**: Windows・macOS・Linux対応

### 1.3 対象読者
- 開発チーム
- 運用担当者
- エンドユーザー
- プロジェクトマネージャー

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

## 2. 配布パッケージ戦略

### 2.1 配布方式

#### 2.1.1 実行可能ファイル
- **PyInstaller**: Pythonアプリケーションの単一実行可能ファイル化
- **Electron**: フロントエンド・バックエンド統合パッケージ
- **スタンドアロン**: 外部依存なしでの動作

#### 2.1.2 インストーラー
- **NSIS**: Windows用インストーラー作成
- **Inno Setup**: Windows用インストーラー作成
- **DMG**: macOS用ディスクイメージ
- **AppImage**: Linux用ポータブルアプリケーション

### 2.2 パッケージ構成

#### 2.2.1 基本構成
```
AI_Secretary_Platform/
├── AI_Secretary.exe          # メイン実行ファイル
├── backend/                  # バックエンド実行ファイル
├── frontend/                 # フロントエンド実行ファイル
├── database/                 # データベースファイル
├── config/                   # 設定ファイル
├── logs/                     # ログファイル
└── docs/                     # ユーザーマニュアル
```

#### 2.2.2 依存関係
- **Python 3.11+**: ランタイム環境
- **PostgreSQL**: データベースエンジン
- **Redis**: キャッシュ専用（オプション）
- **Node.js**: フロントエンド実行環境

## 3. PyInstaller設定

### 3.1 基本設定

#### 3.1.1 specファイル
```python
# AI_Secretary.spec
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config', 'config'),
        ('templates', 'templates'),
        ('static', 'static')
    ],
    hiddenimports=[
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'psycopg2',
        'redis'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False
)
```

#### 3.1.2 ビルドコマンド
```bash
# 基本ビルド
pyinstaller AI_Secretary.spec

# ワンファイルビルド
pyinstaller --onefile AI_Secretary.spec

# デバッグ情報付き
pyinstaller --debug=all AI_Secretary.spec
```

### 3.2 最適化設定

#### 3.2.1 サイズ最適化
```python
# 不要なモジュール除外
excludes = [
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'tkinter'
]

# 必要なファイルのみ含める
datas = [
    ('config/environments', 'config/environments'),
    ('backend/app', 'backend/app'),
    ('frontend/build', 'frontend/build')
]
```

#### 3.2.2 パフォーマンス最適化
```python
# 並列処理有効化
parallel = True

# キャッシュ有効化
cache = True

# 最適化レベル
optimize = 2
```

## 4. インストーラー作成

### 4.1 NSIS設定

#### 4.1.1 基本スクリプト
```nsis
; AI_Secretary_Setup.nsi
!include "MUI2.nsh"

Name "AI Secretary Platform"
OutFile "AI_Secretary_Setup.exe"
InstallDir "$PROGRAMFILES\AI Secretary Platform"
RequestExecutionLevel admin

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "Japanese"

Section "Main Application" SecMain
    SetOutPath "$INSTDIR"
    File "AI_Secretary.exe"
    File "backend\*.*"
    File "frontend\*.*"
    File "config\*.*"
    
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    CreateDirectory "$SMPROGRAMS\AI Secretary Platform"
    CreateShortCut "$SMPROGRAMS\AI Secretary Platform\AI Secretary.lnk" "$INSTDIR\AI_Secretary.exe"
    CreateShortCut "$DESKTOP\AI Secretary.lnk" "$INSTDIR\AI_Secretary.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\AI_Secretary.exe"
    RMDir /r "$INSTDIR"
    Delete "$SMPROGRAMS\AI Secretary Platform\AI Secretary.lnk"
    RMDir "$SMPROGRAMS\AI Secretary Platform"
    Delete "$DESKTOP\AI Secretary.lnk"
    Delete "$INSTDIR\Uninstall.exe"
SectionEnd
```

#### 4.1.2 高度な設定
```nsis
; 環境変数設定
WriteRegStr HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "AI_SECRETARY_HOME" "$INSTDIR"

; サービス登録
nsExec::ExecToLog '"$INSTDIR\backend\install_service.bat"'

; ファイアウォール設定
nsExec::ExecToLog 'netsh advfirewall firewall add rule name="AI Secretary Platform" dir=in action=allow program="$INSTDIR\AI_Secretary.exe"'
```

### 4.2 Inno Setup設定

#### 4.2.1 基本スクリプト
```pascal
; AI_Secretary_Setup.iss
[Setup]
AppName=AI Secretary Platform
AppVersion=1.0.0
DefaultDirName={pf}\AI Secretary Platform
DefaultGroupName=AI Secretary Platform
OutputDir=output
OutputBaseFilename=AI_Secretary_Setup

[Files]
Source: "AI_Secretary.exe"; DestDir: "{app}"
Source: "backend\*"; DestDir: "{app}\backend"; Flags: recursesubdirs
Source: "frontend\*"; DestDir: "{app}\frontend"; Flags: recursesubdirs
Source: "config\*"; DestDir: "{app}\config"; Flags: recursesubdirs

[Icons]
Name: "{group}\AI Secretary"; Filename: "{app}\AI_Secretary.exe"
Name: "{commondesktop}\AI Secretary"; Filename: "{app}\AI_Secretary.exe"

[Run]
Filename: "{app}\AI_Secretary.exe"; Description: "Launch AI Secretary Platform"; Flags: postinstall nowait
```

## 5. 環境構築

### 5.1 自動環境構築

#### 5.1.1 環境チェックスクリプト
```python
# environment_checker.py
import sys
import subprocess
import platform
import os

class EnvironmentChecker:
    def __init__(self):
        self.system = platform.system()
        self.arch = platform.architecture()[0]
        
    def check_python(self):
        """Python環境のチェック"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 11):
            return False, f"Python 3.11+ required, current: {version.major}.{version.minor}"
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    
    def check_postgresql(self):
        """PostgreSQL環境のチェック"""
        try:
            result = subprocess.run(['psql', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, "PostgreSQL not found"
        except FileNotFoundError:
            return False, "PostgreSQL not installed"
    
    def check_redis(self):
        """Redis環境のチェック"""
        try:
            result = subprocess.run(['redis-server', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, "Redis not found"
        except FileNotFoundError:
            return False, "Redis not installed"
    
    def check_all(self):
        """全環境のチェック"""
        checks = {
            'Python': self.check_python(),
            'PostgreSQL': self.check_postgresql(),
            'Redis': self.check_redis()
        }
        
        all_passed = all(check[0] for check in checks.values())
        return all_passed, checks
```

#### 5.1.2 自動インストールスクリプト
```python
# auto_installer.py
import subprocess
import sys
import os

class AutoInstaller:
    def __init__(self):
        self.system = platform.system()
        
    def install_postgresql(self):
        """PostgreSQLの自動インストール"""
        if self.system == "Windows":
            # Chocolatey使用
            subprocess.run(['choco', 'install', 'postgresql', '-y'])
        elif self.system == "Darwin":  # macOS
            # Homebrew使用
            subprocess.run(['brew', 'install', 'postgresql'])
        elif self.system == "Linux":
            # apt使用（Ubuntu/Debian）
            subprocess.run(['sudo', 'apt-get', 'install', 'postgresql', '-y'])
    
    def install_redis(self):
        """Redisの自動インストール"""
        if self.system == "Windows":
            subprocess.run(['choco', 'install', 'redis-64', '-y'])
        elif self.system == "Darwin":
            subprocess.run(['brew', 'install', 'redis'])
        elif self.system == "Linux":
            subprocess.run(['sudo', 'apt-get', 'install', 'redis-server', '-y'])
    
    def setup_database(self):
        """データベースの初期設定"""
        # PostgreSQL初期化
        subprocess.run(['initdb', '-D', 'data'])
        
        # データベース作成
        subprocess.run(['createdb', 'ai_secretary'])
        
        # ユーザー作成
        subprocess.run(['createuser', '-s', 'ai_secretary'])
    
    def install_all(self):
        """全依存関係のインストール"""
        print("Installing PostgreSQL...")
        self.install_postgresql()
        
        print("Installing Redis...")
        self.install_redis()
        
        print("Setting up database...")
        self.setup_database()
        
        print("Installation completed!")
```

### 5.2 手動環境構築

#### 5.2.1 Windows環境
```batch
@echo off
REM Windows環境構築スクリプト

echo Installing Chocolatey...
powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"

echo Installing PostgreSQL...
choco install postgresql -y

echo Installing Redis...
choco install redis-64 -y

echo Installing Python dependencies...
pip install -r requirements.txt

echo Environment setup completed!
pause
```

#### 5.2.2 macOS環境
```bash
#!/bin/bash
# macOS環境構築スクリプト

echo "Installing Homebrew..."
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

echo "Installing PostgreSQL..."
brew install postgresql

echo "Installing Redis..."
brew install redis

echo "Installing Python dependencies..."
pip3 install -r requirements.txt

echo "Starting services..."
brew services start postgresql
brew services start redis

echo "Environment setup completed!"
```

#### 5.2.3 Linux環境
```bash
#!/bin/bash
# Linux環境構築スクリプト

echo "Updating package list..."
sudo apt-get update

echo "Installing PostgreSQL..."
sudo apt-get install postgresql postgresql-contrib -y

echo "Installing Redis..."
sudo apt-get install redis-server -y

echo "Installing Python dependencies..."
pip3 install -r requirements.txt

echo "Starting services..."
sudo systemctl start postgresql
sudo systemctl start redis

echo "Environment setup completed!"
```

## 6. デプロイメント戦略

### 6.1 段階的デプロイ

#### 6.1.1 デプロイフェーズ
```
Phase 1: 開発環境
├── ローカル開発
├── 単体テスト
└── 統合テスト

Phase 2: テスト環境
├── 自動テスト実行
├── パフォーマンステスト
└── セキュリティテスト

Phase 3: ステージング環境
├── E2Eテスト
├── ユーザー受け入れテスト
└── 本番前最終確認

Phase 4: 本番環境
├── 段階的リリース
├── 監視・ログ
└── ロールバック準備
```

#### 6.1.2 ロールバック戦略
```python
# rollback_manager.py
class RollbackManager:
    def __init__(self):
        self.backup_dir = "backups"
        self.current_version = None
        
    def create_backup(self):
        """現在の環境のバックアップ作成"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        
        # データベースバックアップ
        subprocess.run(['pg_dump', 'ai_secretary', '-f', f"{self.backup_dir}/{backup_name}.sql"])
        
        # 設定ファイルバックアップ
        shutil.copytree('config', f"{self.backup_dir}/{backup_name}_config")
        
        return backup_name
    
    def rollback(self, backup_name):
        """指定されたバックアップへの復旧"""
        # データベース復旧
        subprocess.run(['psql', 'ai_secretary', '-f', f"{self.backup_dir}/{backup_name}.sql"])
        
        # 設定ファイル復旧
        shutil.rmtree('config')
        shutil.copytree(f"{self.backup_dir}/{backup_name}_config", 'config')
        
        print(f"Rollback to {backup_name} completed")
```

### 6.2 配布・インストール

#### 6.2.1 配布方法
- **公式Webサイト**: 直接ダウンロード
- **GitHub Releases**: バージョン管理・リリースノート
- **Microsoft Store**: Windows用公式ストア
- **Mac App Store**: macOS用公式ストア

#### 6.2.2 インストール手順
```
1. インストーラーダウンロード
2. インストーラー実行
3. インストール先選択
4. 依存関係自動インストール
5. データベース初期化
6. サービス起動
7. 初回設定ウィザード
8. インストール完了
```

## 7. 運用準備

### 7.1 監視・ログ

#### 7.1.1 ヘルスチェック
```python
# health_checker.py
class HealthChecker:
    def __init__(self):
        self.checks = [
            self.check_database,
            self.check_redis,
            self.check_api,
            self.check_frontend
        ]
    
    def check_database(self):
        """データベース接続チェック"""
        try:
            # データベース接続テスト
            result = db.execute("SELECT 1")
            return True, "Database connection OK"
        except Exception as e:
            return False, f"Database connection failed: {str(e)}"
    
    def check_redis(self):
        """Redis接続チェック"""
        try:
            redis.ping()
            return True, "Redis connection OK"
        except Exception as e:
            return False, f"Redis connection failed: {str(e)}"
    
    def check_api(self):
        """API応答チェック"""
        try:
            response = requests.get("http://localhost:8000/health")
            if response.status_code == 200:
                return True, "API health OK"
            else:
                return False, f"API health check failed: {response.status_code}"
        except Exception as e:
            return False, f"API health check failed: {str(e)}"
    
    def run_all_checks(self):
        """全ヘルスチェック実行"""
        results = {}
        for check in self.checks:
            name = check.__name__.replace('check_', '').title()
            success, message = check()
            results[name] = {'success': success, 'message': message}
        
        return results
```

#### 7.1.2 ログ監視
```python
# log_monitor.py
class LogMonitor:
    def __init__(self):
        self.log_dir = "logs"
        self.alert_thresholds = {
            'error': 10,
            'warning': 50,
            'critical': 5
        }
    
    def monitor_logs(self):
        """ログファイルの監視"""
        for log_file in os.listdir(self.log_dir):
            if log_file.endswith('.log'):
                self.analyze_log(os.path.join(self.log_dir, log_file))
    
    def analyze_log(self, log_file):
        """ログファイルの分析"""
        error_count = 0
        warning_count = 0
        critical_count = 0
        
        with open(log_file, 'r') as f:
            for line in f:
                if 'ERROR' in line:
                    error_count += 1
                elif 'WARNING' in line:
                    warning_count += 1
                elif 'CRITICAL' in line:
                    critical_count += 1
        
        # アラート判定
        if error_count > self.alert_thresholds['error']:
            self.send_alert('ERROR', f"High error count in {log_file}: {error_count}")
        
        if critical_count > self.alert_thresholds['critical']:
            self.send_alert('CRITICAL', f"Critical errors in {log_file}: {critical_count}")
    
    def send_alert(self, level, message):
        """アラート送信"""
        print(f"[{level}] {message}")
        # メール・Slack等への通知実装
```

### 7.2 バックアップ・復旧

#### 7.2.1 自動バックアップ
```python
# backup_manager.py
class BackupManager:
    def __init__(self):
        self.backup_dir = "backups"
        self.retention_days = 30
        
    def create_backup(self):
        """自動バックアップ作成"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"auto_backup_{timestamp}"
        
        # データベースバックアップ
        self.backup_database(backup_name)
        
        # 設定ファイルバックアップ
        self.backup_config(backup_name)
        
        # ログファイルバックアップ
        self.backup_logs(backup_name)
        
        # 古いバックアップの削除
        self.cleanup_old_backups()
        
        return backup_name
    
    def backup_database(self, backup_name):
        """データベースバックアップ"""
        backup_file = f"{self.backup_dir}/{backup_name}.sql"
        subprocess.run([
            'pg_dump', 
            'ai_secretary', 
            '-f', backup_file,
            '--format=custom',
            '--compress=9'
        ])
    
    def backup_config(self, backup_name):
        """設定ファイルバックアップ"""
        config_backup_dir = f"{self.backup_dir}/{backup_name}_config"
        shutil.copytree('config', config_backup_dir)
    
    def backup_logs(self, backup_name):
        """ログファイルバックアップ"""
        logs_backup_dir = f"{self.backup_dir}/{backup_name}_logs"
        shutil.copytree('logs', logs_backup_dir)
    
    def cleanup_old_backups(self):
        """古いバックアップの削除"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        for backup in os.listdir(self.backup_dir):
            backup_path = os.path.join(self.backup_dir, backup)
            if os.path.getctime(backup_path) < cutoff_date.timestamp():
                shutil.rmtree(backup_path)
                print(f"Removed old backup: {backup}")
```

## 8. 成功指標

### 8.1 デプロイメント指標

#### 8.1.1 技術指標
- **インストール成功率**: 95%以上
- **起動成功率**: 98%以上
- **環境構築時間**: 10分以内
- **パッケージサイズ**: 500MB以下

#### 8.1.2 ユーザビリティ指標
- **インストール手順**: 5ステップ以内
- **初回起動時間**: 30秒以内
- **設定完了時間**: 5分以内
- **エラー発生率**: 5%以下

### 8.2 運用指標

#### 8.2.1 安定性指標
- **稼働率**: 99.5%以上
- **平均故障間隔**: 30日以上
- **平均復旧時間**: 10分以内
- **ロールバック成功率**: 100%

#### 8.2.2 パフォーマンス指標
- **起動時間**: 30秒以内
- **応答時間**: 200ms以内
- **リソース使用量**: 1GB以下
- **同時接続数**: 100ユーザー以上

## 9. 今後の拡張予定

### 9.1 短期（3ヶ月以内）
- **自動更新機能**: バージョン管理・自動アップデート
- **クラウド配布**: CDN・クラウドストレージ活用
- **インストーラー改善**: UI/UX向上・エラーハンドリング強化

### 9.2 中期（6ヶ月以内）
- **コンテナ化**: Docker・Kubernetes対応
- **CI/CD統合**: 自動ビルド・デプロイ
- **監視強化**: APM・メトリクス収集

### 9.3 長期（1年以内）
- **クラウドネイティブ**: クラウド環境最適化
- **マイクロサービス**: サービス分割・独立デプロイ
- **DevOps統合**: 開発・運用の自動化

---

**作成日**: 2025-08-13  
**作成者**: AI Assistant  
**バージョン**: 1.0  
**次回更新予定**: 2025-08-20 