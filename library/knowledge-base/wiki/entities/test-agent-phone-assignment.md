---
type: entity
title: "test_agent_phone_assignment"
entity_type: module
status: stub
created: "2026-08-13"
updated: "2026-08-13"
path: "backend/tests/test_api/test_agent_phone_assignment.py"
language: python
source_extension: ".py"
last_commit_hash: ""
depends_on:
  - "[[entities/update-agent-api]]"
  - "[[entities/get-agent-by-phone-number]]"
used_by: []
tags:
  - entity
  - stub
  - test
  - telephony
related:
  - "[[concepts/agent-phone-number-assignment]]"
sources:
  - "backend/tests/test_api/test_agent_phone_assignment.py:1-139"
---

# test_agent_phone_assignment

> [!gap]
> This Python file is outside wiki-guardian v1's ts-morph extraction scope. This module-level stub preserves coverage; the detailed test inventory below is manually cited from the source but does not claim callable-entity extraction.

## Purpose

The module provides focused integration coverage for agent phone assignment and inbound lookup (`backend/tests/test_api/test_agent_phone_assignment.py:1-139`). It uses authenticated HTTP requests for the update endpoint and direct async database reads to prove persisted state (`backend/tests/test_api/test_agent_phone_assignment.py:28-32`, `backend/tests/test_api/test_agent_phone_assignment.py:35-121`).

## Covered contracts

| Test                                                   | Contract proved                                                                               | Evidence                                                        |
| ------------------------------------------------------ | --------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| `test_assigns_phone_number_to_agent`                   | A concrete phone number returns 200, appears in the response, and persists.                   | `backend/tests/test_api/test_agent_phone_assignment.py:35-53`   |
| `test_unassigns_phone_number_from_agent`               | Explicit JSON `null` returns 200 and clears the persisted assignment.                         | `backend/tests/test_api/test_agent_phone_assignment.py:56-72`   |
| `test_reassignment_removes_number_from_previous_agent` | Assigning a number to a new agent clears an equivalent no-plus value from the previous agent. | `backend/tests/test_api/test_agent_phone_assignment.py:75-95`   |
| `test_cannot_assign_number_to_another_users_agent`     | Cross-owner mutation returns 404 and does not alter the other user's agent.                   | `backend/tests/test_api/test_agent_phone_assignment.py:98-121`  |
| `test_inbound_lookup_normalizes_optional_plus_prefix`  | Both plus-prefixed and unprefixed inbound inputs resolve the same agent.                      | `backend/tests/test_api/test_agent_phone_assignment.py:124-139` |

## Test fixtures and helpers

- `PHONE_NUMBER` fixes the test value at `+15551234567` (`backend/tests/test_api/test_agent_phone_assignment.py:15`).
- `make_agent` constructs minimal valid agent rows with optional phone assignment (`backend/tests/test_api/test_agent_phone_assignment.py:18-25`).
- `get_saved_agent` opens a fresh async session so assertions prove committed state rather than identity-map state (`backend/tests/test_api/test_agent_phone_assignment.py:28-32`).

## Verification record

The focused command `uv --directory backend run pytest tests/test_api/test_agent_phone_assignment.py tests/test_api/test_telephony_phone_numbers.py -q` completed with `9 passed` on 2026-08-13. This execution fact is session evidence; the source assertions remain the durable contract.

## Connections

- **Tests:** [[entities/update-agent-api]].
- **Tests:** [[entities/get-agent-by-phone-number]].
- **Documents:** [[concepts/agent-phone-number-assignment]].

## History

- This test module is new and uncommitted, so no truthful `last_commit_hash` exists yet.

## Source

- `backend/tests/test_api/test_agent_phone_assignment.py:1-139`
