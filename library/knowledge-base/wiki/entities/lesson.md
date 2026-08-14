---
type: entity
title: "Lesson"
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
  - "id"
  - "user_id"
  - "agent_id"
  - "workspace_id"
  - "source_call_id"
  - "title"
  - "observation"
  - "recommended_action"
  - "status"
  - "created_at"
  - "updated_at"
tags:
  - entity
  - data-model
related:
  - "[[entities/lessons-lib-api]]"
sources: []
---

# Lesson

## Overview

Exported data model declared by the [[entities/lessons-lib-api]] module at `frontend/src/lib/api/lessons.ts:3`.

## Signature / Definition

```ts
export interface Lesson
```

## Behavior

The source declaration begins at `frontend/src/lib/api/lessons.ts:3`; implementation behavior and side effects remain authoritative in that declaration.

## Connections

- **Defined by:** [[entities/lessons-lib-api]] (`frontend/src/lib/api/lessons.ts:3`)

## Tested by

No test relationship is asserted without direct in-file evidence.

## History

- **Last touched:** commit `5bbaa0ef107051696d129863471d633cd271fcb1` by Greg on 2026-08-13
- **Commit subject:** Add transcript-linked lessons and call details

## Sources

- `frontend/src/lib/api/lessons.ts:3`
