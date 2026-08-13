# Local runtime and deployment topology

**Last verified:** 2026-08-13

## Supported Compose topology

| Service           | Image/runtime                |                               Port | Role                                                                        |
| ----------------- | ---------------------------- | ---------------------------------: | --------------------------------------------------------------------------- |
| `postgres`        | pgvector 0.8 / PostgreSQL 17 |                               5432 | Durable relational/vector store.                                            |
| `redis`           | Redis 7.4 Alpine             |                               6379 | Rate limiting, readiness, and runtime coordination.                         |
| `migrate`         | uv + Python 3.12             |                               none | Ensure/bootstrap database, conditionally stamp legacy DB, run Alembic head. |
| `backend`         | uv + Uvicorn                 | 8000; OAuth relay 1455 on loopback | FastAPI HTTP/SSE/WS service.                                                |
| `frontend`        | Node 22 + Next dev           |                               4173 | Dashboard and public embed UI.                                              |
| `pgadmin`         | optional tools profile       |                               5050 | Database administration.                                                    |
| `redis-commander` | optional tools profile       |                               8081 | Redis inspection.                                                           |

Startup dependencies are health-gated: migration waits for PostgreSQL; backend waits for migration completion and Redis; frontend waits for backend readiness.

## Boot sequence

```mermaid
flowchart LR
  PG[PostgreSQL healthy] --> M[ensure + bootstrap + stamp-if-needed + alembic upgrade]
  M --> B[FastAPI starts]
  R[Redis healthy] --> B
  B --> H[/health/ready succeeds]
  H --> F[Next.js starts]
```

## Environment boundary

Backend `.env` supplies application/provider configuration, while Compose overrides database, Redis, OAuth relay host, and uv environment paths. Frontend `.env` supplies browser-facing values, while Compose sets internal backend URL and `NEXT_PUBLIC_API_URL`. Any `NEXT_PUBLIC_*` value is browser-visible and must never contain secrets.

Important backend categories include JWT secret/lifetimes, CORS origins, database/Redis, OpenAI/Deepgram/ElevenLabs, Telnyx/Twilio, ChatGPT OAuth, provider timeouts/retries, Sentry, and OpenTelemetry.

## Health model

- `/health/live` and `/health` indicate process liveness.
- `/health/ready` evaluates dependencies needed to serve.
- `/health/db` and `/health/redis` isolate dependency diagnosis.
- `/health/cors` exposes safe CORS diagnostics.

Orchestrators should use liveness for restart decisions and readiness for traffic admission. Do not restart healthy processes solely because a downstream dependency is briefly unavailable.

## Database lifecycle

The one-shot migrate service is the normal local deployment gate. It runs repository scripts before Alembic to support fresh and legacy databases. Operators should back up production before migration, inspect heads/merge revisions, and avoid concurrently running multiple uncoordinated migrators.

## Developer checks

Backend quality commands are Ruff check/format and strict mypy; frontend uses its `check`, lint-fix, and formatting scripts. Runtime verification should include backend warning-free startup and frontend compilation. Tests reside under `backend/tests/` and frontend `*.test.*` files.

## Operational cautions

- Compose is configured for development (`--reload`, mounted source, Next dev server), not hardened production hosting.
- Default local database/admin credentials are intentionally weak and must not be reused publicly.
- Backend health startup grace is 60 seconds and frontend 90 seconds; slow dependency installation can exceed these on cold hosts.
- Provider webhooks need a reachable `PUBLIC_URL`; localhost requires a tunnel or equivalent callback endpoint.
- The OAuth relay binds host port 1455 only to loopback in Compose.
- Persistent named volumes retain database, Redis, virtualenv, package, and build state across container recreation.

## Related documentation

- `library/knowledge/private/operations/high-availability.md`
- `library/knowledge/private/architecture/system-architecture.md`

## Governing paths

- `docker-compose.yml`
- `backend/app/core/config.py`
- `backend/app/api/health.py`
- `backend/scripts/`
- `backend/alembic.ini`
- `backend/pyproject.toml`
- `frontend/package.json`
