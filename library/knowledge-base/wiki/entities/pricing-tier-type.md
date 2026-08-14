---
type: entity
title: "PricingTierType"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
entity_type: data-model
path: "frontend/src/lib/languages.ts"
language: ts
last_commit_hash: "b926d429f61de671fc2a26280cef2d97f9f92c81"
depends_on: []
used_by: []
tested_by: []
schema_library: typescript
fields: []
tags:
  - entity
  - data-model
related:
  - "[[entities/languages-src-lib]]"
sources: []
---

# PricingTierType

## Overview

Exported data model declared by the [[entities/languages-src-lib]] module at `frontend/src/lib/languages.ts:124`.

## Signature / Definition

```ts
export type PricingTierType =
  | "budget"
  | "balanced"
  | "premium-mini"
  | "premium";
```

## Behavior

The source declaration begins at `frontend/src/lib/languages.ts:124`; implementation behavior and side effects remain authoritative in that declaration.

## Connections

- **Defined by:** [[entities/languages-src-lib]] (`frontend/src/lib/languages.ts:124`)

## Tested by

No test relationship is asserted without direct in-file evidence.

## History

- **Last touched:** commit `b926d429f61de671fc2a26280cef2d97f9f92c81` by kenkaiii on 2025-11-29
- **Commit subject:** Remove dead code and unused dependencies

## Sources

- `frontend/src/lib/languages.ts:124`
