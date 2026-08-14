# Compliance Register

Snapshot: 2026-08-13 · Commit reviewed: `e5c4bba` + working tree · Reviewed by: GG Coder compliance-guard · **NOT LEGAL ADVICE**

## Assumed exposure profile

- **Confirmed:** authenticated product handling voice-derived transcripts and user-authored improvement notes.
- **Confirmed:** lessons store summaries, source identifiers, ownership/workspace identifiers, and timestamps; they do not duplicate transcripts.
- **Confirmed:** local CSV/JSON exports are initiated by the authenticated user and contain no transcript body.
- **Assumed:** the product is internet-accessible worldwide and may process real personal data.
- **Assumed:** no legal transcript retention duration has been selected; this feature does not invent one.

## Findings

| ID | Severity | Trigger | Evidence (RUNTIME / CODE / DEDUCED) | Obligation | Status | Guard |
|---|---|---|---|---|---|---|
| LESSON-001 | BLOCKER | Transcript-derived records could cross account/workspace boundaries | CODE: `backend/app/api/lessons.py` scopes authorization, source calls, CRUD, list, and export | Restrict access to the owning user and authorized workspace | Implemented | API tests deny a second user's agent and reject unowned source calls |
| LESSON-002 | HIGH | CSV text may execute spreadsheet formulas | RUNTIME: focused API test exports `=HYPERLINK` and `+change prompt` with a tab prefix | Neutralize formula-leading cells before download | Implemented | `test_lesson_crud_and_exports` asserts neutralization |
| LESSON-003 | HIGH | Transcript-derived notes can multiply unnecessary personal data | CODE: UI warns against personal details; lesson model stores summaries without transcript bodies | Data minimization and purpose limitation | Implemented | API response/export tests assert transcript content is absent |
| LESSON-004 | HIGH | Users need deletion of derived notes | RUNTIME: focused API tests delete a lesson and verify source-call cascade | Provide deletion and propagate source deletion | Implemented | CRUD and cascade tests |
| LESSON-005 | MEDIUM | Transcript retention duration is undefined | DEDUCED: no product retention schedule was found or supplied | Select and disclose a defensible retention period | Open | Product/legal decision; do not claim a duration |
| LESSON-006 | MEDIUM | Transcript and lesson data are user-derived personal data | CODE: authenticated storage/export paths exist | Ensure privacy notice and processor/vendor disclosures describe these purposes | Open | Legal/privacy-document review |

## Implemented in this pass

- Added agent/workspace/user authorization at one API chokepoint and revalidated source-call ownership on create.
- Stored concise editable lesson fields linked to—but separate from—the source transcript.
- Added immediate lesson deletion and database cascade when its source call is deleted.
- Added explicit local CSV/JSON downloads; CSV cells beginning with `=`, `+`, `-`, or `@` after whitespace are tab-prefixed.
- Kept transcript and lesson content out of new logs and excluded transcript bodies from lesson exports.
- Added plain-text length bounds and rendered lesson content as React text, not HTML.

## Open — needs a decision from you

- Choose a transcript and lesson retention schedule, then disclose and automate it. Until selected, users can delete lessons immediately and source-call deletion cascades.

## Needs a lawyer

- Review the privacy notice and data-processing terms for voice/transcript processing, subprocessors, international transfers, and the selected retention schedule before relying on them in production.

## Re-verify before relying (date-sensitive)

- Re-run authorization and export tests after any workspace-role or call-retention change.
- This scoped register covers the lessons feature, not a full product-wide legal, accessibility, or security audit.
