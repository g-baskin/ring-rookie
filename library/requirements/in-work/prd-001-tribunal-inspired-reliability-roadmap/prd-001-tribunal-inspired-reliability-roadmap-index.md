# PRD-001: Tribunal-Inspired Reliability Roadmap

> **Status:** Backlog
> **Priority:** P0
> **Effort:** XL (> 3d)
> **Schema changes:** Additive

---

## Overview

Ring Rookie will adopt the highest-value engineering patterns identified in the comparative audit of `Gahroot/the-tribunal`, implemented independently and in five dependency-ordered phases. The work strengthens delivery enforcement, migration safety, side-effect correctness, provider resilience, background processing, observability, API contracts, browser testing, and prompt lifecycle management for Ring Rookie's voice-agent platform.

The Tribunal repository is reference material only. Its `LicenseRef-Proprietary` license states that no license is granted, so no source, tests, documentation, or configuration may be copied verbatim. Every implementation must be designed for Ring Rookie's architecture, dependencies, providers, data model, and risk profile.

---

## Goals

- Enforce backend, frontend, migration, dependency, and secret checks on every pull request.
- Prevent duplicate calls, messages, bookings, usage charges, and webhook effects.
- Contain external-provider outages and recover failed background work predictably.
- Trace and measure voice calls, provider calls, tool execution, workers, and retrieval paths.
- Detect backend/frontend API drift before merge.
- Test critical user journeys and voice-agent configuration end to end.
- Version agent prompts and connect every call outcome to the exact configuration used.

## Non-Goals

- Copying any Tribunal implementation verbatim or reproducing its product-specific CRM, advertising, reputation, or campaign features.
- Introducing automatic prompt traffic allocation before outcome instrumentation is trustworthy.
- Treating Redis-only deduplication as sufficient for billing or irreversible effects.
- Upgrading Ring Rookie's full dependency stack as part of this roadmap.
- Replacing existing Ring Rookie architecture where a targeted reliability layer is sufficient.

---

## Implementation order

