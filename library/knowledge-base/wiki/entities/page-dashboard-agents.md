---
type: entity
title: "page.tsx"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
entity_type: module
path: "frontend/src/app/dashboard/agents/page.tsx"
language: tsx
last_commit_hash: "755552f1b92b3c760799720f2c250e7f0a6bf0bd"
depends_on: []
used_by: []
tested_by: []
exports:
  - "[[entities/agents-page]]"
imports:
  - "react"
  - "@/components/ui/button"
  - "@/components/ui/card"
  - "@/components/ui/badge"
  - "lucide-react"
  - "next/link"
  - "next/navigation"
  - "@tanstack/react-query"
  - "sonner"
  - "@/lib/api/agents"
  - "@/components/ui/dropdown-menu"
  - "@/components/ui/alert-dialog"
  - "@/components/make-call-dialog"
  - "@/components/embed-agent-dialog"
  - "@/components/ui/select"
  - "@/lib/api"
tags:
  - entity
  - module
related:
  - "[[entities/agents-page]]"
sources: []
---

# page.tsx

## Overview

Source module at `frontend/src/app/dashboard/agents/page.tsx:1` exporting 1 documented code entities.

## Exports

- [[entities/agents-page]] — react-component, declaration at `frontend/src/app/dashboard/agents/page.tsx:69`

## Imports

- `react` (import declaration in `frontend/src/app/dashboard/agents/page.tsx:3`)
- `@/components/ui/button` (import declaration in `frontend/src/app/dashboard/agents/page.tsx:4`)
- `@/components/ui/card` (import declaration in `frontend/src/app/dashboard/agents/page.tsx:5`)
- `@/components/ui/badge` (import declaration in `frontend/src/app/dashboard/agents/page.tsx:6`)
- `lucide-react` (import declaration in `frontend/src/app/dashboard/agents/page.tsx:7`)
- `next/link` (import declaration in `frontend/src/app/dashboard/agents/page.tsx:17`)
- `next/navigation` (import declaration in `frontend/src/app/dashboard/agents/page.tsx:18`)
- `@tanstack/react-query` (import declaration in `frontend/src/app/dashboard/agents/page.tsx:19`)
- `sonner` (import declaration in `frontend/src/app/dashboard/agents/page.tsx:20`)
- `@/lib/api/agents` (import declaration in `frontend/src/app/dashboard/agents/page.tsx:21`)
- `@/components/ui/dropdown-menu` (import declaration in `frontend/src/app/dashboard/agents/page.tsx:22`)
- `@/components/ui/alert-dialog` (import declaration in `frontend/src/app/dashboard/agents/page.tsx:29`)
- `@/components/make-call-dialog` (import declaration in `frontend/src/app/dashboard/agents/page.tsx:39`)
- `@/components/embed-agent-dialog` (import declaration in `frontend/src/app/dashboard/agents/page.tsx:40`)
- `@/components/ui/select` (import declaration in `frontend/src/app/dashboard/agents/page.tsx:41`)
- `@/lib/api` (import declaration in `frontend/src/app/dashboard/agents/page.tsx:48`)

## History

- **Last touched:** commit `755552f1b92b3c760799720f2c250e7f0a6bf0bd` by kenkaiii on 2025-12-05
- **Commit subject:** Fix agents user_id type mismatch from UUID to integer

## Sources

- `frontend/src/app/dashboard/agents/page.tsx:1`
