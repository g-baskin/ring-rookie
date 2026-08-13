---
type: entity
title: "page.tsx"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
entity_type: module
path: "frontend/src/app/dashboard/page.tsx"
language: tsx
last_commit_hash: "46ef234c01560711494b3ad02f6d37d39db19b5f"
depends_on: []
used_by: []
tested_by: []
exports:
  - "[[entities/dashboard-page]]"
imports:
  - "next/link"
  - "@tanstack/react-query"
  - "@/components/ui/card"
  - "@/components/ui/button"
  - "lucide-react"
  - "@/lib/api/agents"
  - "@/lib/api/calls"
  - "@/lib/api"
tags:
  - entity
  - module
related:
  - "[[entities/dashboard-page]]"
sources: []
---

# page.tsx

## Overview

Source module at `frontend/src/app/dashboard/page.tsx:1` exporting 1 documented code entities.

## Exports

- [[entities/dashboard-page]] — react-component, declaration at `frontend/src/app/dashboard/page.tsx:37`

## Imports

- `next/link` (import declaration in `frontend/src/app/dashboard/page.tsx:3`)
- `@tanstack/react-query` (import declaration in `frontend/src/app/dashboard/page.tsx:4`)
- `@/components/ui/card` (import declaration in `frontend/src/app/dashboard/page.tsx:5`)
- `@/components/ui/button` (import declaration in `frontend/src/app/dashboard/page.tsx:6`)
- `lucide-react` (import declaration in `frontend/src/app/dashboard/page.tsx:7`)
- `@/lib/api/agents` (import declaration in `frontend/src/app/dashboard/page.tsx:19`)
- `@/lib/api/calls` (import declaration in `frontend/src/app/dashboard/page.tsx:20`)
- `@/lib/api` (import declaration in `frontend/src/app/dashboard/page.tsx:21`)

## History

- **Last touched:** commit `46ef234c01560711494b3ad02f6d37d39db19b5f` by kenkaiii on 2025-11-30
- **Commit subject:** Fix API key fallback to global keys and require workspace before agent creation

## Sources

- `frontend/src/app/dashboard/page.tsx:1`
