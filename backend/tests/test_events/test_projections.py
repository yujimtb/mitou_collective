from __future__ import annotations

from datetime import datetime, timezone

from app.events.commands import (
    ClaimCreated,
    ClaimUpdated,
    ConceptCreated,
    ConceptLinkedToClaim,
    CrossFieldLinkApproved,
    CrossFieldLinkProposed,
    EvidenceLinkedToClaim,
    ProposalApproved,
    ProposalCreated,
)
from app.events.projections import ProjectionEngine


def make_event(sequence_number: int, command: object) -> dict[str, object]:
    event = command.to_event()  # type: ignore[attr-defined]
    event["id"] = f"event-{sequence_number}"
    event["sequence_number"] = sequence_number
    event["created_at"] = datetime(2026, 1, sequence_number, tzinfo=timezone.utc)
    return event


def test_projection_rebuild_updates_read_models() -> None:
    events = [
        make_event(
            1,
            ClaimCreated(
                aggregate_id="claim-1",
                actor_id="actor-1",
                statement="Entropy in isolated systems does not decrease.",
                claim_type="theorem",
                trust_status="tentative",
                context_ids=["context-1"],
                context_names=["Thermodynamics"],
            ),
        ),
        make_event(
            2,
            ClaimUpdated(
                aggregate_id="claim-1",
                actor_id="actor-1",
                changes={"statement": "Entropy in isolated systems never decreases."},
                version=2,
            ),
        ),
        make_event(
            3,
            ConceptCreated(
                aggregate_id="concept-1",
                actor_id="actor-1",
                label="Entropy",
                description="A measure of uncertainty or disorder.",
                domain_field="physics",
            ),
        ),
        make_event(
            4,
            ConceptLinkedToClaim(
                aggregate_id="concept-1",
                actor_id="actor-1",
                claim_id="claim-1",
            ),
        ),
        make_event(
            5,
            EvidenceLinkedToClaim(
                aggregate_id="evidence-1",
                actor_id="actor-2",
                claim_id="claim-1",
                relationship="supports",
            ),
        ),
        make_event(
            6,
            ProposalCreated(
                aggregate_id="proposal-1",
                actor_id="reviewer-1",
                proposal_type="create_claim",
                target_entity_type="claim",
                target_entity_id="claim-1",
                payload_data={"statement": "Entropy claim"},
                rationale="Queue for review",
            ),
        ),
        make_event(
            7,
            ProposalApproved(
                aggregate_id="proposal-1",
                actor_id="reviewer-2",
                review_id="review-1",
            ),
        ),
        make_event(
            8,
            CrossFieldLinkProposed(
                aggregate_id="link-1",
                actor_id="actor-3",
                source_claim_id="claim-1",
                target_claim_id="claim-2",
                connection_type="analogous",
                description="Information entropy is analogous to thermodynamic entropy.",
                confidence=0.87,
            ),
        ),
        make_event(
            9,
            CrossFieldLinkApproved(
                aggregate_id="link-1",
                actor_id="reviewer-3",
                notes="Looks good",
            ),
        ),
    ]

    engine = ProjectionEngine()
    snapshot = engine.rebuild(events)
    claim = engine.get_claim_detail("claim-1")
    graph = engine.get_graph_view()

    assert claim is not None
    assert claim["statement"] == "Entropy in isolated systems never decreases."
    assert claim["version"] == 2
    assert claim["concept_ids"] == ["concept-1"]
    assert claim["evidence_ids"] == ["evidence-1"]
    assert len(claim["history"]) == 2

    assert snapshot["proposal_queue"] == []
    assert snapshot["cross_field_connections"] == [
        {
            "id": "link-1",
            "source_claim_id": "claim-1",
            "target_claim_id": "claim-2",
            "connection_type": "analogous",
            "description": "Information entropy is analogous to thermodynamic entropy.",
            "confidence": 0.87,
            "status": "approved",
        }
    ]
    assert {node["id"] for node in graph["nodes"]} >= {"claim-1", "concept-1"}
    assert graph["edges"] == [
        {"source": "concept-1", "target": "claim-1", "type": "linked_to_claim"}
    ]


def test_apply_processes_incremental_events() -> None:
    engine = ProjectionEngine()

    engine.apply(
        make_event(
            1,
            ClaimCreated(
                aggregate_id="claim-1",
                actor_id="actor-1",
                statement="A claim",
                claim_type="definition",
                trust_status="tentative",
            ),
        )
    )
    engine.apply(
        make_event(
            2,
            EvidenceLinkedToClaim(
                aggregate_id="evidence-1",
                actor_id="actor-2",
                claim_id="claim-1",
                relationship="supports",
            ),
        )
    )

    claim = engine.get_claim_detail("claim-1")

    assert claim is not None
    assert claim["evidence_ids"] == ["evidence-1"]
    assert engine.snapshot()["claim_list"] == [
        {
            "id": "claim-1",
            "statement": "A claim",
            "claim_type": "definition",
            "trust_status": "tentative",
            "context_names": [],
            "concept_count": 0,
            "evidence_count": 1,
            "retracted": False,
            "version": 1,
        }
    ]
