# Effect correctness policy

## Implemented surface

The active state-changing telephony webhooks (`/twilio/voice`, `/twilio/status`,
`/telnyx/voice`, `/telnyx/status`) verify signatures before dispatch, hash provider
identifiers, and acquire a durable workspace-scoped claim. Completed deliveries are
acknowledged without repeating the effect. A concurrent processing delivery receives
503 so the provider retries. A failed execution is marked failed and the next delivery
may acquire it. Call identity is additionally unique by provider and provider call ID.
Terminal call states never regress, and campaign accounting only runs on the first
terminal transition.

Answer endpoints generate XML representations and have no durable database effect;
they retain signature verification but intentionally do not claim an effect.

Outbound `POST /api/v1/telephony/calls` supports a 1–128 character safe ASCII
`Idempotency-Key`. Its workspace-scoped operation digest is claimed before invoking a
provider and completed results are replayed. Processing requests return 503 honestly;
failed attempts become retryable. No provider forwarding is claimed: the installed
clients do not expose a verified provider idempotency parameter. This implements the
RFC 9110 §9.2.2 rationale for making a non-idempotent POST safely retryable without
pretending every POST is intrinsically idempotent.

Claims store SHA-256 digests only—not keys, webhook payloads, phone numbers, or other
PII. Operational logs use truncated digests rather than caller/callee values.

## Inventory and follow-up

| Effect class | Current policy |
| --- | --- |
| Active voice/status webhooks | Implemented above |
| Outbound call creation | Implemented above |
| SMS, email, CRM writes | No active inbound provider webhook/API in this service; require the shared claim pipeline before activation |
| Calendar, billing, payment, subscription | Policy-only; add provider-specific verified adapters and claims when an active route exists |
| Queue/job consumers and scheduled campaigns | Follow-up: claim stable job identity before external or state-changing work |
| File ingestion/RAG and OAuth callbacks | Follow-up: define resource-version identity and workspace scope before claiming |

New effects must define namespace, non-null scope, stable non-PII identity, duplicate
response semantics, processing response semantics, retry transition, and terminal
ordering before production activation.

## Migration and rollback

Migration `018_add_effect_claims` creates the claim table and call uniqueness constraint.
Rollback removes both; application rollback must occur before migration downgrade.
Existing duplicate provider call IDs must be reconciled before production upgrade.
