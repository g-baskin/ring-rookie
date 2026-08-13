# Ring Rookie Library

This directory is the canonical narrative and requirements record for Ring Rookie. It follows library schema v2.

## Map

- [`knowledge/public/`](knowledge/public/) — customer- and operator-facing explanations.
- [`knowledge/private/`](knowledge/private/) — engineering architecture, data, API, integration, security, and operational narratives.
- [`requirements/backlog/`](requirements/backlog/) — queued product requirements.
- [`requirements/in-work/`](requirements/in-work/) — requirements currently being implemented.
- [`requirements/completed/`](requirements/completed/) — shipped requirements and backwards-PRDs.
- [`issues/`](issues/) — issue requirements whose numbers correspond to GitHub issues.
- `notes/` — human-only working notes; agents must not modify it.

## Source-of-truth rule

Code and migrations define runtime behavior. These documents explain that behavior and cite the governing paths. If documentation and implementation disagree, verify the implementation, update the narrative, and record the discrepancy in the documentation drift audit.

## Core reading path

1. [System overview](knowledge/public/overview/system-overview.md)
2. [System architecture](knowledge/private/architecture/system-architecture.md)
3. [Backend architecture](knowledge/private/backend/backend-architecture.md)
4. [Frontend application](knowledge/private/frontend/frontend-application.md)
5. [Data model](knowledge/private/data/data-model.md)
6. [API surface](knowledge/private/api/api-surface.md)
7. [Voice and telephony flows](knowledge/private/voice/voice-and-telephony.md)
8. [CRM, campaigns, and analytics](knowledge/private/domains/crm-campaigns-and-analytics.md)
9. [Chat Champ and RAG](knowledge/private/ai/chat-champ-and-rag.md)
10. [Integrations and tools](knowledge/private/integrations/tool-runtime.md)
11. [Local operations](knowledge/private/operations/local-runtime.md)
12. [Documentation inventory and drift audit](knowledge/private/standards/documentation-inventory.md)

## Maintenance

Narrative docs should include code-path references and a `Last verified` date. Product lifecycle is represented by folder location, not frontmatter alone. QA findings are authored by `quality-guardian`; this library only reserves the conventional `qa/` locations.
