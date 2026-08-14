---
type: entity
title: "NEXT_PUBLIC_API_URL"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
entity_type: env-var
path: "frontend/next.config.ts"
language: ts
name: "NEXT_PUBLIC_API_URL"
last_commit_hash: "bb80c70ea36071bdec833be0fb3d9717d06f6f67"
is_required: false
read_at:
  - "frontend/next.config.ts:39"
  - "frontend/next.config.ts:43"
  - "frontend/src/app/dashboard/phone-numbers/page.tsx:607"
  - "frontend/src/app/dashboard/test/page.tsx:540"
  - "frontend/src/app/dashboard/test/page.tsx:642"
  - "frontend/src/hooks/use-auth.tsx:23"
  - "frontend/src/lib/__tests__/api.test.ts:152"
  - "frontend/src/lib/__tests__/api.test.ts:158"
  - "frontend/src/lib/__tests__/api.test.ts:159"
  - "frontend/src/lib/api.ts:3"
  - "frontend/src/lib/api/agents.ts:5"
  - "frontend/src/lib/api/calls.ts:5"
  - "frontend/src/lib/api/conversations.ts:5"
  - "frontend/src/lib/api/lessons.ts:1"
  - "frontend/src/lib/api/phone-numbers.ts:5"
  - "frontend/src/lib/api/settings.ts:5"
  - "frontend/src/lib/api/telephony.ts:5"
depends_on: []
used_by: []
tested_by: []
tags:
  - entity
  - env-var
related: []
sources: []
---

# NEXT_PUBLIC_API_URL

## Overview

Environment variable read by TypeScript/JavaScript code, first observed at `frontend/next.config.ts:39`.

## Required vs optional

This variable is **optional/defaulted**: production call sites fall back to `http://localhost:8000` when it is absent (`frontend/next.config.ts:39`, `frontend/src/lib/api.ts:3`). The test assignment at `frontend/src/lib/__tests__/api.test.ts:158` does not make it runtime-required.

## Read sites

- `frontend/next.config.ts:39`
- `frontend/next.config.ts:43`
- `frontend/src/app/dashboard/phone-numbers/page.tsx:607`
- `frontend/src/app/dashboard/test/page.tsx:540`
- `frontend/src/app/dashboard/test/page.tsx:642`
- `frontend/src/hooks/use-auth.tsx:23`
- `frontend/src/lib/__tests__/api.test.ts:152`
- `frontend/src/lib/__tests__/api.test.ts:158`
- `frontend/src/lib/__tests__/api.test.ts:159`
- `frontend/src/lib/api.ts:3`
- `frontend/src/lib/api/agents.ts:5`
- `frontend/src/lib/api/calls.ts:5`
- `frontend/src/lib/api/conversations.ts:5`
- `frontend/src/lib/api/lessons.ts:1`
- `frontend/src/lib/api/phone-numbers.ts:5`
- `frontend/src/lib/api/settings.ts:5`
- `frontend/src/lib/api/telephony.ts:5`

## Connections

No dependency relationship is asserted beyond the evidenced read sites above.

## History

- **First-file last touched:** commit `bb80c70ea36071bdec833be0fb3d9717d06f6f67` by Greg on 2026-08-13
- **Commit subject:** feat: add persistent hot-reload development stack

## Sources

- `frontend/next.config.ts:39`
- `frontend/next.config.ts:43`
- `frontend/src/app/dashboard/phone-numbers/page.tsx:607`
- `frontend/src/app/dashboard/test/page.tsx:540`
- `frontend/src/app/dashboard/test/page.tsx:642`
- `frontend/src/hooks/use-auth.tsx:23`
- `frontend/src/lib/__tests__/api.test.ts:152`
- `frontend/src/lib/__tests__/api.test.ts:158`
- `frontend/src/lib/__tests__/api.test.ts:159`
- `frontend/src/lib/api.ts:3`
- `frontend/src/lib/api/agents.ts:5`
- `frontend/src/lib/api/calls.ts:5`
- `frontend/src/lib/api/conversations.ts:5`
- `frontend/src/lib/api/lessons.ts:1`
- `frontend/src/lib/api/phone-numbers.ts:5`
- `frontend/src/lib/api/settings.ts:5`
- `frontend/src/lib/api/telephony.ts:5`
