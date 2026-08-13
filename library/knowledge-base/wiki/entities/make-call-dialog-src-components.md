---
type: entity
title: "make-call-dialog.tsx"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
entity_type: module
path: "frontend/src/components/make-call-dialog.tsx"
language: tsx
last_commit_hash: "755552f1b92b3c760799720f2c250e7f0a6bf0bd"
depends_on: []
used_by: []
tested_by: []
exports:
  - "[[entities/make-call-dialog]]"
imports:
  - "react"
  - "@tanstack/react-query"
  - "sonner"
  - "lucide-react"
  - "@/components/ui/dialog"
  - "@/components/ui/button"
  - "@/components/ui/input"
  - "@/components/ui/label"
  - "@/components/ui/select"
  - "@/lib/api/telephony"
  - "@/lib/api/agents"
  - "@/lib/api"
tags:
  - entity
  - module
related:
  - "[[entities/make-call-dialog]]"
sources: []
---

# make-call-dialog.tsx

## Overview

Source module at `frontend/src/components/make-call-dialog.tsx:1` exporting 1 documented code entities.

## Exports

- [[entities/make-call-dialog]] — react-component, declaration at `frontend/src/components/make-call-dialog.tsx:43`

## Imports

- `react` (import declaration in `frontend/src/components/make-call-dialog.tsx:3`)
- `@tanstack/react-query` (import declaration in `frontend/src/components/make-call-dialog.tsx:4`)
- `sonner` (import declaration in `frontend/src/components/make-call-dialog.tsx:5`)
- `lucide-react` (import declaration in `frontend/src/components/make-call-dialog.tsx:6`)
- `@/components/ui/dialog` (import declaration in `frontend/src/components/make-call-dialog.tsx:7`)
- `@/components/ui/button` (import declaration in `frontend/src/components/make-call-dialog.tsx:15`)
- `@/components/ui/input` (import declaration in `frontend/src/components/make-call-dialog.tsx:16`)
- `@/components/ui/label` (import declaration in `frontend/src/components/make-call-dialog.tsx:17`)
- `@/components/ui/select` (import declaration in `frontend/src/components/make-call-dialog.tsx:18`)
- `@/lib/api/telephony` (import declaration in `frontend/src/components/make-call-dialog.tsx:25`)
- `@/lib/api/agents` (import declaration in `frontend/src/components/make-call-dialog.tsx:26`)
- `@/lib/api` (import declaration in `frontend/src/components/make-call-dialog.tsx:27`)

## History

- **Last touched:** commit `755552f1b92b3c760799720f2c250e7f0a6bf0bd` by kenkaiii on 2025-12-05
- **Commit subject:** Fix agents user_id type mismatch from UUID to integer

## Sources

- `frontend/src/components/make-call-dialog.tsx:1`
