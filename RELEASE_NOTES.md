# Release Notes

## v2025.10.20

Highlights
- Alembic as SSOT with normalization (013)
- Backend entrypoint unified to always run migrations before start
- CI strengthened: E2E (Playwright) + backend pytest coverage gate (≥ 75%)
- Tests use Alembic for DB initialization (no create_all/drop_all)
- Legacy docs moved under `archive/`, references updated

Migrations
- 013_normalize_phase2: canonical columns/constraints/indexes for conversations/messages; normalize assistant_skills; no native ENUM for messages.role

Operational Notes
- Observe `alembic current` → `013_normalize_phase2 (head)` at startup
- See `docs/01-foundation/operations/02-db-rollout.md` for production rollout
- Branch protection policy: `docs/01-foundation/operations/01-branch-protection.md`

