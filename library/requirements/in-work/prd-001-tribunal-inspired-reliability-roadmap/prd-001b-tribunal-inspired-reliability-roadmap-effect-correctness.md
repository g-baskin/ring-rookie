# PRD-001b: Effect Correctness

> **Status:** In Work
> **Priority:** P0
> **Effort:** L (1-3d)
> **Schema changes:** Additive
> **Depends on:** PRD-001a

## Overview

Create one correctness contract for inbound provider events and outbound side effects so retries, reordered delivery, process crashes, and provider redelivery cannot produce duplicate calls, messages, bookings, usage charges, or subscription changes.

## Goals

- Verify and normalize every provider webhook before domain handling.
- Give every retryable external effect a stable identity.
- Test Ring Rookie against realistic, sanitized provider payloads.

## Non-Goals

- A generic event bus.
- Redis-only correctness for billing or irreversible actions.
- Persisting full provider payloads without retention and privacy review.

## Requirements

### Shared webhook pipeline

Implement the lifecycle:

```text
receive raw bytes → verify signature/timestamp → parse → normalize → claim delivery → dispatch → commit → acknowledge
```

The pipeline must:

- Verify signatures against raw bytes before JSON parsing.
- Normalize provider events into typed internal envelopes.
- Distinguish malformed, unauthorized, duplicate, unsupported, retryable, and successfully applied events.
- Keep routes thin; provider adapters own verification/parsing and domain handlers own effects.
- Preserve a trace/request identifier without logging secret or personal payload fields.

Initial providers should cover active Ring Rookie integrations: Telnyx first, then Twilio, Stripe, and configured calendar/CRM webhook providers.

### Idempotency policy

- Derive stable keys from a namespaced operation and immutable business identifiers.
- Persist keys with effect records where duplicate execution has financial, communication, or irreversible consequences.
- Use unique database constraints as the final concurrency guard.
- Use Redis atomic `SET NX EX` only for bounded webhook-delivery suppression where fail-open behavior is acceptable.
- Forward provider-supported idempotency headers or client state.
- Define TTL, replay, failure, and retention behavior per effect class.

### Effect inventory

At minimum, classify and cover:

- Starting a phone call.
- Sending SMS.
- Creating or changing an appointment.
- Recording usage or enforcing a usage tier.
- Provisioning payment/subscription state.
- Advancing a campaign contact.
- Processing terminal call events.

### Provider contract tests

- Store sanitized fixtures that retain provider structure and signatures generated with test secrets.
- Test missing/malformed signatures, stale timestamps, duplicate IDs, unknown types, field omission, event reordering, and handler failure.
- Test workspace isolation on every event that resolves tenant-owned data.
- Document fixture provenance and refresh procedure.

## Acceptance criteria

- [ ] Duplicate webhook delivery returns a documented success/no-op response without repeating domain effects.
- [ ] Concurrent duplicate outbound requests create at most one durable effect record and at most one provider request.
- [ ] Signature verification occurs before parsing or side effects.
- [ ] Unknown event types do not crash routes or mutate state.
- [ ] A Redis outage follows the documented policy for each event class and cannot duplicate durable financial effects.
- [ ] Every supported provider has sanitized contract fixtures and negative verification tests.
- [ ] Workspace-isolation tests prove one tenant's event cannot mutate another tenant's records.

## Verification

- Race two requests with the same key and assert one provider invocation.
- Replay stored provider fixtures multiple times and compare database state.
- Inject a crash between local persistence and provider response, then retry.
- Run provider contract tests in Phase 1 CI.

## Ring Rookie evidence

- No shared idempotency service or shared webhook processing pipeline was found.
- Telephony, usage, campaigns, compliance, and external integrations create multiple costly or irreversible effect boundaries.

## Tribunal architectural references

- `backend/app/services/idempotency.py`
- `backend/app/services/webhook_pipeline.py`
- `backend/app/api/webhooks/`
- `backend/tests/contract/`
- `backend/tests/api/test_calcom_webhook_idempotency.py`
- `backend/tests/services/test_idempotency_primitives.py`
- `backend/tests/services/telephony/test_telnyx_idempotency.py`

Do not copy these proprietary files; define Ring Rookie-specific event envelopes, keys, storage, and provider adapters.
