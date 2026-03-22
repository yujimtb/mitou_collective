from __future__ import annotations

from app.agent.candidate_generator import CandidateGenerator
from app.agent.candidate_search import CandidateSearch
from app.agent.config import LinkingAgentConfig
from app.agent.context_collector import ContextCollector
from app.agent.proposal_formatter import ProposalFormatter
from app.agent.trigger import manual_trigger
from app.interfaces import IClaimService, IConceptService, ILinkingAgent, IProposalService
from app.schemas import PaginatedResponse, ProposalRead, ProposalType


class LinkingAgent(ILinkingAgent):
    def __init__(
        self,
        *,
        claim_service: IClaimService,
        concept_service: IConceptService,
        proposal_service: IProposalService,
        collector: ContextCollector,
        candidate_search: CandidateSearch,
        candidate_generator: CandidateGenerator,
        proposal_formatter: ProposalFormatter,
        config: LinkingAgentConfig | None = None,
        agent_actor_id: str | None = None,
    ):
        self._claim_service = claim_service
        self._concept_service = concept_service
        self._proposal_service = proposal_service
        self._collector = collector
        self._candidate_search = candidate_search
        self._candidate_generator = candidate_generator
        self._proposal_formatter = proposal_formatter
        self._config = config or LinkingAgentConfig()
        self._agent_actor_id = agent_actor_id

    async def suggest_connections(
        self,
        *,
        source_entity_type: str,
        source_entity_id: str,
        target_field: str | None = None,
        actor_id: str,
    ) -> list[ProposalRead]:
        manual_trigger(
            source_entity_type=source_entity_type,
            source_entity_id=source_entity_id,
            requested_by=actor_id,
            target_field=target_field,
        )
        proposal_actor_id = self._agent_actor_id or actor_id

        if source_entity_type == "claim":
            snapshot = await self._collector.collect_for_claim(source_entity_id)
            candidates = await self._candidate_search.search_claim_candidates(
                snapshot,
                target_field=target_field,
            )
            generated = await self._candidate_generator.generate_for_claim(snapshot, candidates)
            return await self._proposal_formatter.create_proposals(
                generated, actor_id=proposal_actor_id
            )

        if source_entity_type == "concept":
            snapshot = await self._collector.collect_for_concept(
                source_entity_id,
                target_field=target_field,
            )
            candidates = await self._candidate_search.search_concept_candidates(
                snapshot,
                target_field=target_field,
            )
            generated = await self._candidate_generator.generate_for_concept(snapshot, candidates)
            return await self._proposal_formatter.create_proposals(
                generated, actor_id=proposal_actor_id
            )

        raise ValueError("source_entity_type must be 'claim' or 'concept'")

    async def list_suggestions(
        self,
        *,
        page: int = 1,
        per_page: int = 20,
        **filters: object,
    ) -> PaginatedResponse[ProposalRead]:
        proposal_page = await self._proposal_service.list(
            page=page,
            per_page=per_page,
            proposal_type=ProposalType.CONNECT_CONCEPTS,
        )
        items = [
            proposal for proposal in proposal_page.items if _matches_filters(proposal, filters)
        ]
        return PaginatedResponse[ProposalRead](
            total_count=len(items),
            current_page=page,
            per_page=per_page,
            items=items,
        )


def _matches_filters(proposal: ProposalRead, filters: dict[str, object]) -> bool:
    status = filters.get("status")
    if status is not None and proposal.status != status:
        return False

    min_confidence = filters.get("min_confidence")
    if min_confidence is not None:
        confidence = float(proposal.payload.get("confidence", 0.0))
        if confidence < float(min_confidence):
            return False

    max_confidence = filters.get("max_confidence")
    if max_confidence is not None:
        confidence = float(proposal.payload.get("confidence", 0.0))
        if confidence > float(max_confidence):
            return False

    return True
