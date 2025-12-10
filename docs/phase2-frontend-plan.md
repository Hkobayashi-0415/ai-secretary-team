# Phase2 フロント拡張メモ (P2-T09〜T12)

## 追加した機能
- ChatPage にモード切替を追加（テキスト / Thinking / 画像生成）
- /chat/new でアシスタント選択UIを追加（セレクト＋開始ボタン）
- 画像生成は `/api/v1/llm/image` を呼び、Base64を画像表示
- Thinkingモードは WS クエリに `thinking_level` / `include_thoughts` を付与

## 追加が必要なUI/UX（今後）
- モデル選択UI（現状は環境変数ベース）
- Thinking予算、エラーメッセージのユーザ向け表示
- 画像生成の履歴保存/再表示のデザイン
- Playwright E2Eの拡張（画像/Thinkingシナリオの検証）

## 手動確認のポイント
1. `/chat/new` でアシスタント選択→「チャットを開始」で会話IDに遷移すること
2. テキスト/ThinkingモードでWS応答が届くこと
3. 画像モードで送信すると画像が表示されること（Base64がimgタグで表示）
4. 既存E2E (`frontend/tests/chat-flow.spec.ts`) が新UIで通ること
