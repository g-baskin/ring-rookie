---
type: entity
title: "ChatGPTConnectionStatus"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
entity_type: data-model
path: "frontend/src/lib/api/settings.ts"
language: ts
last_commit_hash: "9920d822cbf596cfdd6b16efd6fce09e73cb4e86"
depends_on: []
used_by: []
tested_by: []
schema_library: typescript
fields:
  - "connected"
  - "workspace_id"
  - "account_email"
  - "account_name"
  - "plan_type"
  - "expires_at"
  - "can_refresh"
  - "updated_at"
tags:
  - entity
  - data-model
related:
  - "[[entities/settings-lib-api]]"
sources: []
---

# ChatGPTConnectionStatus

## Overview

Exported data model declared by the [[entities/settings-lib-api]] module at `frontend/src/lib/api/settings.ts:66`.

## Signature / Definition

```ts
export interface ChatGPTConnectionStatus
```

## Behavior

The source declaration begins at `frontend/src/lib/api/settings.ts:66`; implementation behavior and side effects remain authoritative in that declaration.

## Connections

- **Defined by:** [[entities/settings-lib-api]] (`frontend/src/lib/api/settings.ts:66`)

## Tested by

No test relationship is asserted without direct in-file evidence.

## History

- **Last touched:** commit `9920d822cbf596cfdd6b16efd6fce09e73cb4e86` by Greg on 2026-08-13
- **Commit subject:** Add persistent OpenAI OAuth connection

## Sources

- `frontend/src/lib/api/settings.ts:66`
