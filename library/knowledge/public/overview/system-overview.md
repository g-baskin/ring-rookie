# Ring Rookie system overview

**Audience:** users, evaluators, operators, and new contributors  
**Last verified:** 2026-08-13

Ring Rookie is a self-hostable platform for configuring AI agents that converse over phone calls, a browser voice widget, and text chat. The product combines a Next.js dashboard, a FastAPI control plane, PostgreSQL persistence, Redis-backed runtime coordination, provider APIs, and browser/telephony realtime transports.

## Product surfaces

- **Agent configuration:** create agents, select price/quality tier, language and voice, tune turn detection, write instructions, enable tools, assign workspaces, and publish an embed identity.
- **Voice:** test an agent in the browser, embed it on another site, receive inbound calls, and initiate outbound calls.
- **CRM and scheduling:** manage contacts and appointments; expose selected CRM and booking operations as AI-callable tools.
- **Campaigns:** group contacts into an outbound campaign, control campaign lifecycle, retry calls, and record dispositions.
- **Call and chat records:** inspect transcripts and aggregate analytics; export or analyze selected records.
- **Chat Champ:** expose a public text-chat API, persist conversations/messages, enforce per-agent usage tiers, and optionally retrieve agent knowledge.
- **Integrations:** store workspace-scoped credentials for GoHighLevel, Calendly, Shopify, Twilio SMS, Telnyx SMS, and other catalog entries.
- **Compliance controls:** configure recording/transcription and retention preferences; record consent; request export, opt-out, withdrawal, cleanup, or deletion.

## Typical voice-agent journey

1. Register or sign in.
2. Create a workspace and agent.
3. Configure instructions, provider credentials, voice behavior, tools, and optionally a phone number.
4. Test through browser realtime voice.
5. Publish the embed or connect Telnyx/Twilio for telephone traffic.
6. Review calls, transcripts, analytics, contacts, appointments, and learned lessons.

## Typical Chat Champ journey

1. Use an agent's public ID to load public chat configuration.
2. Send or stream a message with a visitor session ID.
3. The backend creates or resumes a conversation, optionally retrieves knowledge, generates a response, persists messages, and increments usage.
4. Authenticated owners inspect conversation history and analytics.

## Important implementation truths

- The current dashboard stores its bearer token in browser `localStorage`; public `/embed` routes do not require dashboard authentication.
- Data tenancy is transitioning: core users and agents use integer user IDs, while several settings, call, integration, phone, and campaign records use deterministic UUID user identity. Backend code must call `user_id_to_uuid()` at those boundaries.
- Workspace membership scopes agents, contacts, appointments, credentials, phone numbers, and calls in different parts of the model. Not every legacy relation is non-null yet.
- The implementation exposes fewer fully executable integrations than the broad catalog displayed by the product: execution routing is explicit in the backend registry.

## Governing code

- `frontend/src/app/` — routed product surfaces.
- `frontend/src/components/app-sidebar.tsx` — primary dashboard navigation.
- `backend/app/main.py` — middleware, routers, startup, and shutdown.
- `backend/app/api/` — HTTP and WebSocket contracts.
- `backend/app/services/` — voice, chat, campaigns, knowledge, integrations, and compliance logic.
- `backend/app/models/` and `backend/migrations/versions/` — persisted domain model and its evolution.
- `docker-compose.yml` — supported local service topology.
