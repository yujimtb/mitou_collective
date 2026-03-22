from __future__ import annotations

from app.agent.candidate_generator import GeneratedConnectionCandidate
from app.agent.config import LinkingAgentConfig
from app.interfaces import IProposalService
from app.schemas import (
    PaginatedResponse,
    ProposalCreate,
    ProposalRead,
    ProposalStatus,
    ProposalType,
)

ACTIVE_DUPLICATE_STATUSES = {ProposalStatus.PENDING, ProposalStatus.IN_REVIEW}


class ProposalFormatter:
    def __init__(
        self, *, proposal_service: IProposalService, config: LinkingAgentConfig | None = None
    ):
        self._proposal_service = proposal_service
        self._config = config or LinkingAgentConfig()

    async def create_proposals(
        self,
        candidates: list[GeneratedConnectionCandidate],
        *,
        actor_id: str,
    ) -> list[ProposalRead]:
        created: list[ProposalRead] = []
        for candidate in candidates:
            if candidate.confidence < self._config.suggestion_confidence_threshold:
                continue
            if await self._is_duplicate(candidate):
                continue

            payload = self._build_payload(candidate)
            proposal = await self._proposal_service.create(
                ProposalCreate(
                    proposal_type=ProposalType.CONNECT_CONCEPTS,
                    target_entity_type=candidate.target_entity_type,
                    target_entity_id=candidate.target_entity_id,
                    payload=payload,
                    rationale=candidate.rationale,
                ),
                actor_id,
            )
            created.append(proposal)
        return created

    async def _is_duplicate(self, candidate: GeneratedConnectionCandidate) -> bool:
        page = await self._proposal_service.list(
            page=1,
            per_page=self._config.duplicate_check_page_size,
            proposal_type=ProposalType.CONNECT_CONCEPTS,
        )
        return _contains_duplicate(page, candidate)

    @staticmethod
    def _build_payload(candidate: GeneratedConnectionCandidate) -> dict[str, object]:
        if candidate.source_entity_type == "claim" and candidate.target_entity_type == "claim":
            payload = {
                "source_claim_id": candidate.source_entity_id,
                "target_claim_id": candidate.target_entity_id,
            }
        else:
            payload = {
                "source_concept_id": candidate.source_entity_id,
                "target_concept_id": candidate.target_entity_id,
            }

        payload.update(
            {
                "connection_type": candidate.connection_type.value,
                "confidence": candidate.confidence,
                "rationale": candidate.rationale,
                "caveats": candidate.caveats,
            }
        )
        return payload


def _contains_duplicate(
    page: PaginatedResponse[ProposalRead],
    candidate: GeneratedConnectionCandidate,
) -> bool:
    for proposal in page.items:
        if proposal.status not in ACTIVE_DUPLICATE_STATUSES:
            continue

        payload = proposal.payload
        if candidate.source_entity_type == "claim" and candidate.target_entity_type == "claim":
            if (
                payload.get("source_claim_id") == candidate.source_entity_id
                and payload.get("target_claim_id") == candidate.target_entity_id
            ):
                return True
        if candidate.source_entity_type == "concept" and candidate.target_entity_type == "concept":
            if (
                payload.get("source_concept_id") == candidate.source_entity_id
                and payload.get("target_concept_id") == candidate.target_entity_id
            ):
                return True
    return False
