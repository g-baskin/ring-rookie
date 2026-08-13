# API and transport surface

**Last verified:** 2026-08-13  
**Source:** route decorators in `backend/app/api/*.py`, mounted by `backend/app/main.py`.

## Contract conventions

Authenticated control-plane routes use JWT bearer authentication unless explicitly public/provider-facing. Request and response bodies are Pydantic schemas under `backend/app/schemas/`. The API uses JSON for ordinary operations, SSE for streamed text chat, and WebSockets/WebRTC helpers for realtime voice.

Prefixes are not globally uniform. CRM, workspaces, and campaigns receive `/api/v1` when mounted in `main.py`; several other routers include that prefix themselves, while public chat, knowledge, usage, webhook, and WebSocket groups use distinct roots. Consumers must preserve the mounted paths below.

## Route groups

| Prefix                                     | Methods and resources                                                           |
| ------------------------------------------ | ------------------------------------------------------------------------------- |
| `/api/v1/auth`                             | register, login, current user.                                                  |
| `/api/v1/agents`                           | CRUD; embed config; regenerate public ID.                                       |
| `/api/v1/calls`                            | list/detail, analytics, agent stats, export, analyze.                           |
| `/api/v1/conversations`                    | list/detail, analytics, export, analyze.                                        |
| `/api/v1/integrations`                     | list/detail/connect/update/disconnect.                                          |
| `/api/v1/phone-numbers`                    | persisted phone-number CRUD.                                                    |
| `/api/v1/settings`                         | get/update provider settings.                                                   |
| `/api/v1/compliance`                       | status/privacy/consent/export/CCPA/withdraw/delete/cleanup.                     |
| `/api/v1/oauth/chatgpt`                    | connect, callback, status, refresh, disconnect.                                 |
| `/api/v1/agents/{agent_id}/lessons`        | CRUD and CSV/JSON exports.                                                      |
| `/api/v1/realtime`                         | WebRTC session, ephemeral token, transcript save.                               |
| `/api/v1/telephony`                        | provider number search/purchase/release; call start/hangup.                     |
| `/api/v1/tools/execute`                    | direct tool execution.                                                          |
| `/api/v1/workspaces`                       | workspace CRUD and agent membership.                                            |
| `/api/v1/crm`                              | contacts, appointments, requirements, stats.                                    |
| `/api/v1/campaigns`                        | campaign/contact CRUD, filtering, start/pause/stop/restart, stats/dispositions. |
| `/api/knowledge-bases`                     | KB CRUD, text/URL documents, listing/deletion, KB/agent search.                 |
| `/api/usage`                               | tiers, status, summary, daily usage, agent billing.                             |
| `/api/public/chat/{public_id}`             | config, message, stream, conversation message history.                          |
| `/api/public/embed/{public_id}`            | config, session, token, tool call, transcript, history.                         |
| `/webhooks/twilio/*`, `/webhooks/telnyx/*` | voice answer/status callbacks.                                                  |
| `/health*`                                 | aggregate, live, ready, database, Redis, CORS.                                  |

## Realtime endpoints

| Endpoint                              | Transport    | Role                                               |
| ------------------------------------- | ------------ | -------------------------------------------------- |
| `/ws/realtime/{agent_id}`             | WebSocket    | Authenticated browser voice proxy.                 |
| `/ws/public/embed/{public_id}`        | WebSocket    | Public voice widget stream with origin validation. |
| `/ws/telephony/twilio/{agent_id}`     | WebSocket    | Twilio media stream.                               |
| `/ws/telephony/telnyx/{agent_id}`     | WebSocket    | Telnyx media stream.                               |
| `/api/public/chat/{public_id}/stream` | SSE response | Token/event streaming for text chat.               |

## Public-ID security boundary

Agent `public_id` locates published/embed-enabled behavior without owner JWT. Public embed requests validate origin against `allowed_domains`; wildcard subdomains are supported, and null origins are conditionally accepted for localhost development. Public text chat also enforces agent availability and usage/rate controls. Public history endpoints must constrain data by conversation/session semantics rather than trusting caller-supplied IDs alone.

## Telephony callback boundary

Provider webhooks are internet-facing. Signature verification, idempotent event handling, and call/provider ID correlation belong at this edge. Media WebSockets are separate from REST status callbacks; either can terminate unexpectedly, so call finalization must tolerate reordered or duplicate events.

## Errors and observability

API errors should use meaningful HTTP status codes and safe `detail` messages. Middleware attaches request IDs and security headers. Structured logs should include stable resource/provider identifiers while excluding tokens, credentials, raw authorization headers, and unnecessary transcript content.

## Client mapping

Frontend adapters live in `frontend/src/lib/api/`. Changes to route prefixes, auth, schemas, or streaming event shapes require coordinated client updates. OpenAPI is available from the FastAPI application unless disabled by deployment configuration; route decorators remain the source used for this inventory.

## Detailed inventory

See [`endpoint-catalog.md`](endpoint-catalog.md) for the statically derived method/path catalog.

## Governing paths

- `backend/app/main.py`
- `backend/app/api/`
- `backend/app/schemas/`
- `frontend/src/lib/api/`
