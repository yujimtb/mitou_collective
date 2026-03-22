## Why

Client-side authenticated mutations (create claim, submit review, AI suggestions) are likely broken in production because `process.env.CS_API_TOKEN` is a server-only environment variable that is not accessible in browser-executed code. Additionally, every detail page converts all fetch failures—including 401, 403, 500, and 503—into `notFound()`, masking real backend and auth problems from users and operators.

## What Changes

- Move authenticated mutation calls (create claim, submit review, AI suggest) behind Next.js server actions or route handlers so the token stays server-side
- Refactor detail page error handling to distinguish genuine 404s from other HTTP errors and surface appropriate error states for each
- Add a typed API error class to `lib/api.ts` that preserves HTTP status codes for downstream consumers

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `web-ui`: Client-side mutation auth path moves to server boundary; detail page error handling distinguishes 404 from other failures

## Impact

- `frontend/src/lib/api.ts` — auth header and error propagation changes
- `frontend/src/components/CreateClaimDialog.tsx` — mutation call path changes
- `frontend/src/components/proposals/ReviewDialog.tsx` — mutation call path changes
- `frontend/src/components/claims/ClaimDetail.tsx` — mutation call path changes
- `frontend/src/app/claims/[id]/page.tsx` — error handling refinement
- `frontend/src/app/concepts/[id]/page.tsx` — error handling refinement
- Other detail pages (`contexts`, `evidence`, `terms`) — same error handling refinement
- No backend changes required
