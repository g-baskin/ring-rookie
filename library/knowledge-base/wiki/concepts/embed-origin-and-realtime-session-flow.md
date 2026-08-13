---
type: concept
title: "Embed origin and realtime session flow"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
complexity: advanced
domain: "security"
aliases: []
tags:
  - concept
  - security
related:
  - "[[entities/embed]]"
  - "[[entities/realtime]]"
sources: []
---

# Embed origin and realtime session flow

## Overview

The public widget configuration endpoint validates the request origin before exposing agent configuration. (`backend/app/api/embed.py:129`)

## Flow and invariants

- The public widget configuration endpoint validates the request origin before exposing agent configuration. (`backend/app/api/embed.py:129`)
- The embed WebSocket binds a public agent identifier and session token to a realtime connection. (`backend/app/api/embed.py:334`)
- Authenticated dashboard realtime sessions use an agent and workspace-scoped WebSocket route. (`backend/app/api/realtime.py:97`)

## Connections

[[entities/embed]] owns public widget configuration and embed WebSocket handling (`backend/app/api/embed.py:129`, `backend/app/api/embed.py:334`). [[entities/realtime]] owns the authenticated agent/workspace WebSocket route (`backend/app/api/realtime.py:97`).

## Sources

- `backend/app/api/embed.py:129`
- `backend/app/api/embed.py:334`
- `backend/app/api/realtime.py:97`
