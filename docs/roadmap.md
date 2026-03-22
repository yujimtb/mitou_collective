# Roadmap

## Current State

The project is a working full-stack prototype after `mvp-completion`, but it still needs one focused pass to become the demo-ready MVP described in `prototype_design.md` section 1.1.

### Implemented baseline

- **Data model**: SQLAlchemy models and Alembic migrations for the core research entities
- **Event store**: Append-only event log with tested projection utilities retained in the codebase
- **Authentication and authorization**: JWT login plus the four-tier trust model and policy checks
- **Domain services**: CRUD, search, workflow, and event recording services across the backend
- **Proposal workflow**: Pending/in-review/approved/rejected lifecycle with human review
- **AI linking agent**: Provider-backed proposal generation pipeline with API readiness checks
- **REST API**: Authenticated route groups with pagination, filtering, and error handling
- **Frontend**: Next.js app with SSR, dashboard, graph view, claim detail, and create dialogs for core entities
- **CLI**: Existing operational command groups with table and JSON output
- **Demo dataset**: Seed content for the entropy theme across multiple research fields
- **Testing**: Backend automated tests are in place and passing
- **Docker Compose**: PostgreSQL, backend, and frontend services can run together locally

## MVP Finish Change (`mvp-finish`)

The `mvp-finish` change closes the remaining 12 gaps between the current prototype and a demoable MVP.

1. Fix the broken Context filter by accepting Context IDs while preserving name-based fallback.
2. Return formatted Claim history with human-readable titles, summaries, actor names, and timestamps.
3. Add the missing Term list/detail/create UI.
4. Add the missing Evidence list/detail UI.
5. Add a dedicated AI suggestions page.
6. Replace the static graph card layout with an interactive force-directed graph.
7. Replace the dashboard's hard-coded empty activity feed with real recent-event data.
8. Add Claim retraction (`DELETE /api/v1/claims/{id}`) as a soft-delete style workflow.
9. Add the missing CLI commands for Context, Term, Evidence, and `concept create`.
10. Make Docker startup MVP-safe with migration, optional seed, health check, and lockfile fixes.
11. Add the minimum frontend/component and end-to-end style test coverage needed for MVP confidence.
12. Clarify that `ProjectionEngine` is retained as a post-MVP CQRS foundation rather than part of the current read path.

### Planned execution flow

- **Phase 1**: Service fixes, frontend foundation work, CLI commands, and Agent 8 documentation updates
- **Phase 2**: REST API changes that depend on the new service-layer behavior
- **Phase 3**: Frontend/API integration and Docker startup hardening
- **Phase 4**: Follow-up tests and spec sync after implementation is complete

### ProjectionEngine documentation note

Task `7.1` is documentation-owned work for Agent 8. The following module comment text is the wording to apply at the top of `backend/app/events/projections.py` when the implementation agent updates that file:

```python
"""
ProjectionEngine is retained as a tested foundation for post-MVP CQRS integration.
During the MVP phase, read APIs continue to use direct SQLAlchemy queries rather
than projection-backed read models. Events are still recorded so projections can
be rebuilt later when the CQRS read path is introduced.
"""
```

## Near-Term Goals

1. Finish and verify the `mvp-finish` change so the product matches the MVP demo scope.
2. Tighten the UX around graph interaction, filtering, and entity creation flows.
3. Expand CLI and frontend automated coverage beyond the initial MVP smoke tests.
4. Improve local environment reliability with clearer operational guidance and compose defaults.
5. Prepare the main OpenSpec documents for sync once all implementation tasks are done.

## Medium-Term Goals

1. Introduce CQRS-backed read models when the MVP baseline is stable.
2. Embed vectors for semantic similarity in candidate search.
3. Support richer evidence modeling and provenance tracking.
4. Add user registration and OAuth authentication.
5. Implement real-time notifications for proposal state changes.
6. Formalize deployment and operational guidance.
7. Build evaluation scenarios for cross-field link quality assessment.

## Long-Term Vision

1. Multi-language support for terms and claims.
2. Federation across multiple CollectiveScience instances.
3. AI agent autonomy levels, from human-review-all to semi-autonomous.
4. Collaborative editing and conflict resolution.
5. Public API and partner-facing integrations.
