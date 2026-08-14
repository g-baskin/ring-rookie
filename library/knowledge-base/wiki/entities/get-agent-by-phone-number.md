---
type: entity
title: "get_agent_by_phone_number"
entity_type: function
status: active
created: "2026-08-13"
updated: "2026-08-13"
path: "backend/app/api/telephony.py"
language: python
last_commit_hash: "e5c4bbaf1606727b39ad6372c9e353ab99fc0d70"
depends_on:
  - "[[entities/normalize-phone-number]]"
  - "[[entities/agent]]"
used_by: []
tested_by:
  - "[[entities/test-agent-phone-assignment]]"
tags:
  - entity
  - function
  - telephony
  - inbound-routing
related:
  - "[[concepts/agent-phone-number-assignment]]"
sources:
  - "backend/app/api/telephony.py:165-172"
---

# get_agent_by_phone_number

## Overview

`get_agent_by_phone_number` resolves an inbound telephone destination to the assigned `Agent` by matching the agent's `phone_number_id` with or without a leading plus sign (`backend/app/api/telephony.py:165-172`). It is the routing-side consumer of the assignment written through the agent update API.

## Signature / Definition

```python
async def get_agent_by_phone_number(
    phone_number: str,
    db: AsyncSession,
) -> Agent | None
```

## Behavior

1. Converts the incoming number to a plus-insensitive comparison key using [[entities/normalize-phone-number]] (`backend/app/api/telephony.py:165-167`).
2. Queries `Agent.phone_number_id` for either the normalized form or the same form prefixed with `+` (`backend/app/api/telephony.py:169-171`).
3. Returns the single matching `Agent`, or `None` when no assignment exists (`backend/app/api/telephony.py:172`).
4. Uses `scalar_one_or_none()`, so duplicate matching assignments are an invalid data state and can raise rather than silently selecting an arbitrary agent (`backend/app/api/telephony.py:172`).

## Assignment invariant

The agent update path clears matching assignments from other agents owned by the same user before storing a new assignment (`backend/app/api/agents.py:331-346`). That behavior is what normally preserves the single-result expectation used here. The lookup itself is not scoped by user because an inbound phone number must identify the agent without an authenticated owner context (`backend/app/api/telephony.py:165-172`).

## Connections

- **Depends on:** [[entities/normalize-phone-number]] (`backend/app/api/telephony.py:167`).
- **Reads:** [[entities/agent]] through `Agent.phone_number_id` (`backend/app/api/telephony.py:169-171`).
- **Contract producer:** [[entities/update-agent-api]] stores or clears the assignment (`backend/app/api/agents.py:331-346`).
- **Related concept:** [[concepts/agent-phone-number-assignment]].

## Tested by

- [[entities/test-agent-phone-assignment]] parametrically proves that both `+15551234567` and `15551234567` resolve the same assigned agent (`backend/tests/test_api/test_agent_phone_assignment.py:124-139`).

## Failure semantics

- No assignment returns `None` (`backend/app/api/telephony.py:172`).
- Multiple equivalent assignments violate `scalar_one_or_none()`'s cardinality expectation; reassignment logic and operational data hygiene must prevent that state (`backend/app/api/agents.py:331-346`, `backend/app/api/telephony.py:172`).

## History

- The working-tree contract adds optional-plus normalization; `last_commit_hash` records the last committed baseline because the current change is uncommitted.
- **Baseline commit:** `e5c4bbaf1606727b39ad6372c9e353ab99fc0d70` by Greg on 2026-08-13.

## Sources

- `backend/app/api/telephony.py:160-172`
- `backend/app/api/agents.py:331-346`
- `backend/tests/test_api/test_agent_phone_assignment.py:124-139`
