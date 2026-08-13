---
type: entity
title: "hangupCall"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
entity_type: function
path: "frontend/src/lib/api/telephony.ts"
language: ts
last_commit_hash: "9de19e18ffa7642560ee78caeda9c6d22d1683a9"
depends_on: []
used_by: []
tested_by: []
tags:
  - entity
  - function
related:
  - "[[entities/telephony-lib-api]]"
sources: []
---

# hangupCall

## Overview

Exported function declared by the [[entities/telephony-lib-api]] module at `frontend/src/lib/api/telephony.ts:230`.

## Signature / Definition

```ts
export async function hangupCall(
  callId: string,
  provider: Provider,
): Promise<void>;
```

## Behavior

The source declaration begins at `frontend/src/lib/api/telephony.ts:230`; implementation behavior and side effects remain authoritative in that declaration.

## Connections

- **Defined by:** [[entities/telephony-lib-api]] (`frontend/src/lib/api/telephony.ts:230`)

## Tested by

No test relationship is asserted without direct in-file evidence.

## History

- **Last touched:** commit `9de19e18ffa7642560ee78caeda9c6d22d1683a9` by Greg on 2026-08-13
- **Commit subject:** Add Telnyx phone number account sync

## Sources

- `frontend/src/lib/api/telephony.ts:230`
