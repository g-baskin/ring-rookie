# Tribunal Feature Gap Discovery and Roadmap

> **Status:** Draft, discovery-gated  
> **Last verified:** 2026-08-13

This document preserves product patterns observed in [The Tribunal](https://github.com/Gahroot/the-tribunal) that Ring Rookie may independently implement. The Tribunal is proprietary (`LicenseRef-Proprietary`); borrow product ideas and general workflows only—never copy code, tests, configuration, copy, assets, or trade dress.

## Executive decision

Start with a **Unified Revenue Inbox / Today Queue** discovery cycle. Ring Rookie already contains the records needed for a manual experiment, but work is fragmented across calls, conversations, appointments, campaigns, CRM contacts, and compliance surfaces. Do not build queue infrastructure until operators demonstrate repeat use and measurable workflow improvement.

## Ring Rookie baseline

| Capability | Local evidence |
|---|---|
| Voice agents and phone numbers | `backend/app/models/agent.py`, `backend/app/models/phone_number.py`, `frontend/src/app/dashboard/agents/page.tsx`, `frontend/src/app/dashboard/phone-numbers/page.tsx` |
| Calls and transcripts | `backend/app/models/call_record.py`, `backend/app/models/call_interaction.py`, `backend/app/api/calls.py`, `frontend/src/app/dashboard/calls/page.tsx` |
| Contacts and CRM | `backend/app/models/contact.py`, `backend/app/api/crm.py`, `frontend/src/app/dashboard/crm/page.tsx` |
| Conversations | `backend/app/models/conversation.py`, `backend/app/api/conversations.py`, `frontend/src/app/dashboard/conversations/page.tsx` |
| Campaigns | `backend/app/models/campaign.py`, `backend/app/api/campaigns.py`, `frontend/src/app/dashboard/campaigns/page.tsx` |
| Appointments | `backend/app/models/appointment.py`, `frontend/src/app/dashboard/appointments/page.tsx` |
| Knowledge and RAG | `backend/app/models/knowledge_base.py`, `backend/app/api/knowledge_base.py` |
| Integrations and tools | `backend/app/models/user_integration.py`, `backend/app/api/integrations.py`, `backend/app/api/tools.py`, `frontend/src/app/dashboard/integrations/page.tsx` |
| Compliance and consent | `backend/app/models/privacy_settings.py`, `backend/app/api/compliance.py` |
| Usage and workspaces | `backend/app/models/usage.py`, `backend/app/models/workspace.py`, `backend/app/api/usage.py`, `backend/app/api/workspaces.py` |

## Feature opportunities preserved

Scores are directional inputs from 1–5; risk 5 is worst.

| Priority | Opportunity | Pattern references | Reach | Impact | Confidence | Risk | Status |
|---:|---|---|---:|---:|---:|---:|---|
| 1 | Unified Revenue Inbox / Today Queue | Close, Front, Chatwoot, Tribunal | 5 | 5 | 3 | 3 | Active discovery; see PRD-003 |
| 2 | Evidence-backed AI next-best actions | Gong, HubSpot Breeze, Agentforce, Intercom Fin | 4 | 5 | 2 | 4 | Deferred pending queue evidence |
| 3 | General tasks, ownership, and team queues | Salesforce, Close, Salesloft | 5 | 4 | 3 | 3 | Deferred |
| 4 | Account/company relationship graph | Attio, HubSpot, Twenty | 4 | 4 | 3 | 4 | Deferred |
| 5 | Consent and deliverability control center | Outreach, Salesloft, Telnyx/Twilio guidance | 4 | 5 | 4 | 4 | Deferred; compliance review required |
| 6 | Connector foundation and governed marketplace | Zapier, n8n, Activepieces | 3 | 4 | 3 | 4 | Deferred |
| 7 | Shared support inbox and ticket lifecycle | Front, Intercom, Chatwoot | 2 | 3 | 2 | 3 | Deferred pending segment evidence |
| 8 | Durable visual workflow engine | n8n, Inngest, Trigger.dev, Windmill | 3 | 4 | 3 | 4 | Deferred |
| 9 | Custom fields, objects, and saved views | Attio, Salesforce, Twenty | 4 | 4 | 2 | 4 | Deferred |
| 10 | Revenue intelligence and forecasting | Gong, HubSpot, Salesforce | 3 | 5 | 2 | 4 | Deferred until activity data matures |

## Phased roadmap

1. **Discovery:** run the PRD-003 concierge and shadow-mode study without product code.
2. **Validated work surface:** if the gate passes, add only the item types, evidence, dispositions, and ownership proven useful.
3. **Trusted assistance:** introduce evidence-backed recommendations in shadow mode before consequential actions.
4. **Data and execution foundations:** separately validate tasks, Accounts, consent, connectors, workflows, and extensibility.
5. **Expansion:** consider forecasting and support only after the earlier data and segment assumptions hold.

## God sequence

1. `discovery-research-guardian` + `discovery-research-weapon` executes the prepared study.
2. `library-guardian` + `library-weapon` revises PRD-003 only after a recorded pass decision.
3. `db-guardian`, `python-guardian`, `react-guardian`, and `ux-ui-guardian` plan validated delivery boundaries.
4. `security-guardian` + `security-weapon` reviews workspace isolation, PII, consent, and action authorization.
5. `quality-guardian` + `quality-weapon` verifies implementation against the validated PRD.

## Resume checkpoint

Read [`library/discovery/README.md`](../../../discovery/README.md), assign a discovery owner, confirm the provisional operator segment, and begin recruitment. All opportunities other than the Unified Revenue Inbox remain preserved in this document and require separate discovery before implementation.
