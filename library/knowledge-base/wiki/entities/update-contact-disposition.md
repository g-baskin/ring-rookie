---
type: entity
title: "updateContactDisposition"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
entity_type: function
path: "frontend/src/lib/api/campaigns.ts"
language: ts
last_commit_hash: "e2de7645c7daa2883f6027f47da6052bf4ed0055"
depends_on: []
used_by: []
tested_by: []
tags:
  - entity
  - function
related:
  - "[[entities/campaigns-lib-api]]"
sources: []
---

# updateContactDisposition

## Overview

Exported function declared by the [[entities/campaigns-lib-api]] module at `frontend/src/lib/api/campaigns.ts:292`.

## Signature / Definition

```ts
export async function updateContactDisposition(
  campaignId: string,
  contactId: number,
  data: UpdateDispositionRequest,
): Promise<CampaignContact>;
```

## Behavior

The source declaration begins at `frontend/src/lib/api/campaigns.ts:292`; implementation behavior and side effects remain authoritative in that declaration.

## Connections

- **Defined by:** [[entities/campaigns-lib-api]] (`frontend/src/lib/api/campaigns.ts:292`)

## Tested by

No test relationship is asserted without direct in-file evidence.

## History

- **Last touched:** commit `e2de7645c7daa2883f6027f47da6052bf4ed0055` by kenkaiii on 2025-12-04
- **Commit subject:** Add outbound campaign dialer with CRM integration and telephony improvements

## Sources

- `frontend/src/lib/api/campaigns.ts:292`
