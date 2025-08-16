# Cipher MCP セットアップガイド

## 1. 事前準備

### 必要なもの
- Gemini API Key
- Qdrant（ローカルまたはクラウド）

## 2. 環境設定

### Gemini API Keyの設定
1. `.env`ファイルを開く
2. `GEMINI_API_KEY=your-gemini-api-key-here`を実際のAPIキーに置き換える

### Qdrantのセットアップ（ローカル版）
```bash
# Qdrantをダウンロード（Windows用）
curl -L https://github.com/qdrant/qdrant/releases/download/v1.7.4/qdrant-x86_64-pc-windows-msvc.zip -o qdrant.zip
# 解凍して実行
```

## 3. Claude Codeとの連携

### 方法1: グローバル設定（推奨）
1. Claude Codeの設定ファイルを開く
   - Windows: `%APPDATA%\ClaudeCode\claude_config.json`
   
2. 以下の内容を追加：
```json
{
  "mcpServers": {
    "cipher": {
      "type": "stdio",
      "command": "node",
      "args": [
        "C:\\Users\\sugar\\OneDrive\\デスクトップ\\ai-secretary-team-main\\cipher-source\\dist\\src\\app\\index.cjs",
        "--mode", "mcp",
        "--agent", "C:\\Users\\sugar\\OneDrive\\デスクトップ\\ai-secretary-team-main\\cipher-source\\memAgent\\cipher.yml"
      ],
      "env": {
        "GEMINI_API_KEY": "your-actual-gemini-api-key"
      }
    }
  }
}
```

### 方法2: プロジェクト固有設定
1. プロジェクトルートに`.claudecode/config.json`を作成
2. 上記と同じ内容を記入

## 4. テスト方法

### Cipherの動作確認
```bash
# CLIモードでテスト
npx cipher "テストメッセージ"

# APIサーバーモードでテスト
npx cipher --mode api

# MCPサーバーモードでテスト
npx cipher --mode mcp
```

### Claude Codeでの確認
1. Claude Codeを再起動
2. `/mcp`コマンドを実行してCipherが表示されることを確認

## 5. 使用方法

### メモリーへの保存
```
cipher_memory_store("プロジェクトの重要な情報をここに記載")
```

### メモリーの検索
```
cipher_memory_search("検索キーワード")
```

### Cipherに質問
```
ask_cipher("質問内容")
```

## トラブルシューティング

### Cipherが認識されない場合
1. Claude Codeを完全に終了して再起動
2. 設定ファイルのパスが正しいか確認
3. `npx cipher --mode mcp`が単体で動作するか確認

### エラーが発生する場合
1. `.env`ファイルのAPIキーが正しいか確認
2. Qdrantが起動しているか確認（ローカルの場合）
3. ログを確認：`%TEMP%\claude-code-logs`