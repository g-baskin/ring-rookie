---
type: entity
title: "deleteLesson"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
entity_type: function
path: "frontend/src/lib/api/lessons.ts"
language: ts
last_commit_hash: "5bbaa0ef107051696d129863471d633cd271fcb1"
depends_on: []
used_by: []
tested_by: []
tags:
  - entity
  - function
related:
  - "[[entities/lessons-lib-api]]"
sources: []
---

# deleteLesson

## Overview

Exported function declared by the [[entities/lessons-lib-api]] module at `frontend/src/lib/api/lessons.ts:84`.

## Signature / Definition

```ts
export async function deleteLesson(
  agentId: string,
  lessonId: string,
  workspaceId?: string | null,
): Promise<void>;
```

## Behavior

The source declaration begins at `frontend/src/lib/api/lessons.ts:84`; implementation behavior and side effects remain authoritative in that declaration.

## Connections

- **Defined by:** [[entities/lessons-lib-api]] (`frontend/src/lib/api/lessons.ts:84`)

## Tested by

No test relationship is asserted without direct in-file evidence.

## History

- **Last touched:** commit `5bbaa0ef107051696d129863471d633cd271fcb1` by Greg on 2026-08-13
- **Commit subject:** Add transcript-linked lessons and call details

## Sources

- `frontend/src/lib/api/lessons.ts:84`
