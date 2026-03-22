# Demo Dataset

The repository contains a seeded demo dataset centered on entropy and related concepts across multiple disciplines.

## Purpose

The dataset makes the value of the platform understandable without requiring users to build the graph from scratch. It demonstrates cross-field connections between thermodynamic entropy, statistical entropy, Shannon entropy, quantum entropy, and Kolmogorov complexity.

## Covered Fields

| Context | Field | Topic |
|---------|-------|-------|
| Classical Thermodynamics | physics | Macroscopic entropy, heat, work |
| Statistical Mechanics | physics | Boltzmann entropy, microstates, partition functions |
| Shannon Information Theory | information_theory | Information entropy, channel capacity |
| Quantum Information Theory | information_theory | Von Neumann entropy, entanglement |
| Algorithmic Information Theory | computer_science | Kolmogorov complexity, incompressibility |
| Cross-field | cross_field | Comparative entropy concepts |

## Included Data

| Entity | Count |
|--------|-------|
| Contexts | 6 |
| Terms | 9 |
| Concepts | 7 |
| Claims | 120 |
| Evidence | 33 |
| Cross-field Connections | 4 |
| CIR examples | 3 |

## Seed Command

```bash
cd backend
python manage.py seed
```

To also create an admin user with a JWT token:

```bash
python manage.py create-admin
```

## Data Files

JSON source files live under `backend/app/seeds/data/`:

```
contexts.json       # 6 contexts with fields and assumptions
terms.json          # 9 terms with English/Japanese labels
concepts.json       # 7 concepts mapped to terms
claims.json         # 24 base + 96 generated = 120 claims
evidence.json       # 8 base + 25 generated = 33 evidence records
connections.json    # 4 cross-field connections
cir.json            # 3 CIR formal representations
```

## Design Notes

- The seed script is idempotent — running it multiple times does not create duplicates
- Entity relationships (Claim↔Context, Claim↔Concept, Claim↔Evidence) are reconstructed explicitly
- The data is designed for demos and prototype evaluation, not as a production knowledge base