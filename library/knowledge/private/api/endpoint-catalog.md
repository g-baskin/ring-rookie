# Endpoint catalog

**Last verified:** 2026-08-13  
**Derivation:** static inspection of FastAPI router prefixes, decorators, and mounts. Path parameters are shown literally. Consult request/response schemas and generated OpenAPI before integrating.

## Authentication and agents

| Method | Path                                            | Operation                                   |
| ------ | ----------------------------------------------- | ------------------------------------------- |
| POST   | `/api/v1/auth/register`                         | Create user.                                |
| POST   | `/api/v1/auth/login`                            | Exchange form credentials for bearer token. |
| GET    | `/api/v1/auth/me`                               | Resolve current user.                       |
| POST   | `/api/v1/agents`                                | Create agent.                               |
| GET    | `/api/v1/agents`                                | List owned agents.                          |
| GET    | `/api/v1/agents/{agent_id}`                     | Get agent.                                  |
| PUT    | `/api/v1/agents/{agent_id}`                     | Replace/update agent configuration.         |
| DELETE | `/api/v1/agents/{agent_id}`                     | Delete agent.                               |
| GET    | `/api/v1/agents/{agent_id}/embed`               | Get owner embed settings.                   |
| PATCH  | `/api/v1/agents/{agent_id}/embed`               | Update embed settings.                      |
| POST   | `/api/v1/agents/{agent_id}/embed/regenerate-id` | Rotate public ID.                           |

## Workspaces and settings

| Method         | Path                                                  | Operation                                     |
| -------------- | ----------------------------------------------------- | --------------------------------------------- |
| GET/POST       | `/api/v1/workspaces`                                  | List/create workspaces.                       |
| GET/PUT/DELETE | `/api/v1/workspaces/{workspace_id}`                   | Read/update/delete workspace.                 |
| GET/POST       | `/api/v1/workspaces/{workspace_id}/agents`            | List/add workspace agents.                    |
| DELETE         | `/api/v1/workspaces/{workspace_id}/agents/{agent_id}` | Remove membership.                            |
| GET            | `/api/v1/workspaces/agent/{agent_id}`                 | List an agent's workspaces.                   |
| PUT            | `/api/v1/workspaces/agent/{agent_id}/workspaces`      | Replace agent memberships.                    |
| GET/POST       | `/api/v1/settings`                                    | Get/update workspace-aware provider settings. |

## CRM and appointments

| Method         | Path                                        | Operation                       |
| -------------- | ------------------------------------------- | ------------------------------- |
| GET            | `/api/v1/crm/contacts/requirements`         | Return required contact fields. |
| GET/POST       | `/api/v1/crm/contacts`                      | List/create contacts.           |
| GET/PUT/DELETE | `/api/v1/crm/contacts/{contact_id}`         | Read/update/delete contact.     |
| GET            | `/api/v1/crm/stats`                         | CRM aggregate statistics.       |
| GET/POST       | `/api/v1/crm/appointments`                  | List/create appointments.       |
| GET/PUT/DELETE | `/api/v1/crm/appointments/{appointment_id}` | Read/update/delete appointment. |

## Campaigns

| Method         | Path                                                                | Operation                           |
| -------------- | ------------------------------------------------------------------- | ----------------------------------- |
| GET/POST       | `/api/v1/campaigns`                                                 | List/create campaigns.              |
| GET/PUT/DELETE | `/api/v1/campaigns/{campaign_id}`                                   | Read/update/delete campaign.        |
| GET/POST       | `/api/v1/campaigns/{campaign_id}/contacts`                          | List/add explicit contacts.         |
| POST           | `/api/v1/campaigns/{campaign_id}/contacts/filter/preview`           | Preview filtered contact selection. |
| POST           | `/api/v1/campaigns/{campaign_id}/contacts/filter`                   | Add filtered contacts.              |
| DELETE         | `/api/v1/campaigns/{campaign_id}/contacts/{contact_id}`             | Remove campaign contact.            |
| POST           | `/api/v1/campaigns/{campaign_id}/start`                             | Start campaign.                     |
| POST           | `/api/v1/campaigns/{campaign_id}/pause`                             | Pause campaign.                     |
| POST           | `/api/v1/campaigns/{campaign_id}/stop`                              | Stop campaign.                      |
| POST           | `/api/v1/campaigns/{campaign_id}/restart`                           | Restart campaign.                   |
| GET            | `/api/v1/campaigns/{campaign_id}/stats`                             | Campaign statistics.                |
| GET            | `/api/v1/campaigns/{campaign_id}/dispositions`                      | Disposition aggregates.             |
| PUT            | `/api/v1/campaigns/{campaign_id}/contacts/{contact_id}/disposition` | Set business disposition.           |
| GET            | `/api/v1/campaigns/dispositions/options`                            | Enumerate disposition options.      |

