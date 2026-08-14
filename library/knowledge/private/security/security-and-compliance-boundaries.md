# Security, privacy, and compliance boundaries

**Last verified:** 2026-08-13  
**Scope:** architecture narrative only; this is not a security or QA audit.

## Authentication

Dashboard users register/login through `/api/v1/auth`; the frontend stores the bearer token in `localStorage` and sends it to backend routes. Backend dependencies are the enforcement point. Mixed integer/UUID owner identity requires deterministic conversion at schema boundaries.

## Public surfaces

Public chat and embed routes use an agent public ID and intentionally bypass dashboard JWT auth. Voice embed additionally validates `Origin` against agent domains. Provider webhook and media endpoints are also public by necessity. Treat all four surfaces as hostile-input boundaries with dedicated rate, size, timeout, signature, and ownership controls.

## Secret storage

Deployment secrets are environment settings. Workspace provider keys and integration credentials are persisted through settings/integration models; integration crypto encrypts sensitive values. ChatGPT OAuth stores access/refresh metadata and uses a configured token-encryption key. Secrets must be redacted in logs, API responses, exports, exceptions, and seed files.

## Tenant isolation

The principal authorization dimensions are owner and workspace. Routes/services should verify both where a resource is workspace-scoped. The presence of nullable legacy workspace foreign keys means “no workspace” cannot safely mean “all workspaces.” Agent/workspace association governs shared-agent use.

## Voice data

Calls may contain recording URLs, transcripts, summaries, sentiment, action items, caller/callee numbers, provider identifiers, and cost data. Agent recording/transcript toggles express product intent, while privacy settings and consent records express user/legal constraints. Data collection should follow the stricter applicable rule.

## Compliance service

The compliance API exposes privacy settings/status, consent recording/withdrawal, user export, CCPA opt-out/opt-in, retention cleanup, and data deletion. `PrivacySettings` stores preferences/retention policy; `ConsentRecord` preserves event evidence. Destructive operations should be authenticated, scoped, auditable, and designed around referential/cascade effects.

## Public chat and RAG

Conversation metadata can identify visitors even without accounts. Minimize and hash where possible. URL ingestion is an outbound-request boundary; embeddings send source text to the configured model provider. Retrieved documents are untrusted context and can contain prompt injection.

## Security middleware and observability

The backend installs request tracing and security headers and configures CORS from typed settings. Sentry and OpenTelemetry are optional. Observability exporters must avoid recording authorization headers, integration credentials, raw audio, or full transcript/message bodies by default.

## Required reviews when changing boundaries

- Auth/session behavior: threat model XSS, token theft, expiry, logout, and refresh semantics.
- Public embed/chat: origin/session/ownership/rate-limit tests.
- Webhooks: provider signature verification and replay/idempotency tests.
- Integration credentials: encryption/key rotation/redaction tests.
- Export/deletion: inventory every related table and external provider copy.
- Recording/transcription: consent and retention behavior by deployment jurisdiction.
- URL ingestion: SSRF protections, content limits, MIME handling, redirects, and timeouts.

## Governing paths

- `backend/app/core/auth.py`
- `backend/app/core/security.py`
- `backend/app/middleware/security.py`
- `backend/app/api/compliance.py`
- `backend/app/services/compliance.py`
- `backend/app/services/integration_crypto.py`
- `backend/app/api/embed.py`
- `backend/app/api/chat.py`
- `backend/app/models/privacy_settings.py`
- `frontend/src/hooks/use-auth.tsx`
