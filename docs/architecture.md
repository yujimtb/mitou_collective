# Architecture Overview

CollectiveScience is structured as a claim-centered knowledge platform with explicit support for contexts, evidence, proposals, reviews, and cross-field links.

## Core Model

The core entities are:

- `Claim`: an atomic scientific statement
- `Context`: the assumptions and disciplinary frame in which a claim is meaningful
- `Concept`: a conceptual unit that may map across domains
- `Term`: a surface form in one or more languages
- `Evidence`: a source supporting or contradicting claims
- `CIR`: a structured formal representation of a claim
- `CrossFieldConnection`: an explicit relation between claims across fields
- `Proposal` and `Review`: workflow entities for moderated evolution of the graph

## Backend

The backend is implemented with:

- FastAPI for HTTP APIs
- SQLAlchemy for ORM models
- Alembic for migrations
- service-layer abstractions for domain logic
- an append-only event store for history and reconstruction

## Frontend and CLI

- The frontend is a Next.js application for graph exploration, proposals, reviews, and search.
- The CLI provides a scriptable interface over the API.

## Specification-Driven Development

System behavior is described in `openspec/specs/`. These specifications document the intended behavior for the knowledge graph, API, event store, trust model, web UI, CLI, proposal workflow, linking agent, and demo dataset.

## Current State

The repository is still a prototype. Some tracks are already implemented and tested, while others are under active development.