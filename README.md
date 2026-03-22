# CollectiveScience

CollectiveScience is a prototype platform for representing scientific knowledge as a claim-centered graph and exploring conceptual links across disciplines.

The current prototype focuses on entropy-related concepts across thermodynamics, statistical mechanics, information theory, quantum information theory, and algorithmic information theory.

## Status

This repository is a research prototype under active development.

- Backend domain models, services, API endpoints, and seed dataset are implemented.
- CLI and frontend are under active implementation.
- Some test areas outside the currently stabilized tracks may still be in progress.

## Why This Project Exists

Scientific concepts often appear under different names, assumptions, and formal systems in different fields. CollectiveScience aims to make those relationships inspectable by treating claims, contexts, evidence, and cross-field connections as first-class objects.

The prototype is designed to support:

- claim-centered knowledge representation
- explicit contextualization of statements
- evidence-linked review and proposal workflows
- AI-assisted discovery of cross-field conceptual links

## Repository Structure

```text
backend/     FastAPI + SQLAlchemy backend, tests, seed data
frontend/    Next.js frontend prototype
cli/         Typer-based command-line interface
openspec/    specification documents used during development
docs/        public-facing project documentation
```

## Getting Started

### Backend

Requirements:

- Python 3.11+

Setup:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
```

Run tests:

```bash
python -m pytest tests
```

Run the API:

```bash
uvicorn app.main:app --reload
```

### Frontend

Requirements:

- Node.js 20+

Setup:

```bash
cd frontend
npm install
npm run dev
```

### Demo Dataset

You can seed the entropy-centered demo dataset with:

```bash
cd backend
python -m app.seeds.entropy_dataset
```

The seeded dataset currently contains:

- 6 contexts
- 9 terms
- 7 concepts
- 120 claims
- 33 evidence items
- 4 cross-field connections
- 3 CIR examples

## Documentation

- [Architecture](docs/architecture.md)
- [Demo Dataset](docs/demo-dataset.md)
- [Roadmap](docs/roadmap.md)
- [Specification Index](docs/specs-index.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)

## OpenSpec

The repository includes specification documents under `openspec/specs/`. These documents describe the intended behavior of the main subsystems and are kept in the repository because they are part of the development process and help explain the architecture.

## Public Repository Notes

This public repository intentionally excludes internal proposal drafts, agent-operation directories, and local development artifacts from future tracking.

## License

No open-source license file has been added yet. Reuse conditions are therefore not yet defined in this repository.