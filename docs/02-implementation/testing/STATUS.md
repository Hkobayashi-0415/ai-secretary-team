# Testing Status (2025-10-19)

- Backend coverage: ~82% (pytest-cov)
- Recently added tests:
  - Conversations API: paging, invalid anchor, CRUD 404s
  - Routing: exception propagation (500)
  - WebSocket chat: empty message error event, invalid conversation_id close 4404
- Notes:
  - When not running in Docker, tests fall back to `localhost` Postgres (`test_db`).

How to run
- Docker:
  - `DOCKERIZED=1 TEST_DATABASE_URL=postgresql+asyncpg://ai_secretary_user:ai_secretary_password@postgres_test:5432/ai_secretary_test docker-compose -f docker-compose.test.yml run --rm backend_test pytest -q`
  - Coverage: `docker-compose -f docker-compose.test.yml run --rm backend_test python -m coverage report -m`
- Local Postgres:
  - `TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/test_db pytest -q`
