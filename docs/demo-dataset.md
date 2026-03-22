# Demo Dataset

The repository contains a seeded demo dataset centered on entropy and related concepts across multiple disciplines.

## Purpose

The dataset is intended to make the value of the platform understandable without requiring users to build the graph from scratch.

## Covered Fields

- classical thermodynamics
- statistical mechanics
- Shannon information theory
- quantum information theory
- algorithmic information theory
- cross-field comparative studies

## Included Data

Current seed output includes:

- 6 contexts
- 9 terms
- 7 concepts
- 120 claims
- 33 evidence records
- 4 cross-field connections
- 3 CIR examples

## Seed Command

```bash
cd backend
python -m app.seeds.entropy_dataset
```

## Design Notes

- the dataset is idempotent
- JSON source files live under `backend/app/seeds/data/`
- the seed script reconstructs entity relationships explicitly
- the data is designed for demos and prototype evaluation, not as a production knowledge base