---
type: entity
title: "GET /api/v1/telephony/phone-numbers"
entity_type: endpoint
status: active
created: "2026-08-13"
updated: "2026-08-13"
path: "backend/app/api/telephony.py"
language: python
last_commit_hash: "e5c4bbaf1606727b39ad6372c9e353ab99fc0d70"
depends_on:
  - "[[entities/normalize-phone-number]]"
  - "[[entities/agent]]"
used_by:
  - "[[entities/edit-agent-page]]"
tested_by:
  - "[[entities/test-telephony-phone-numbers]]"
tags:
  - entity
  - endpoint
  - telephony
  - provider-inventory
  - assignment
related:
  - "[[concepts/agent-phone-number-assignment]]"
sources:
  - "backend/app/api/telephony.py:302-367"
---

# GET /api/v1/telephony/phone-numbers

## Overview

This authenticated endpoint lists phone numbers directly from the selected Twilio or Telnyx provider account and enriches each result with the ID of the current user's assigned agent (`backend/app/api/telephony.py:302-367`). It is the server-state source for the **Agents → Advanced** phone-number selector.

## Contract

```http
GET /api/v1/telephony/phone-numbers
    ?provider=twilio|telnyx
    [&workspace_id=<uuid>]
Authorization: Bearer <token>
```

- `provider` defaults to `twilio` and accepts `twilio` or `telnyx` (`backend/app/api/telephony.py:303-310`, `backend/app/api/telephony.py:328-343`).
- `workspace_id` is optional; omission uses account-level credentials, while a supplied UUID selects workspace credentials (`backend/app/api/telephony.py:307-315`).
- Each response includes provider ID, phone number, friendly name, provider, capabilities, and `assigned_agent_id` (`backend/app/api/telephony.py:357-365`).

## Behavior

1. Binds user, provider, and workspace identifiers to structured logs (`backend/app/api/telephony.py:316-317`).
2. Parses an optional workspace UUID and returns HTTP 400 for malformed values (`backend/app/api/telephony.py:319-324`).
3. Resolves provider credentials at account or workspace scope (`backend/app/api/telephony.py:328-340`).
4. Returns an empty list when the selected provider has no configured credentials; missing configuration is a UI state, not an API error (`backend/app/api/telephony.py:328-340`).
5. Returns HTTP 400 for an unsupported provider (`backend/app/api/telephony.py:342-343`).
6. Reads non-null assignments only from agents owned by the authenticated user (`backend/app/api/telephony.py:345-350`).
7. Builds a plus-insensitive assignment map using [[entities/normalize-phone-number]] (`backend/app/api/telephony.py:351-355`).
8. Enriches every live provider number with the matching assigned agent ID or `null` (`backend/app/api/telephony.py:357-367`).

## Security and tenancy

- Provider credential selection is based on the authenticated user and optional workspace (`backend/app/api/telephony.py:303-315`, `backend/app/api/telephony.py:328-340`).
- Assignment metadata is filtered by `Agent.user_id == current_user.id`, so the response does not disclose assignments belonging to other users (`backend/app/api/telephony.py:345-350`).
- The endpoint reads live provider inventory; it is distinct from persisted `/api/v1/phone-numbers` CRUD (`backend/app/api/telephony.py:311-315`).

## Connections

- **Used by:** [[entities/edit-agent-page]] with a TanStack Query key containing workspace and provider (`frontend/src/app/dashboard/agents/[id]/page.tsx:423-447`).
- **Depends on:** [[entities/normalize-phone-number]] for assignment joins (`backend/app/api/telephony.py:351-364`).
- **Related concept:** [[concepts/agent-phone-number-assignment]].

## Tested by

[[entities/test-telephony-phone-numbers]] verifies account-level and workspace-level credential resolution and response mapping. Its mocks explicitly supply the assignment-query result required by enrichment (`backend/tests/test_api/test_telephony_phone_numbers.py`).

## Operational caveats

- An empty response can mean no credentials or no provider numbers; the current contract does not distinguish those cases (`backend/app/api/telephony.py:328-340`).
- Provider inventory is fetched live, so latency and provider availability affect selector loading (`backend/app/api/telephony.py:328-340`).
- Assignment matching only ignores a leading plus sign; inconsistent punctuation or whitespace is not normalized (`backend/app/api/telephony.py:351-364`).

## History

- The assignment-enrichment working-tree change is uncommitted; `last_commit_hash` records the source file's committed baseline.
- **Baseline commit:** `e5c4bbaf1606727b39ad6372c9e353ab99fc0d70` by Greg on 2026-08-13.

## Sources

- `backend/app/api/telephony.py:302-367`
- `frontend/src/app/dashboard/agents/[id]/page.tsx:423-447`
- `backend/tests/test_api/test_telephony_phone_numbers.py`
