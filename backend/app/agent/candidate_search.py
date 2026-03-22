from __future__ import annotations

import asyncio
import re
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass
from difflib import SequenceMatcher

from app.agent.config import LinkingAgentConfig
from app.agent.context_collector import ClaimContextSnapshot, ConceptContextSnapshot
from app.interfaces import IClaimService, IConceptService
from app.schemas import ClaimRead, ConceptRead, ContextRead, TermRead

ContextLoader = Callable[[str], Awaitable[ContextRead | None]]
TermLoader = Callable[[str], Awaitable[TermRead | None]]


@dataclass(slots=True)
class CandidateRecord:
    entity_type: str
    entity_id: str
    field: str | None
    score: float
    summary: str
    details: dict[str, object]


class CandidateSearch:
    def __init__(
        self,
        *,
        claim_service: IClaimService,
        concept_service: IConceptService,
        context_loader: ContextLoader | None = None,
        term_loader: TermLoader | None = None,
        config: LinkingAgentConfig | None = None,
    ):
        self._claim_service = claim_service
        self._concept_service = concept_service
        self._context_loader = context_loader
        self._term_loader = term_loader
        self._config = config or LinkingAgentConfig()
        self._concept_cache: dict[str, ConceptRead] = {}

    async def search_claim_candidates(
        self,
        snapshot: ClaimContextSnapshot,
        *,
        target_field: str | None = None,
    ) -> list[CandidateRecord]:
        page = await self._claim_service.list(page=1, per_page=self._config.search_pool_size)
        source_text = self._compose_claim_text(snapshot.claim, snapshot.concepts)
        source_tokens = _tokenize(source_text)
        scored: list[CandidateRecord] = []

        for candidate in page.items:
            if candidate.id == snapshot.claim.id:
                continue

            candidate_concepts = await self._load_concepts(candidate.concept_ids)
            candidate_field = await self._infer_claim_field(candidate, candidate_concepts)
            if target_field is not None and candidate_field != target_field:
                continue
            if (
                target_field is None
                and snapshot.source_field is not None
                and candidate_field == snapshot.source_field
            ):
                continue

            candidate_text = self._compose_claim_text(candidate, candidate_concepts)
            if not source_tokens & _tokenize(candidate_text):
                continue
            score = _blended_similarity(source_text, candidate_text)
            if score <= 0:
                continue

            scored.append(
                CandidateRecord(
                    entity_type="claim",
                    entity_id=candidate.id,
                    field=candidate_field,
                    score=round(score, 4),
                    summary=candidate.statement,
                    details={
                        "statement": candidate.statement,
                        "concept_labels": [concept.label for concept in candidate_concepts],
                    },
                )
            )

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[: self._config.max_candidates]

    async def search_concept_candidates(
        self,
        snapshot: ConceptContextSnapshot,
        *,
        target_field: str | None = None,
    ) -> list[CandidateRecord]:
        page = await self._concept_service.list(page=1, per_page=self._config.search_pool_size)
        source_text = self._compose_concept_text(snapshot.concept, snapshot.terms)
        source_tokens = _tokenize(source_text)
        scored: list[CandidateRecord] = []

        for candidate in page.items:
            if candidate.id == snapshot.concept.id:
                continue
            if target_field is not None and candidate.field != target_field:
                continue
            if target_field is None and candidate.field == snapshot.concept.field:
                continue

            candidate_terms = await self._load_terms(candidate.term_ids)
            candidate_text = self._compose_concept_text(candidate, candidate_terms)
            if not source_tokens & _tokenize(candidate_text):
                continue
            score = _blended_similarity(source_text, candidate_text)
            if score <= 0:
                continue

            scored.append(
                CandidateRecord(
                    entity_type="concept",
                    entity_id=candidate.id,
                    field=candidate.field,
                    score=round(score, 4),
                    summary=candidate.label,
                    details={
                        "label": candidate.label,
                        "description": candidate.description,
                        "term_surface_forms": [term.surface_form for term in candidate_terms],
                    },
                )
            )

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[: self._config.max_candidates]

    async def _infer_claim_field(
        self,
        claim: ClaimRead,
        concepts: Sequence[ConceptRead],
    ) -> str | None:
        if concepts:
            return concepts[0].field
        contexts = await self._load_contexts(claim.context_ids)
        if contexts:
            return contexts[0].field
        return None

    async def _load_concepts(self, concept_ids: Sequence[str]) -> list[ConceptRead]:
        missing_ids = [
            concept_id for concept_id in concept_ids if concept_id not in self._concept_cache
        ]
        if missing_ids:
            concepts = await asyncio.gather(
                *(self._concept_service.get(concept_id) for concept_id in missing_ids)
            )
            for concept in concepts:
                self._concept_cache[concept.id] = concept
        return [
            self._concept_cache[concept_id]
            for concept_id in concept_ids
            if concept_id in self._concept_cache
        ]

    async def _load_contexts(self, context_ids: Sequence[str]) -> list[ContextRead]:
        if self._context_loader is None or not context_ids:
            return []
        contexts = await asyncio.gather(
            *(self._context_loader(context_id) for context_id in context_ids)
        )
        return [context for context in contexts if context is not None]

    async def _load_terms(self, term_ids: Sequence[str]) -> list[TermRead]:
        if self._term_loader is None or not term_ids:
            return []
        terms = await asyncio.gather(*(self._term_loader(term_id) for term_id in term_ids))
        return [term for term in terms if term is not None]

    @staticmethod
    def _compose_claim_text(claim: ClaimRead, concepts: Sequence[ConceptRead]) -> str:
        concept_text = " ".join(f"{concept.label} {concept.description}" for concept in concepts)
        return f"{claim.statement} {concept_text}".strip()

    @staticmethod
    def _compose_concept_text(concept: ConceptRead, terms: Sequence[TermRead]) -> str:
        term_text = " ".join(term.surface_form for term in terms)
        return f"{concept.label} {concept.description} {term_text}".strip()


def _tokenize(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", value.casefold()))


def _blended_similarity(left: str, right: str) -> float:
    left_tokens = _tokenize(left)
    right_tokens = _tokenize(right)
    if not left_tokens or not right_tokens:
        return 0.0
    jaccard = len(left_tokens & right_tokens) / len(left_tokens | right_tokens)
    ratio = SequenceMatcher(None, left.casefold(), right.casefold()).ratio()
    return (0.65 * jaccard) + (0.35 * ratio)
