---
type: entity
title: "CreateAgentRequest"
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
  - "name"
  - "description"
  - "pricing_tier"
  - "system_prompt"
  - "system_prompt_character_target"
  - "language"
  - "voice"
  - "enabled_tools"
  - "enabled_tool_ids"
  - "phone_number_id"
  - "enable_recording"
  - "enable_transcript"
  - "initial_greeting"
  - "temperature"
  - "max_tokens"
tags:
  - entity
  - data-model
related:
  - "[[entities/agents-lib-api]]"
sources: []
---

# CreateAgentRequest

## Overview

Exported data model declared by the [[entities/agents-lib-api]] module at `frontend/src/lib/api/agents.ts:78`.

## Signature / Definition

```ts
export interface CreateAgentRequest
```

## Behavior

The source declaration begins at `frontend/src/lib/api/agents.ts:78`; implementation behavior and side effects remain authoritative in that declaration.

## Connections

- **Defined by:** [[entities/agents-lib-api]] (`frontend/src/lib/api/agents.ts:78`)

## Tested by

No test relationship is asserted without direct in-file evidence.

## History

- **Last touched:** commit `8cc53566e2534abc817ebf966bb247d7b370e28f` by Greg on 2026-08-13
- **Commit subject:** Add configurable system prompt character target

## Sources

- `frontend/src/lib/api/agents.ts:78`
