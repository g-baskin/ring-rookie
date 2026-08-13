---
type: entity
title: "NEXT_DIST_DIR"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
entity_type: env-var
path: "frontend/next.config.ts"
language: ts
name: "NEXT_DIST_DIR"
last_commit_hash: "bb80c70ea36071bdec833be0fb3d9717d06f6f67"
is_required: true
read_at:
  - "frontend/next.config.ts:10"
depends_on: []
used_by: []
tested_by: []
tags:
  - entity
  - env-var
related: []
sources: []
---

# NEXT_DIST_DIR

## Overview

Environment variable read by TypeScript/JavaScript code, first observed at `frontend/next.config.ts:10`.

## Required vs optional

The static call-site heuristic classifies this variable as **required**. Each read site remains authoritative for runtime behavior.

## Read sites

- `frontend/next.config.ts:10`

## Connections

No dependency relationship is asserted beyond the evidenced read sites above.

## History

- **First-file last touched:** commit `bb80c70ea36071bdec833be0fb3d9717d06f6f67` by Greg on 2026-08-13
- **Commit subject:** feat: add persistent hot-reload development stack

## Sources

- `frontend/next.config.ts:10`
