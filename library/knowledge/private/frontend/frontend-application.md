# Frontend application narrative

**Last verified:** 2026-08-13

## Shell and providers

The frontend is a Next.js App Router application using React 19, TypeScript, Tailwind, shadcn-style primitives, TanStack Query, Zustand, and Framer Motion. The client root directly configures auth state, TanStack Query caching, error handling, a preloader, and toast notifications. The dashboard layout renders a persistent sidebar/top bar around a scrollable route body; responsive navigation owns its own Zustand state. Workspace selection is handled within workspace, agent, phone, integration, and settings screens rather than a global workspace provider.

Authentication is client-managed by `frontend/src/hooks/use-auth.tsx`: it reads `access_token` from `localStorage`, validates it through `/api/v1/auth/me`, redirects unauthenticated private routes to `/login`, and permits `/embed/*` without auth. This means initial authorization is not enforced by Next.js middleware; backend authorization remains mandatory.

## Route inventory

| Route                                                  | Behavior                                                                                                |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| `/`, `/login`, `/register`                             | Entry and account flows.                                                                                |
| `/dashboard`                                           | Overview and aggregate product status.                                                                  |
| `/dashboard/agents`                                    | Agent list; creation routes exist at `/new` and `/create-agent`; detail supports editing/configuration. |
| `/dashboard/agents/[id]/transcripts`                   | Agent-scoped transcript view.                                                                           |
| `/dashboard/workspaces`                                | Workspace creation, selection, and management.                                                          |
| `/dashboard/crm`                                       | Contacts and CRM statistics.                                                                            |
| `/dashboard/appointments`                              | Appointment management.                                                                                 |
| `/dashboard/campaigns`                                 | Outbound campaign management.                                                                           |
| `/dashboard/integrations`                              | Integration catalog and credential connection.                                                          |
| `/dashboard/phone-numbers`                             | Number inventory and assignment.                                                                        |
| `/dashboard/calls`, `/calls/[id]`, `/calls/analytics`  | Call history, detail/transcript, and analytics.                                                         |
| `/dashboard/conversations`, `/conversations/analytics` | Chat Champ history and analytics.                                                                       |
| `/dashboard/test`                                      | Authenticated browser voice test.                                                                       |
| `/dashboard/settings`                                  | Workspace/provider credentials and preferences.                                                         |
| `/embed/[publicId]`, `/preview`                        | Public voice widget and owner preview.                                                                  |

## State and data boundaries

- **Auth context:** current user, bearer token, login/register/logout, redirect state.
- **Workspace screen/query state:** workspace lists and per-screen selected workspace IDs drive workspace-aware requests.
- **TanStack Query:** server state, fetching, invalidation, and mutation lifecycle.
- **Zustand sidebar store:** presentation state only.
- **Domain API modules:** agents, calls, campaigns, conversations, CRM, integrations, workspaces, settings, telephony, and compliance.

Components should not embed alternate backend prefixes. The actual API has historical prefix variation, so each domain client is the contract adapter.

## Agent configuration flow

The agent editor maps user configuration onto the `Agent` API model: identity, description, pricing tier/provider profile, system prompt and target length, language/voice, initial greeting, temperature/token cap, turn-detection values, tool/integration selection, recording/transcription, status, inbound phone assignment, and embed settings. Agent workspace membership is handled through workspace endpoints rather than a single agent field.

Under **Advanced**, the phone selector queries live provider inventory with the active provider and either the first selected workspace or account-level credential scope. It uses the actual phone-number string as the form value, labels numbers assigned to another agent, and converts the local `none` sentinel to explicit API `null`. Assignment therefore moves a number from another owned agent, while selecting no number disables inbound routing. See [Agent phone-number assignment](../voice/agent-phone-number-assignment.md) for the complete contract.

## Realtime UI

The voice tester and embed components manage microphone permission, connection state, audio visualization, transcripts, tool events, and cleanup. Depending on the path, the browser uses backend WebSocket proxying or WebRTC ephemeral-session/token APIs. Public embed flows send origin-sensitive requests and use public IDs rather than owner JWTs.

## Design-system layer

Reusable primitives are under `frontend/src/components/ui/`; product components compose them. `app-sidebar.tsx` is the canonical visible navigation list. Theme CSS and token definitions live in `frontend/src/app/globals.css`. Motion is primarily Framer Motion and should respect interaction state rather than own business state.

## Known UX/architecture edges

- Both `/agents/new` and `/agents/create-agent` exist; maintainers should designate one canonical creation route.
- Sidebar active matching is prefix-based. More specific analytics/detail links can overlap parent routes, so active-state behavior should be tested when navigation changes.
- Token-in-localStorage simplifies SPA auth but increases the impact of XSS; this is current behavior, not an endorsement.
- Public embed routes intentionally bypass dashboard redirects and must not import owner-only assumptions.

## Governing paths

- `frontend/src/app/`
- `frontend/src/components/app-sidebar.tsx`
- `frontend/src/app/layout.tsx`
- `frontend/src/hooks/use-auth.tsx`
- `frontend/src/lib/api.ts`
- `frontend/src/lib/realtime-webrtc.ts`
- `frontend/src/app/dashboard/agents/[id]/page.tsx`
- `frontend/src/app/dashboard/test/page.tsx`
- `frontend/src/app/embed/[publicId]/page.tsx`
