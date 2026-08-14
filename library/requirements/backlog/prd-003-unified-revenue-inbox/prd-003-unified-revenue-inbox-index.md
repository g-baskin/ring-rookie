# PRD-003: Unified Revenue Inbox / Today Queue

> **Status:** Backlog — Discovery Gate  
> **Priority:** P0 discovery; implementation uncommitted  
> **Effort:** S for validation; delivery estimate deferred  
> **Schema changes:** None during discovery

## Overview

Ring Rookie's revenue work is distributed across calls, conversations, contacts, appointments, campaigns, compliance, and agent configuration. This PRD tests whether operators repeatedly use one evidence-backed, actionable briefing before Ring Rookie commits to a durable queue, task model, or AI-ranking system.

**Discovery rule:** this PRD authorizes research only. Passing the gate authorizes validated delivery planning—not coding by default.

## Desired outcome

Representative operators consistently identify and complete high-value follow-up work from one ordered briefing while reducing time-to-first-action and context switching, without cross-workspace exposure or unauthorized action.

## Assumptions

- Daily prioritization and fragmentation are material operator pains.
- Calls, conversations, appointments, campaign follow-ups, compliance blocks, and configuration gaps can share one queue.
- Source evidence, recency, rationale, and confidence make recommendations trustworthy.
- Act, complete, defer, dismiss, and reassign cover the core workflow.
- Existing read APIs can support a manual study without a new persistent task model.

## Non-goals

- Building queue/task tables, autonomous agents, workflow infrastructure, tickets, Accounts, forecasting, or connectors during discovery.
- Sending messages, placing calls, changing records, or mutating campaign state from shadow output.
- Copying Tribunal source or reproducing its distinctive design.

## Smallest validation

Recruit 5–8 representative operators across at least two profiles. Observe at least 3 baseline business days, then run a 10-business-day concierge briefing with 5–15 read-only items per participant per day. Each item records an opaque participant/workspace key, source pointer, evidence timestamp, rationale, confidence, proposed action, disposition, and outcome.

Shadow-mode recommendations are evaluated but never shown as facts or executed. Any cross-workspace/entity mismatch or unauthorized consequential action stops the study.

## Gate thresholds

All safety/data criteria and at least four of five behavior/value criteria must pass.

### Safety/data — all required

- Zero cross-workspace or entity-linkage incidents.
- Zero autonomous or unauthorized consequential actions.
- At least 95% of surfaced items link to current, inspectable source records; invalid/stale items remain below 5%.
- Every item records evidence, rationale, confidence, and disposition.

### Behavior/value — four of five required

- At least 5 participants finish; at least 70% use the briefing on 7 of 10 intervention days.
- Median time-to-first-meaningful-action improves by at least 25%.
- Median context switches per completed priority item decrease by at least 30%.
- At least 60% of items are acted on, completed, or explicitly deferred; fewer than 20% are dismissed as wrong/irrelevant.
- At least 70% request continued access and rate usefulness at least 4/5.

## Decision

- **Pass:** revise this PRD with validated requirements before moving it to `in-work/`.
- **Pivot:** narrow the segment or item taxonomy, then rerun.
- **Stop:** archive the rationale; do not implement the queue.

## Dependencies and risks

- A named discovery owner, representative participants, consent, and approved read-only production-data access.
- PII-minimized research storage with access and deletion dates.
- Existing evidence sources: `backend/app/api/calls.py`, `backend/app/api/conversations.py`, `backend/app/api/crm.py`, `backend/app/api/campaigns.py`, `backend/app/api/compliance.py`, and `frontend/src/app/dashboard/page.tsx`.
- Risks include researcher-ranking bias, power-user sampling, stale evidence, activity-over-value optimization, scope expansion, and PII leakage.

## Discovery acceptance criteria

- Study owner, segment, consent, retention, metrics, and stop rules are frozen before recruitment.
- 5–8 operators across at least two profiles are recruited.
- Baseline and intervention periods complete with traceable, workspace-safe records.
- Quantitative results are calculated against every threshold with missing data and attrition disclosed.
- Qualitative findings include observed stories, trust evidence, ignored work, and specialist-surface fallback.
- A pass/pivot/stop decision is recorded; no validation is inferred from this plan alone.

## Resume checkpoint

The execution pack is prepared but unexecuted at [`library/discovery/README.md`](../../../discovery/README.md). Next owner: `discovery-research-guardian` + `discovery-research-weapon`. Do not hand off to delivery guardians until the gate decision is recorded and `library-guardian` revises this PRD.

## Related

- [Tribunal feature-gap discovery and roadmap](../../../knowledge/private/product/tribunal-feature-gap-discovery-and-roadmap.md)
- [External reference repository](https://github.com/Gahroot/the-tribunal)
