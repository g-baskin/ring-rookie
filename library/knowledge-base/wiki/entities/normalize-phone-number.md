---
type: entity
title: "_normalize_phone_number"
entity_type: function
status: active
created: "2026-08-13"
updated: "2026-08-13"
path: "backend/app/api/telephony.py"
language: python
last_commit_hash: "e5c4bbaf1606727b39ad6372c9e353ab99fc0d70"
depends_on: []
used_by:
  - "[[entities/get-agent-by-phone-number]]"
  - "[[entities/list-phone-numbers-api]]"
tested_by:
  - "[[entities/test-agent-phone-assignment]]"
tags:
  - entity
  - function
  - telephony
  - normalization
related:
  - "[[concepts/agent-phone-number-assignment]]"
sources:
  - "backend/app/api/telephony.py:160-162"
---

# _normalize_phone_number

## Overview

`_normalize_phone_number` creates the canonical comparison key used when phone numbers may be stored or received with an optional leading `+` (`backend/app/api/telephony.py:160-162`). It intentionally performs a narrow normalization rather than rewriting formatting, country codes, punctuation, or national-number semantics.

## Signature / Definition

```python
def _normalize_phone_number(phone_number: str) -> str
```

## Behavior

- Accepts a string and removes every leading `+` character through `str.lstrip("+")` (`backend/app/api/telephony.py:160-162`).
- Leaves all non-leading-plus content unchanged; the function does not strip whitespace, punctuation, extensions, or international dialing prefixes (`backend/app/api/telephony.py:160-162`).
- Supplies a stable lookup key for both inbound routing and provider-number assignment metadata (`backend/app/api/telephony.py:165-172`, `backend/app/api/telephony.py:351-364`).

## Connections

- **Used by:** [[entities/get-agent-by-phone-number]] to compare inbound numbers against both stored forms (`backend/app/api/telephony.py:165-172`).
- **Used by:** [[entities/list-phone-numbers-api]] to join live provider inventory to agent assignments (`backend/app/api/telephony.py:345-365`).
- **Related concept:** [[concepts/agent-phone-number-assignment]].

## Tested by

- [[entities/test-agent-phone-assignment]] exercises inbound lookup with `+15551234567` and `15551234567` (`backend/tests/test_api/test_agent_phone_assignment.py:124-139`).

## Operational boundary

This helper is assignment normalization, not full E.164 validation. Callers must not assume it corrects malformed phone numbers; it only makes the optional leading plus sign comparison-insensitive (`backend/app/api/telephony.py:160-162`).

## History

- The working-tree implementation is not yet represented by a commit; `last_commit_hash` identifies the most recent committed baseline for the source file.
- **Baseline commit:** `e5c4bbaf1606727b39ad6372c9e353ab99fc0d70` by Greg on 2026-08-13 — “Add prompt target interaction coverage.”

## Sources

- `backend/app/api/telephony.py:160-172`
- `backend/app/api/telephony.py:345-365`
- `backend/tests/test_api/test_agent_phone_assignment.py:124-139`
