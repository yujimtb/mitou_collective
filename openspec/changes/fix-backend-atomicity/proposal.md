## Why

Database writes (`session.commit()`) complete before event-store writes (`event_store.append()`), so a failure in the event-store step leaves the domain change persisted but the audit/event record missing. Separately, when a request supplies related IDs (context, concept, evidence) that don't exist, the service silently drops the invalid ones instead of rejecting the request, producing partial relationships that don't match the caller's intent.

## What Changes

- Wrap domain writes and event-store writes in a unified transactional boundary (or introduce an outbox pattern) so events cannot be lost after a successful database commit
- Add strict validation for all submitted related IDs: if any ID does not exist, return a 400 error before committing
- Apply both fixes consistently across all services: `claim_service`, `concept_service`, `context_service`, `term_service`, `proposal_service`

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `event-store`: Event writes become part of the database transaction boundary (outbox or unified commit)
- `knowledge-graph`: Related-ID validation rejects invalid IDs instead of silently dropping them

## Impact

- `backend/app/services/claim_service.py` — transactional boundary + ID validation
- `backend/app/services/concept_service.py` — same pattern
- `backend/app/services/context_service.py` — same pattern
- `backend/app/services/term_service.py` — same pattern
- `backend/app/services/proposal_service.py` — transactional boundary
- `backend/app/events/store.py` — may need transactional integration support
- `backend/app/models/` — potential outbox model if outbox pattern chosen
- Existing tests need updates for new validation errors
