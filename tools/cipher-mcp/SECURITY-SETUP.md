# 🔐 Cipher MCP Server - セキュリティセットアップガイド

## 📋 **必須環境変数設定**

### **Windows環境変数設定**
```bash
# システム環境変数として設定（推奨）
setx GEMINI_API_KEY "your-gemini-api-key" /M
setx ANTHROPIC_API_KEY "your-claude-api-key" /M  
setx VOYAGE_API_KEY "your-voyage-api-key" /M

# または、ユーザー環境変数として設定
setx GEMINI_API_KEY "your-gemini-api-key"
setx ANTHROPIC_API_KEY "your-claude-api-key"
setx VOYAGE_API_KEY "your-voyage-api-key"
```

### **環境変数確認**
```bash
echo %GEMINI_API_KEY%
echo %ANTHROPIC_API_KEY%
echo %VOYAGE_API_KEY%
```

## ⚠️ **セキュリティ注意事項**

### **絶対に避けるべき行為**
- ❌ `.env` ファイルに平文でAPIキーを記載
- ❌ GitにAPIキーをコミット
- ❌ 公開リポジトリでのAPIキー露出
- ❌ スクリーンショットでのAPIキー表示

### **安全な管理方法**
- ✅ システム環境変数での管理
- ✅ `.env.local` ファイル（Git除外設定）
- ✅ PowerShell Profile での設定
- ✅ 定期的なAPIキーローテーション

## 🚨 **緊急時の対処**

### **APIキー露出時**
1. **即座にAPIキー無効化**（各プロバイダーの管理画面）
2. **新しいAPIキー発行**
3. **環境変数の更新**
4. **cipher サーバー再起動**

### **設定復旧手順**
```bash
# 1. 環境変数設定
setx ANTHROPIC_API_KEY "新しいAPIキー"

# 2. cipher サーバー再起動
cd cipher-source
npm start

# 3. 動作確認
# Claude Code から ask_cipher でテスト
```

## 🎯 **推奨設定構成**

### **本番運用**
- システム環境変数
- 制限付きAPIキー（必要最小限の権限）
- ログ監視
- 定期的なセキュリティ確認

### **開発環境**
- ユーザー環境変数 または .env.local
- テスト用制限付きキー
- デバッグログ有効

---

**🔒 このガイドに従って、APIキーを安全に管理してください。**