---
type: entity
title: "UpdateEmbedSettingsRequest"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
entity_type: data-model
path: "frontend/src/lib/api/agents.ts"
language: ts
last_commit_hash: "8cc53566e2534abc817ebf966bb247d7b370e28f"
depends_on: []
used_by: []
tested_by: []
schema_library: typescript
fields:
  - "embed_enabled"
  - "allowed_domains"
  - "embed_settings"
tags:
  - entity
  - data-model
related:
  - "[[entities/agents-lib-api]]"
sources: []
---

# UpdateEmbedSettingsRequest

## Overview

Exported data model declared by the [[entities/agents-lib-api]] module at `frontend/src/lib/api/agents.ts:216`.

## Signature / Definition

```ts
export interface UpdateEmbedSettingsRequest
```

## Behavior

The source declaration begins at `frontend/src/lib/api/agents.ts:216`; implementation behavior and side effects remain authoritative in that declaration.

## Connections

- **Defined by:** [[entities/agents-lib-api]] (`frontend/src/lib/api/agents.ts:216`)

## Tested by

No test relationship is asserted without direct in-file evidence.

## History

- **Last touched:** commit `8cc53566e2534abc817ebf966bb247d7b370e28f` by Greg on 2026-08-13
- **Commit subject:** Add configurable system prompt character target

## Sources

- `frontend/src/lib/api/agents.ts:216`
