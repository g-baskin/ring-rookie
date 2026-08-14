---
title: "PRD-002: Current Platform Baseline"
status: completed
type: backwards-prd
created: 2026-08-13
last-verified: 2026-08-13
owners:
  - Product
  - Engineering
source: reverse-engineered
---

# PRD-002: Current platform baseline

## Purpose

This backwards-PRD records the product behavior already implemented across Ring Rookie. It is descriptive, not evidence that every path is production-complete. Folder location marks it completed because the documented capabilities exist in current code.

## Problem statement

Teams need one control plane to configure and operate AI agents across telephone calls, browser voice, and text chat without independently assembling provider transport, AI, CRM, scheduling, campaign, retrieval, usage, and compliance infrastructure.

## Users and jobs

- **Workspace owner:** configure credentials, agents, phone numbers, tools, and data controls.
- **Agent operator:** test/publish agents, inspect calls/chats, manage contacts/appointments/campaigns.
- **Website visitor:** talk or chat with an agent through a public embed.
- **Telephone caller/contact:** interact with an inbound or outbound AI call.
- **Maintainer:** deploy, migrate, diagnose, and extend integrations safely.

## Implemented capabilities and acceptance evidence

### Identity and workspaces

- Users can register, log in, retrieve their profile, and log out from the client.
- Users can create/update/delete workspaces and assign agents many-to-many.
- Workspace context scopes settings, integrations, and operational records.

**Evidence:** `backend/app/api/auth.py`, `backend/app/api/workspaces.py`, `frontend/src/hooks/use-auth.tsx`, `frontend/src/contexts/workspace-context.tsx`.

### Agent lifecycle

- Users can create, list, inspect, update, and delete agents.
- Configuration includes prompt, prompt target, tier/provider profile, language, voice, greeting, generation and turn-detection settings, tools, recording/transcription, status, and embed policy.
- Agents can receive/regenerate a public ID and domain allowlist.

**Evidence:** `backend/app/api/agents.py`, `backend/app/models/agent.py`, `frontend/src/app/dashboard/agents/`.

### Voice channels

- Authenticated browser voice supports realtime WebSocket and WebRTC bootstrap paths.
- Public embeds load config, create sessions/tokens, connect realtime voice, execute tools, and save/retrieve transcripts.
- Telnyx/Twilio support number operations, inbound/outbound call callbacks, status updates, and media WebSockets.

**Evidence:** `backend/app/api/realtime.py`, `embed.py`, `telephony.py`, `telephony_ws.py`, `backend/app/services/gpt_realtime.py`.

### CRM, appointments, campaigns, and tools

- Operators manage contacts and appointments and view CRM stats.
- Campaigns support contact selection/filtering, lifecycle controls, attempts/retries, stats, and dispositions.
- AI tools expose internal CRM/bookings/call controls and selected external adapters with granular function filtering.

**Evidence:** `backend/app/api/crm.py`, `campaigns.py`, `backend/app/services/campaign.py`, `campaign_scheduler.py`, `tools/registry.py`.

### Calls and conversations

- Call records support list/detail, agent stats, analytics, export, and analysis.
- Public text chat supports regular and streamed responses plus history.
- Owners can list/detail/export/analyze conversations and view analytics.

**Evidence:** `backend/app/api/calls.py`, `chat.py`, `conversations.py`, `frontend/src/app/dashboard/calls/`, `conversations/`.

### Knowledge and usage

- Agent knowledge bases accept text/URL sources, embed chunks, and support semantic search.
- Per-agent daily usage tracks messages, conversations, tokens, and knowledge bytes.
- Billing configuration defines effective tier/custom limits.

**Evidence:** `backend/app/api/knowledge_base.py`, `usage.py`, `backend/app/services/knowledge_base.py`, models and migrations 015–017.

### Integrations, settings, and compliance

- Workspace credentials can be connected, updated, listed, and disconnected.
- OpenAI access can use workspace API keys or ChatGPT OAuth.
- Privacy settings, consent, export, opt choices, retention cleanup, and deletion endpoints exist.

**Evidence:** `backend/app/api/integrations.py`, `settings.py`, `chatgpt_oauth.py`, `compliance.py`.

### Operations

- Compose supplies PostgreSQL/pgvector, Redis, migrations, backend, frontend, and optional admin tools.
- Health endpoints distinguish liveness/readiness/dependencies.
- Sentry/OpenTelemetry are configurable.

**Evidence:** `docker-compose.yml`, `backend/app/main.py`, `backend/app/api/health.py`.

## Non-goals inferred from current implementation

- No native mobile application.
- No fully generic arbitrary integration executor; tools are allowlisted adapters.
- No guarantee that every integration catalog item is executable end to end.
- No production orchestration manifest in this repository; Compose is development-oriented.
- No server-managed browser session/cookie flow in the current frontend auth hook.

## Product invariants

1. Owner/workspace scope must be checked before data or credentials are returned.
2. Integer owner IDs must be converted with `user_id_to_uuid()` at UUID-backed boundaries.
3. Public IDs are locators, not secrets.
4. Enabled tool families/functions are allowlists; model output cannot bypass dispatch rules.
5. Provider callbacks and streamed sessions can duplicate, reorder, or disconnect and must be finalized idempotently.
6. Recording/transcript behavior must respect agent and privacy/consent configuration.
7. Durable schema changes require Alembic migrations.

## Known gaps and follow-up candidates

- Reconcile broad “30+ integrations” marketing claims with adapters that are actually executable.
- Designate one canonical agent-creation route.
- Add or document an owner UI for knowledge-base management.
- Normalize API prefixes in a versioned migration rather than silently changing clients.
- Continue eliminating nullable legacy workspace associations and mixed-ID confusion.
- Validate production topology, horizontal realtime scaling, and externally shared runtime state.

## Narrative documentation

See `library/README.md` and `library/knowledge/private/` for architecture, API, data, voice, chat/RAG, integrations, security, and operations narratives.

## QA

The `qa/` directory is reserved for `quality-guardian`. No QA findings are authored by this PRD.
