from __future__ import annotations

import asyncio

from sqlalchemy.orm import Session, sessionmaker

from app.events.models import EventStoreBase
from app.events.store import EventStore
from app.models import Actor
from app.schemas import (
    ActorType,
    ProposalCreate,
    ProposalStatus,
    ProposalType,
    ProposalUpdate,
    TrustLevel,
)
from app.services.proposal_service import ProposalService


def make_service(engine) -> ProposalService:
    EventStoreBase.metadata.create_all(engine)
    factory = sessionmaker(
        bind=engine, class_=Session, autoflush=False, autocommit=False, future=True
    )
    return ProposalService(factory, EventStore(factory))


def test_proposal_service_creates_proposal_and_records_event(engine) -> None:
    service = make_service(engine)
    with Session(engine) as session:
        actor = Actor(
            actor_type=ActorType.HUMAN,
            name="Reviewer",
            trust_level=TrustLevel.REVIEWER,
        )
        session.add(actor)
        session.commit()
        actor_id = str(actor.id)

    created = asyncio.run(
        service.create(
            ProposalCreate(
                proposal_type=ProposalType.CREATE_CLAIM,
                target_entity_type="claim",
                payload={"statement": "Entropy grows", "claim_type": "theorem"},
                rationale="Seed a claim",
            ),
            actor_id,
        )
    )

    assert created.status is ProposalStatus.PENDING

    events = asyncio.run(
        service._event_store.query_by_aggregate(
            aggregate_type="proposal",
            aggregate_id=created.id,
        )
    )
    assert [event["event_type"] for event in events] == ["ProposalCreated"]


def test_proposal_service_lists_and_withdraws_author_proposal(engine) -> None:
    service = make_service(engine)
    with Session(engine) as session:
        actor = Actor(
            actor_type=ActorType.HUMAN,
            name="Contributor",
            trust_level=TrustLevel.CONTRIBUTOR,
        )
        session.add(actor)
        session.commit()
        actor_id = str(actor.id)

    created = asyncio.run(
        service.create(
            ProposalCreate(
                proposal_type=ProposalType.ADD_EVIDENCE,
                target_entity_type="claim",
                payload={
                    "title": "Paper",
                    "source": "Archive",
                    "evidence_type": "paper",
                    "claim_links": [{"claim_id": actor_id, "relationship": "supports"}],
                },
                rationale="Add support",
            ),
            actor_id,
        )
    )

    listing = asyncio.run(service.list(status=ProposalStatus.PENDING))
    updated = asyncio.run(
        service.update(
            created.id,
            ProposalUpdate(status=ProposalStatus.WITHDRAWN),
            actor_id,
        )
    )

    assert listing.total_count >= 1
    assert updated.status is ProposalStatus.WITHDRAWN
