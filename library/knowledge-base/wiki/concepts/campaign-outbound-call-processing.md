---
type: concept
title: "Campaign outbound call processing"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
complexity: advanced
domain: "telephony"
aliases: []
tags:
  - concept
  - telephony
related:
  - "[[entities/campaign-worker]]"
sources: []
---

# Campaign outbound call processing

## Overview

A background worker owns campaign polling and outbound-call orchestration. (`backend/app/services/campaign_worker.py:39`)

## Flow and invariants

- A background worker owns campaign polling and outbound-call orchestration. (`backend/app/services/campaign_worker.py:39`)
- The worker repeatedly processes running campaigns on a polling interval. (`backend/app/services/campaign_worker.py:70`)
- Campaign processing enforces schedules, concurrency, rate limits, locking, retry state, and provider selection. (`backend/app/services/campaign_worker.py:111`)

## Connections

[[entities/campaign-worker]] owns the polling loop and outbound-call orchestration described here (`backend/app/services/campaign_worker.py:39`, `backend/app/services/campaign_worker.py:70`).

## Sources

- `backend/app/services/campaign_worker.py:39`
- `backend/app/services/campaign_worker.py:70`
- `backend/app/services/campaign_worker.py:111`
