from __future__ import annotations

import json

from app.agent.candidate_search import CandidateRecord
from app.agent.context_collector import ClaimContextSnapshot, ConceptContextSnapshot


def build_claim_prompt(snapshot: ClaimContextSnapshot, candidates: list[CandidateRecord]) -> str:
    payload = {
        "source_claim": {
            "id": snapshot.claim.id,
            "statement": snapshot.claim.statement,
            "claim_type": snapshot.claim.claim_type.value,
            "trust_status": snapshot.claim.trust_status.value,
            "concepts": [
                {
                    "id": concept.id,
                    "label": concept.label,
                    "field": concept.field,
                    "description": concept.description,
                }
                for concept in snapshot.concepts
            ],
            "contexts": [
                {
                    "id": context.id,
                    "name": context.name,
                    "field": context.field,
                    "assumptions": context.assumptions,
                }
                for context in snapshot.contexts
            ],
            "evidence": [
                {
                    "id": evidence.id,
                    "title": evidence.title,
                    "excerpt": evidence.excerpt,
                }
                for evidence in snapshot.evidence
            ],
        },
        "candidate_claims": [
            {
                "id": candidate.entity_id,
                "field": candidate.field,
                "score": candidate.score,
                "summary": candidate.summary,
                "details": candidate.details,
            }
            for candidate in candidates
        ],
        "instructions": {
            "return_format": [
                {
                    "target_claim_id": "candidate claim id",
                    "connection_type": "equivalent|analogous|generalizes|contradicts|complements",
                    "rationale": "2-3 sentences",
                    "confidence": 0.0,
                    "caveats": ["optional note"],
                }
            ]
        },
    }
    return json.dumps(payload, ensure_ascii=True, indent=2)


def build_concept_prompt(
    snapshot: ConceptContextSnapshot, candidates: list[CandidateRecord]
) -> str:
    payload = {
        "source_concept": {
            "id": snapshot.concept.id,
            "label": snapshot.concept.label,
            "description": snapshot.concept.description,
            "field": snapshot.concept.field,
            "terms": [term.surface_form for term in snapshot.terms],
            "related_claim_ids": [claim.id for claim in snapshot.related_claims],
        },
        "candidate_concepts": [
            {
                "id": candidate.entity_id,
                "field": candidate.field,
                "score": candidate.score,
                "summary": candidate.summary,
                "details": candidate.details,
            }
            for candidate in candidates
        ],
        "instructions": {
            "return_format": [
                {
                    "target_concept_id": "candidate concept id",
                    "connection_type": "equivalent|analogous|generalizes|contradicts|complements",
                    "rationale": "2-3 sentences",
                    "confidence": 0.0,
                    "caveats": ["optional note"],
                }
            ]
        },
    }
    return json.dumps(payload, ensure_ascii=True, indent=2)
