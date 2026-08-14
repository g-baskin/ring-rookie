---
type: entity
title: "recordConsent"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
entity_type: function
path: "frontend/src/lib/api/compliance.ts"
language: ts
last_commit_hash: "b0f0d5135af06717a3d59dbcddc2e7641472314b"
depends_on: []
used_by: []
tested_by: []
tags:
  - entity
  - function
related:
  - "[[entities/compliance-lib-api]]"
sources: []
---

# recordConsent

## Overview

Exported function declared by the [[entities/compliance-lib-api]] module at `frontend/src/lib/api/compliance.ts:98`.

## Signature / Definition

```ts
export async function recordConsent(
  consentType: string,
  granted: boolean
): Promise<
```

## Behavior

The source declaration begins at `frontend/src/lib/api/compliance.ts:98`; implementation behavior and side effects remain authoritative in that declaration.

## Connections

- **Defined by:** [[entities/compliance-lib-api]] (`frontend/src/lib/api/compliance.ts:98`)

## Tested by

No test relationship is asserted without direct in-file evidence.

## History

- **Last touched:** commit `b0f0d5135af06717a3d59dbcddc2e7641472314b` by kenkaiii on 2025-11-28
- **Commit subject:** Add GDPR/CCPA compliance features with privacy controls

## Sources

- `frontend/src/lib/api/compliance.ts:98`
