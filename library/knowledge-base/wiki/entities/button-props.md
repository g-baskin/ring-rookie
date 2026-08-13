---
type: entity
title: "ButtonProps"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
entity_type: react-component
path: "frontend/src/components/ui/button.tsx"
language: tsx
last_commit_hash: "4073bfec6052c2409fbc51db186b48f0b688e9ac"
depends_on: []
used_by: []
tested_by: []
props_summary: "asChild"
tags:
  - entity
  - react-component
related:
  - "[[entities/button-components-ui]]"
sources: []
---

# ButtonProps

## Overview

Exported react component declared by the [[entities/button-components-ui]] module at `frontend/src/components/ui/button.tsx:34`.

## Signature / Definition

```tsx
export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants>
```

## Behavior

The source declaration begins at `frontend/src/components/ui/button.tsx:34`; implementation behavior and side effects remain authoritative in that declaration.

## Connections

- **Defined by:** [[entities/button-components-ui]] (`frontend/src/components/ui/button.tsx:34`)

## Tested by

No test relationship is asserted without direct in-file evidence.

## History

- **Last touched:** commit `4073bfec6052c2409fbc51db186b48f0b688e9ac` by kenkaiii on 2025-11-29
- **Commit subject:** Update GPT realtime to latest model and fix agent deletion 404 errors

## Sources

- `frontend/src/components/ui/button.tsx:34`
