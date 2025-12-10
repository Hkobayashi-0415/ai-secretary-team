# Work Log: Obsidian importer skeleton & frontend API base normalization (2025-12-02)

## What I changed
- Added Obsidian career importer skeleton under `tools/career_profile_importer/` (config loader, Gemini client stub, LLM parser, Markdown builder, CLI, sample config).
- Fixed frontend API base URL normalization to prevent `/api/api/...` and `/api/v1/api/v1/...` issues (`frontend/src/services/api.ts`, `ConversationsPage.tsx`, `AssistantsPage.tsx`).
- CI compose updated to pin `DOCKERIZED=1` and `TEST_DATABASE_URL` for backend tests.
- Docs added: `docs/02-implementation/guides/04-obsidian-career-importer.md`; implementation plan/TODO refreshed.

## Errors / symptoms and fixes
- **Symptoms**
  - `ERR_NAME_NOT_RESOLVED` (browser tried `http://backend:8000/...` which is not resolvable from host).
  - `404` on `/api/api/v1/...` and `/api/v1/api/v1/...` (double prefix in frontend bundle).
  - UI missing assistant/model picker and chat responses echoing user input.
- **Repro (before fix)**
  - Access `http://localhost:3000/chat/new` or `/conversations` → Network shows `backend:8000` or `/api/api/v1/...` requests.
- **Fixes**
  - `frontend/src/services/api.ts`: Normalize `VITE_API_URL`:
    - strip trailing `/`
    - collapse `/api/v1` → `/api`
    - if endswith `/api`, do not append another `/api`; final base becomes `/api/v1`.
  - `frontend/src/pages/ConversationsPage.tsx`: Normalize base same way; fetch to `${apiBase}/conversations/` (avoid adding `/api/v1` twice).
  - `frontend/src/pages/AssistantsPage.tsx`: Normalize `/api/v1` → `/api`, ensure final base is `/api/v1`.
  - Rebuild frontend with `VITE_API_URL=/api` and hard reload to purge old bundle.
  - `docker-compose.ci.yml`: backend env set with `DOCKERIZED=1`, `TEST_DATABASE_URL=postgresql+asyncpg://ai_secretary_user:ai_secretary_password@postgres:5432/ai_secretary` so pytest always hits compose DB.
- **Remaining limitations**
  - Chat LLM is a mock/echo; real Gemini/OpenAI/Claude responses not implemented yet.
  - Assistant selection UI is auto-pick first assistant; no manual chooser yet.

## Steps/commands used
- Frontend rebuild and run:
  - `docker compose -f docker-compose.yml -f docker-compose.ci.yml down -v --remove-orphans` (when needed)
  - `docker compose -f docker-compose.yml -f docker-compose.ci.yml build --no-cache frontend`
  - `docker compose -f docker-compose.yml -f docker-compose.ci.yml up -d backend frontend`
  - Hard reload browser (Ctrl+Shift+R) to flush cached JS.
- Backend tests (coverage gate 75%):
  - `docker compose -f docker-compose.yml -f docker-compose.ci.yml run --rm backend sh -lc "cd /app && pytest --cov=app --cov-report=term-missing --cov-fail-under=75"` → PASS, cov ~76.8%.
- E2E (Playwright):
  - `docker compose -f docker-compose.yml -f docker-compose.ci.yml run --rm e2e` → 6/6 PASS.
- Health check:
  - `curl http://localhost:8000/health` → 200.

## Known limitations / TODO
- Chat uses mock LLM (echo) → need real LLM integration for responses.
- Assistant selection UI absent → add dropdown/selector before starting conversation.
- Obsidian importer: currently skeleton with dry-run; hook real Gemini call and add tests.

## Key commands/tests
- Backend tests (coverage gate 75%): `docker compose -f docker-compose.yml -f docker-compose.ci.yml run --rm backend sh -lc "cd /app && pytest --cov=app --cov-report=term-missing --cov-fail-under=75"` → PASS, cov ~76.8%.
- E2E (Playwright): `docker compose -f docker-compose.yml -f docker-compose.ci.yml run --rm e2e` → 6/6 PASS.
- Health check: `curl http://localhost:8000/health` → 200.

## Notes / limitations
- Chat still uses mock LLM (echo); real Gemini/OpenAI/Claude responses not implemented yet.
- Assistant selection UI is auto-pick first assistant (no manual chooser yet).

## Follow-ups (potential)
- Implement real LLM client integration for chat responses.
- Add assistant selection UI before starting a conversation.
- Extend importer to actually call Gemini (non-dry-run) and add tests.
