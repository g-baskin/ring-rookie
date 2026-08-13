# Contributing

Use Python 3.12+, `uv`, Node 22, Docker, and Docker Compose 2.22+. Install host dependencies with `make install`.

## Persistent local development

Compose owns the complete local stack. Normal checks run beside it and must not call `docker compose down`.

```sh
make dev-up       # Start and wait for PostgreSQL, Redis, backend, and frontend
make dev-status   # Show service and health state
make dev-logs     # Follow application and dependency logs
make dev-smoke    # Verify dependencies, readiness, login, and API proxy
make dev-restart  # Restart frontend and backend only
make dev-down     # Stop containers; preserve named data volumes
```

Use `make dev-watch` in the foreground when Compose source-watch output is useful. The backend runs Uvicorn reload against `backend/app`; Next.js hot reload serves from `frontend/.next-dev`. Production builds write `frontend/.next-build`, so `npm run build` cannot replace manifests used by the running development server.

PostgreSQL and Redis data survive `make dev-down`. Database volumes are removed only by the explicit destructive command `make reset-database CONFIRM_RESET=yes`. A single local container is durable development infrastructure, **not high availability**.

Before opening a pull request run:

```sh
make backend-ci
make frontend-ci
make env-check
# With disposable PostgreSQL and DATABASE_URL configured:
make migration-check
# With gitleaks installed and network access:
make security-check dependency-check
```

`make ci` runs every gate. `make clean` removes generated artifacts only and does not stop the stack.

`backend/tests/ci-known-failures.txt` temporarily deselects the 17 legacy failures exposed when CI was introduced. CI runs every other test and enforces the measured 37% coverage baseline; delete entries as defects are repaired, and never add one without a tracked issue and owner.

`backend/migrations/schema-drift-baseline.sha256` fingerprints the pre-existing ORM/migration drift. `make migration-check` fails if that drift changes; remove the baseline after a dedicated schema-reconciliation migration makes `alembic check` clean.

## Required GitHub repository settings

Maintainers must configure settings that files cannot enforce:

1. **Actions / General:** set workflow permissions to “Read repository contents and packages”; disallow approval bypass. Allow only GitHub-authored, verified required actions, plus the SHA-pinned `astral-sh/setup-uv` and `gitleaks/gitleaks-action` used here.
2. **Rules / Rulesets:** protect `main`; require pull requests, CODEOWNER approval, resolved conversations, linear history, branches up to date, and all checks from CI, Migrations, CodeQL, and Security. Block force pushes/deletion.
3. **Code security:** enable dependency graph, Dependabot alerts/security updates, CodeQL default/setup as appropriate, secret scanning, and push protection. `security/dependency-audit-baseline.json` records the pre-existing advisory backlog: CI reports all active findings, fails on new advisory IDs, and announces resolved IDs so maintainers can shrink the baseline. Never add an advisory without a documented reachability review, owner, and expiry.
