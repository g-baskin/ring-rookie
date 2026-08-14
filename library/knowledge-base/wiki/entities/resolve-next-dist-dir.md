---
type: entity
title: "resolveNextDistDir"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
entity_type: function
path: "frontend/next.config.ts"
language: ts
last_commit_hash: "bb80c70ea36071bdec833be0fb3d9717d06f6f67"
depends_on: []
used_by: []
tested_by: []
tags:
  - entity
  - function
related:
  - "[[entities/next-config-frontend]]"
sources: []
---

# resolveNextDistDir

## Overview

Exported function declared by the [[entities/next-config-frontend]] module at `frontend/next.config.ts:8`.

## Signature / Definition

```ts
export function resolveNextDistDir(
  nodeEnvironment = process.env.NODE_ENV,
  configuredDistDir = process.env.NEXT_DIST_DIR,
): string;
```

## Behavior

The source declaration begins at `frontend/next.config.ts:8`; implementation behavior and side effects remain authoritative in that declaration.

## Connections

- **Defined by:** [[entities/next-config-frontend]] (`frontend/next.config.ts:8`)

## Tested by

No test relationship is asserted without direct in-file evidence.

## History

- **Last touched:** commit `bb80c70ea36071bdec833be0fb3d9717d06f6f67` by Greg on 2026-08-13
- **Commit subject:** feat: add persistent hot-reload development stack

## Sources

- `frontend/next.config.ts:8`