## Call records and telephony

| Method         | Path                                                | Operation                            |
| -------------- | --------------------------------------------------- | ------------------------------------ |
| GET            | `/api/v1/calls`                                     | List calls.                          |
| GET            | `/api/v1/calls/analytics`                           | Call analytics.                      |
| GET            | `/api/v1/calls/{call_id}`                           | Call detail.                         |
| GET            | `/api/v1/calls/agent/{agent_id}/stats`              | Agent call stats.                    |
| POST           | `/api/v1/calls/export`                              | Export selected calls.               |
| POST           | `/api/v1/calls/analyze`                             | Analyze selected calls.              |
| GET            | `/api/v1/telephony/phone-numbers`                   | List provider numbers.               |
| POST           | `/api/v1/telephony/phone-numbers/search`            | Search purchasable numbers.          |
| POST           | `/api/v1/telephony/phone-numbers/purchase`          | Purchase number.                     |
| DELETE         | `/api/v1/telephony/phone-numbers/{phone_number_id}` | Release provider number.             |
| POST           | `/api/v1/telephony/calls`                           | Initiate call.                       |
| POST           | `/api/v1/telephony/calls/{call_id}/hangup`          | Hang up call.                        |
| GET/POST       | `/api/v1/phone-numbers`                             | List/create persisted number.        |
| GET/PUT/DELETE | `/api/v1/phone-numbers/{phone_number_id}`           | Read/update/delete persisted number. |

## Provider callbacks and media

| Method    | Path                              | Operation                   |
| --------- | --------------------------------- | --------------------------- |
| POST      | `/webhooks/twilio/voice`          | Twilio voice webhook.       |
| POST      | `/webhooks/twilio/status`         | Twilio status callback.     |
| POST      | `/webhooks/twilio/answer`         | Twilio answer instructions. |
| POST      | `/webhooks/telnyx/voice`          | Telnyx voice webhook.       |
| POST      | `/webhooks/telnyx/answer`         | Telnyx answer instructions. |
| POST      | `/webhooks/telnyx/status`         | Telnyx status callback.     |
| WebSocket | `/ws/telephony/twilio/{agent_id}` | Twilio media stream.        |
| WebSocket | `/ws/telephony/telnyx/{agent_id}` | Telnyx media stream.        |

## Browser and public voice

| Method    | Path                                       | Operation                     |
| --------- | ------------------------------------------ | ----------------------------- |
| WebSocket | `/ws/realtime/{agent_id}`                  | Authenticated realtime voice. |
| POST      | `/api/v1/realtime/session/{agent_id}`      | Create WebRTC session.        |
| GET       | `/api/v1/realtime/token/{agent_id}`        | Get ephemeral provider token. |
| POST      | `/api/v1/realtime/transcript/{agent_id}`   | Persist transcript.           |
| GET       | `/api/public/embed/{public_id}/config`     | Public widget config.         |
| POST      | `/api/public/embed/{public_id}/session`    | Create public embed session.  |
| WebSocket | `/ws/public/embed/{public_id}`             | Public embed voice stream.    |
| POST      | `/api/public/embed/{public_id}/token`      | Public ephemeral token.       |
| POST      | `/api/public/embed/{public_id}/tool-call`  | Execute embed tool call.      |
| POST      | `/api/public/embed/{public_id}/transcript` | Persist embed transcript.     |
| GET       | `/api/public/embed/{public_id}/history`    | Embed conversation history.   |

## Public chat, conversation ownership, knowledge, and usage

