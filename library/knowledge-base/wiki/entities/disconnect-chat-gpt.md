---
type: entity
title: "disconnectChatGPT"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
entity_type: function
path: "frontend/src/lib/api/settings.ts"
language: ts
last_commit_hash: "9920d822cbf596cfdd6b16efd6fce09e73cb4e86"
depends_on: []
used_by: []
tested_by: []
tags:
  - entity
  - function
related:
  - "[[entities/settings-lib-api]]"
sources: []
---

# disconnectChatGPT

## Overview

Exported function declared by the [[entities/settings-lib-api]] module at `frontend/src/lib/api/settings.ts:109`.

## Signature / Definition

```ts
export function disconnectChatGPT(workspaceId?: string): Promise<
```

## Behavior

The source declaration begins at `frontend/src/lib/api/settings.ts:109`; implementation behavior and side effects remain authoritative in that declaration.

## Connections

- **Defined by:** [[entities/settings-lib-api]] (`frontend/src/lib/api/settings.ts:109`)

## Tested by

No test relationship is asserted without direct in-file evidence.

## History

- **Last touched:** commit `9920d822cbf596cfdd6b16efd6fce09e73cb4e86` by Greg on 2026-08-13
- **Commit subject:** Add persistent OpenAI OAuth connection

## Sources

- `frontend/src/lib/api/settings.ts:109`
