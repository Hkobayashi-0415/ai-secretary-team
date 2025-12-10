# Handover: Phase 2 LLM/Chat UI (2025-12-02)

## Branch
- `feature/phase2-llm-ui` (based on origin/main @ 8da5cb5)

## Current status
- Frontend API base URL normalization fixed (`services/api.ts`, `ConversationsPage.tsx`, `AssistantsPage.tsx`) to avoid `/api/api/...` 404。
- Obsidian career importer skeleton added (`tools/career_profile_importer/` + `docs/02-implementation/guides/04-obsidian-career-importer.md`), CLI/config/Markdown builder in place.
- CI compose now pins `DOCKERIZED=1` / `TEST_DATABASE_URL` for backend tests。
- Tests: pytest (cov ~76.8%, gate 75%) and Playwright E2E 6/6 PASS on compose stack。
- Known limitations: chat uses mock LLM (echo); assistant selection UI is auto-pick-first (no manual chooser)。

## Open items (per TODO)
- Phase 2 Week5 (AI連携): P2-T05〜T08 未着手  
  - Gemini API service実装、AI応答REST/WS統合、AI向けテスト追加。
- Phase 2 Week6 (UI/E2E): P2-T09〜T12 未着手  
  - チャットUI強化（ストリーム表示UX、履歴ロード、エラー表示、Zustand整備）、チャットE2E拡充。
- Backlog: `message_role` ENUM掃除、索引/制約調整、Runbook GUI設定など。
- Obsidian importer: スケルトン完成。TODO上は done に更新済みだが、実運用レベル（実LLM呼び出し・テスト）は未着手。

## Suggested next steps
1) Implement Gemini client integration for chat (replace mock echo) and add REST/WS unit tests (P2-T05〜T08)。
2) Add assistant selection UI before starting conversations; polish chat UI/stream handling and extend Playwright coverage (P2-T09〜T12)。
3) Optionally extend Obsidian importer with real Gemini calls + tests。
