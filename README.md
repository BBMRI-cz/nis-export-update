# data-catalogue-upload

Scheduled sync job that reads biobank export and related APIs (sequencing, WSI, radiology) and upserts records into the data catalogue.

## Database

Copy [`.env.example`](.env.example) to `.env` and set `POSTGRES_PORT` if the default port is in use. Start PostgreSQL:

```bash
docker compose -f compose.prod.yml up -d
```

Apply Alembic migrations (place `.env` in the **project root**; `src/migrations/env.py` loads it before connecting):

```bash
cd src && uv run alembic -c alembic.ini upgrade head
```

The ORM defines two application tables, both created by the initial migration: `sync_run` and `sync_state` (plus `alembic_version` for migration history).
