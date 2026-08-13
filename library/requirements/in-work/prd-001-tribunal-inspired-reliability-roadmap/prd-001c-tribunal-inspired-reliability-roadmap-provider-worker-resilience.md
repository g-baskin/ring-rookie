# PRD-001c: Provider and Worker Resilience

> **Status:** In Work
> **Priority:** P0
> **Effort:** XL (> 3d)
> **Schema changes:** Additive
> **Depends on:** PRD-001b

## Overview

Contain provider failures with circuit breakers and standardize background work with bounded retries, stable item identity, cancellation, observability, and a recoverable dead-letter queue (DLQ).

## Goals

- Prevent one degraded provider from exhausting Ring Rookie resources.
- Make worker retries deterministic and idempotent.
- Preserve exhausted failures for safe inspection and replay.

## Non-Goals

- Retrying validation failures or local programming errors.
- Storing sensitive payloads in retry or DLQ records.
- Building a general-purpose distributed workflow engine.

## Requirements

### Provider circuit breakers

Create one breaker per remote dependency, initially:

- Telnyx
- Twilio
- OpenAI
- Deepgram
- ElevenLabs
- Active calendar providers
- Active CRM providers
- Stripe when billing calls are enabled

Each breaker must:

- Use a provider-specific configuration with sane shared defaults.
- Open only for classified remote/transient failures.
- Fail fast with stable domain exceptions.
- Support native async calls.
- Transition through closed, open, and half-open recovery states.
- Emit bounded metrics and structured state-change logs.
- Exclude caller validation, authorization, and deterministic 4xx failures from failure counts unless provider semantics require otherwise.

### Retryable worker contract

Provide a reusable worker abstraction with:

- Stable worker and item names.
- Stable idempotency key from Phase 2.
- Explicit retryable/non-retryable exception classification.
- Exponential backoff with jitter.
- Maximum attempt and maximum age controls.
- Concurrency/lease rules preventing simultaneous processing.
- Cooperative shutdown and cancellation.
- Per-item success, retry, failure, and duration measurements.

### Dead-letter queue

Every exhausted item records only the minimum recoverable metadata:

- Worker name and item key.
- Attempt count and failure timestamps.
- Redacted exception type and bounded message.
- Trace ID.
- Reference to durable domain data rather than copied payload content.
- Replay state and operator attribution.

DLQ insertion and replay must be idempotent. Replaying an item must pass through the same claim and effect-correctness contracts as ordinary work.

### Initial adoption

Apply the framework first to campaign/contact work and any existing scheduled/background processors with external effects. Migrate additional workers only after the common contract proves stable.

## Acceptance criteria

- [ ] A failing provider opens its breaker after the configured threshold and unrelated providers continue operating.
- [ ] Half-open probes recover a provider without a process restart.
- [ ] Worker retries include jitter and never exceed configured attempt/age limits.
- [ ] Concurrent workers cannot process the same leased item simultaneously.
- [ ] Exhausted work produces one redacted DLQ record regardless of duplicate failure delivery.
- [ ] DLQ replay cannot duplicate an already-applied effect.
- [ ] Shutdown stops new claims and allows bounded cleanup of in-flight work.
- [ ] Unit tests cover every breaker transition and worker/DLQ state transition.

## Verification

- Simulate timeouts, connection errors, provider 429/5xx responses, deterministic 4xx responses, and recovery.
- Use deterministic clocks/randomness in retry tests.
- Crash a worker after claiming and verify lease expiry/recovery.
- Replay the same DLQ item twice and assert one effect.

## Ring Rookie evidence

- No common circuit-breaker module was found.
- No common retry/DLQ framework was found.
- Campaign and provider-driven operations need consistent failure semantics before expansion.

## Tribunal architectural references

- `backend/app/core/circuit_breakers.py`
- `backend/app/workers/retryable.py`
- `backend/tests/core/test_circuit_breakers.py`
- `backend/tests/workers/test_retryable_dlq.py`
- `backend/tests/workers/test_idempotency_keys.py`
- `backend/tests/workers/test_runner.py`

Do not copy these proprietary files or inherit provider assumptions; independently select implementation dependencies and contracts after checking their current APIs.
