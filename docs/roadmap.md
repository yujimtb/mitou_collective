# Roadmap

## Current State

The project is a working full-stack prototype with all core subsystems implemented and tested.

### Implemented (complete)

- **Data model**: 12 SQLAlchemy models with Alembic migrations
- **Event store**: Append-only event log with projection engine
- **Authentication**: JWT tokens, 4-tier trust model (admin/reviewer/contributor/observer), PolicyEngine
- **Domain services**: 12 service classes covering CRUD, search, versioning, and event recording
- **Proposal workflow**: State machine (pending → in_review → approved/rejected), trust transitions, change applier
- **AI linking agent**: Full pipeline (trigger, context collector, candidate search, generator, formatter) with provider-backed OpenAI/Anthropic adapter support and API readiness checks
- **REST API**: 9 route groups with auth, pagination, filtering, error handling
- **Frontend**: Next.js 15 with 10 pages, 20 components, SSR with live API integration plus create dialogs, AI suggestion trigger, and review toast feedback
- **CLI**: 6 command groups with table/JSON output, auth management
- **Demo dataset**: Entropy theme across 5 fields — 6 contexts, 120 claims, 33 evidence, 9 terms/concepts
- **Testing**: 69 backend tests passing across 34 test files
- **Docker Compose**: PostgreSQL 16 + backend + frontend

## Near-Term Goals

1. Finish the remaining MVP completion tasks for frontend forms, manual suggestion UX, and environment/docker documentation
2. Polish graph visualization (zoom, filtering, layout options)
3. Add end-to-end CLI workflow tests
4. Improve search with PostgreSQL full-text search in production
5. Add frontend validation and richer form ergonomics for the new create flows

## Medium-Term Goals

1. Embed vectors for semantic similarity in candidate search
2. Support richer evidence modeling and provenance tracking
3. Add user registration and OAuth authentication
4. Implement real-time notifications for proposal state changes
5. Formalize deployment and operational guidance
6. Build evaluation scenarios for cross-field link quality assessment

## Long-Term Vision

1. Multi-language support for terms and claims
2. Federation across multiple CollectiveScience instances
3. AI agent autonomy levels (from human-review-all to semi-autonomous)
4. Collaborative editing and conflict resolution
5. Public API for third-party integrations