| Method     | Path                                                                    | Operation                             |
| ---------- | ----------------------------------------------------------------------- | ------------------------------------- |
| GET        | `/api/public/chat/{public_id}/config`                                   | Public chat config.                   |
| POST       | `/api/public/chat/{public_id}/message`                                  | Non-streaming message.                |
| POST       | `/api/public/chat/{public_id}/stream`                                   | SSE message stream.                   |
| GET        | `/api/public/chat/{public_id}/conversations/{conversation_id}/messages` | Public session conversation messages. |
| GET        | `/api/v1/conversations`                                                 | Owner conversation list.              |
| GET        | `/api/v1/conversations/analytics`                                       | Conversation analytics.               |
| GET        | `/api/v1/conversations/{conversation_id}`                               | Conversation detail.                  |
| POST       | `/api/v1/conversations/export`                                          | Export conversations.                 |
| POST       | `/api/v1/conversations/analyze`                                         | Analyze conversations.                |
| POST       | `/api/knowledge-bases`                                                  | Create knowledge base.                |
| GET/DELETE | `/api/knowledge-bases/{kb_id}`                                          | Read/delete knowledge base.           |
| GET        | `/api/knowledge-bases/agent/{agent_id}`                                 | List agent knowledge bases.           |
| POST       | `/api/knowledge-bases/{kb_id}/documents/text`                           | Ingest text.                          |
| POST       | `/api/knowledge-bases/{kb_id}/documents/url`                            | Ingest URL.                           |
| GET        | `/api/knowledge-bases/{kb_id}/documents`                                | List source chunks/documents.         |
| DELETE     | `/api/knowledge-bases/{kb_id}/documents/{source_id}`                    | Delete source chunks.                 |
| POST       | `/api/knowledge-bases/{kb_id}/search`                                   | Search one KB.                        |
| POST       | `/api/knowledge-bases/agent/{agent_id}/search`                          | Search agent knowledge.               |
| GET        | `/api/usage/tiers`                                                      | Billing tier definitions.             |
| GET        | `/api/usage/agent/{agent_id}/status`                                    | Current limit status.                 |
| GET        | `/api/usage/agent/{agent_id}/summary`                                   | Usage summary.                        |
| GET        | `/api/usage/agent/{agent_id}/daily`                                     | Daily usage series.                   |
| GET/PUT    | `/api/usage/agent/{agent_id}/billing`                                   | Read/update billing config.           |

## Integrations, OAuth, lessons, compliance, and diagnostics

| Method         | Path                                            | Operation                           |
| -------------- | ----------------------------------------------- | ----------------------------------- |
| GET/POST       | `/api/v1/integrations`                          | List/connect integration.           |
| GET/PUT/DELETE | `/api/v1/integrations/{integration_id}`         | Read/update/disconnect integration. |
| POST           | `/api/v1/oauth/chatgpt/connect`                 | Start OAuth.                        |
| GET            | `/api/v1/oauth/chatgpt/callback`                | OAuth callback.                     |
| GET            | `/api/v1/oauth/chatgpt/status`                  | Connection status.                  |
| POST           | `/api/v1/oauth/chatgpt/refresh`                 | Refresh connection.                 |
| DELETE         | `/api/v1/oauth/chatgpt/connection`              | Disconnect OAuth.                   |
| POST/GET       | `/api/v1/agents/{agent_id}/lessons`             | Create/list lessons.                |
| PATCH/DELETE   | `/api/v1/agents/{agent_id}/lessons/{lesson_id}` | Update/delete lesson.               |
| GET            | `/api/v1/agents/{agent_id}/lessons/export/csv`  | CSV export.                         |
| GET            | `/api/v1/agents/{agent_id}/lessons/export/json` | JSON export.                        |
| GET            | `/api/v1/compliance/status`                     | Compliance status.                  |
| GET/PATCH      | `/api/v1/compliance/privacy-settings`           | Read/update privacy settings.       |
| POST           | `/api/v1/compliance/consent`                    | Record consent.                     |
| GET            | `/api/v1/compliance/export`                     | Export user data.                   |
| POST           | `/api/v1/compliance/ccpa/opt-out`               | Opt out.                            |
| POST           | `/api/v1/compliance/ccpa/opt-in`                | Opt in.                             |
| POST           | `/api/v1/compliance/consent/withdraw`           | Withdraw consent.                   |
| DELETE         | `/api/v1/compliance/data`                       | Delete user data.                   |
| POST           | `/api/v1/compliance/retention/cleanup`          | Trigger retention cleanup.          |
| POST           | `/api/v1/tools/execute`                         | Execute allowlisted AI tool.        |
| GET            | `/health`, `/health/live`, `/health/ready`      | Aggregate/liveness/readiness.       |
| GET            | `/health/db`, `/health/redis`, `/health/cors`   | Dependency diagnostics.             |

## Governing paths

- `backend/app/main.py`
- `backend/app/api/*.py`
- `backend/app/schemas/*.py`
