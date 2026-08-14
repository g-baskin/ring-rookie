# Agent phone-number assignment

> Category: Internal feature reference | Version: 1.0 | Date: August 2026 | Status: Active

This document defines the implemented contract for assigning an inbound Twilio or Telnyx number under **Agents → Advanced**, including UI behavior, API semantics, ownership boundaries, reassignment, inbound lookup, and verification evidence.

**Related:**

- [Voice, realtime, and telephony flows](voice-and-telephony.md)
- [Frontend application narrative](../frontend/frontend-application.md)
- [API and transport surface](../api/api-surface.md)
- [Atomic wiki concept](../../../knowledge-base/wiki/concepts/agent-phone-number-assignment.md)

**Last verified:** 2026-08-13

## Scope

This feature connects four existing system surfaces:

1. The agent editor fetches live provider inventory and presents it under **Advanced**.
2. The authenticated agent update endpoint persists assignment or unassignment.
3. Reassignment clears an equivalent number from another agent owned by the same user.
4. Inbound telephony resolves the stored assignment with optional-leading-plus normalization.

The feature does **not** purchase numbers, configure provider credentials, validate full E.164 syntax, or make provider-side webhook changes. Number purchase and management remain under `/dashboard/phone-numbers`; credentials remain account- or workspace-scoped provider settings.

## User experience

### Location

Navigate to **Voice Agents**, open an existing agent, and select the **Advanced** tab. The field is labeled **Phone Number for Inbound Calls** (`frontend/src/app/dashboard/agents/[id]/page.tsx:1629-1635`).

### Provider and credential scope

The editor watches `telephonyProvider` and the agent's selected workspaces (`frontend/src/app/dashboard/agents/[id]/page.tsx:423-425`). It loads numbers from:

- the first selected workspace when one exists; or
- account-level provider credentials when no workspace is selected.

The query includes `provider` always and adds `workspace_id` conditionally (`frontend/src/app/dashboard/agents/[id]/page.tsx:427-444`). This permits phone assignment before workspace membership exists, provided account-level provider credentials are configured.

### Selector states

| State                     | UI behavior                                                                               | Source                                                      |
| ------------------------- | ----------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Loading                   | Number selector is disabled while the query resolves.                                     | `frontend/src/app/dashboard/agents/[id]/page.tsx:1653-1657` |
| No provider numbers       | Dashed empty state says no numbers are available and links to **Purchase Phone Numbers**. | `frontend/src/app/dashboard/agents/[id]/page.tsx:1635-1650` |
| Inventory available       | Selector includes an explicit no-number option followed by live provider numbers.         | `frontend/src/app/dashboard/agents/[id]/page.tsx:1652-1677` |
| Friendly name available   | Item renders `<number> (<friendly name>)`.                                                | `frontend/src/app/dashboard/agents/[id]/page.tsx:1667-1670` |
| Assigned to another agent | Item remains selectable and receives “In use by another agent.”                           | `frontend/src/app/dashboard/agents/[id]/page.tsx:1671-1674` |
| Inventory management      | **Manage Numbers** links to `/dashboard/phone-numbers`.                                   | `frontend/src/app/dashboard/agents/[id]/page.tsx:1682-1690` |

The control deliberately allows choosing a number assigned elsewhere. Copy below the selector states that assignment moves the number from any other agent (`frontend/src/app/dashboard/agents/[id]/page.tsx:1678-1681`).

### Value contract

The option value is the actual provider phone-number string, not the provider inventory record ID (`frontend/src/app/dashboard/agents/[id]/page.tsx:1667-1670`). This matters because `Agent.phone_number_id` is consumed as a dialable/routable number by inbound lookup despite its historical field name.

The UI uses `none` only as a local select sentinel. Submission converts `none`, empty, or missing form values to JSON `null`; a concrete selection sends the number string (`frontend/src/app/dashboard/agents/[id]/page.tsx:588-601`).

## Provider inventory API

### Request

```http
GET /api/v1/telephony/phone-numbers?provider=telnyx
Authorization: Bearer <JWT>
```

For workspace-scoped provider credentials:

```http
GET /api/v1/telephony/phone-numbers?provider=telnyx&workspace_id=<uuid>
Authorization: Bearer <JWT>
```

The endpoint accepts `twilio` or `telnyx`; unsupported providers return HTTP 400 (`backend/app/api/telephony.py:328-343`). A malformed workspace UUID also returns HTTP 400 (`backend/app/api/telephony.py:319-324`).

### Credential behavior

