# Documentation inventory and drift audit

**Audit date:** 2026-08-13  
**Audit scope:** repository README/CLAUDE context, existing `library/`, backend application/models/routes/services/migrations/tests, frontend routes/components/API clients/tests, and Compose topology.  
**Not QA:** this is a documentation synchronization record, not an implementation-quality report.

## Canonical structure result

The repository had a partial schema-v2 library containing one operations narrative and PRD-001, but no `library/README.md` or broad narrative layer. This update added the canonical root index, public overview, private domain narratives, required lifecycle roots, and a completed backwards-PRD. Existing `high-availability.md` and PRD-001 were preserved without edits. No files under `library/notes/`, any `qa/`, or legacy `library/knowledge-base/wiki/` were edited.

## Coverage matrix

| Area                  | Narrative                                                                                | Governing implementation                                         |
| --------------------- | ---------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| Product/system        | `knowledge/public/overview/system-overview.md`                                           | root README, route trees, agent model.                           |
| Architecture          | `knowledge/private/architecture/system-architecture.md`                                  | backend composition, frontend layouts/providers, Compose.        |
| Backend               | `knowledge/private/backend/backend-architecture.md`                                      | `backend/app/api`, `services`, `core`, tests.                    |
| Frontend              | `knowledge/private/frontend/frontend-application.md`                                     | App Router pages, sidebar, auth/workspace contexts, API clients. |
| Data                  | `knowledge/private/data/data-model.md`                                                   | 23 model classes and 34 migration files discovered.              |
| API                   | `knowledge/private/api/api-surface.md`                                                   | route decorators in 22 route-bearing API modules.                |
| Voice/telephony       | `knowledge/private/voice/voice-and-telephony.md` plus `agent-phone-number-assignment.md` | realtime/embed/telephony routes, assignment UI/API, tests.       |
| Chat/RAG/usage        | `knowledge/private/ai/chat-champ-and-rag.md`                                             | chat/conversation/knowledge/usage models, routes, services.      |
| Integrations/tools    | `knowledge/private/integrations/tool-runtime.md`                                         | integration API/crypto and explicit tool registry.               |
| Security/compliance   | `knowledge/private/security/security-and-compliance-boundaries.md`                       | auth, middleware, compliance, public boundaries.                 |
| Operations            | `knowledge/private/operations/local-runtime.md` plus preserved HA doc                    | Compose, health, config, scripts.                                |
| Requirements baseline | `requirements/completed/prd-002-current-platform-baseline/`                              | backwards-PRD across existing behavior.                          |

## Feature synchronization: agent phone assignment

The 2026-08-13 synchronization pass added an extreme-detail feature reference for assigning provider numbers from **Agents → Advanced** and updated the API, frontend, and telephony narratives. The synchronized contract covers live account/workspace provider inventory, owner-scoped assignment metadata, omitted-versus-null update semantics, same-owner reassignment, optional-leading-plus inbound lookup, UI empty/loading/in-use states, concurrency caveats, focused backend tests, and rendered screenshot evidence.

Atomic entity and concept pages were also authored under the legacy-but-active `library/knowledge-base/wiki/` graph by `wiki-guardian`. Its global state files were intentionally not changed because the Legion TypeScript driver exclusively owns wiki index/log/hot/hash reconciliation.

## Confirmed drift

### D-001: local frontend URL

Root README says to open `http://localhost:3000`, while checked-in Compose publishes the frontend at port 4173 and backend CORS comments identify 4173 as Ring Rookie. Local-runtime docs use 4173 for the Compose path. Sources: `README.md`, `docker-compose.yml`, `backend/app/core/config.py`.

### D-002: knowledge chunking claim

Project context describes 500 tokens with 50 overlap; current service constants are 1,000 and 200 and the algorithm measures Python string length, not tokens. Narrative docs now describe current implementation. Source: `backend/app/services/knowledge_base.py`.

### D-003: integration breadth

Root README advertises 30+ integrations and names several vendors. The executable registry explicitly imports call control, internal CRM, GoHighLevel, Calendly, Shopify, Twilio SMS, and Telnyx SMS adapters. Catalog visibility should not be represented as end-to-end execution without adapter/registry evidence. Sources: `README.md`, `frontend/src/data/integrations.ts`, `backend/app/services/tools/registry.py`.

### D-004: product naming/schema terminology

Project context refers to `greeting_message`, `embed_config`, and a singular `knowledge_base_id` on Agent. Current model uses `initial_greeting`, `embed_settings`, and separate agent-owned `KnowledgeBase` rows; chat greeting customization is nested in embed settings. Source: `backend/app/models/agent.py`, `backend/app/models/knowledge_base.py`.

### D-005: API path examples

Project context lists `/api/knowledge/{kb_id}/upload`; implemented knowledge routes are under `/api/knowledge-bases`, with `/documents/text` and `/documents/url`. It lists public chat history, while implemented history is conversation-message scoped. Source: `backend/app/api/knowledge_base.py`, `backend/app/api/chat.py`.

### D-006: local database hostname examples

Project context describes Docker hostname `db`; checked-in Compose names the service `postgres`, and its configured URL uses `postgres:5432`. Source: `docker-compose.yml`.

### D-007: agent creation route duplication

Frontend contains both `/dashboard/agents/new` and `/dashboard/agents/create-agent`. Documentation records both but recommends choosing one canonical route. Source: `frontend/src/app/dashboard/agents/`.

## Unresolved or incomplete coverage

- Exact production deployment is not present; Compose uses development reload/dev-server commands.
- Provider behavior cannot be verified without credentials and live callbacks.
- Generated OpenAPI was not queried from a running server; API inventory was derived statically from route decorators and mounts.
- No dedicated dashboard route for knowledge-base administration was discovered.
- Migration/model parity was not validated against a live PostgreSQL schema.
- Existing PRD-001 makes planned reliability claims that remain lifecycle-scoped to `in-work`; this audit did not reinterpret its completion state.
- Concurrent wiki work under legacy `library/knowledge-base/wiki/` was excluded by instruction and is not part of this narrative inventory.

## Maintenance protocol

1. Update a narrative in the same change as a contract, data model, provider flow, or operator command.
2. Use `Last verified` dates and cite governing paths.
3. Re-run route/page/model inventory after structural changes.
4. Keep feature lifecycle represented by folder location.
5. Delegate implementation audit findings to `quality-guardian`; keep this file limited to documentation drift.
