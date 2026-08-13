---
type: entity
title: "page.tsx"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
entity_type: module
path: "frontend/src/app/dashboard/agents/[id]/page.tsx"
language: tsx
last_commit_hash: "e5c4bbaf1606727b39ad6372c9e353ab99fc0d70"
depends_on: []
used_by: []
tested_by: []
exports:
  - "[[entities/edit-agent-page]]"
imports:
  - "react"
  - "@hookform/resolvers/zod"
  - "react-hook-form"
  - "next/navigation"
  - "@tanstack/react-query"
  - "sonner"
  - "zod"
  - "next/link"
  - "@/lib/api/agents"
  - "@/components/ui/button"
  - "@/components/ui/card"
  - "@/components/ui/form"
  - "@/components/ui/input"
  - "@/components/ui/textarea"
  - "@/components/ui/select"
  - "@/components/ui/separator"
  - "@/components/ui/tabs"
  - "@/components/ui/switch"
  - "@/components/ui/badge"
  - "lucide-react"
  - "@/lib/api"
  - "@/lib/languages"
  - "@/lib/integrations"
  - "@/components/ui/collapsible"
  - "@/components/ui/alert-dialog"
  - "@/components/ui/checkbox"
  - "@/components/ui/slider"
  - "@/lib/utils"
  - "./prompt-character-target"
  - "@/components/ui/info-tooltip"
tags:
  - entity
  - module
related:
  - "[[entities/edit-agent-page]]"
sources: []
---

# page.tsx

## Overview

Source module at `frontend/src/app/dashboard/agents/[id]/page.tsx:1` exporting 1 documented code entities.

## Exports

- [[entities/edit-agent-page]] — react-component, declaration at `frontend/src/app/dashboard/agents/[id]/page.tsx:244`

## Imports

- `react` (import declaration in `frontend/src/app/dashboard/agents/[id]/page.tsx:3`)
- `@hookform/resolvers/zod` (import declaration in `frontend/src/app/dashboard/agents/[id]/page.tsx:4`)
- `react-hook-form` (import declaration in `frontend/src/app/dashboard/agents/[id]/page.tsx:5`)
- `next/navigation` (import declaration in `frontend/src/app/dashboard/agents/[id]/page.tsx:6`)
- `@tanstack/react-query` (import declaration in `frontend/src/app/dashboard/agents/[id]/page.tsx:7`)
- `sonner` (import declaration in `frontend/src/app/dashboard/agents/[id]/page.tsx:8`)
- `zod` (import declaration in `frontend/src/app/dashboard/agents/[id]/page.tsx:9`)
- `next/link` (import declaration in `frontend/src/app/dashboard/agents/[id]/page.tsx:10`)
- `@/lib/api/agents` (import declaration in `frontend/src/app/dashboard/agents/[id]/page.tsx:11`)
- `@/components/ui/button` (import declaration in `frontend/src/app/dashboard/agents/[id]/page.tsx:19`)
- `@/components/ui/card` (import declaration in `frontend/src/app/dashboard/agents/[id]/page.tsx:20`)
- `@/components/ui/form` (import declaration in `frontend/src/app/dashboard/agents/[id]/page.tsx:21`)
- `@/components/ui/input` (import declaration in `frontend/src/app/dashboard/agents/[id]/page.tsx:30`)
- `@/components/ui/textarea` (import declaration in `frontend/src/app/dashboard/agents/[id]/page.tsx:31`)
- `@/components/ui/select` (import declaration in `frontend/src/app/dashboard/agents/[id]/page.tsx:32`)
- `@/components/ui/separator` (import declaration in `frontend/src/app/dashboard/agents/[id]/page.tsx:39`)
- `@/components/ui/tabs` (import declaration in `frontend/src/app/dashboard/agents/[id]/page.tsx:40`)
- `@/components/ui/switch` (import declaration in `frontend/src/app/dashboard/agents/[id]/page.tsx:41`)
- `@/components/ui/badge` (import declaration in `frontend/src/app/dashboard/agents/[id]/page.tsx:42`)
- `lucide-react` (import declaration in `frontend/src/app/dashboard/agents/[id]/page.tsx:43`)
- `@/lib/api` (import declaration in `frontend/src/app/dashboard/agents/[id]/page.tsx:55`)
- `@/lib/languages` (import declaration in `frontend/src/app/dashboard/agents/[id]/page.tsx:56`)
- `@/lib/integrations` (import declaration in `frontend/src/app/dashboard/agents/[id]/page.tsx:57`)
- `@/components/ui/collapsible` (import declaration in `frontend/src/app/dashboard/agents/[id]/page.tsx:58`)
- `@/components/ui/alert-dialog` (import declaration in `frontend/src/app/dashboard/agents/[id]/page.tsx:60`)
- `@/components/ui/checkbox` (import declaration in `frontend/src/app/dashboard/agents/[id]/page.tsx:71`)
- `@/components/ui/slider` (import declaration in `frontend/src/app/dashboard/agents/[id]/page.tsx:72`)
- `@/lib/utils` (import declaration in `frontend/src/app/dashboard/agents/[id]/page.tsx:73`)
- `./prompt-character-target` (import declaration in `frontend/src/app/dashboard/agents/[id]/page.tsx:74`)
- `@/components/ui/info-tooltip` (import declaration in `frontend/src/app/dashboard/agents/[id]/page.tsx:79`)

## History

- **Last touched:** commit `e5c4bbaf1606727b39ad6372c9e353ab99fc0d70` by Greg on 2026-08-13
- **Commit subject:** Add prompt target interaction coverage

## Sources

- `frontend/src/app/dashboard/agents/[id]/page.tsx:1`
