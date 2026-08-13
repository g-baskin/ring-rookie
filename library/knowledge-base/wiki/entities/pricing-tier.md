---
type: entity
title: "PricingTier"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
entity_type: data-model
path: "frontend/src/lib/pricing-tiers.ts"
language: ts
last_commit_hash: "2ce28c6f3d42d0b84b225d973b9caca99dabf07d"
depends_on: []
used_by: []
tested_by: []
schema_library: typescript
fields:
  - "id"
  - "name"
  - "description"
  - "costPerHour"
  - "costPerMinute"
  - "recommended"
  - "underConstruction"
  - "features"
  - "config"
  - "performance"
tags:
  - entity
  - data-model
related:
  - "[[entities/pricing-tiers-src-lib]]"
sources: []
---

# PricingTier

## Overview

Exported data model declared by the [[entities/pricing-tiers-src-lib]] module at `frontend/src/lib/pricing-tiers.ts:1`.

## Signature / Definition

```ts
export interface PricingTier
```

## Behavior

The source declaration begins at `frontend/src/lib/pricing-tiers.ts:1`; implementation behavior and side effects remain authoritative in that declaration.

## Connections

- **Defined by:** [[entities/pricing-tiers-src-lib]] (`frontend/src/lib/pricing-tiers.ts:1`)

## Tested by

No test relationship is asserted without direct in-file evidence.

## History

- **Last touched:** commit `2ce28c6f3d42d0b84b225d973b9caca99dabf07d` by AutomationGod on 2026-08-13
- **Commit subject:** Establish PRD-001a delivery spine (#2)

## Sources

- `frontend/src/lib/pricing-tiers.ts:1`
