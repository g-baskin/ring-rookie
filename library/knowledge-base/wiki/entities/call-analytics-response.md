---
type: entity
title: "CallAnalyticsResponse"
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
  - "total_calls"
  - "total_duration_seconds"
  - "avg_duration_seconds"
  - "efficiency_scores"
  - "calls_by_efficiency"
  - "avg_words_per_minute"
  - "avg_turns_per_call"
  - "estimated_cost_total"
  - "estimated_cost_wasted"
tags:
  - entity
  - data-model
related:
  - "[[entities/calls-lib-api]]"
sources: []
---

# CallAnalyticsResponse

## Overview

Exported data model declared by the [[entities/calls-lib-api]] module at `frontend/src/lib/api/calls.ts:98`.

## Signature / Definition

```ts
export interface CallAnalyticsResponse
```

## Behavior

The source declaration begins at `frontend/src/lib/api/calls.ts:98`; implementation behavior and side effects remain authoritative in that declaration.

## Connections

- **Defined by:** [[entities/calls-lib-api]] (`frontend/src/lib/api/calls.ts:98`)

## Tested by

No test relationship is asserted without direct in-file evidence.

## History

- **Last touched:** commit `5c86e6eab31567a8c75c70496d63f7ebab6e1f7b` by g-baskin on 2026-01-23
- **Commit subject:** feat: add Chat Champ infrastructure with knowledge base, usage metering, and analytics

## Sources

- `frontend/src/lib/api/calls.ts:98`
