# Testing Database Initialization

- Test DB schema is created via Alembic, not `create_all`.
- Fixture truncates all user tables per test to keep isolation while preserving schema.
- Extensions required for tests are enabled if available (`vector`, `pgcrypto`).

Rationale
- Aligns tests with production schema (SSOT = Alembic).
- Avoids divergences in CHECK constraints and indexes.

