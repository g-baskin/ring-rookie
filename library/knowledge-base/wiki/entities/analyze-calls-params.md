---
type: entity
title: "AnalyzeCallsParams"
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
  - "call_ids"
  - "agent_id"
  - "date_from"
  - "date_to"
tags:
  - entity
  - data-model
related:
  - "[[entities/calls-lib-api]]"
sources: []
---

# AnalyzeCallsParams

## Overview

Exported data model declared by the [[entities/calls-lib-api]] module at `frontend/src/lib/api/calls.ts:70`.

## Signature / Definition

```ts
export interface AnalyzeCallsParams
```

## Behavior

The source declaration begins at `frontend/src/lib/api/calls.ts:70`; implementation behavior and side effects remain authoritative in that declaration.

## Connections

- **Defined by:** [[entities/calls-lib-api]] (`frontend/src/lib/api/calls.ts:70`)

## Tested by

No test relationship is asserted without direct in-file evidence.

## History

- **Last touched:** commit `5c86e6eab31567a8c75c70496d63f7ebab6e1f7b` by g-baskin on 2026-01-23
- **Commit subject:** feat: add Chat Champ infrastructure with knowledge base, usage metering, and analytics

## Sources

- `frontend/src/lib/api/calls.ts:70`
