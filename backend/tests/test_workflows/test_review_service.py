from __future__ import annotations

import asyncio
import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.events.models import EventStoreBase
from app.events.store import EventStore
from app.models import Actor, Claim, Context, Proposal, Review
from app.schemas import (
    ActorType,
    ClaimType,
    ProposalStatus,
    ProposalType,
    ReviewCreate,
    ReviewDecision,
    TrustLevel,
    TrustStatus,
)
from app.services.review_service import ReviewService


class FailingEventStore(EventStore):
    async def append(self, *args, **kwargs):
        await super().append(*args, **kwargs)
        raise RuntimeError("event write failed")


def make_service(engine, event_store_cls=EventStore) -> ReviewService:
    EventStoreBase.metadata.create_all(engine)
    factory = sessionmaker(
        bind=engine, class_=Session, autoflush=False, autocommit=False, future=True
    )
    return ReviewService(factory, event_store_cls(factory))


def test_review_service_approves_proposal_and_applies_change(engine) -> None:
    service = make_service(engine)
    with Session(engine) as session:
        proposer = Actor(
            actor_type=ActorType.HUMAN,
            name="Contributor",
            trust_level=TrustLevel.CONTRIBUTOR,
        )
        reviewer = Actor(
            actor_type=ActorType.HUMAN,
            name="Reviewer",
            trust_level=TrustLevel.REVIEWER,
        )
        context = Context(
            name="Thermodynamics",
            description="TD",
            field="physics",
            assumptions=[],
        )
        session.add_all([proposer, reviewer, context])
        session.flush()
        proposal = Proposal(
            proposal_type=ProposalType.CREATE_CLAIM,
            proposed_by_id=proposer.id,
            target_entity_type="claim",
            payload={
                "statement": "Entropy increases in isolated systems.",
                "claim_type": ClaimType.THEOREM.value,
                "trust_status": TrustStatus.AI_SUGGESTED.value,
                "context_ids": [str(context.id)],
            },
            rationale="Create a vetted claim",
            status=ProposalStatus.PENDING,
        )
        session.add(proposal)
        session.commit()
        proposal_id = str(proposal.id)
        reviewer_id = str(reviewer.id)

    review = asyncio.run(
        service.create(
            ReviewCreate(
                proposal_id=proposal_id,
                decision=ReviewDecision.APPROVE,
                comment="Looks correct",
                confidence=0.93,
            ),
            reviewer_id,
        )
    )

    assert review.decision is ReviewDecision.APPROVE

    with Session(engine) as session:
        proposal = session.get(Proposal, uuid.UUID(proposal_id))
        claim = session.scalar(select(Claim))
        assert proposal is not None
        assert proposal.status is ProposalStatus.APPROVED
        assert claim is not None
        assert claim.trust_status is TrustStatus.TENTATIVE

    events = asyncio.run(
        service._event_store.query_by_aggregate(
            aggregate_type="proposal",
            aggregate_id=proposal_id,
        )
    )
    assert [event["event_type"] for event in events] == ["ProposalApproved"]


def test_review_service_rejects_self_review(engine) -> None:
    service = make_service(engine)
    with Session(engine) as session:
        actor = Actor(
            actor_type=ActorType.HUMAN,
            name="Reviewer",
            trust_level=TrustLevel.REVIEWER,
        )
        session.add(actor)
        session.flush()
        proposal = Proposal(
            proposal_type=ProposalType.UPDATE_TRUST,
            proposed_by_id=actor.id,
            target_entity_type="claim",
            payload={"new_status": TrustStatus.TENTATIVE.value},
            rationale="Cannot self-review",
            status=ProposalStatus.PENDING,
        )
        session.add(proposal)
        session.commit()
        proposal_id = str(proposal.id)
        actor_id = str(actor.id)

    with pytest.raises(PermissionError):
        asyncio.run(
            service.create(
                ReviewCreate(proposal_id=proposal_id, decision=ReviewDecision.REJECT),
                actor_id,
            )
        )


def test_review_service_lists_reviews_for_proposal(engine) -> None:
    service = make_service(engine)
    with Session(engine) as session:
        proposer = Actor(
            actor_type=ActorType.HUMAN,
            name="Contributor",
            trust_level=TrustLevel.CONTRIBUTOR,
        )
        reviewer = Actor(
            actor_type=ActorType.HUMAN,
            name="Reviewer",
            trust_level=TrustLevel.REVIEWER,
        )
        claim = Claim(
            statement="Pending trust update",
            claim_type=ClaimType.CONJECTURE,
            trust_status=TrustStatus.AI_SUGGESTED,
        )
        session.add_all([proposer, reviewer, claim])
        session.flush()
        proposal = Proposal(
            proposal_type=ProposalType.UPDATE_TRUST,
            proposed_by_id=proposer.id,
            target_entity_type="claim",
            target_entity_id=claim.id,
            payload={"new_status": TrustStatus.TENTATIVE.value},
            rationale="Request changes",
            status=ProposalStatus.PENDING,
        )
        session.add(proposal)
        session.commit()
        proposal_id = str(proposal.id)
        reviewer_id = str(reviewer.id)

    asyncio.run(
        service.create(
            ReviewCreate(
                proposal_id=proposal_id,
                decision=ReviewDecision.REQUEST_CHANGES,
                comment="Need better evidence",
            ),
            reviewer_id,
        )
    )

    reviews = asyncio.run(service.list_for_proposal(proposal_id))

    assert len(reviews) == 1
    assert reviews[0].decision is ReviewDecision.REQUEST_CHANGES


def test_review_service_approval_rolls_back_when_event_append_fails(engine) -> None:
    service = make_service(engine, FailingEventStore)
    with Session(engine) as session:
        proposer = Actor(
            actor_type=ActorType.HUMAN,
            name="Contributor",
            trust_level=TrustLevel.CONTRIBUTOR,
        )
        reviewer = Actor(
            actor_type=ActorType.HUMAN,
            name="Reviewer",
            trust_level=TrustLevel.REVIEWER,
        )
        context = Context(
            name="Rollback Thermodynamics",
            description="TD",
            field="physics",
            assumptions=[],
        )
        session.add_all([proposer, reviewer, context])
        session.flush()
        proposal = Proposal(
            proposal_type=ProposalType.CREATE_CLAIM,
            proposed_by_id=proposer.id,
            target_entity_type="claim",
            payload={
                "statement": "Rollback candidate",
                "claim_type": ClaimType.THEOREM.value,
                "trust_status": TrustStatus.AI_SUGGESTED.value,
                "context_ids": [str(context.id)],
            },
            rationale="Create a vetted claim",
            status=ProposalStatus.PENDING,
        )
        session.add(proposal)
        session.commit()
        proposal_id = str(proposal.id)
        reviewer_id = str(reviewer.id)

    with pytest.raises(RuntimeError, match="event write failed"):
        asyncio.run(
            service.create(
                ReviewCreate(
                    proposal_id=proposal_id,
                    decision=ReviewDecision.APPROVE,
                    comment="Looks correct",
                    confidence=0.93,
                ),
                reviewer_id,
            )
        )

    with Session(engine) as session:
        proposal = session.get(Proposal, uuid.UUID(proposal_id))
        assert proposal is not None
        assert proposal.status is ProposalStatus.PENDING
        assert session.scalar(select(Review)) is None
        assert session.scalar(select(Claim)) is None
