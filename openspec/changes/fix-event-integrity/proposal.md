## Why

Proposal events generate `href` links pointing to `/proposals/{id}`, but no such route exists in the frontend, producing broken links in the dashboard activity feed. Separately, the `ClaimCreated` event stores context UUIDs in the `context_names` field instead of actual human-readable context names, corrupting any downstream read-model or activity-feed summary that consumes this field.

## What Changes

- Fix `event_href()` in `backend/app/events/formatting.py` to map proposal events to an existing frontend route (e.g., `/review` or `/suggestions`) instead of the non-existent `/proposals/{id}`
- Fix `ClaimCreated` event construction in `backend/app/services/claim_service.py` to populate `context_names` from actual `Context.name` values instead of passing `context_ids`
- Add tests to verify both fixes

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `event-store`: Fix event href generation for proposals and fix ClaimCreated payload integrity

## Impact

- `backend/app/events/formatting.py` — proposal href mapping
- `backend/app/services/claim_service.py` — ClaimCreated event construction (line 65)
- `backend/tests/test_events/` — new/updated test coverage
- `backend/tests/test_services/` — updated test for correct context_names
- No frontend changes required (existing links will start working)
