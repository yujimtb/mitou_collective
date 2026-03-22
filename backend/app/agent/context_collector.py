from __future__ import annotations

import asyncio
import re
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass
from typing import TypeVar

from app.interfaces import IClaimService, IConceptService
from app.schemas import ClaimRead, ConceptRead, ContextRead, EvidenceRead, TermRead

ContextLoader = Callable[[str], Awaitable[ContextRead | None]]
EvidenceLoader = Callable[[str], Awaitable[EvidenceRead | None]]
TermLoader = Callable[[str], Awaitable[TermRead | None]]
ItemT = TypeVar("ItemT")


@dataclass(slots=True)
class ClaimContextSnapshot:
    claim: ClaimRead
    concepts: list[ConceptRead]
    contexts: list[ContextRead]
    evidence: list[EvidenceRead]
    adjacent_claims: list[ClaimRead]
    source_field: str | None


@dataclass(slots=True)
class ConceptContextSnapshot:
    concept: ConceptRead
    terms: list[TermRead]
    related_claims: list[ClaimRead]
    similar_concepts: list[ConceptRead]


class ContextCollector:
    def __init__(
        self,
        *,
        claim_service: IClaimService,
        concept_service: IConceptService,
        context_loader: ContextLoader | None = None,
        evidence_loader: EvidenceLoader | None = None,
        term_loader: TermLoader | None = None,
        page_size: int = 100,
    ):
        self._claim_service = claim_service
        self._concept_service = concept_service
        self._context_loader = context_loader
        self._evidence_loader = evidence_loader
        self._term_loader = term_loader
        self._page_size = page_size

    async def collect_for_claim(self, claim_id: str) -> ClaimContextSnapshot:
        claim = await self._claim_service.get(claim_id)
        concepts = await self._load_concepts(claim.concept_ids)
        contexts = await self._load_many(claim.context_ids, self._context_loader)
        evidence = await self._load_many(claim.evidence_ids, self._evidence_loader)

        page = await self._claim_service.list(page=1, per_page=self._page_size)
        adjacent_claims = [
            candidate
            for candidate in page.items
            if candidate.id != claim.id and self._shares_relationship(claim, candidate)
        ]

        return ClaimContextSnapshot(
            claim=claim,
            concepts=concepts,
            contexts=contexts,
            evidence=evidence,
            adjacent_claims=adjacent_claims,
            source_field=self._derive_claim_field(concepts, contexts),
        )

    async def collect_for_concept(
        self, concept_id: str, *, target_field: str | None = None
    ) -> ConceptContextSnapshot:
        concept = await self._concept_service.get(concept_id)
        terms = await self._load_many(concept.term_ids, self._term_loader)

        claim_page = await self._claim_service.list(page=1, per_page=self._page_size)
        related_claims = [claim for claim in claim_page.items if concept.id in claim.concept_ids]

        concept_page = await self._concept_service.list(page=1, per_page=self._page_size)
        source_text = self._compose_concept_text(concept, terms)
        scored: list[tuple[float, ConceptRead]] = []
        for candidate in concept_page.items:
            if candidate.id == concept.id:
                continue
            if target_field is not None and candidate.field != target_field:
                continue
            if target_field is None and candidate.field == concept.field:
                continue

            score = _text_similarity(source_text, self._compose_concept_text(candidate, []))
            if score <= 0:
                continue
            scored.append((score, candidate))

        scored.sort(key=lambda item: item[0], reverse=True)
        similar_concepts = [candidate for _, candidate in scored[: self._page_size]]
        return ConceptContextSnapshot(
            concept=concept,
            terms=terms,
            related_claims=related_claims,
            similar_concepts=similar_concepts,
        )

    async def _load_concepts(self, concept_ids: Sequence[str]) -> list[ConceptRead]:
        tasks = [self._concept_service.get(concept_id) for concept_id in concept_ids]
        if not tasks:
            return []
        return list(await asyncio.gather(*tasks))

    async def _load_many(
        self,
        ids: Sequence[str],
        loader: Callable[[str], Awaitable[ItemT | None]] | None,
    ) -> list[ItemT]:
        if loader is None or not ids:
            return []

        loaded = await asyncio.gather(*(loader(item_id) for item_id in ids))
        return [item for item in loaded if item is not None]

    @staticmethod
    def _shares_relationship(source: ClaimRead, candidate: ClaimRead) -> bool:
        return bool(set(source.context_ids) & set(candidate.context_ids)) or bool(
            set(source.concept_ids) & set(candidate.concept_ids)
        )

    @staticmethod
    def _derive_claim_field(
        concepts: Sequence[ConceptRead], contexts: Sequence[ContextRead]
    ) -> str | None:
        if concepts:
            return concepts[0].field
        if contexts:
            return contexts[0].field
        return None

    @staticmethod
    def _compose_concept_text(concept: ConceptRead, terms: Sequence[TermRead]) -> str:
        term_text = " ".join(term.surface_form for term in terms)
        return f"{concept.label} {concept.description} {term_text}".strip()


def _tokenize(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", value.casefold()))


def _text_similarity(left: str, right: str) -> float:
    left_tokens = _tokenize(left)
    right_tokens = _tokenize(right)
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)
