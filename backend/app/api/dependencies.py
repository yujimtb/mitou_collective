from __future__ import annotations

from typing import cast

from fastapi import Request

from app.interfaces import (
    IClaimService,
    IConceptService,
    IContextService,
    IEventStore,
    IEvidenceService,
    ILinkingAgent,
    IProposalService,
    IReviewService,
    ISearchService,
    ITermService,
)


def _get_service(request: Request, attribute: str):
    service = getattr(request.app.state, attribute, None)
    if service is None:
        raise RuntimeError(f"request.app.state.{attribute} is not configured")
    return service


def get_claim_service(request: Request) -> IClaimService:
    return cast(IClaimService, _get_service(request, "claim_service"))


def get_concept_service(request: Request) -> IConceptService:
    return cast(IConceptService, _get_service(request, "concept_service"))


def get_context_service(request: Request) -> IContextService:
    return cast(IContextService, _get_service(request, "context_service"))


def get_evidence_service(request: Request) -> IEvidenceService:
    return cast(IEvidenceService, _get_service(request, "evidence_service"))


def get_event_store(request: Request) -> IEventStore:
    return cast(IEventStore, _get_service(request, "event_store"))


def get_term_service(request: Request) -> ITermService:
    return cast(ITermService, _get_service(request, "term_service"))


def get_proposal_service(request: Request) -> IProposalService:
    return cast(IProposalService, _get_service(request, "proposal_service"))


def get_review_service(request: Request) -> IReviewService:
    return cast(IReviewService, _get_service(request, "review_service"))


def get_linking_agent(request: Request) -> ILinkingAgent:
    return cast(ILinkingAgent, _get_service(request, "linking_agent"))


def get_search_service(request: Request) -> ISearchService:
    return cast(ISearchService, _get_service(request, "search_service"))
