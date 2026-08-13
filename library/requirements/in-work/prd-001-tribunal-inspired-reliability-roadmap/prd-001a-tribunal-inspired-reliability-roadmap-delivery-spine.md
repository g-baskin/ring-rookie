# PRD-001a: Delivery Spine

> **Status:** In Work
> **Implementation PR:** TBD
> **Implementation commit:** TBD
> **Quality review:** `qa/prd-001a-quality-review.md`
> **Priority:** P0
> **Effort:** L (1-3d)
> **Schema changes:** None
> **Depends on:** None

## Overview

Create the enforcement layer that all later reliability work depends on: CI, migration safety, security automation, repository governance, deterministic dependency installation, and environment drift detection.

## Goals

- Make local quality commands and pull-request checks equivalent.
- Reject invalid migration graphs and schema drift before deployment.
- Automate dependency, static-analysis, and secret checks.
- Establish review ownership and consistent issue/PR intake.

## Non-Goals

- Redesigning deployment infrastructure.
- Raising coverage to an arbitrary external target immediately.
- Resolving every dependency advisory regardless of exploitability.

## Requirements

### Backend CI

- Check `uv.lock` consistency and install with a frozen lockfile.
- Run Ruff lint and format checks without mutation.
- Run strict mypy.
- Run pytest with a measured coverage floor based on Ring Rookie's initial baseline.
- Provide isolated PostgreSQL and Redis services where integration tests need them.

### Frontend CI

- Require a committed, synchronized `package-lock.json` and run `npm ci`.
- Run ESLint, TypeScript, Prettier check, Vitest, and `next build`.
- Cache dependencies without caching build output as proof of correctness.

### Migration CI

- Require exactly one Alembic head.
- Run `alembic upgrade head` and `alembic check` against disposable PostgreSQL.
- Downgrade one revision and upgrade again where the migration contract supports rollback.
- Require an explicit exception and recovery plan for deliberately irreversible migrations.

### Security and governance

- Add CodeQL for Python and TypeScript/JavaScript.
- Add Gitleaks with redacted output.
- Add scheduled and pull-request dependency auditing with triage instructions.
- Add Dependabot grouping suitable for backend and frontend lockfiles.
- Add CODEOWNERS, PR template, structured bug report, and feature request forms.
- Move or mirror pre-commit configuration to the repository root so it covers both applications.

### Environment drift

- Compare backend settings, frontend environment reads, and checked-in environment templates.
- Reject undocumented variables, stale template entries, unsafe secret defaults, and secret-shaped `NEXT_PUBLIC_*` variables.

### Developer commands

- Extend `Makefile` with CI-parity targets rather than duplicating shell logic inside workflows.
- Keep destructive database reset distinct from ordinary cleanup and require an explicit warning.

## Acceptance criteria

- [ ] A pull request cannot merge when backend or frontend lint, type, format, test, or build checks fail.
- [ ] CI fails with zero or multiple Alembic heads.
- [ ] CI proves current migrations can create the expected schema from a clean database.
- [ ] CodeQL, Gitleaks, and dependency audit jobs run with least-privilege workflow permissions.
- [ ] Environment templates and actual config usage cannot drift silently.
- [ ] Root governance files identify ownership and require testing, migration, security, and rollout notes.
- [ ] Local `make` targets reproduce each CI job.

## Verification

- Introduce a temporary controlled failure for each workflow class and confirm the expected job rejects it before removing the failure.
- Run all CI-parity Make targets locally where platform dependencies permit.
- Inspect workflow permissions and pin third-party actions to immutable commit SHAs.

## Ring Rookie evidence

- `.github/workflows/` is absent.
- Existing `Makefile` provides local commands but no frozen installs, security audit, environment drift, generated artifact, or migration graph checks.
- Pre-commit configuration exists under `backend/`, not at repository scope.

## Tribunal architectural references

- `.github/workflows/backend-ci.yml`
- `.github/workflows/frontend-ci.yml`
- `.github/workflows/audit.yml`
- `.github/workflows/migrations.yml`
- `.github/workflows/codeql.yml`
- `.github/workflows/gitleaks.yml`
- `.github/dependabot.yml`
- `.github/CODEOWNERS`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/ISSUE_TEMPLATE/`
- `Makefile`
- `scripts/dev/check_env_drift.py`

Do not copy these proprietary files; independently implement equivalent Ring Rookie controls.
