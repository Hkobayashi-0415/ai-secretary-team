# Migration Normalization (013)

Goal: Enterprise-grade, canonical DB schema managed solely by Alembic.

- Canonicalize `conversations` and `messages` columns to match ORM models.
- Replace native ENUM for `messages.role` with `VARCHAR` + CHECK constraint.
- Normalize `assistant_skills` to `(assistant_id, skill_id)` and migrate data.
- Add GIN/BTREE indexes for metadata and relationships.

Policy
- Alembic is the single source of truth. Init SQL only enables extensions.
- Production does not adopt existing schemas via `stamp head`.
- CI/E2E uses ephemeral DB; entrypoint performs `upgrade head` after ensuring Alembic table exists.

Observability
- On boot, check `alembic current` in logs; expect `head`.

