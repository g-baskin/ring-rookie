---
type: entity
title: "ExportConversationsParams"
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
  - "format"
  - "conversation_ids"
  - "agent_id"
  - "date_from"
  - "date_to"
  - "include_messages"
tags:
  - entity
  - data-model
related:
  - "[[entities/conversations-lib-api]]"
sources: []
---

# ExportConversationsParams

## Overview

Exported data model declared by the [[entities/conversations-lib-api]] module at `frontend/src/lib/api/conversations.ts:52`.

## Signature / Definition

```ts
export interface ExportConversationsParams
```

## Behavior

The source declaration begins at `frontend/src/lib/api/conversations.ts:52`; implementation behavior and side effects remain authoritative in that declaration.

## Connections

- **Defined by:** [[entities/conversations-lib-api]] (`frontend/src/lib/api/conversations.ts:52`)

## Tested by

No test relationship is asserted without direct in-file evidence.

## History

- **Last touched:** commit `5c86e6eab31567a8c75c70496d63f7ebab6e1f7b` by g-baskin on 2026-01-23
- **Commit subject:** feat: add Chat Champ infrastructure with knowledge base, usage metering, and analytics

## Sources

- `frontend/src/lib/api/conversations.ts:52`
