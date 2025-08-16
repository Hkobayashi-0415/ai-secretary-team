# Cursor + Cipher Aggregator Mode セットアップガイド

## 概要
CipherをMCP Aggregatorモードで動作させることで、Cursorから21個の拡張ツールを利用できるようになります。

## セットアップ手順

### 1. 環境変数の設定（.envファイル）

`cipher-source/.env`に以下を追加：

```env
# MCP Server Mode Configuration
MCP_SERVER_MODE=aggregator
AGGREGATOR_CONFLICT_RESOLUTION=prefix
AGGREGATOR_TIMEOUT=120000

# API Keys
GEMINI_API_KEY=your_api_key_here
```

### 2. Cipher側のコード修正（実装済み）

`cipher-source/src/core/env.ts`で以下の修正を実施：

```typescript
// 修正前：MCPモードでは.envを読み込まない
if (isMcpMode) {
  // Skip .env loading
} else {
  config();
}

// 修正後：常に.envを読み込む
config();  // Always load .env file
const isMcpMode = process.argv.includes('--mode') && ...
```

環境変数スキーマにMCP設定を追加：
```typescript
// MCP Server Configuration
MCP_SERVER_MODE: z.enum(['default', 'aggregator']).optional(),
AGGREGATOR_CONFLICT_RESOLUTION: z.enum(['prefix', 'error', 'rename']).optional(),
AGGREGATOR_TIMEOUT: z.number().optional(),
```

### 3. Cursor用のMCP設定（.mcp.json）

プロジェクトルートに`.mcp.json`を作成：

```json
{
  "mcpServers": {
    "cipher_cursor": {
      "type": "stdio",
      "command": "node",
      "args": [
        "./cipher-source/dist/src/app/index.cjs",
        "--mode",
        "mcp",
        "--agent",
        "./cipher-source/memAgent/cipher.yml"
      ],
      "env": {
        "MCP_SERVER_MODE": "aggregator",
        "AGGREGATOR_CONFLICT_RESOLUTION": "prefix",
        "AGGREGATOR_TIMEOUT": "120000",
        "CIPHER_SESSION_PERSIST_MEMORY": "true",
        "CIPHER_MEMORY_ENABLE_LEARNING": "true",
        "CIPHER_PROJECT_MEMORY": "true",
        "GEMINI_API_KEY": "${GEMINI_API_KEY}"
      }
    }
  }
}
```

### 4. ビルド

TypeScriptコードを変更した場合は必ずビルド：

```bash
cd cipher-source
npm run build
```

## 動作確認方法

### 方法1: 手動起動して確認

```bash
cd cipher-source
node dist/src/app/index.cjs --mode mcp --agent memAgent/cipher.yml
```

### 方法2: ログファイルで確認

ログファイル: `C:\Users\{username}\AppData\Local\Temp\cipher-mcp.log`

成功時のログ：
```
[MCP Handler] Initializing MCP server with agent capabilities (mode: aggregator)
[MCP Handler] Registering 21 tools: read_file, read_text_file, ...
[MCP Mode] Cipher is now running as aggregator MCP server
```

### 方法3: バッチファイルで起動

`start_cipher.bat`：
```batch
@echo off
set MCP_SERVER_MODE=aggregator
set AGGREGATOR_CONFLICT_RESOLUTION=prefix
set AGGREGATOR_TIMEOUT=120000

cd cipher-source
node dist\src\app\index.cjs --mode mcp --agent memAgent\cipher.yml
```

## モードの違い

### デフォルトモード
- **ツール数**: 1個（ask_cipherのみ）
- **用途**: シンプルな対話

### Aggregatorモード
- **ツール数**: 21個
- **利用可能なツール**:
  - ファイル操作: read_file, write_file, edit_file, create_directory など
  - メモリ操作: cipher_memory_search, cipher_store_reasoning_memory など
  - 推論ツール: cipher_extract_reasoning_steps, cipher_evaluate_reasoning など
  - メインツール: ask_cipher

## トラブルシューティング

### 問題1: デフォルトモードで起動してしまう

**原因**: 環境変数が読み込まれていない

**解決策**:
1. `.env`ファイルの確認
2. `cipher-source/src/core/env.ts`で`config()`が呼ばれているか確認
3. ビルドの実行（`npm run build`）

### 問題2: ツールが1個しか表示されない

**原因**: Aggregatorモードが有効になっていない

**解決策**:
ログで以下を確認：
```
grep "mode\|aggregator" cipher-mcp.log
```

### 問題3: Cursorで認識されない

**原因**: `.mcp.json`の配置場所が間違っている

**解決策**:
- プロジェクトルートに`.mcp.json`を配置
- Cursorを再起動

## 重要なポイント

1. **3つの設定ファイルの連携**:
   - `.env`: 基本的な環境変数
   - `.mcp.json`: Cursor用のMCP設定
   - `cipher.yml`: Cipherのエージェント設定

2. **優先順位**:
   - `.mcp.json`の`env`セクション > `.env`ファイル > デフォルト値

3. **ビルドの必要性**:
   - TypeScriptコードを変更した場合は必ずビルド
   - 設定ファイルの変更のみなら不要

## ClaudeCodeとの共存

同じCipherサーバーをClaudeCodeとCursorで共有可能：

- **ClaudeCode**: `claude_code_config.json`
- **Cursor**: `.mcp.json`

両方とも同じ環境変数とモード設定を使用。

## 実装の詳細

### なぜ.envが読み込まれなかったか

元のコード（`src/core/env.ts`）:
```typescript
if (isMcpMode) {
  // MCPモードでは.envを読み込まない
  // MCPホストが環境変数を提供すると想定
} else {
  config(); // 通常モードのみ.envを読み込む
}
```

この仮定は間違っており、MCPモードでも`.env`の読み込みが必要でした。

### 修正のポイント

1. **常に.envを読み込む**: MCPモードでも環境変数が必要
2. **環境変数スキーマの拡張**: MCP関連の変数を追加
3. **Proxyパターンでの動的読み込み**: 実行時の環境変数を参照

## まとめ

この設定により、Cursorから21個の強力なツールを使用できるようになります。
ファイル操作、メモリ管理、推論機能などが統合され、開発効率が大幅に向上します。

---

*最終更新: 2025-08-14*
*Cipher Version: 0.2.0*