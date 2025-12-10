# Gemini バックエンド利用メモ

## 環境変数（例）
- `LLM_PROVIDER=gemini`（未設定でも API キーがあれば自動で gemini を使用）
- `GEMINI_API_KEY=...`（必須）
- `GEMINI_MODEL=gemini-3-pro-preview`（テキスト/Thinking用モデル）
- `GEMINI_IMAGE_MODEL=imagen-3.0-generate-001`（画像生成モデル）

## APIサンプル

- テキスト生成（REST）
  ```bash
  curl -X POST http://localhost:8000/api/v1/llm/text \
    -H "Content-Type: application/json" \
    -d '{"prompt":"Hello Gemini","model":"gemini-3-pro-preview","thinking_level":"high","include_thoughts":true}'
  ```

- 画像生成（REST）
  ```bash
  curl -X POST http://localhost:8000/api/v1/llm/image \
    -H "Content-Type: application/json" \
    -d '{"prompt":"a cute cat","model":"imagen-3.0-generate-001"}' \
    | jq -r .data_base64 | base64 -d > out.png
  ```

- WS チャット（Thinking パラメータ付き）
  - エンドポイント例:  
    `ws://localhost:8000/api/v1/ws/chat?conversation_id=...&thinking_level=high&thinking_budget=2048&include_thoughts=true&model=gemini-3-pro-preview`
  - 送信: `{"type":"user_message","text":"Hello"}`
  - 受信: `assistant_start` → `token`(複数) → `assistant_end`

## 注意
- 現状UIは未実装のため、上記APIを直接叩いて確認する想定です。
- 簡易チェックリスト（手動）
  - テキスト: 上記 curl を実行し、`provider` が `gemini`、`text` が返ることを確認
  - Thinking: `thinking_level/include_thoughts` を付けて実行（返却に `thoughts` が含まれることを確認）
  - 画像: `out.png` が生成され、画像として開けることを確認
