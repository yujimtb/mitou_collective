from __future__ import annotations

import asyncio

from app.schemas import ClaimCreate, ClaimType, ContextCreate, SearchQuery, TermCreate
from app.services import ClaimService, ContextService, SearchService, TermService


def test_search_service_returns_matches(session_factory, event_store) -> None:
    actor_id = "11111111-1111-1111-1111-111111111111"
    context_service = ContextService(session_factory, event_store)
    term_service = TermService(session_factory, event_store)
    claim_service = ClaimService(session_factory, event_store)
    search_service = SearchService(session_factory)

    context = asyncio.run(
        context_service.create(
            ContextCreate(name="Information Theory", description="entropy context", field="cs", assumptions=[]),
            actor_id,
        )
    )
    asyncio.run(term_service.create(TermCreate(surface_form="entropy", language="en"), actor_id))
    asyncio.run(
        claim_service.create(
            ClaimCreate(statement="Entropy measures uncertainty", claim_type=ClaimType.DEFINITION, context_ids=[context.id]),
            actor_id,
        )
    )

    result = asyncio.run(search_service.search(SearchQuery(q="entropy")))

    assert result.total_count >= 2
    assert {item.entity_type for item in result.items} >= {"claim", "term", "context"}