---
type: entity
title: "campaigns.ts"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
entity_type: module
path: "frontend/src/lib/api/campaigns.ts"
language: ts
last_commit_hash: "e2de7645c7daa2883f6027f47da6052bf4ed0055"
depends_on: []
used_by: []
tested_by: []
exports:
  - "[[entities/list-campaigns]]"
  - "[[entities/get-campaign]]"
  - "[[entities/create-campaign]]"
  - "[[entities/update-campaign]]"
  - "[[entities/delete-campaign]]"
  - "[[entities/get-campaign-contacts]]"
  - "[[entities/add-contacts-to-campaign]]"
  - "[[entities/remove-contact-from-campaign]]"
  - "[[entities/start-campaign]]"
  - "[[entities/pause-campaign]]"
  - "[[entities/stop-campaign]]"
  - "[[entities/restart-campaign]]"
  - "[[entities/get-campaign-stats]]"
  - "[[entities/get-disposition-stats]]"
  - "[[entities/update-contact-disposition]]"
  - "[[entities/get-disposition-options]]"
  - "[[entities/preview-contacts-by-filter]]"
  - "[[entities/add-contacts-by-filter]]"
  - "[[entities/campaign-api]]"
  - "[[entities/campaign-status]]"
  - "[[entities/campaign-contact]]"
  - "[[entities/campaign-stats]]"
  - "[[entities/create-campaign-request]]"
  - "[[entities/update-campaign-request]]"
  - "[[entities/disposition-stats]]"
  - "[[entities/update-disposition-request]]"
  - "[[entities/disposition-option]]"
  - "[[entities/disposition-options]]"
  - "[[entities/add-contacts-by-filter-request]]"
  - "[[entities/filtered-contacts-response]]"
  - "[[entities/add-contacts-by-filter-response]]"
imports:
  - "@/lib/api"
tags:
  - entity
  - module
related:
  - "[[entities/list-campaigns]]"
  - "[[entities/get-campaign]]"
  - "[[entities/create-campaign]]"
  - "[[entities/update-campaign]]"
  - "[[entities/delete-campaign]]"
  - "[[entities/get-campaign-contacts]]"
  - "[[entities/add-contacts-to-campaign]]"
  - "[[entities/remove-contact-from-campaign]]"
  - "[[entities/start-campaign]]"
  - "[[entities/pause-campaign]]"
  - "[[entities/stop-campaign]]"
  - "[[entities/restart-campaign]]"
  - "[[entities/get-campaign-stats]]"
  - "[[entities/get-disposition-stats]]"
  - "[[entities/update-contact-disposition]]"
  - "[[entities/get-disposition-options]]"
  - "[[entities/preview-contacts-by-filter]]"
  - "[[entities/add-contacts-by-filter]]"
  - "[[entities/campaign-api]]"
  - "[[entities/campaign-status]]"
  - "[[entities/campaign-contact]]"
  - "[[entities/campaign-stats]]"
  - "[[entities/create-campaign-request]]"
  - "[[entities/update-campaign-request]]"
  - "[[entities/disposition-stats]]"
  - "[[entities/update-disposition-request]]"
  - "[[entities/disposition-option]]"
  - "[[entities/disposition-options]]"
  - "[[entities/add-contacts-by-filter-request]]"
  - "[[entities/filtered-contacts-response]]"
  - "[[entities/add-contacts-by-filter-response]]"
sources: []
---

# campaigns.ts

## Overview

Source module at `frontend/src/lib/api/campaigns.ts:1` exporting 31 documented code entities.

## Exports

- [[entities/list-campaigns]] — function, declaration at `frontend/src/lib/api/campaigns.ts:152`
- [[entities/get-campaign]] — function, declaration at `frontend/src/lib/api/campaigns.ts:168`
- [[entities/create-campaign]] — function, declaration at `frontend/src/lib/api/campaigns.ts:176`
- [[entities/update-campaign]] — function, declaration at `frontend/src/lib/api/campaigns.ts:184`
- [[entities/delete-campaign]] — function, declaration at `frontend/src/lib/api/campaigns.ts:195`
- [[entities/get-campaign-contacts]] — function, declaration at `frontend/src/lib/api/campaigns.ts:202`
- [[entities/add-contacts-to-campaign]] — function, declaration at `frontend/src/lib/api/campaigns.ts:221`
- [[entities/remove-contact-from-campaign]] — function, declaration at `frontend/src/lib/api/campaigns.ts:234`
- [[entities/start-campaign]] — function, declaration at `frontend/src/lib/api/campaigns.ts:244`
- [[entities/pause-campaign]] — function, declaration at `frontend/src/lib/api/campaigns.ts:252`
- [[entities/stop-campaign]] — function, declaration at `frontend/src/lib/api/campaigns.ts:260`
- [[entities/restart-campaign]] — function, declaration at `frontend/src/lib/api/campaigns.ts:268`
- [[entities/get-campaign-stats]] — function, declaration at `frontend/src/lib/api/campaigns.ts:276`
- [[entities/get-disposition-stats]] — function, declaration at `frontend/src/lib/api/campaigns.ts:284`
- [[entities/update-contact-disposition]] — function, declaration at `frontend/src/lib/api/campaigns.ts:292`
- [[entities/get-disposition-options]] — function, declaration at `frontend/src/lib/api/campaigns.ts:307`
- [[entities/preview-contacts-by-filter]] — function, declaration at `frontend/src/lib/api/campaigns.ts:333`
- [[entities/add-contacts-by-filter]] — function, declaration at `frontend/src/lib/api/campaigns.ts:344`
- [[entities/campaign-api]] — data-model, declaration at `frontend/src/lib/api/campaigns.ts:7`
- [[entities/campaign-status]] — data-model, declaration at `frontend/src/lib/api/campaigns.ts:44`
- [[entities/campaign-contact]] — data-model, declaration at `frontend/src/lib/api/campaigns.ts:52`
- [[entities/campaign-stats]] — data-model, declaration at `frontend/src/lib/api/campaigns.ts:71`
- [[entities/create-campaign-request]] — data-model, declaration at `frontend/src/lib/api/campaigns.ts:86`
- [[entities/update-campaign-request]] — data-model, declaration at `frontend/src/lib/api/campaigns.ts:107`
- [[entities/disposition-stats]] — data-model, declaration at `frontend/src/lib/api/campaigns.ts:125`
- [[entities/update-disposition-request]] — data-model, declaration at `frontend/src/lib/api/campaigns.ts:131`
- [[entities/disposition-option]] — data-model, declaration at `frontend/src/lib/api/campaigns.ts:137`
- [[entities/disposition-options]] — data-model, declaration at `frontend/src/lib/api/campaigns.ts:142`
- [[entities/add-contacts-by-filter-request]] — data-model, declaration at `frontend/src/lib/api/campaigns.ts:313`
- [[entities/filtered-contacts-response]] — data-model, declaration at `frontend/src/lib/api/campaigns.ts:319`
- [[entities/add-contacts-by-filter-response]] — data-model, declaration at `frontend/src/lib/api/campaigns.ts:325`

## Imports

- `@/lib/api` (import declaration in `frontend/src/lib/api/campaigns.ts:5`)

## History

- **Last touched:** commit `e2de7645c7daa2883f6027f47da6052bf4ed0055` by kenkaiii on 2025-12-04
- **Commit subject:** Add outbound campaign dialer with CRM integration and telephony improvements

## Sources

- `frontend/src/lib/api/campaigns.ts:1`
