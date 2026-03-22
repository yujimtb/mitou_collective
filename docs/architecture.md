# Architecture Overview

CollectiveScience is a claim-centered knowledge platform for representing scientific knowledge as a structured graph and exploring conceptual links across disciplines. Claims, contexts, evidence, proposals, reviews, and cross-field connections are all first-class objects.

## Core Data Model

The system manages 12 entity types:

| Entity | Role |
|--------|------|
| **Claim** | Atomic scientific statement (versioned, with trust status) |
| **Context** | Assumptions and disciplinary frame in which claims are meaningful |
| **Concept** | Conceptual unit that may map across domains |
| **Term** | Surface form in one or more languages, linked to concepts |
| **Evidence** | Source supporting or contradicting claims (with reliability rating) |
| **CIR** | Claim in Formal Representation — structured formal encoding of a claim |
| **CrossFieldConnection** | Explicit relation between claims across fields |
| **Proposal** | Change request (create claim, link claims, update trust, etc.) |
| **Review** | Decision on a proposal (approve / reject / request changes) |
| **Actor** | Human or AI agent with trust level |
| **Referent** | Target object that a term or concept refers to |
| **Event** | Append-only event record for history and reconstruction |

Key N:M relationships: Claim↔Context, Claim↔Concept, Claim↔Evidence, Term↔Concept.

## System Architecture

```
┌─────────────┐  ┌─────────────┐
│  Frontend   │  │    CLI      │
│  (Next.js)  │  │  (Typer)    │
└──────┬──────┘  └──────┬──────┘
       │  HTTP/REST      │
       └────────┬────────┘
                ▼
┌───────────────────────────────┐
│        REST API Layer         │
│   FastAPI (9 route groups)    │
├───────────────────────────────┤
│       Service Layer           │
│   12 domain services          │
│   + Workflow engine           │
│   + AI Linking Agent          │
├───────────────────────────────┤
│       Data Layer              │
│   SQLAlchemy ORM (12 models)  │
│   Append-only Event Store     │
│   JWT Auth + PolicyEngine     │
├───────────────────────────────┤
│       Database                │
│   SQLite (dev) / PostgreSQL   │
└───────────────────────────────┘
```

## Backend

**Framework**: FastAPI + SQLAlchemy 2.x + Alembic

### Layer breakdown

| Layer | Directory | Contents |
|-------|-----------|----------|
| Models | `app/models/` | 12 SQLAlchemy models with UUID PKs, timestamps, mixins |
| Schemas | `app/schemas/` | 14 Pydantic schema modules (Create/Read/Update per entity) |
| Interfaces | `app/interfaces/` | 14 abstract service interfaces (ABC) for DI |
| Services | `app/services/` | 12 service implementations (CRUD, search, event recording) |
| Workflows | `app/workflows/` | Proposal state machine, trust transitions, change applier |
| Events | `app/events/` | Append-only event store, commands, projections |
| Auth | `app/auth/` | JWT (python-jose), PolicyEngine, FastAPI dependencies |
| Agent | `app/agent/` | AI linking pipeline (trigger, context, candidates, formatter) |
| API | `app/api/` | 9 route groups + DI + error handlers |
| Seeds | `app/seeds/` | Demo dataset (entropy theme, 120+ claims) |

### API routes

| Route | Endpoints |
|-------|-----------|
| `/api/v1/auth` | Login, create admin |
| `/api/v1/claims` | List, create, get, update, history |
| `/api/v1/concepts` | List, create, get, connections |
| `/api/v1/contexts` | List, create, get, update |
| `/api/v1/evidence` | List, create, get |
| `/api/v1/terms` | List, create, get, lookup |
| `/api/v1/proposals` | List, create, get, submit, review |
| `/api/v1/agent` | Suggest connections, list suggestions |
| `/api/v1/search` | Full-text search across entities |

### Authentication & authorization

- JWT tokens with embedded `actor_type`, `trust_level`
- 4-tier trust model: admin > reviewer > contributor > observer
- PolicyEngine enforces operation × trust_level permissions
- Self-review prohibition

## Frontend

**Framework**: Next.js 15 + React 19 + Tailwind CSS 3.4 + TypeScript

All pages use server-side rendering (SSR) with `force-dynamic` export. The frontend authenticates to the backend via the `CS_API_TOKEN` environment variable and augments SSR views with client-side dialogs for create/review workflows.

| Page | Path | Description |
|------|------|-------------|
| Dashboard | `/` | Stats summary + recent claims/proposals |
| Claims | `/claims` | Filterable list with table/card views and a create-claim dialog |
| Claim detail | `/claims/[id]` | Full claim with evidence, CIR, history, evidence creation, and manual AI suggestion trigger |
| Concepts | `/concepts` | Concept list with create-concept dialog |
| Concept detail | `/concepts/[id]` | Concept with cross-field connections |
| Contexts | `/contexts` | Context list with create-context dialog |
| Context detail | `/contexts/[id]` | Context with associated claims |
| Review queue | `/review` | Proposal list with approve/reject actions, toast feedback, and fade-out completion |
| Graph | `/graph` | D3 force-directed graph visualization |
| Search | `/search` | Full-text search across all entities |

20 React components organized by domain: layout, claims, evidence, proposals, graph, common, cir, and create/feedback workflows.

## CLI

**Framework**: Typer + httpx + Rich

6 command groups: `auth`, `claim`, `concept`, `proposal`, `agent`, `search`. All commands communicate with the backend via REST API. Supports `--json` output mode.

## Event Store

Append-only event log recording all state changes (ClaimCreated, ClaimUpdated, ClaimTrustChanged, etc.). Supports:

- Query by aggregate ID (entity history)
- Query by sequence number (global ordering)
- Projection engine for read model reconstruction

## AI Linking Agent

Pipeline for discovering cross-field conceptual links:

1. **Trigger** — detect new claims/concepts or manual request
2. **Context collector** — gather surrounding claim/concept information
3. **Candidate search** — find related claims across fields
4. **Candidate generator** — generate connection proposals via a provider adapter (`OpenAIAdapter` or `AnthropicAdapter`)
5. **Proposal formatter** — format as Proposals with confidence filtering and deduplication

The backend wires `LLMConfig` from environment variables at application startup. When a supported API key is present, `main.py` injects the selected adapter's `generate()` method into `CandidateGenerator`; otherwise it keeps the no-op fallback so the API can boot without secrets.

Manual AI suggestion requests are guarded at the API layer: `POST /api/v1/agent/suggest-connections` returns `503` with `llm_unavailable` when no provider API key is configured.

## Specification-Driven Development

9 OpenSpec documents under `openspec/specs/` describe intended behavior: knowledge-graph, event-store, trust-model, proposal-review, linking-agent, rest-api, cli, web-ui, demo-dataset. See [Specification Index](specs-index.md) for details.

## Testing

69 backend tests across 34 test files covering:

- API integration tests (8 route groups)
- Service unit tests
- Workflow tests (state machine, trust transitions, change applier)
- Auth tests (JWT, policy engine, dependencies)
- Agent tests (all pipeline stages)
- LLM adapter/config tests for OpenAI, Anthropic, factory selection, and API readiness behavior
- Event store tests
- Seed dataset tests
- Model smoke tests

## Deployment

- **Development**: SQLite + `uvicorn --reload` + `npm run dev`
- **Production**: Docker Compose with PostgreSQL 16, backend, and frontend containers
- Key backend environment variables: `LLM_PROVIDER`, `LLM_MODEL`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `LLM_TEMPERATURE`, `LLM_MAX_TOKENS`, `LLM_TIMEOUT_SECONDS`
- Environment variables: see `.env.example`
