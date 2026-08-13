---
type: entity
title: "ListCallsParams"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
entity_type: data-model
path: "frontend/src/lib/api/calls.ts"
language: ts
last_commit_hash: "5c86e6eab31567a8c75c70496d63f7ebab6e1f7b"
depends_on: []
used_by: []
tested_by: []
schema_library: typescript
fields:
  - "page"
  - "page_size"
  - "agent_id"
  - "workspace_id"
  - "direction"
  - "status"
tags:
  - entity
  - data-model
related:
  - "[[entities/calls-lib-api]]"
sources: []
---

# ListCallsParams

## Overview

Exported data model declared by the [[entities/calls-lib-api]] module at `frontend/src/lib/api/calls.ts:43`.

## Signature / Definition

```ts
export interface ListCallsParams
```

## Behavior

The source declaration begins at `frontend/src/lib/api/calls.ts:43`; implementation behavior and side effects remain authoritative in that declaration.

## Connections

- **Defined by:** [[entities/calls-lib-api]] (`frontend/src/lib/api/calls.ts:43`)

## Tested by

No test relationship is asserted without direct in-file evidence.

## History

- **Last touched:** commit `5c86e6eab31567a8c75c70496d63f7ebab6e1f7b` by g-baskin on 2026-01-23
- **Commit subject:** feat: add Chat Champ infrastructure with knowledge base, usage metering, and analytics

## Sources

- `frontend/src/lib/api/calls.ts:43`
