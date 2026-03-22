## Why

`npm run lint` launches the interactive Next.js ESLint setup wizard and exits non-zero, making it unusable in CI pipelines and local automation. A working lint command is needed for code quality enforcement.

## What Changes

- Add a proper ESLint configuration file (`.eslintrc.json` or `eslint.config.mjs`) to the frontend so `next lint` runs non-interactively
- Configure rules appropriate for a Next.js + TypeScript project
- Ensure `npm run lint` exits cleanly (zero or only warnings) on the current codebase

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `web-ui`: ESLint configuration added so `npm run lint` works non-interactively

## Impact

- `frontend/.eslintrc.json` or `frontend/eslint.config.mjs` — new configuration file
- `frontend/package.json` — possible devDependency additions
- No source code logic changes expected (config-only)
