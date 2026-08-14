---
type: entity
title: "API_INTERNAL_URL"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
entity_type: env-var
path: "frontend/next.config.ts"
language: ts
name: "API_INTERNAL_URL"
last_commit_hash: "bb80c70ea36071bdec833be0fb3d9717d06f6f67"
is_required: false
read_at:
  - "frontend/next.config.ts:39"
  - "frontend/next.config.ts:43"
depends_on: []
used_by: []
tested_by: []
tags:
  - entity
  - env-var
related: []
sources: []
---

# API_INTERNAL_URL

## Overview

Environment variable read by TypeScript/JavaScript code, first observed at `frontend/next.config.ts:39`.

## Required vs optional

The static call-site heuristic classifies this variable as **optional/defaulted**. Each read site remains authoritative for runtime behavior.

## Read sites

- `frontend/next.config.ts:39`
- `frontend/next.config.ts:43`

## Connections

No dependency relationship is asserted beyond the evidenced read sites above.

## History

- **First-file last touched:** commit `bb80c70ea36071bdec833be0fb3d9717d06f6f67` by Greg on 2026-08-13
- **Commit subject:** feat: add persistent hot-reload development stack

## Sources

- `frontend/next.config.ts:39`
- `frontend/next.config.ts:43`
