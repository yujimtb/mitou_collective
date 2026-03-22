from app.events.commands import ClaimCreated, EVENT_COMMANDS, ProposalCreated


def test_event_command_registry_matches_spec() -> None:
    expected_names = {
        "ClaimCreated",
        "ClaimUpdated",
        "ClaimTrustChanged",
        "ClaimRetracted",
        "ConceptCreated",
        "ConceptUpdated",
        "ConceptLinkedToClaim",
        "EvidenceCreated",
        "EvidenceLinkedToClaim",
        "ContextCreated",
        "ContextUpdated",
        "ProposalCreated",
        "ProposalApproved",
        "ProposalRejected",
        "CrossFieldLinkProposed",
        "CrossFieldLinkApproved",
        "CrossFieldLinkRejected",
    }
    assert {command.__name__ for command in EVENT_COMMANDS} == expected_names


def test_claim_command_converts_to_event_payload() -> None:
    command = ClaimCreated(
        aggregate_id="claim-1",
        actor_id="actor-1",
        statement="Entropy increases in closed systems.",
        claim_type="theorem",
        trust_status="established",
        context_ids=["context-1"],
        context_names=["Thermodynamics"],
    )

    assert command.to_event() == {
        "event_type": "ClaimCreated",
        "aggregate_type": "claim",
        "aggregate_id": "claim-1",
        "payload": {
            "statement": "Entropy increases in closed systems.",
            "claim_type": "theorem",
            "trust_status": "established",
            "version": 1,
            "context_ids": ["context-1"],
            "context_names": ["Thermodynamics"],
            "concept_ids": [],
            "evidence_ids": [],
            "cir_id": None,
        },
        "actor_id": "actor-1",
        "proposal_id": None,
    }


def test_proposal_command_renames_nested_payload_field() -> None:
    command = ProposalCreated(
        aggregate_id="proposal-1",
        actor_id="reviewer-1",
        proposal_type="create_claim",
        target_entity_type="claim",
        payload_data={"statement": "A new claim"},
        rationale="Seed a new claim",
    )

    event = command.to_event()

    assert event["payload"] == {
        "proposal_type": "create_claim",
        "target_entity_type": "claim",
        "target_entity_id": None,
        "payload": {"statement": "A new claim"},
        "rationale": "Seed a new claim",
        "status": "pending",
    }
