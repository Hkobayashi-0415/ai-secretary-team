# 🔧 Cipher MCP 連携修正ドキュメント

**作成日**: 2025年8月17日  
**作成者**: 中野五月（Claude Code）

## 📋 修正内容

### 1. ディレクトリ構造の変更
- **旧**: `cipher-source/`
- **新**: `tools/cipher-mcp/`

### 2. 設定ファイルの修正

#### Claude Code設定 (`claude_code_config.json`)
```json
{
  "mcpServers": {
    "cipher": {
      "type": "stdio",
      "command": "node",
      "args": [
        "./tools/cipher-mcp/dist/src/app/index.cjs",
        "--mode", "mcp",
        "--agent", "./tools/cipher-mcp/memAgent/cipher-simple.yml"
      ],
      "env": {
        "GEMINI_API_KEY": "${GEMINI_API_KEY}"
      }
    }
  }
}
```

#### Cursor設定 (`.mcp.json`)
```json
{
  "mcpServers": {
    "cipher": {
      "type": "stdio",
      "command": "cmd",
      "args": [
        "/c",
        "cd tools\\cipher-mcp && node dist\\src\\app\\index.cjs --mode mcp --agent memAgent\\cipher-simple.yml"
      ]
    }
  }
}
```

### 3. 簡略化設定ファイル (`cipher-simple.yml`)
外部MCPサーバー依存を排除し、Cipherのコア機能のみに集中：
- メモリ管理機能
- ベクトルストレージ（in-memory）
- Gemini API統合

### 4. バッチファイルの更新
- `start_cipher.bat` - パス修正
- `start_cipher_cursor.bat` - パス修正  
- `test_cipher.bat` - パス修正
- `start_qdrant.bat` - 新規作成（ベクトルDB用）

## 🚀 使用方法

### Claude Code
プロジェクトルートで以下を実行：
```bash
# Cipherが自動的に起動します
# claude_code_config.jsonの設定に従って動作
```

### Cursor
1. `.mcp.json`がプロジェクトルートに配置されていることを確認
2. Cursorを再起動
3. Cipherが自動的に接続

### 手動テスト
```bash
cd tools/cipher-mcp
node dist/src/app/index.cjs --mode mcp --agent memAgent/cipher-simple.yml
```

## ⚠️ 既知の問題

1. **Qdrant接続エラー**
   - 現在はin-memoryフォールバックで動作
   - 永続化が必要な場合は`start_qdrant.bat`を実行

2. **Filesystem MCPサーバー**
   - 現在無効化中
   - 必要に応じて別途インストール

## ✅ 動作確認済み機能

- ✅ メモリ記憶・検索
- ✅ セッション管理
- ✅ Gemini API統合
- ✅ 基本的なMCP通信

## 📝 今後の改善案

1. Qdrantサーバーの自動起動
2. Filesystem MCPサーバーの統合
3. データベースパスの最適化
4. エラーハンドリングの強化

---

*このドキュメントは、Cipher MCPとの連携修正作業の記録です。*