# PRD-001c quality and security review

## Acceptance trace

- Circuit transitions, transient classification, excluded failures, retry-after, and single half-open probe: `app/core/circuit_breaker.py`; focused tests cover open/recovery/exclusion/concurrency.
- Durable identity, tenant scope, payload references, attempts/age, leases, retry wait, completion/dead metadata, and replay audit: `app/models/worker_item.py`, migration 019, and `app/services/durable_workers.py`.
- PostgreSQL claims use `FOR UPDATE SKIP LOCKED`; SQLite is explicitly a unit fallback.
- DLQ dead transition is an update of the uniquely identified item. Replay rejects completed items and a second replay is a no-op.
- Error persistence deliberately discards exception messages/data. Safe references are constrained opaque identifiers.
- No active safe campaign/background runner entry point was found. Production scheduler invention is out of scope; adoption is documented.

## Security review

No Critical or High findings identified in self-review. Durable records contain opaque scope/digests/references and bounded generic error metadata. Logs contain provider and state only. Operator authentication belongs at the future administrative API boundary; this PR exposes no replay endpoint.

## Honest limitations

The common primitives are not yet wired across every provider SDK because doing so safely requires boundary-specific contract tests and rollout. No production runner is introduced. PostgreSQL concurrency, migration scratch/downgrade, and full CI evidence must be recorded from verification; focused SQLite tests do not prove `SKIP LOCKED` semantics.
