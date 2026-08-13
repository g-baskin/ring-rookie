---
type: entity
title: "SettingsResponse"
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
  - "openai_api_key_set"
  - "deepgram_api_key_set"
  - "elevenlabs_api_key_set"
  - "telnyx_api_key_set"
  - "twilio_account_sid_set"
  - "workspace_id"
tags:
  - entity
  - data-model
related:
  - "[[entities/settings-lib-api]]"
sources: []
---

# SettingsResponse

## Overview

Exported data model declared by the [[entities/settings-lib-api]] module at `frontend/src/lib/api/settings.ts:47`.

## Signature / Definition

```ts
export interface SettingsResponse
```

## Behavior

The source declaration begins at `frontend/src/lib/api/settings.ts:47`; implementation behavior and side effects remain authoritative in that declaration.

## Connections

- **Defined by:** [[entities/settings-lib-api]] (`frontend/src/lib/api/settings.ts:47`)

## Tested by

No test relationship is asserted without direct in-file evidence.

## History

- **Last touched:** commit `9920d822cbf596cfdd6b16efd6fce09e73cb4e86` by Greg on 2026-08-13
- **Commit subject:** Add persistent OpenAI OAuth connection

## Sources

- `frontend/src/lib/api/settings.ts:47`
