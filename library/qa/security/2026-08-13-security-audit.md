# Security audit — high availability and safe hot reload

**Date:** 2026-08-13
**Branch:** `batch/high-availability-hot-reload`
**Scope:** Current branch diff; full fidelity for Next.js/React, reduced framework-specific coverage for FastAPI/Python.

## Executive summary

One Critical dependency finding was detected and remediated. The frontend was running Next.js 15.5.9 and React 19.2.0 with current published vulnerabilities in Next.js and transitive production dependencies. `frontend/package.json` and `frontend/package-lock.json` now pin Next.js 16.3.0, React/React DOM 19.2.8, and patched direct dependency versions. `npm audit --omit=dev` reports zero vulnerabilities after the upgrade.

No High application-code findings were detected in the changed health, Compose, smoke, build-isolation, lifecycle, or documentation surfaces. The Python health implementation received universal secret/error checks, but a separate FastAPI-focused audit is recommended for full backend coverage.

## Findings scorecard

| Severity | Open | Fixed |
|---|---:|---:|
| Critical | 0 | 1 |
| High | 0 | 0 |
| Medium | 0 | 0 |
| Low | 0 | 0 |

## Findings

### SEC-001 — Critical — vulnerable production framework dependencies — Fixed

- **Evidence:** `frontend/package.json` previously resolved `next@15.5.9` and `react@19.2.0`; the 2026-08-13 production audit reported High Next.js advisories and vulnerable transitive `postcss`/`sharp` packages.
- **Risk:** published framework vulnerabilities included denial-of-service, request-smuggling, middleware bypass, server-side request forgery, and internal endpoint disclosure classes.
- **Remediation:** `frontend/package.json` and `frontend/package-lock.json` now pin `next@16.3.0`, `react@19.2.8`, `react-dom@19.2.8`, and patched direct production dependencies.
- **Verification:** `npm audit --omit=dev --json` reports 0 Critical, 0 High, 0 Moderate, and 0 Low vulnerabilities; frontend check, 196 tests, and production build pass.

## Category review

| Category | Result |
|---|---|
| Hardcoded secrets / `NEXT_PUBLIC_` secret exposure | None detected in changed code |
| Verbose dependency errors | Health responses redact driver and connection details; failure test passes |
| Command / SQL injection | None detected in changed code; fixed SQL is not user-controlled |
| XSS / unsafe HTML | None detected in changed code |
| Authentication / authorization bypass | No auth boundary changed |
| Server Actions | None added or changed |
| Client token or PII storage | None added or changed |
| Compose secret handling | Existing local `.env` injection retained; no secret added to Compose |
| Container exposure | Application ports remain local development interfaces; OAuth relay is loopback-bound on the host |
| Unicode rules-file backdoor | Deterministic scan found no changed instruction-file issue |
| Production dependency CVEs | SEC-001 fixed; production audit clean |

## Verification evidence

- Backend Ruff check and format check: pass.
- Backend mypy: pass.
- Backend health tests: 13 passed.
- Frontend ESLint, TypeScript, and Prettier: pass.
- Frontend tests: 196 passed.
- Frontend Next.js 16.3.0 production build: pass.
- `npm audit --omit=dev`: zero vulnerabilities.
- Docker Compose config validation: pass.
- Full-stack smoke: PostgreSQL, Redis, backend readiness, frontend login, and same-origin proxy pass.
- `git diff --stat` reviewed after remediation; changes remain scoped to this implementation plus the dependency security fix.

## Recommended follow-up

Run a dedicated FastAPI/Python dependency and authorization audit for full backend fidelity. No merge-blocking security follow-up remains for this plan.
