from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.agent.config import LLMConfig
from app.auth.jwt import create_access_token
from app.interfaces import ILinkingAgent
from app.main import create_app
from app.models import Actor
from app.schemas import (
    ActorRead,
    ActorType,
    PaginatedResponse,
    ProposalRead,
    ProposalStatus,
    ProposalType,
    TrustLevel,
)
from app.services import (
    ActorService,
    ClaimService,
    ConceptService,
    ContextService,
    EvidenceService,
    ProposalService,
    ReviewService,
    SearchService,
    TermService,
)


class FakeLinkingAgent(ILinkingAgent):
    async def suggest_connections(
        self,
        *,
        source_entity_type: str,
        source_entity_id: str,
        target_field: str | None = None,
        actor_id: str,
    ) -> list[ProposalRead]:
        return [
            ProposalRead(
                id=str(uuid.uuid4()),
                proposal_type=ProposalType.CONNECT_CONCEPTS,
                proposed_by={
                    "id": actor_id,
                    "actor_type": ActorType.HUMAN,
                    "name": "Reviewer",
                    "trust_level": TrustLevel.REVIEWER,
                    "agent_model": None,
                },
                target_entity_type=source_entity_type,
                target_entity_id=source_entity_id,
                payload={"confidence": 0.82, "target_field": target_field},
                rationale="Suggested by fake linking agent",
                status=ProposalStatus.PENDING,
                created_at="2026-03-22T00:00:00Z",
                reviewed_at=None,
                reviewed_by=None,
            )
        ]

    async def list_suggestions(
        self,
        *,
        page: int = 1,
        per_page: int = 20,
        **filters: object,
    ) -> PaginatedResponse[ProposalRead]:
        item = (
            await self.suggest_connections(
                source_entity_type="claim",
                source_entity_id=str(uuid.uuid4()),
                actor_id=str(uuid.uuid4()),
            )
        )[0]
        return PaginatedResponse[ProposalRead](
            total_count=1,
            current_page=page,
            per_page=per_page,
            items=[item],
        )


@pytest.fixture
def api_services(session_factory, event_store):
    actor_service = ActorService(session_factory)
    return {
        "actor_service": actor_service,
        "claim_service": ClaimService(session_factory, event_store),
        "concept_service": ConceptService(session_factory, event_store),
        "context_service": ContextService(session_factory, event_store),
        "evidence_service": EvidenceService(session_factory, event_store),
        "term_service": TermService(session_factory, event_store),
        "proposal_service": ProposalService(session_factory, event_store),
        "review_service": ReviewService(session_factory, event_store),
        "search_service": SearchService(session_factory),
        "linking_agent": FakeLinkingAgent(),
        "llm_config": LLMConfig(api_key="test-key"),
    }


@pytest.fixture
def client(api_services):
    app = create_app(api_services)
    return TestClient(app)


@pytest.fixture
def reviewer_auth_header(engine) -> dict[str, str]:
    with Session(engine) as session:
        reviewer = Actor(
            actor_type=ActorType.HUMAN,
            name="Reviewer",
            trust_level=TrustLevel.REVIEWER,
        )
        session.add(reviewer)
        session.commit()
        actor_read = ActorRead(
            id=str(reviewer.id),
            actor_type=reviewer.actor_type,
            name=reviewer.name,
            trust_level=reviewer.trust_level,
            agent_model=reviewer.agent_model,
            created_at=reviewer.created_at,
        )

    token = create_access_token(actor_read)
    return {"Authorization": f"Bearer {token.access_token}"}


@pytest.fixture
def contributor_auth_header(engine) -> dict[str, str]:
    with Session(engine) as session:
        contributor = Actor(
            actor_type=ActorType.HUMAN,
            name="Contributor",
            trust_level=TrustLevel.CONTRIBUTOR,
        )
        session.add(contributor)
        session.commit()
        actor_read = ActorRead(
            id=str(contributor.id),
            actor_type=contributor.actor_type,
            name=contributor.name,
            trust_level=contributor.trust_level,
            agent_model=contributor.agent_model,
            created_at=contributor.created_at,
        )

    token = create_access_token(actor_read)
    return {"Authorization": f"Bearer {token.access_token}"}
