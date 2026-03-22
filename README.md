# CollectiveScience

CollectiveScience is a prototype platform for representing scientific knowledge as a claim-centered graph and exploring conceptual links across disciplines.

The current prototype focuses on entropy-related concepts across thermodynamics, statistical mechanics, information theory, quantum information theory, and algorithmic information theory.

## Status

This repository is a working full-stack prototype with all core subsystems implemented and tested.

- **Backend**: FastAPI + SQLAlchemy with 12 services, 9 API route groups, JWT auth, event store, and AI linking agent with OpenAI/Anthropic adapters. 69 tests passing.
- **Frontend**: Next.js 15 + React 19 + Tailwind CSS, 10 pages with SSR and client-side creation/review flows connected to the live backend API.
- **CLI**: Typer-based command-line client with 6 command groups.
- **Docker**: Docker Compose setup with PostgreSQL 16, backend, and frontend containers.

## Why This Project Exists

Scientific concepts often appear under different names, assumptions, and formal systems in different fields. CollectiveScience aims to make those relationships inspectable by treating claims, contexts, evidence, and cross-field connections as first-class objects.

The prototype is designed to support:

- claim-centered knowledge representation
- explicit contextualization of statements
- evidence-linked review and proposal workflows
- AI-assisted discovery of cross-field conceptual links

## Repository Structure

```text
backend/     FastAPI + SQLAlchemy backend (12 services, 9 API routes, 69 tests)
frontend/    Next.js 15 frontend (10 pages, 20 components)
cli/         Typer-based command-line interface (6 command groups)
openspec/    OpenSpec specification documents (9 subsystems)
docs/        Project documentation
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
python manage.py seed
python manage.py create-admin
```

Run tests:

```bash
python -m pytest tests
```

Run the API server:

```bash
python manage.py serve
# or: uvicorn app.main:app --reload
```

To enable real LLM-backed connection suggestions, configure one provider:

```bash
# OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=
LLM_MODEL=gpt-4o

# Anthropic
# LLM_PROVIDER=anthropic
# ANTHROPIC_API_KEY=
# LLM_MODEL=claude-sonnet-4-20250514

LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=4096
LLM_TIMEOUT_SECONDS=60
```

If no LLM API key is configured, the backend still starts normally, but `POST /api/v1/agent/suggest-connections` returns `503` with `llm_unavailable`.

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
Set `CS_API_TOKEN` to a valid JWT for server-side authentication (obtain one via `python manage.py create-admin` in the backend directory).

The current web UI supports:

- creating Claims, Concepts, Contexts, and Evidence from modal dialogs
- manually triggering AI connection suggestions from the Claim detail page
- reviewing proposals in-place with toast feedback and automatic refresh

### Docker Compose (Full Stack)

Run the entire stack with Docker Compose:

```bash
docker compose up --build
```

This starts PostgreSQL, the backend API (port 8000), and the frontend (port 3000).

### Demo Dataset

Seed the entropy-centered demo dataset:

```bash
cd backend
python manage.py seed
```

The seeded dataset contains:

- 6 contexts (5 fields + cross-field)
- 9 terms and 7 concepts
- 120 claims
- 33 evidence items
- 4 cross-field connections
- 3 CIR examples

See [Demo Dataset](docs/demo-dataset.md) for details.

## Documentation

- [Architecture](docs/architecture.md) — System design and component overview
- [Demo Dataset](docs/demo-dataset.md) — Entropy-themed seed data description
- [Roadmap](docs/roadmap.md) — Current state and future plans
- [Quality Audit](docs/quality-audit.md) — Current defect summary and remediation priorities
- [Specification Index](docs/specs-index.md) — OpenSpec documents for all subsystems
- [Parallel Development Guide](parallel_dev_guide.md) — Multi-agent parallel development setup
- [Agent Assignments](docs/agent-assignments.md) — Agent roles, file ownership, and collision map
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)

## OpenSpec

The repository includes specification documents under `openspec/specs/`. These documents describe the intended behavior of 9 subsystems (knowledge-graph, event-store, trust-model, proposal-review, linking-agent, rest-api, cli, web-ui, demo-dataset) and are part of the development process.

## Configuration

Copy `.env.example` to `.env` and adjust values as needed:

```bash
# Backend
DATABASE_URL=sqlite:///./collective_science.db
JWT_SECRET=change-me-in-production
CORS_ORIGINS=http://localhost:3000
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=4096
LLM_TIMEOUT_SECONDS=60

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
CS_API_TOKEN=
```

## Public Repository Notes

This public repository intentionally excludes internal proposal drafts, agent-operation directories, and local development artifacts from future tracking.

## License

This repository is licensed under the Apache License 2.0. See [LICENSE](LICENSE).
