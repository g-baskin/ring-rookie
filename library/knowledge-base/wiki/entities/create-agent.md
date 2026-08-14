---
type: entity
title: "createAgent"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
entity_type: function
path: "frontend/src/lib/api/agents.ts"
language: ts
last_commit_hash: "8cc53566e2534abc817ebf966bb247d7b370e28f"
depends_on: []
used_by: []
tested_by: []
tags:
  - entity
  - function
related:
  - "[[entities/agents-lib-api]]"
sources: []
---

# createAgent

## Overview

Exported function declared by the [[entities/agents-lib-api]] module at `frontend/src/lib/api/agents.ts:99`.

## Signature / Definition

```ts
export async function createAgent(request: CreateAgentRequest): Promise<Agent>;
```

## Behavior

The source declaration begins at `frontend/src/lib/api/agents.ts:99`; implementation behavior and side effects remain authoritative in that declaration.

## Connections

- **Defined by:** [[entities/agents-lib-api]] (`frontend/src/lib/api/agents.ts:99`)

## Tested by

No test relationship is asserted without direct in-file evidence.

## History

- **Last touched:** commit `8cc53566e2534abc817ebf966bb247d7b370e28f` by Greg on 2026-08-13
- **Commit subject:** Add configurable system prompt character target

## Sources

- `frontend/src/lib/api/agents.ts:99`
