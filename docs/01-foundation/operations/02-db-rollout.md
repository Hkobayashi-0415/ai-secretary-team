# Database Rollout (Production)

Checklist
- Take a full logical backup prior to rollout (pg_dump -Fc)
- Confirm required extensions exist: pgcrypto, vector, pg_trgm (init enables IF NOT EXISTS)
- Ensure app image includes latest Alembic migrations
- Scale down traffic or use maintenance window as needed

Steps
1) Backup: `pg_dump -h <host> -U <user> -d <db> -Fc -f backup_<date>.dump`
2) Deploy new backend image and restart service
3) Observe startup logs for `alembic current` → `013_normalize_phase2 (head)`
4) Smoke test API (health, assistants CRUD, conversations/messages)
5) Monitor errors and DB locks for 10–15 minutes

Rollback (if needed)
- Restore from backup: `pg_restore -h <host> -U <user> -d <db_new> -c -Fc backup_<date>.dump`
- Point app to restored DB

Notes
- We no longer use native ENUM for `messages.role`; DB enforces CHECK and app validates roles.
- Old unused ENUM types can be dropped later after verifying no dependencies.

