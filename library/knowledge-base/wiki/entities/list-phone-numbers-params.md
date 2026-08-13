---
type: entity
title: "ListPhoneNumbersParams"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
entity_type: data-model
path: "frontend/src/lib/api/phone-numbers.ts"
language: ts
last_commit_hash: "ca3237d6c21d6f6c768dfa57d1e99c6b2d712d64"
depends_on: []
used_by: []
tested_by: []
schema_library: typescript
fields:
  - "page"
  - "page_size"
  - "workspace_id"
  - "status"
tags:
  - entity
  - data-model
related:
  - "[[entities/phone-numbers-lib-api]]"
sources: []
---

# ListPhoneNumbersParams

## Overview

Exported data model declared by the [[entities/phone-numbers-lib-api]] module at `frontend/src/lib/api/phone-numbers.ts:41`.

## Signature / Definition

```ts
export interface ListPhoneNumbersParams
```

## Behavior

The source declaration begins at `frontend/src/lib/api/phone-numbers.ts:41`; implementation behavior and side effects remain authoritative in that declaration.

## Connections

- **Defined by:** [[entities/phone-numbers-lib-api]] (`frontend/src/lib/api/phone-numbers.ts:41`)

## Tested by

No test relationship is asserted without direct in-file evidence.

## History

- **Last touched:** commit `ca3237d6c21d6f6c768dfa57d1e99c6b2d712d64` by kenkaiii on 2025-11-27
- **Commit subject:** Add top bar stats, phone numbers API, and refresh dashboard UI

## Sources

- `frontend/src/lib/api/phone-numbers.ts:41`
