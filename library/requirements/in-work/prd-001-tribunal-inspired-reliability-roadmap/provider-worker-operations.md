# Provider and worker operations

Provider breakers are registered only at active outbound boundaries. Transient transport failures, HTTP 429, and 5xx count; validation, authentication, deterministic 4xx, and programming errors do not. Defaults are five failures and a 30-second recovery window; tune per provider from observed SLOs. Logs and metric hooks use only bounded provider/state labels.

Worker defaults are five attempts, 24-hour maximum age, a 60-second lease, and capped exponential full jitter. `payload_ref` must be an opaque `domain-type:identifier`, never a phone number, transcript, prompt, credential, header, webhook body, exception text, or raw personal payload. Workspace-owned work uses an opaque workspace scope key in every identity and query.

On shutdown, runners must stop claiming first, await in-flight handlers for a bounded grace period, then cancel them. Lease expiry makes interrupted work recoverable. External-effect handlers must use the Phase 2 effect claim service with the same stable domain identity before calling a provider.

For DLQ triage, inspect domain data via `payload_ref`, provider status, and trace tooling. Do not copy sensitive data into the item. Replay requires an authenticated operator identifier and concise reason. Replay is idempotent, cannot target completed work, and returns through ordinary lease and effect-claim paths.

No safe active campaign runner was present at implementation time, so this phase supplies service primitives rather than inventing a scheduler. Adopt incrementally: campaign contacts first when its production runner is introduced, then other background effects. Provider adapters should wrap their narrow SDK/network call and supply an SDK-specific classifier where status extraction differs.