- Omitting `workspace_id` resolves account-level credentials (`backend/app/api/telephony.py:307-315`).
- Supplying it resolves credentials isolated to that workspace (`backend/app/api/telephony.py:307-315`, `backend/app/api/telephony.py:328-340`).
- Missing provider credentials return `[]`, not an error (`backend/app/api/telephony.py:328-340`).

The empty-list contract means the frontend cannot distinguish “credentials missing” from “provider account contains no numbers”; both display the same no-inventory state.

### Assignment enrichment

After provider inventory loads, the endpoint queries non-null assignments only from agents owned by the authenticated user (`backend/app/api/telephony.py:345-350`). It normalizes each stored number by removing leading `+`, then maps live provider numbers to `assigned_agent_id` using that normalized key (`backend/app/api/telephony.py:351-365`).

Representative response:

```json
[
  {
    "id": "provider-number-id",
    "phone_number": "+15551234567",
    "friendly_name": "Main sales line",
    "provider": "telnyx",
    "capabilities": {
      "voice": true,
      "sms": true
    },
    "assigned_agent_id": "53e0492a-146c-4131-9a2c-5956f04c872e"
  }
]
```

`assigned_agent_id` is `null` when the current user's agents do not hold that number. Other users' assignment metadata is not included because enrichment is owner-filtered (`backend/app/api/telephony.py:345-350`).

## Agent update API

### Request shape

Assignment uses the existing update endpoint:

```http
PUT /api/v1/agents/{agent_id}
Authorization: Bearer <JWT>
Content-Type: application/json

{
  "phone_number_id": "+15551234567"
}
```

Unassignment is explicit:

```json
{
  "phone_number_id": null
}
```

### Three-state semantics

The backend inspects `UpdateAgentRequest.model_fields_set`, not only the parsed value (`backend/app/api/agents.py:331-332`). This preserves three distinct contracts:

| Payload         | Meaning                        | Database effect                                                              |
| --------------- | ------------------------------ | ---------------------------------------------------------------------------- |
| Field omitted   | No telephony change requested. | Existing assignment remains unchanged.                                       |
| Concrete number | Assign or reassign.            | Equivalent sibling assignment is cleared; target stores the submitted value. |
| Explicit `null` | Unassign.                      | Target `phone_number_id` becomes `NULL`.                                     |

This special handling is required because the generic `_apply_agent_updates` loop ignores `None` values (`backend/app/api/agents.py:357-389`). If `phone_number_id` remained in that generic loop, unassignment could not work.

### Authorization

The endpoint queries by both target UUID and authenticated `current_user.id` (`backend/app/api/agents.py:317-323`). A missing or differently owned agent returns HTTP 404 (`backend/app/api/agents.py:325-329`). The same owner boundary applies to reassignment: only other agents with `Agent.user_id == current_user.id` are candidates for clearing (`backend/app/api/agents.py:335-342`).

This has two security effects:

1. A user cannot assign a number by mutating another user's agent.
2. Assigning a number cannot clear another user's agent assignment.

### Reassignment algorithm

For a concrete number (`backend/app/api/agents.py:331-346`):

1. Remove leading plus signs to obtain a comparison key.
2. Query other agents owned by the current user.
3. Match either `<normalized>` or `+<normalized>`.
4. Set every match's `phone_number_id` to `NULL`.
5. Set the target agent to the submitted string.
6. Commit and refresh through the same SQLAlchemy session.

Because the sibling clears and target write are committed together (`backend/app/api/agents.py:344-352`), ordinary database failures roll back the reassignment as one transaction. The endpoint does not call Twilio or Telnyx during assignment; provider inventory and local routing assignment are separate operations.

## Inbound lookup

`get_agent_by_phone_number` is the routing-side consumer (`backend/app/api/telephony.py:165-172`). It:

1. removes leading `+` from the incoming value;
2. searches `Agent.phone_number_id` for normalized and plus-prefixed forms;
3. returns one matching agent or `None`.

This supports both of these equivalent inputs:

```text
+15551234567
15551234567
```

Normalization is deliberately narrow. It does not remove spaces, hyphens, parentheses, extensions, or international dialing prefixes (`backend/app/api/telephony.py:160-162`). Number acquisition should therefore continue producing consistent provider-formatted values.

The lookup uses `scalar_one_or_none()` (`backend/app/api/telephony.py:172`). Duplicate equivalent assignments are an invalid data state, not a tie resolved arbitrarily. Reassignment logic prevents duplicates within one owner, but old/manual data or cross-owner duplicates can still violate this cardinality expectation because inbound lookup is globally unscoped.

## Data ownership and source of truth

Two data sources participate:

