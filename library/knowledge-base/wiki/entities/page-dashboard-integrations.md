---
type: entity
title: "page.tsx"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
entity_type: module
path: "frontend/src/app/dashboard/integrations/page.tsx"
language: tsx
last_commit_hash: "b08b80b4e8aa6f3e3f1fcd5b08da01235d933400"
depends_on: []
used_by: []
tested_by: []
exports:
  - "[[entities/integrations-page]]"
imports:
  - "react"
  - "use-debounce"
  - "@tanstack/react-query"
  - "sonner"
  - "@/components/ui/button"
  - "@/components/ui/card"
  - "@/components/ui/badge"
  - "@/lib/api"
  - "@/components/ui/input"
  - "@/components/ui/label"
  - "@/components/ui/tabs"
  - "lucide-react"
  - "@/components/ui/dialog"
  - "@/components/ui/alert-dialog"
  - "@/lib/integrations"
  - "@/components/ui/select"
tags:
  - entity
  - module
related:
  - "[[entities/integrations-page]]"
sources: []
---

# page.tsx

## Overview

Source module at `frontend/src/app/dashboard/integrations/page.tsx:1` exporting 1 documented code entities.

## Exports

- [[entities/integrations-page]] — react-component, declaration at `frontend/src/app/dashboard/integrations/page.tsx:97`

## Imports

- `react` (import declaration in `frontend/src/app/dashboard/integrations/page.tsx:3`)
- `use-debounce` (import declaration in `frontend/src/app/dashboard/integrations/page.tsx:4`)
- `@tanstack/react-query` (import declaration in `frontend/src/app/dashboard/integrations/page.tsx:5`)
- `sonner` (import declaration in `frontend/src/app/dashboard/integrations/page.tsx:6`)
- `@/components/ui/button` (import declaration in `frontend/src/app/dashboard/integrations/page.tsx:7`)
- `@/components/ui/card` (import declaration in `frontend/src/app/dashboard/integrations/page.tsx:8`)
- `@/components/ui/badge` (import declaration in `frontend/src/app/dashboard/integrations/page.tsx:9`)
- `@/lib/api` (import declaration in `frontend/src/app/dashboard/integrations/page.tsx:10`)
- `@/components/ui/input` (import declaration in `frontend/src/app/dashboard/integrations/page.tsx:11`)
- `@/components/ui/label` (import declaration in `frontend/src/app/dashboard/integrations/page.tsx:12`)
- `@/components/ui/tabs` (import declaration in `frontend/src/app/dashboard/integrations/page.tsx:13`)
- `lucide-react` (import declaration in `frontend/src/app/dashboard/integrations/page.tsx:14`)
- `@/components/ui/dialog` (import declaration in `frontend/src/app/dashboard/integrations/page.tsx:39`)
- `@/components/ui/alert-dialog` (import declaration in `frontend/src/app/dashboard/integrations/page.tsx:47`)
- `@/lib/integrations` (import declaration in `frontend/src/app/dashboard/integrations/page.tsx:57`)
- `@/components/ui/select` (import declaration in `frontend/src/app/dashboard/integrations/page.tsx:58`)

## History

- **Last touched:** commit `b08b80b4e8aa6f3e3f1fcd5b08da01235d933400` by kenkaiii on 2025-11-29
- **Commit subject:** Add workspace dropdown filtering across all dashboard pages

## Sources

- `frontend/src/app/dashboard/integrations/page.tsx:1`
