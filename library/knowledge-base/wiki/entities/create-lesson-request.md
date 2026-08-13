---
type: entity
title: "CreateLessonRequest"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
entity_type: data-model
path: "frontend/src/lib/api/lessons.ts"
language: ts
last_commit_hash: "5bbaa0ef107051696d129863471d633cd271fcb1"
depends_on: []
used_by: []
tested_by: []
schema_library: typescript
fields:
  - "source_call_id"
  - "title"
  - "observation"
  - "recommended_action"
  - "status"
tags:
  - entity
  - data-model
related:
  - "[[entities/lessons-lib-api]]"
sources: []
---

# CreateLessonRequest

## Overview

Exported data model declared by the [[entities/lessons-lib-api]] module at `frontend/src/lib/api/lessons.ts:17`.

## Signature / Definition

```ts
export interface CreateLessonRequest
```

## Behavior

The source declaration begins at `frontend/src/lib/api/lessons.ts:17`; implementation behavior and side effects remain authoritative in that declaration.

## Connections

- **Defined by:** [[entities/lessons-lib-api]] (`frontend/src/lib/api/lessons.ts:17`)

## Tested by

No test relationship is asserted without direct in-file evidence.

## History

- **Last touched:** commit `5bbaa0ef107051696d129863471d633cd271fcb1` by Greg on 2026-08-13
- **Commit subject:** Add transcript-linked lessons and call details

## Sources

- `frontend/src/lib/api/lessons.ts:17`
