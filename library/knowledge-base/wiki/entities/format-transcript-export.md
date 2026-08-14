---
type: entity
title: "formatTranscriptExport"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
entity_type: function
path: "frontend/src/lib/transcript-export.ts"
language: ts
last_commit_hash: "c5a3703d7815d1eabc5418f8eb56e292ef623b58"
depends_on: []
used_by: []
tested_by: []
tags:
  - entity
  - function
related:
  - "[[entities/transcript-export-src-lib]]"
sources: []
---

# formatTranscriptExport

## Overview

Exported function declared by the [[entities/transcript-export-src-lib]] module at `frontend/src/lib/transcript-export.ts:7`.

## Signature / Definition

```ts
export function formatTranscriptExport(
  items: ExportableTranscriptItem[],
  agentName: string | undefined,
): string;
```

## Behavior

The source declaration begins at `frontend/src/lib/transcript-export.ts:7`; implementation behavior and side effects remain authoritative in that declaration.

## Connections

- **Defined by:** [[entities/transcript-export-src-lib]] (`frontend/src/lib/transcript-export.ts:7`)

## Tested by

No test relationship is asserted without direct in-file evidence.

## History

- **Last touched:** commit `c5a3703d7815d1eabc5418f8eb56e292ef623b58` by Greg on 2026-08-13
- **Commit subject:** Fix OpenAI OAuth Realtime sessions and transcript export

## Sources

- `frontend/src/lib/transcript-export.ts:7`
