# Work Log: Frontend CI rollup fix & Gemini UI stabilisation (2025-12-10)

## What I changed
- フロントのビルドベースを `node:20-bullseye` (glibc) に変更し、Alpine/musl での rollup ネイティブバイナリ欠如問題を解消 (`frontend/Dockerfile`)。
- rollup ネイティブ依存を optionalDependencies に追加（glibc/musl 両方）し、lock を再生成 (`frontend/package.json`, `package-lock.json`)。
- ChatPage で `createAssistant` を正しく import する修正を含め、最新の Playwright テストが安定して通る構成に更新。

## Errors / symptoms and fixes
- **症状**: CI ビルドで `Cannot find module @rollup/rollup-linux-x64-gnu` / `...-musl` が発生しフロントの `npm run build` が失敗。
- **原因**: musl ベースの optional dep 取りこぼし、ならびに glibc 版がインストールされないまま rollup が実行されていた。
- **修正**:
  - builder イメージを glibc ベースに変更 (`node:20-bullseye`)。
  - optionalDependencies に `@rollup/rollup-linux-x64-gnu` / `...-musl` を追加し、lock を同期。
  - Dockerfile で glibc 用 rollup バイナリを明示インストールするワークアラウンドを追加。

## Steps/commands used
- Lock/依存同期: `cd frontend && npm install --ignore-scripts && cd ..`
- CI用ビルド: `docker compose -f docker-compose.yml -f docker-compose.ci.yml build --no-cache frontend`
- E2E: `docker compose -f docker-compose.yml -f docker-compose.ci.yml run --rm e2e` （6/6 PASS）

## Remaining limitations / follow-ups
- モデル選択UIはテキスト入力のまま（プルダウン化は今後）。
- 画像生成・Thinkingの詳細UX（エラー表示や予算指定 UI）は未実装。
