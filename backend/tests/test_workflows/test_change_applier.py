from __future__ import annotations

import uuid

import pytest

from app.models import Actor, Claim, Concept, Context, CrossFieldConnection, Evidence, Proposal
from app.schemas import (
    ActorType,
    ClaimType,
    ConnectionType,
    ProposalStatus,
    ProposalType,
    Reliability,
    TrustLevel,
    TrustStatus,
)
from app.workflows import ChangeApplier


def make_actor(*, trust_level: TrustLevel = TrustLevel.REVIEWER) -> Actor:
    return Actor(actor_type=ActorType.HUMAN, name=str(uuid.uuid4()), trust_level=trust_level)


def test_change_applier_creates_claim_from_proposal(db_session) -> None:
    proposer = make_actor()
    context = Context(name="Thermodynamics", description="TD", field="physics", assumptions=[])
    concept = Concept(label="Entropy", description="State function", field="physics")
    db_session.add_all([proposer, context, concept])
    db_session.commit()

    proposal = Proposal(
        proposal_type=ProposalType.CREATE_CLAIM,
        proposed_by_id=proposer.id,
        target_entity_type="claim",
        payload={
            "statement": "Entropy increases in isolated systems.",
            "claim_type": ClaimType.THEOREM.value,
            "trust_status": TrustStatus.AI_SUGGESTED.value,
            "context_ids": [str(context.id)],
            "concept_ids": [str(concept.id)],
        },
        rationale="Promote a vetted AI suggestion",
        status=ProposalStatus.IN_REVIEW,
    )
    db_session.add(proposal)
    db_session.commit()

    applied = ChangeApplier().apply(db_session, proposal, actor_id=str(proposer.id))
    db_session.commit()

    claim = db_session.get(Claim, uuid.UUID(applied.entity_ids["claim_id"]))
    assert claim is not None
    assert claim.trust_status is TrustStatus.TENTATIVE
    assert {event.event_type for event in applied.events} == {"ClaimCreated"}


@pytest.mark.parametrize("proposal_type", [ProposalType.LINK_CLAIMS, ProposalType.CONNECT_CONCEPTS])
def test_change_applier_creates_connections_for_linking_proposals(
    db_session, proposal_type: ProposalType
) -> None:
    proposer = make_actor()
    source = Claim(
        statement="Source", claim_type=ClaimType.THEOREM, trust_status=TrustStatus.TENTATIVE
    )
    target = Claim(
        statement="Target", claim_type=ClaimType.THEOREM, trust_status=TrustStatus.TENTATIVE
    )
    db_session.add_all([proposer, source, target])
    db_session.commit()

    proposal = Proposal(
        proposal_type=proposal_type,
        proposed_by_id=proposer.id,
        target_entity_type="connection",
        payload={
            "source_claim_id": str(source.id),
            "target_claim_id": str(target.id),
            "connection_type": ConnectionType.ANALOGOUS.value,
            "description": "These claims exhibit similar monotonic behavior.",
            "confidence": 0.82,
        },
        rationale="Link cross-field claims",
        status=ProposalStatus.IN_REVIEW,
    )
    db_session.add(proposal)
    db_session.commit()

    applied = ChangeApplier().apply(db_session, proposal, actor_id=str(proposer.id))
    db_session.commit()

    connection = db_session.get(
        CrossFieldConnection, uuid.UUID(applied.entity_ids["connection_id"])
    )
    assert connection is not None
    assert connection.status is ProposalStatus.APPROVED
    assert {event.event_type for event in applied.events} == {"CrossFieldLinkApproved"}


def test_change_applier_adds_evidence_and_updates_claim_trust(db_session) -> None:
    proposer = make_actor()
    claim = Claim(
        statement="Closed-system entropy never decreases.",
        claim_type=ClaimType.THEOREM,
        trust_status=TrustStatus.ESTABLISHED,
    )
    db_session.add_all([proposer, claim])
    db_session.commit()

    proposal = Proposal(
        proposal_type=ProposalType.ADD_EVIDENCE,
        proposed_by_id=proposer.id,
        target_entity_type="claim",
        target_entity_id=claim.id,
        payload={
            "evidence_type": "paper",
            "title": "Counterexample under coarse graining",
            "source": "Journal of Statistical Mechanics",
            "reliability": Reliability.HIGH.value,
            "claim_links": [
                {
                    "claim_id": str(claim.id),
                    "relationship": "contradicts",
                }
            ],
        },
        rationale="Attach a contradictory result",
        status=ProposalStatus.IN_REVIEW,
    )
    db_session.add(proposal)
    db_session.commit()

    applied = ChangeApplier().apply(db_session, proposal, actor_id=str(proposer.id))
    db_session.commit()
    db_session.refresh(claim)

    evidence = db_session.get(Evidence, uuid.UUID(applied.entity_ids["evidence_id"]))
    assert evidence is not None
    assert claim.trust_status is TrustStatus.DISPUTED
    assert {event.event_type for event in applied.events} == {
        "ClaimTrustChanged",
        "EvidenceCreated",
        "EvidenceLinkedToClaim",
    }


def test_change_applier_updates_trust_with_rule_validation(db_session) -> None:
    proposer = make_actor()
    claim = Claim(
        statement="AI proposal",
        claim_type=ClaimType.CONJECTURE,
        trust_status=TrustStatus.AI_SUGGESTED,
    )
    db_session.add_all([proposer, claim])
    db_session.commit()

    proposal = Proposal(
        proposal_type=ProposalType.UPDATE_TRUST,
        proposed_by_id=proposer.id,
        target_entity_type="claim",
        target_entity_id=claim.id,
        payload={
            "new_status": TrustStatus.TENTATIVE.value,
            "reason": "Human reviewer approved the suggestion",
        },
        rationale="Promote the claim after review",
        status=ProposalStatus.IN_REVIEW,
    )
    db_session.add(proposal)
    db_session.commit()

    applied = ChangeApplier().apply(db_session, proposal, actor_id=str(proposer.id))
    db_session.commit()
    db_session.refresh(claim)

    assert claim.trust_status is TrustStatus.TENTATIVE
    assert {event.event_type for event in applied.events} == {"ClaimTrustChanged"}