| Phase | Sub-PRD | Scope | Priority | Status |
|---|---|---|---|---|
| 1 | [`prd-001a-tribunal-inspired-reliability-roadmap-delivery-spine`](./prd-001a-tribunal-inspired-reliability-roadmap-delivery-spine.md) | CI, security automation, migration verification, governance, environment drift | P0 | Completed ([#2](https://github.com/Gahroot/ring-rookie/pull/2), `2ce28c6`) |
| 2 | [`prd-001b-tribunal-inspired-reliability-roadmap-effect-correctness`](./prd-001b-tribunal-inspired-reliability-roadmap-effect-correctness.md) | Webhook pipeline, idempotency, provider contract tests | P0 | Completed ([#3](https://github.com/Gahroot/ring-rookie/pull/3), `5e7c692584e8127a1c6923200b5d0ba57f49e676`) |
| 3 | [`prd-001c-tribunal-inspired-reliability-roadmap-provider-worker-resilience`](./prd-001c-tribunal-inspired-reliability-roadmap-provider-worker-resilience.md) | Circuit breakers, retry framework, DLQ | P0 | In Work |
| 4 | [`prd-001d-tribunal-inspired-reliability-roadmap-observability-supervision`](./prd-001d-tribunal-inspired-reliability-roadmap-observability-supervision.md) | OpenTelemetry, metrics, voice-session supervision | P1 | Draft |
| 5 | [`prd-001e-tribunal-inspired-reliability-roadmap-contracts-quality-prompts`](./prd-001e-tribunal-inspired-reliability-roadmap-contracts-quality-prompts.md) | OpenAPI generation, Playwright, prompt versioning | P1 | Draft |

Phases are sequential at the dependency level. Work inside a phase may run in parallel only when files and contracts do not overlap.

---

## Acceptance criteria

| ID | Criterion |
|---|---|
| AC-1 | Every pull request runs deterministic backend, frontend, migration, security, and generated-contract checks. |
| AC-2 | Every retried external effect has a stable identity and a documented duplicate-delivery policy. |
| AC-3 | Provider outages fail through domain exceptions without cascading across unrelated requests or workers. |
| AC-4 | Exhausted background jobs are recoverable from a redacted, deduplicated dead-letter queue. |
| AC-5 | A production call can be traced across HTTP/WebSocket entry, STT, LLM, tools, TTS, persistence, and finalization. |
| AC-6 | Frontend API types are generated from FastAPI OpenAPI and CI rejects drift. |
| AC-7 | Critical journeys have browser-level tests and critical providers have sanitized payload contract tests. |
| AC-8 | Every call records the immutable prompt/configuration version that produced it. |
| AC-9 | No Tribunal proprietary source is present in the resulting git diff. |

---

## Cross-cutting rules

### Licensing and provenance

- Treat Tribunal paths as architectural evidence, not templates.
- Do not paste or mechanically translate source, comments, tests, workflows, or documentation.
- Record Ring Rookie-specific design decisions in implementation PR descriptions.
- Prefer official provider and framework documentation when defining concrete APIs.

### Security and privacy

- Never store raw phone numbers, transcripts, credentials, authorization headers, prompts, or full webhook bodies in metrics, traces, logs, retry payloads, or DLQ entries.
- Verify webhook signatures against raw request bytes before parsing.
- Use durable database-backed claims for financial or irreversible effects.
- Bound metric label cardinality; tenant identifiers require explicit review before use as labels.

### Verification order

Each implementation phase ends with:

1. Targeted tests for the new contracts.
2. Full backend and frontend quality checks affected by the phase.
3. Security review before quality/plan conformance review.
4. Evidence that generated files and migration state are clean.

---

## Deferred opportunities

These findings are retained but intentionally excluded from the first five phases:

- Knowledge-ingestion quality harnesses for extraction, chunking, retrieval, and answer relevance.
- Voicemail workflows, missed-call automation, and follow-up automation.
- Campaign selector virtualization for very large contact sets.
- Lead enrichment workers and human approval queues for risky automation.
- Transcript analysis, outcome classification, and sentiment classification.
- Reusable agent/tool configuration manifests.
- Load testing after representative production traffic profiles are known.
- Query-level frontend error boundaries, route error/loading states, offline recovery, and broader accessibility status regions.
- Database backup/restore and encryption-key rotation runbooks.

---

## Source audit evidence

### Ring Rookie gaps observed

- No files under `.github/workflows/`.
- No root `.github/CODEOWNERS`, PR template, issue forms, or Dependabot configuration.
- `Makefile` runs local checks but lacks frozen dependency, migration graph, generated artifact, security, and CI-parity targets.
- `backend/app/core/config.py` defines OpenTelemetry settings, but no application instrumentation consumes them.
- `frontend/src/lib/api/` contains handwritten clients without a generated OpenAPI contract artifact.
- Test inventory at audit time: 14 backend test files and 10 frontend test files; no Playwright E2E suite.
- No shared idempotency, provider circuit-breaker, retry/DLQ, prompt-version lifecycle, or provider contract-test layer was found.

### Tribunal reference paths reviewed

- `.github/workflows/backend-ci.yml`
- `.github/workflows/frontend-ci.yml`
- `.github/workflows/audit.yml`
- `.github/workflows/migrations.yml`
- `.github/workflows/codeql.yml`
- `.github/workflows/gitleaks.yml`
- `.github/dependabot.yml`
- `.github/CODEOWNERS`
- `Makefile`
- `scripts/dev/check_env_drift.py`
- `backend/app/services/idempotency.py`
- `backend/app/services/webhook_pipeline.py`
- `backend/app/core/circuit_breakers.py`
- `backend/app/workers/retryable.py`
- `backend/app/core/telemetry.py`
- `backend/app/core/metrics.py`
- `backend/app/services/ai/prompt_version_lifecycle_service.py`
- `backend/app/services/ai/bandit_statistics.py`
- `backend/tests/contract/`
- `backend/tests/voice_ws/`
- `backend/tests/workers/`
- `frontend/e2e/`
- `frontend/src/components/ui/query-error-boundary.tsx`

---

## Open questions

- [ ] Select the production OTLP backend before Phase 4 deployment; implementation should remain vendor-neutral.
- [ ] Define the current backend and frontend coverage baselines during Phase 1, then ratchet without lowering them.
- [ ] Identify which external effects require durable database claims versus bounded Redis delivery deduplication during Phase 2.
- [ ] Define business outcome signals and minimum sample sizes before enabling prompt winner recommendations in Phase 5.

---

## Related

- External reference: `https://github.com/Gahroot/the-tribunal`
- License reviewed: Tribunal `LICENSE`, `LicenseRef-Proprietary`, no license granted.
