# Phase2 フロント拡張メモ (P2-T09〜T12)

## 追加した機能
- ChatPage にモード切替を追加（テキスト / Thinking / 画像生成）
- /chat/new でアシスタント選択UIを追加（セレクト＋開始ボタン）
- 画像生成は `/api/v1/llm/image` を呼び、Base64を画像表示
- Thinkingモードは WS クエリに `thinking_level` / `include_thoughts` を付与
- CI安定化のためフロントビルドを glibc ベース（node:20-bullseye）に変更し、rollup ネイティブ依存を optionalDependencies に追加済み

## 追加が必要なUI/UX（今後）
- モデル選択UI（現状は入力/ENVベース。プルダウン化など）
- Thinking予算、エラーメッセージのユーザ向け表示
- 画像生成の履歴保存/再表示のデザイン
- Playwright E2Eの拡張（画像/Thinkingシナリオの検証）

## 手動確認のポイント
1. `/chat/new` でアシスタント選択→「チャットを開始」で会話IDに遷移すること
2. テキスト/ThinkingモードでWS応答が届くこと
3. 画像モードで送信すると画像が表示されること（Base64がimgタグで表示）
4. E2E (`frontend/tests/chat-flow.spec.ts` ほか) が新UIで通ること
   - `docker compose -f docker-compose.yml -f docker-compose.ci.yml run --rm e2e`
