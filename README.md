# CollectiveScience

CollectiveScience is a prototype platform for representing scientific knowledge as a claim-centered graph and exploring conceptual links across disciplines.

The current prototype focuses on entropy-related concepts across thermodynamics, statistical mechanics, information theory, quantum information theory, and algorithmic information theory.

## Status

This repository is a working prototype with a connected full-stack application.

- **Backend**: FastAPI + SQLAlchemy with 12 services, 8 API routers, JWT auth, event store, and linking agent.
- **Frontend**: Next.js 15 + React 19, connected to the live backend API.
- **CLI**: Typer-based command-line client.
- **Tests**: 61 backend tests passing.

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
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -e .[dev]
```

Seed the demo dataset and create an admin user:

```bash
python -c "from manage import seed; seed()"
python -c "from manage import create_admin; create_admin()"
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

The frontend connects to the backend at `http://localhost:8000` by default.
Set `NEXT_PUBLIC_API_URL` environment variable to change the API URL, and `CS_API_TOKEN` for server-side authentication.

### Docker Compose (Full Stack)

Run the entire stack with Docker Compose:

```bash
docker compose up --build
```

This starts PostgreSQL, the backend API (port 8000), and the frontend (port 3000).

### Demo Dataset

You can seed the entropy-centered demo dataset with:

```bash
cd backend
python -c "from manage import seed; seed()"
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

This repository is licensed under the Apache License 2.0. See [LICENSE](LICENSE).