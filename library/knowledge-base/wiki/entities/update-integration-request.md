---
type: entity
title: "UpdateIntegrationRequest"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
entity_type: data-model
path: "frontend/src/lib/api.ts"
language: ts
last_commit_hash: "c5a3703d7815d1eabc5418f8eb56e292ef623b58"
depends_on: []
used_by: []
tested_by: []
schema_library: typescript
fields:
  - "credentials"
  - "metadata"
  - "is_active"
tags:
  - entity
  - data-model
related:
  - "[[entities/api-src-lib]]"
sources: []
---

# UpdateIntegrationRequest

## Overview

Exported data model declared by the [[entities/api-src-lib]] module at `frontend/src/lib/api.ts:120`.

## Signature / Definition

```ts
export interface UpdateIntegrationRequest
```

## Behavior

The source declaration begins at `frontend/src/lib/api.ts:120`; implementation behavior and side effects remain authoritative in that declaration.

## Connections

- **Defined by:** [[entities/api-src-lib]] (`frontend/src/lib/api.ts:120`)

## Tested by

No test relationship is asserted without direct in-file evidence.

## History

- **Last touched:** commit `c5a3703d7815d1eabc5418f8eb56e292ef623b58` by Greg on 2026-08-13
- **Commit subject:** Fix OpenAI OAuth Realtime sessions and transcript export

## Sources

- `frontend/src/lib/api.ts:120`
