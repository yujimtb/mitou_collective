# Specification Index

This repository includes OpenSpec documents describing the intended behavior of major subsystems. All specifications are implemented and tested.

## Main Specifications

| Spec | Path | Covers |
|------|------|--------|
| Knowledge Graph | `openspec/specs/knowledge-graph/spec.md` | Data model, entities, relationships |
| Event Store | `openspec/specs/event-store/spec.md` | Append-only events, projections |
| Trust Model | `openspec/specs/trust-model/spec.md` | Actor types, trust levels, permissions |
| Proposal Review | `openspec/specs/proposal-review/spec.md` | Proposal state machine, review workflow |
| Linking Agent | `openspec/specs/linking-agent/spec.md` | AI cross-field link suggestions |
| REST API | `openspec/specs/rest-api/spec.md` | HTTP endpoints, auth, pagination |
| CLI | `openspec/specs/cli/spec.md` | Command-line interface commands |
| Web UI | `openspec/specs/web-ui/spec.md` | Frontend pages and interactions |
| Demo Dataset | `openspec/specs/demo-dataset/spec.md` | Seed data (entropy theme) |

## How to Read Them

1. Start with **knowledge-graph** for the data model (entities, relationships, constraints)
2. Read **trust-model** and **proposal-review** for governance (who can do what, how changes are reviewed)
3. Read **rest-api**, **cli**, and **web-ui** for the three interface layers
4. Read **linking-agent** for the AI-assisted cross-field discovery pipeline
5. Read **event-store** for the history and event sourcing architecture
6. Read **demo-dataset** for the seeded evaluation corpus

## Changes Directory

Active and archived changes live under `openspec/changes/`. Each change follows the OpenSpec artifact workflow: proposal → delta specs → design → tasks.