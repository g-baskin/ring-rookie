---
type: entity
title: "PrivacySettings"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
entity_type: data-model
path: "frontend/src/lib/api/compliance.ts"
language: ts
last_commit_hash: "b0f0d5135af06717a3d59dbcddc2e7641472314b"
depends_on: []
used_by: []
tested_by: []
schema_library: typescript
fields:
  - "privacy_policy_url"
  - "privacy_policy_accepted_at"
  - "data_retention_days"
  - "openai_dpa_signed"
  - "openai_dpa_signed_at"
  - "telnyx_dpa_signed"
  - "telnyx_dpa_signed_at"
  - "deepgram_dpa_signed"
  - "deepgram_dpa_signed_at"
  - "elevenlabs_dpa_signed"
  - "elevenlabs_dpa_signed_at"
  - "ccpa_opt_out"
  - "ccpa_opt_out_at"
  - "last_data_export_at"
tags:
  - entity
  - data-model
related:
  - "[[entities/compliance-lib-api]]"
sources: []
---

# PrivacySettings

## Overview

Exported data model declared by the [[entities/compliance-lib-api]] module at `frontend/src/lib/api/compliance.ts:28`.

## Signature / Definition

```ts
export interface PrivacySettings
```

## Behavior

The source declaration begins at `frontend/src/lib/api/compliance.ts:28`; implementation behavior and side effects remain authoritative in that declaration.

## Connections

- **Defined by:** [[entities/compliance-lib-api]] (`frontend/src/lib/api/compliance.ts:28`)

## Tested by

No test relationship is asserted without direct in-file evidence.

## History

- **Last touched:** commit `b0f0d5135af06717a3d59dbcddc2e7641472314b` by kenkaiii on 2025-11-28
- **Commit subject:** Add GDPR/CCPA compliance features with privacy controls

## Sources

- `frontend/src/lib/api/compliance.ts:28`
