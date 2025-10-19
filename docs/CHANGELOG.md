# Changelog

Date: 2025-10-19

Summary
- Implemented structured logging foundation (JSON) and global exception handlers in backend.
- Expanded conversations API with paging and CRUD; aligned tests and behavior.
- WebSocket chat: invalid `conversation_id` closes with code 4404; empty message emits `{type:"error"}`.
- Added routing service unit tests and API edge-case tests; resolved duplicate test naming.
- CI test suite passing on main; backend coverage ~82% (pytest-cov).

Details
- Logging
  - Added `app.core.logging` with `LoggerBase` and `BasicLogger`.
  - Replaced `print()` in routing core with structured logs.
  - FastAPI global exception handlers for `HTTPException` and unhandled `Exception` with JSON logs.
- Conversations API
  - `GET /api/v1/conversations/{id}/messages/page`: supports `before_id` anchor + `limit`; when `before_id` is invalid or belongs to a different conversation, returns `200` with `messages: []` and `has_more: false`.
  - `PATCH /api/v1/conversations/{id}` and `DELETE /api/v1/conversations/{id}`: return `404` with `{"detail":"Conversation not found"}` when missing.
- WebSocket
  - `GET /api/v1/ws/chat?conversation_id=...`: server closes with `4404` if conversation does not exist; empty `text` triggers `{type:"error", message:"empty text"}`.
- Tests
  - Added API tests for conversations edge cases, routing exceptions, WebSocket edge cases.
  - Added routing service unit tests (TaskAnalyzer, SkillMatcher, LLMRouter, AgentSelector, Orchestrator).
  - Adjusted WS tests to use `localhost` DB fallback when not running in Docker.

How To Run (Backend)
- Docker (recommended):
  - `DOCKERIZED=1 TEST_DATABASE_URL=postgresql+asyncpg://ai_secretary_user:ai_secretary_password@postgres_test:5432/ai_secretary_test docker-compose -f docker-compose.test.yml run --rm backend_test pytest -q`
  - Coverage: `docker-compose -f docker-compose.test.yml run --rm backend_test python -m coverage report -m`
- Local Postgres:
  - `TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/test_db pytest -q`

