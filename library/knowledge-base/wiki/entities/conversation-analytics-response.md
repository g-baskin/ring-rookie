---
type: entity
title: "ConversationAnalyticsResponse"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
entity_type: data-model
path: "frontend/src/lib/api/conversations.ts"
language: ts
last_commit_hash: "5c86e6eab31567a8c75c70496d63f7ebab6e1f7b"
depends_on: []
used_by: []
tested_by: []
schema_library: typescript
fields:
  - "total_conversations"
  - "total_messages"
  - "total_tokens"
  - "avg_messages_per_conversation"
  - "avg_tokens_per_conversation"
  - "efficiency_scores"
  - "conversations_by_efficiency"
  - "avg_duration_seconds"
  - "estimated_cost_total"
  - "estimated_cost_wasted"
tags:
  - entity
  - data-model
related:
  - "[[entities/conversations-lib-api]]"
sources: []
---

# ConversationAnalyticsResponse

## Overview

Exported data model declared by the [[entities/conversations-lib-api]] module at `frontend/src/lib/api/conversations.ts:90`.

## Signature / Definition

```ts
export interface ConversationAnalyticsResponse
```

## Behavior

The source declaration begins at `frontend/src/lib/api/conversations.ts:90`; implementation behavior and side effects remain authoritative in that declaration.

## Connections

- **Defined by:** [[entities/conversations-lib-api]] (`frontend/src/lib/api/conversations.ts:90`)

## Tested by

No test relationship is asserted without direct in-file evidence.

## History

- **Last touched:** commit `5c86e6eab31567a8c75c70496d63f7ebab6e1f7b` by g-baskin on 2026-01-23
- **Commit subject:** feat: add Chat Champ infrastructure with knowledge base, usage metering, and analytics

## Sources

- `frontend/src/lib/api/conversations.ts:90`
