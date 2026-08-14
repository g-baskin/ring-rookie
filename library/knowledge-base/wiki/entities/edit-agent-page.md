---
type: entity
title: "EditAgentPage"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
entity_type: react-component
path: "frontend/src/app/dashboard/agents/[id]/page.tsx"
language: tsx
last_commit_hash: "e5c4bbaf1606727b39ad6372c9e353ab99fc0d70"
depends_on:
  - "[[entities/list-provider-phone-numbers-endpoint]]"
  - "[[entities/update-agent]]"
used_by: []
tested_by: []
props_summary: ""
tags:
  - entity
  - react-component
related:
  - "[[entities/page-agents-id]]"
  - "[[concepts/agent-phone-number-assignment]]"
sources: []
---

# EditAgentPage

## Overview

Exported react component declared by the [[entities/page-agents-id]] module at `frontend/src/app/dashboard/agents/[id]/page.tsx:244`.

## Signature / Definition

```tsx
export default function EditAgentPage(
```

## Behavior

The component owns the multi-tab agent editor, including the **Advanced** telephony controls (`frontend/src/app/dashboard/agents/[id]/page.tsx:244`, `frontend/src/app/dashboard/agents/[id]/page.tsx:1629-1697`).

### Phone-number server state

- Watches the selected workspace list and telephony provider (`frontend/src/app/dashboard/agents/[id]/page.tsx:423-425`).
- Queries live provider numbers with a key containing the first selected workspace or `null`, plus the provider; this keeps caches distinct across credential scopes (`frontend/src/app/dashboard/agents/[id]/page.tsx:427-447`).
- Includes `workspace_id` only when a workspace is selected, allowing account-level numbers to load without requiring workspace membership (`frontend/src/app/dashboard/agents/[id]/page.tsx:430-443`).
- Enables the query once the agent exists and deletion is not underway (`frontend/src/app/dashboard/agents/[id]/page.tsx:446`).

### Phone-number interaction

- Shows a purchase CTA when loading is complete and no provider numbers are available (`frontend/src/app/dashboard/agents/[id]/page.tsx:1629-1650`).
- Uses the actual provider phone-number string as both item value and React key, not the provider record ID (`frontend/src/app/dashboard/agents/[id]/page.tsx:1667-1674`).
- Includes a sentinel `none` item that means inbound calling is disabled (`frontend/src/app/dashboard/agents/[id]/page.tsx:1663-1666`).
- Labels numbers assigned to another agent while still allowing selection; the explanatory copy states that assignment moves the number (`frontend/src/app/dashboard/agents/[id]/page.tsx:1671-1681`).
- Converts empty or sentinel form values to JSON `null` so the backend can distinguish unassignment from omission (`frontend/src/app/dashboard/agents/[id]/page.tsx:588-601`).

## Connections

- **Defined by:** [[entities/page-agents-id]] (`frontend/src/app/dashboard/agents/[id]/page.tsx:244`).
- **Reads:** [[entities/list-provider-phone-numbers-endpoint]] (`frontend/src/app/dashboard/agents/[id]/page.tsx:427-447`).
- **Writes through:** [[entities/update-agent]] (`frontend/src/app/dashboard/agents/[id]/page.tsx:588-618`).
- **Implements:** [[concepts/agent-phone-number-assignment]].

## Tested by

Backend contract coverage is captured by [[entities/test-agent-phone-assignment]]. Rendered verification for the Advanced selector is stored at `.gg/screenshots/phone-assignment-advanced-populated.png`; this screenshot is evidence, not an automated frontend regression test.

## History

- The working-tree phone selector enhancement is uncommitted; `last_commit_hash` remains the committed baseline.
- **Last committed baseline:** `e5c4bbaf1606727b39ad6372c9e353ab99fc0d70` by Greg on 2026-08-13.
- **Commit subject:** Add prompt target interaction coverage.

## Sources

- `frontend/src/app/dashboard/agents/[id]/page.tsx:244`
- `frontend/src/app/dashboard/agents/[id]/page.tsx:423-447`
- `frontend/src/app/dashboard/agents/[id]/page.tsx:573-618`
- `frontend/src/app/dashboard/agents/[id]/page.tsx:1629-1697`
