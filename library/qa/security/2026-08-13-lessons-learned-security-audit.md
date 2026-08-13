# Lessons Learned Security Audit

**Date:** 2026-08-13
**Scope:** Current working-tree implementation of transcript-linked lessons
**Ordering:** Security review completed before final quality review
**Scope note:** The Python/FastAPI backend received universal access-control, injection, PII, and logging checks at reduced stack-specific fidelity.

## Executive summary

One High implementation defect was found and fixed: frontend item/export URLs appended path segments after an existing workspace query string, producing malformed requests and potentially dropping the intended workspace context. No Critical findings remain.

## Scorecard

| Category | Result | Evidence |
|---|---|---|
| Authentication and object authorization | Pass | `backend/app/api/lessons.py` authorizes agent context and scopes every lesson/source query by user, agent, and workspace |
| Cross-tenant access | Pass | `backend/tests/test_api/test_lessons.py::test_cross_user_agent_is_denied` |
| Source transcript ownership | Pass | Create requires owned, completed, provider=`test` source call |
| PII/transcript leakage | Pass | API and exports omit transcript body; new logs contain identifiers only |
| CSV injection | Pass | Formula-leading cells after whitespace receive a tab prefix; focused test covers `=` and `+` |
| Input rendering/validation | Pass | Pydantic bounds plain text; React renders text without `dangerouslySetInnerHTML` |
| Dependency/CVE scan | No feature finding | Installed security script could not locate its expected root lockfile; frontend quality/build still passed against installed Next.js 16.3.0 / React 19 |

## Findings

### SEC-LESSON-001 — High — Fixed

**Evidence:** `frontend/src/lib/api/lessons.ts:75`, `:89`, and `:102` originally appended `/{lessonId}` or `/export/{format}` to the string returned by `lessonUrl()`. When `workspace_id` existed, the result had the shape `lessons?workspace_id=X/lesson`, so the route did not preserve the intended authorized workspace context.

**Fix:** `lessonUrl()` now accepts a path suffix and constructs the full pathname before adding query parameters.

**Guard:** Frontend checks/tests/build and backend workspace-scoped API tests.

## Critical findings

None detected.

## Medium and low findings

None introduced by this feature.

## Verification

- Backend Ruff check and format check: passed.
- Backend mypy: passed.
- Alembic upgrade through `020_add_lessons`: passed.
- Focused backend API suite: 5 passed.
- Frontend ESLint, TypeScript, and Prettier check: passed.
- Focused frontend interaction suite: 4 passed.
- Next.js production build: passed.
- `git diff --check`: passed.

## Files changed by security remediation

| File | Change |
|---|---|
| `frontend/src/lib/api/lessons.ts` | Build item/export paths before workspace query parameters |

## Residual risk

The feature has no automatic retention duration; deletion and source-call cascade exist, but retention policy remains a product/legal decision recorded in `COMPLIANCE.md`.
