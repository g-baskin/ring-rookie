# PRD-001b quality review

## Defensive security review

- Signature checks occur before route parsing/dispatch; Starlette caches the exact body/form values used by verification.
- Telnyx timestamps older/newer than five minutes are rejected.
- Persisted claim identity is SHA-256 only, with non-null scope and database uniqueness.
- Telephony logs no longer include caller/callee values on changed webhook paths.
- Idempotency keys are bounded and restricted to safe ASCII; raw keys are not stored.
- No Critical or High issue remained after review.

## Conformance review

Implemented durable PostgreSQL atomic claims with a SQLite savepoint fallback, retryable
failed claims, completed replay/no-op, processing 503, active voice/status wiring,
terminal ordering, once-only campaign terminal updates, outbound replay, call identity
uniqueness, policy inventory, migration, and model exports. Answer endpoints remain
unclaimed because they only render XML. Provider idempotency forwarding is intentionally
not asserted because the installed service APIs do not expose a verified parameter.

## Verification record

See the PR checks and description for exact commands and outcomes. Migration upgrade
requires reconciliation if a deployment already contains duplicate `(provider,
provider_call_id)` rows.
