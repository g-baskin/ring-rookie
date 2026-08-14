---
type: entity
title: "compliance.ts"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
entity_type: module
path: "frontend/src/lib/api/compliance.ts"
language: ts
last_commit_hash: "b0f0d5135af06717a3d59dbcddc2e7641472314b"
depends_on: []
used_by: []
tested_by: []
exports:
  - "[[entities/fetch-compliance-status]]"
  - "[[entities/fetch-privacy-settings]]"
  - "[[entities/update-privacy-settings]]"
  - "[[entities/record-consent]]"
  - "[[entities/export-user-data]]"
  - "[[entities/ccpa-opt-out]]"
  - "[[entities/ccpa-opt-in]]"
  - "[[entities/withdraw-consent]]"
  - "[[entities/delete-user-data]]"
  - "[[entities/compliance-check-item]]"
  - "[[entities/compliance-status]]"
  - "[[entities/compliance-overview]]"
  - "[[entities/privacy-settings-api]]"
  - "[[entities/update-privacy-settings-request]]"
  - "[[entities/data-export]]"
  - "[[entities/data-deletion-response]]"
imports:
  - "@/lib/api"
tags:
  - entity
  - module
related:
  - "[[entities/fetch-compliance-status]]"
  - "[[entities/fetch-privacy-settings]]"
  - "[[entities/update-privacy-settings]]"
  - "[[entities/record-consent]]"
  - "[[entities/export-user-data]]"
  - "[[entities/ccpa-opt-out]]"
  - "[[entities/ccpa-opt-in]]"
  - "[[entities/withdraw-consent]]"
  - "[[entities/delete-user-data]]"
  - "[[entities/compliance-check-item]]"
  - "[[entities/compliance-status]]"
  - "[[entities/compliance-overview]]"
  - "[[entities/privacy-settings-api]]"
  - "[[entities/update-privacy-settings-request]]"
  - "[[entities/data-export]]"
  - "[[entities/data-deletion-response]]"
sources: []
---

# compliance.ts

## Overview

Source module at `frontend/src/lib/api/compliance.ts:1` exporting 16 documented code entities.

## Exports

- [[entities/fetch-compliance-status]] — function, declaration at `frontend/src/lib/api/compliance.ts:72`
- [[entities/fetch-privacy-settings]] — function, declaration at `frontend/src/lib/api/compliance.ts:80`
- [[entities/update-privacy-settings]] — function, declaration at `frontend/src/lib/api/compliance.ts:88`
- [[entities/record-consent]] — function, declaration at `frontend/src/lib/api/compliance.ts:98`
- [[entities/export-user-data]] — function, declaration at `frontend/src/lib/api/compliance.ts:112`
- [[entities/ccpa-opt-out]] — function, declaration at `frontend/src/lib/api/compliance.ts:120`
- [[entities/ccpa-opt-in]] — function, declaration at `frontend/src/lib/api/compliance.ts:128`
- [[entities/withdraw-consent]] — function, declaration at `frontend/src/lib/api/compliance.ts:136`
- [[entities/delete-user-data]] — function, declaration at `frontend/src/lib/api/compliance.ts:152`
- [[entities/compliance-check-item]] — data-model, declaration at `frontend/src/lib/api/compliance.ts:7`
- [[entities/compliance-status]] — data-model, declaration at `frontend/src/lib/api/compliance.ts:16`
- [[entities/compliance-overview]] — data-model, declaration at `frontend/src/lib/api/compliance.ts:23`
- [[entities/privacy-settings-api]] — data-model, declaration at `frontend/src/lib/api/compliance.ts:28`
- [[entities/update-privacy-settings-request]] — data-model, declaration at `frontend/src/lib/api/compliance.ts:45`
- [[entities/data-export]] — data-model, declaration at `frontend/src/lib/api/compliance.ts:55`
- [[entities/data-deletion-response]] — data-model, declaration at `frontend/src/lib/api/compliance.ts:144`

## Imports

- `@/lib/api` (import declaration in `frontend/src/lib/api/compliance.ts:5`)

## History

- **Last touched:** commit `b0f0d5135af06717a3d59dbcddc2e7641472314b` by kenkaiii on 2025-11-28
- **Commit subject:** Add GDPR/CCPA compliance features with privacy controls

## Sources

- `frontend/src/lib/api/compliance.ts:1`
