# Contributing

Thank you for your interest in contributing.

## Scope

This repository is currently maintained as a research prototype. Contributions are welcome, but changes should remain aligned with the current architectural direction and specification documents.

## Before Opening a Pull Request

Please:

1. open an issue or discussion if the change is large
2. keep changes focused and easy to review
3. add or update tests when behavior changes
4. update public documentation when setup or behavior changes

## Development Workflow

Backend:

```bash
cd backend
pip install -e .[dev]
python -m pytest tests
```

Frontend:

```bash
cd frontend
npm install
npm run typecheck
```

## Style Expectations

- prefer small, reviewable changes
- preserve existing naming and structure where practical
- avoid unrelated refactors in feature or fix branches
- keep docs and specs consistent with implementation

## Specifications

Major behavior is described in `openspec/specs/`. If a change affects system behavior or public interfaces, update the relevant spec or explain why the spec does not need to change.