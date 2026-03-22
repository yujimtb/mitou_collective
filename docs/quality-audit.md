# Quality Audit

## Scope

This document summarizes a repository-wide quality audit of the current CollectiveScience prototype. The goal was to identify likely defects, validate the current build and test baseline, and capture the most actionable risks before further feature work.

Audit snapshot:

- Backend: `python -m pytest tests` -> 81 tests passed
- CLI: `python -m pytest tests` -> 16 tests passed
- Frontend: `npm run typecheck`, `npm run test -- --run`, and `npm run build` passed
- Frontend lint: `npm run lint` is currently not automation-safe because it launches the interactive Next.js ESLint setup flow and exits non-zero

## Findings Summary

| Severity | Area | Problem |
| --- | --- | --- |
| Critical | Frontend auth | Client-side mutations rely on a server-only token source, so authenticated browser actions are likely to fail |
| Critical | Frontend error handling | Multiple detail pages turn all fetch failures into `404 Not Found`, masking real backend and auth problems |
| Critical | Backend consistency | Database writes commit before event-store writes, so state and audit history can diverge on failures |
| Medium | Backend validation | Invalid related IDs are silently dropped instead of rejected |
| Medium | Frontend navigation | Event links can point to `/proposals/{id}`, but the frontend has no proposal detail route |
| Medium | Event payload integrity | `ClaimCreated` stores context IDs in `context_names`, corrupting event-derived summaries |

## Detailed Findings

### 1. Client-side authenticated mutations are likely broken

**Evidence**

- `frontend/src/lib/api.ts:163-169` builds the `Authorization` header from `process.env.CS_API_TOKEN`
- Client components call those helpers directly:
  - `frontend/src/components/CreateClaimDialog.tsx:1-8,51-66`
  - `frontend/src/components/proposals/ReviewDialog.tsx:1-6,25-34`
  - `frontend/src/components/claims/ClaimDetail.tsx:13,29-35`
- Backend write/review routes require authorization:
  - `backend/app/api/claims.py:38-45`
  - `backend/app/api/agent.py:31-37`
  - similar patterns exist in other create/review routes

**Why this matters**

`CS_API_TOKEN` is a server-side environment variable. Browser-executed code cannot reliably use it, so client-triggered create, review, and AI suggestion requests are likely to reach the API without a bearer token and fail with `401` or `403`.

**Recommended fix**

Move authenticated mutations behind a server-only boundary such as Next.js route handlers or server actions, or introduce a real user session/token flow for client requests.

### 2. Detail pages mask real failures as 404s

**Evidence**

- `frontend/src/app/claims/[id]/page.tsx:10-25`
- `frontend/src/app/concepts/[id]/page.tsx:9-84`
- The same `catch { notFound(); }` pattern also appears in context, evidence, and term detail pages

**Why this matters**

A backend outage, a permission problem, a transient network error, or an LLM-related `503` can be presented to the user as "resource not found". That makes real incidents harder to diagnose and leads users to the wrong conclusion.

**Recommended fix**

Only convert known `404` responses to `notFound()`. Surface `401`, `403`, `500`, and `503` as explicit application errors or dedicated error states.

### 3. Service writes are not atomic with event-store writes

**Evidence**

- `backend/app/services/claim_service.py:51-70`
- `backend/app/services/claim_service.py:150-168`
- `backend/app/services/claim_service.py:203-214`
- The same `session.commit()` followed by `await self._event_store.append(...)` pattern appears in other services, including:
  - `backend/app/services/concept_service.py:32-36,94-98`
  - `backend/app/services/context_service.py:29-33,85-89`
  - `backend/app/services/term_service.py:31-35,85-89`
  - `backend/app/services/proposal_service.py:59-64`

**Why this matters**

If the event-store write fails after the database commit succeeds, the system keeps the domain change but loses the corresponding audit/event record. That breaks event integrity and any downstream read-model or activity-feed logic derived from events.

**Recommended fix**

Use a single transactional boundary where possible, or introduce an outbox pattern so event publication cannot be lost after a successful database commit.

### 4. Invalid related IDs are silently ignored

**Evidence**

- `backend/app/services/claim_service.py:36-44`
- `backend/app/services/claim_service.py:123-133`
- Similar lookup-without-cardinality-check patterns exist in:
  - `backend/app/services/concept_service.py:29,87`
  - `backend/app/services/term_service.py:27,80`

**Why this matters**

If a request submits multiple related IDs and some do not exist, the current code loads only the valid rows and silently drops the rest. The request appears to succeed, but the stored relationships do not match the caller's intent.

**Recommended fix**

Validate that every submitted related ID exists before committing. If any are missing, return a clear `400` or `404` instead of partially applying the change.

### 5. Proposal event links point to a missing frontend route

**Evidence**

- `backend/app/events/formatting.py:132-135` maps proposal events to `/proposals/{id}`
- `frontend/src/app/page.tsx:45-55` renders `event.href` directly in the dashboard activity feed
- No matching route exists under `frontend/src/app/proposals/**`

**Why this matters**

Recent activity can render links that lead users to a page that does not exist. That makes the dashboard activity feed unreliable as a navigation surface.

**Recommended fix**

Either add a proposal detail route in the frontend or map proposal activity to an existing destination such as `/review` or `/suggestions`.

### 6. `ClaimCreated` event payload uses IDs where names are expected

**Evidence**

- `backend/app/services/claim_service.py:65` sets `context_names=schema.context_ids`
- `backend/app/events/commands.py:44` defines `context_names` as a list of strings representing names
- `backend/app/events/projections.py:76,275` carries `context_names` into derived claim summaries
- `backend/app/workflows/change_applier.py:95-119` shows the intended pattern by collecting actual context names

**Why this matters**

The event payload is internally inconsistent. Anything that consumes `context_names` from events or projections will see UUIDs instead of human-readable context labels.

**Recommended fix**

Populate `context_names` from the linked `Context.name` values when building the `ClaimCreated` event.

## Remediation Order

1. Fix the frontend authentication path for browser-side mutations.
2. Narrow the use of `notFound()` so it only handles real not-found cases.
3. Make domain writes and event writes atomic, or adopt an outbox workflow.
4. Enforce strict related-ID validation instead of partial success.
5. Align event `href` generation with actual frontend routes.
6. Correct the `ClaimCreated.context_names` payload field.
7. Add a real ESLint configuration so `npm run lint` can run non-interactively in CI and local automation.

## Notes

- This document captures audit findings only; it does not apply fixes.
- Existing test and build results indicate that several issues are currently hidden by coverage gaps or runtime-only conditions rather than caught by the present automated checks.
