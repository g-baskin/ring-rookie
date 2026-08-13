---
type: concept
title: "Workspace-scoped resource isolation"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
complexity: advanced
domain: "multi-tenancy"
aliases: []
tags:
  - concept
  - multi-tenancy
related:
  - "[[entities/phone-numbers]]"
  - "[[entities/chatgpt-oauth-services]]"
sources: []
---

# Workspace-scoped resource isolation

## Overview

Workspace access is checked by matching both workspace UUID and owning integer user ID. (`backend/app/api/phone_numbers.py:22`)

## Flow and invariants

- Workspace access is checked by matching both workspace UUID and owning integer user ID. (`backend/app/api/phone_numbers.py:22`)
- OAuth state binds user and optional workspace context to a one-time PKCE authorization request. (`backend/app/services/chatgpt_oauth.py:88`)
- Credential retrieval is scoped by mapped user UUID and optional workspace UUID. (`backend/app/services/chatgpt_oauth.py:239`)

## Connections

[[entities/phone-numbers]] contains the workspace ownership check (`backend/app/api/phone_numbers.py:22`). [[entities/chatgpt-oauth-services]] binds OAuth authorization and credential retrieval to user/workspace context (`backend/app/services/chatgpt_oauth.py:88`, `backend/app/services/chatgpt_oauth.py:239`).

## Sources

- `backend/app/api/phone_numbers.py:22`
- `backend/app/services/chatgpt_oauth.py:88`
- `backend/app/services/chatgpt_oauth.py:239`
