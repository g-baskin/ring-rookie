---
type: concept
title: "Knowledge-base RAG pipeline"
status: mature
created: "2026-08-13"
updated: "2026-08-13"
complexity: advanced
domain: "ai"
aliases: []
tags:
  - concept
  - ai
related:
  - "[[entities/knowledge-base-services]]"
sources: []
---

# Knowledge-base RAG pipeline

## Overview

The knowledge-base service owns document ingestion, embeddings, persistence, retrieval, and context construction. (`backend/app/services/knowledge_base.py:34`)

## Flow and invariants

- The knowledge-base service owns document ingestion, embeddings, persistence, retrieval, and context construction. (`backend/app/services/knowledge_base.py:34`)
- Documents are normalized and split into sentence-aware overlapping chunks. (`backend/app/services/knowledge_base.py:101`)
- Text ingestion deduplicates a source, generates batch embeddings, and persists one row per chunk. (`backend/app/services/knowledge_base.py:169`)
- Similarity search embeds the query and orders pgvector cosine distance results. (`backend/app/services/knowledge_base.py:340`)
- Retrieved chunks are assembled into a bounded prompt context with source attribution. (`backend/app/services/knowledge_base.py:423`)

## Connections

The flow is implemented by [[entities/knowledge-base-services]], whose source module contains the ingestion, retrieval, and context-building operations (`backend/app/services/knowledge_base.py:34`).

## Sources

- `backend/app/services/knowledge_base.py:34`
- `backend/app/services/knowledge_base.py:101`
- `backend/app/services/knowledge_base.py:169`
- `backend/app/services/knowledge_base.py:340`
- `backend/app/services/knowledge_base.py:423`
