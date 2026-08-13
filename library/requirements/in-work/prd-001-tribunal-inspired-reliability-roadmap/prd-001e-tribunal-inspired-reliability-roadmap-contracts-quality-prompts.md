# PRD-001e: Generated Contracts, End-to-End Quality, and Prompt Versions

> **Status:** Backlog
> **Priority:** P1
> **Effort:** XL (> 3d)
> **Schema changes:** Additive
> **Depends on:** PRD-001d

## Overview

Close the reliability loop by generating frontend API contracts from FastAPI, testing critical browser journeys, and recording immutable prompt/configuration versions against call outcomes.

## Goals

- Detect backend/frontend API drift at generation time.
- Prove core user journeys in a real browser.
- Make prompt changes auditable, reversible, and measurable.

## Non-Goals

- Replacing all handwritten API wrappers with generated runtime clients.
- Broad visual-regression testing in the first iteration.
- Automatically choosing or routing prompt variants before trustworthy outcome data exists.

## Requirements

### OpenAPI contract generation

- Export FastAPI OpenAPI deterministically without starting production infrastructure.
- Generate TypeScript types with a verified current tool/API.
- Commit the OpenAPI and generated TypeScript artifacts.
- Keep thin handwritten domain wrappers and React Query hooks around generated types.
- Add `make codegen` and `make codegen/check` targets.
- Regenerate in CI and reject any diff.
- Ensure export uses explicit non-production test configuration and no real secrets.

### Playwright journeys

Add isolated browser tests for:

1. Authentication and protected-route behavior.
2. Creating and configuring an agent.
3. Assigning/configuring a phone path and initiating a safe test call or mocked equivalent.
4. Creating/updating a CRM contact.
5. Loading and interacting with the embed widget.
6. Usage-limit and recoverable-error behavior.

Tests must use deterministic fixtures, tenant isolation, trace/screenshots on failure, and no real provider effects in ordinary CI.

### Prompt/configuration versions

Create an immutable version record containing at minimum:

- Agent ID and sequential version.
- System prompt and greeting.
- Model, voice, temperature, and relevant inference settings.
- Tool configuration snapshot or immutable reference.
- RAG configuration snapshot or immutable reference.
- Creator, change summary, creation time, activation time, and supersession time.
- Baseline/active state.

Every call record must reference the exact version used.

Support:

- Create draft version.
- Activate version atomically.
- Roll back to a prior version by creating/activating a new immutable state or by a documented immutable activation model.
- Compare bounded outcome, latency, quality, cost, booking, escalation, and tool-success metrics.
- Require minimum samples and uncertainty reporting before recommending a winner.

Automatic traffic splitting and bandit allocation remain disabled until outcome definitions and safeguards are validated.

### Frontend failure isolation follow-up

Where Phase 5 journeys expose broad failure blast radius, add focused React Query reset boundaries, route `error.tsx`/`loading.tsx`, accessible status messaging, and explicit offline recovery using existing design patterns.

## Acceptance criteria

- [ ] CI rejects stale OpenAPI or generated TypeScript artifacts.
- [ ] Handwritten API wrappers use generated request/response types for covered endpoints.
- [ ] Playwright covers all six critical journeys without contacting billable production providers.
- [ ] Every new call references one immutable prompt/configuration version.
- [ ] Activation and rollback are atomic and workspace-scoped.
- [ ] Historical calls retain their original version association after future edits.
- [ ] Comparisons display sample size and uncertainty; no winner is asserted below configured evidence thresholds.
- [ ] Automatic prompt traffic allocation is off by default.

## Verification

- Change a FastAPI response schema without regeneration and confirm CI fails.
- Run Playwright in CI against disposable services and inspect failure artifacts.
- Activate, roll back, and compare prompt versions while verifying historical call associations.
- Test cross-workspace version access and concurrent activation attempts.

## Ring Rookie evidence

- `frontend/src/lib/api/` contains handwritten clients but no generated `_generated.ts` contract.
- No committed backend OpenAPI artifact or codegen drift target was found.
- No Playwright E2E suite was found.
- No prompt-version model or lifecycle service was found.

## Tribunal architectural references

- `backend/openapi.json`
- `frontend/src/lib/api/_generated.ts`
- `frontend/package.json` codegen script
- `Makefile` codegen and drift-check targets
- `frontend/e2e/`
- `backend/app/services/ai/prompt_version_lifecycle_service.py`
- `backend/app/services/ai/bandit_statistics.py`
- `backend/tests/api/test_voice_campaigns_workspace_isolation.py`
- `frontend/src/components/ui/query-error-boundary.tsx`

Do not copy these proprietary files; independently define Ring Rookie's generated contract, browser fixtures, version schema, lifecycle, statistics, and UI.
