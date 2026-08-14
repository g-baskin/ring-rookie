---
type: entity
title: "PUT /api/v1/agents/{agent_id}"
entity_type: endpoint
status: active
created: "2026-08-13"
updated: "2026-08-13"
path: "backend/app/api/agents.py"
language: python
last_commit_hash: "e5c4bbaf1606727b39ad6372c9e353ab99fc0d70"
depends_on:
  - "[[entities/agent]]"
  - "[[entities/update-agent-request]]"
used_by:
  - "[[entities/edit-agent-page]]"
tested_by:
  - "[[entities/test-agent-phone-assignment]]"
tags:
  - entity
  - endpoint
  - agent
  - telephony
  - authorization
related:
  - "[[concepts/agent-phone-number-assignment]]"
sources:
  - "backend/app/api/agents.py:295-354"
---

# PUT /api/v1/agents/{agent_id}

## Overview

The agent update endpoint owns authenticated changes to an agent, including assignment, unassignment, and reassignment of `phone_number_id` (`backend/app/api/agents.py:295-354`). Phone assignment is handled explicitly before generic field updates so that `null` remains meaningful and reassignment side effects are committed with the target update (`backend/app/api/agents.py:331-351`, `backend/app/api/agents.py:357-389`).

## Signature / Definition

```python
async def update_agent(
    agent_id: str,
    update_request: UpdateAgentRequest,
    request: Request,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> AgentResponse
```

## Authorization

- Loads the target only when both `Agent.id` equals the requested UUID and `Agent.user_id` equals the authenticated user's integer ID (`backend/app/api/agents.py:317-323`).
- Returns HTTP 404 when the target is missing or belongs to another user, preventing resource-existence disclosure and unauthorized mutation (`backend/app/api/agents.py:325-329`).
- Reassignment searches only other agents owned by the same authenticated user (`backend/app/api/agents.py:335-342`). It does not clear another user's assignment.

## Phone assignment behavior

1. Checks `update_request.model_fields_set` so omitted `phone_number_id` means “leave unchanged,” while explicit JSON `null` means “unassign” (`backend/app/api/agents.py:331-332`).
2. For a non-empty value, removes a leading `+` to construct equivalent stored forms (`backend/app/api/agents.py:333-340`).
3. Selects every other agent owned by the current user whose assignment matches either normalized form (`backend/app/api/agents.py:335-343`).
4. Clears each previous matching assignment (`backend/app/api/agents.py:344-345`).
5. Writes the requested value to the target agent; explicit `null` therefore clears the target (`backend/app/api/agents.py:346`).
6. Commits reassignment and target update together through the same SQLAlchemy session transaction, refreshes the target, and returns its current API representation (`backend/app/api/agents.py:348-354`).

## Why phone_number_id is excluded from generic updates

`_apply_agent_updates` only writes generic fields when their values are non-null (`backend/app/api/agents.py:357-389`). Keeping `phone_number_id` there would make explicit unassignment impossible. The endpoint instead handles the field before `_apply_agent_updates`, preserving the three distinct states: omitted, concrete value, and explicit null (`backend/app/api/agents.py:331-349`).

## Response and failure semantics

- Success returns `AgentResponse` after commit and refresh (`backend/app/api/agents.py:351-354`).
- Missing or unauthorized agent returns 404 (`backend/app/api/agents.py:325-329`).
- Invalid UUID syntax is converted by `uuid.UUID(agent_id)` during lookup and follows FastAPI's error handling path (`backend/app/api/agents.py:317-321`).
- Database failures prevent commit; no separate provider API call is made by this endpoint (`backend/app/api/agents.py:331-354`).

## Connections

- **Consumes:** [[entities/update-agent-request]].
- **Mutates:** [[entities/agent]].
- **Used by:** [[entities/edit-agent-page]] through the frontend `updateAgent` mutation (`frontend/src/app/dashboard/agents/[id]/page.tsx:588-618`).
- **Feeds:** [[entities/get-agent-by-phone-number]] because inbound lookup reads `Agent.phone_number_id` (`backend/app/api/telephony.py:165-172`).
- **Related concept:** [[concepts/agent-phone-number-assignment]].

## Tested by

[[entities/test-agent-phone-assignment]] proves:

- assignment persists and is returned (`backend/tests/test_api/test_agent_phone_assignment.py:35-53`);
- explicit null unassigns (`backend/tests/test_api/test_agent_phone_assignment.py:56-72`);
- reassignment clears a previous no-plus assignment and stores the plus-prefixed request (`backend/tests/test_api/test_agent_phone_assignment.py:75-95`);
- another user's agent returns 404 and remains unchanged (`backend/tests/test_api/test_agent_phone_assignment.py:98-121`).

## History

- The working-tree phone-assignment contract is uncommitted; `last_commit_hash` records the last committed baseline of `backend/app/api/agents.py`.
- **Baseline commit:** `e5c4bbaf1606727b39ad6372c9e353ab99fc0d70` by Greg on 2026-08-13.

## Sources

- `backend/app/api/agents.py:295-354`
- `backend/app/api/agents.py:357-389`
- `frontend/src/app/dashboard/agents/[id]/page.tsx:588-618`
- `backend/tests/test_api/test_agent_phone_assignment.py:35-121`