| Data                                            | Source of truth                                     | Why                                                      |
| ----------------------------------------------- | --------------------------------------------------- | -------------------------------------------------------- |
| Available numbers, friendly names, capabilities | Live Twilio/Telnyx provider API                     | The selector must reflect provider inventory.            |
| Which agent receives inbound calls              | `Agent.phone_number_id`                             | Inbound lookup must resolve without a dashboard session. |
| Displayed assignment status                     | Join of live provider inventory to owned Agent rows | UI needs both availability and local assignment.         |

Persisted `PhoneNumber` inventory under `/api/v1/phone-numbers` remains related but is not the selector's read source. The Advanced editor calls `/api/v1/telephony/phone-numbers` directly (`frontend/src/app/dashboard/agents/[id]/page.tsx:435-444`).

## Concurrency and consistency caveats

The implemented reassignment sequence is atomic within one request's session, but no database uniqueness constraint is documented here for normalized phone assignments. Concurrent requests assigning the same number to different agents could race unless transaction isolation or a future normalized unique key closes that window. Inbound lookup's single-result requirement makes this important operationally.

Recommended diagnostics for a duplicate-routing incident:

```sql
SELECT id, user_id, name, phone_number_id
FROM agents
WHERE ltrim(phone_number_id, '+') = ltrim(:phone_number, '+');
```

Do not run destructive cleanup without confirming the intended destination agent. Correct through the authenticated update API when possible so reassignment semantics remain centralized.

## Failure-mode matrix

| Failure                         | Observable result                                                                | Recovery                                                    |
| ------------------------------- | -------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| No provider credentials         | Provider endpoint returns `[]`; UI shows purchase/no-number state.               | Configure account/workspace provider settings, then reload. |
| Provider account has no numbers | Same empty UI state.                                                             | Purchase/manage a number under Phone Numbers.               |
| Invalid workspace ID            | HTTP 400.                                                                        | Use a valid selected workspace UUID.                        |
| Unsupported provider            | HTTP 400.                                                                        | Select Twilio or Telnyx.                                    |
| Unauthorized agent ID           | HTTP 404; assignment unchanged.                                                  | Use an agent owned by the authenticated account.            |
| Explicit no-number selection    | Update succeeds with `phone_number_id: null`.                                    | Select a concrete number to re-enable inbound routing.      |
| Duplicate equivalent rows       | Inbound lookup can raise a multiple-results error.                               | Inspect and resolve duplicate assignments.                  |
| Provider listing outage         | TanStack Query request fails; assignment already stored remains in the database. | Retry provider listing; do not rewrite assignment blindly.  |

## Test evidence

Focused backend coverage lives in `backend/tests/test_api/test_agent_phone_assignment.py`:

- assignment response and persistence (`:35-53`);
- explicit-null unassignment (`:56-72`);
- reassignment from an unprefixed sibling to a plus-prefixed target (`:75-95`);
- cross-owner authorization and no mutation (`:98-121`);
- inbound lookup for both optional-plus forms (`:124-139`).

Provider-list behavior is covered in `backend/tests/test_api/test_telephony_phone_numbers.py`, including account-level and workspace-level credential paths and the enrichment query's mocked empty assignment set.

Verified commands on 2026-08-13:

```bash
uv --directory backend run pytest \
  tests/test_api/test_agent_phone_assignment.py \
  tests/test_api/test_telephony_phone_numbers.py -q
# 9 passed

npm --prefix frontend run check
# ESLint, TypeScript, and Prettier passed
```

Rendered evidence: `.gg/screenshots/phone-assignment-advanced-populated.png` shows the Advanced selector open with `+15551234567 (Main sales line)`.

## Maintenance checklist

When changing this feature:

1. Preserve omitted-versus-null semantics in `UpdateAgentRequest` handling.
2. Keep provider inventory assignment metadata owner-scoped.
3. Keep UI option values aligned with inbound lookup storage format.
4. Update both assignment and inbound normalization tests when normalization changes.
5. Re-test account-level and workspace-level number listing.
6. Verify the no-inventory, assigned-elsewhere, and unassignment UI states.
7. Revisit database uniqueness if concurrency requirements increase.
8. Update this document and the related atomic wiki pages in the same change.

## Governing paths

- `frontend/src/app/dashboard/agents/[id]/page.tsx`
- `frontend/src/lib/api/agents.ts`
- `backend/app/api/agents.py`
- `backend/app/api/telephony.py`
- `backend/app/models/agent.py`
- `backend/tests/test_api/test_agent_phone_assignment.py`
- `backend/tests/test_api/test_telephony_phone_numbers.py`
