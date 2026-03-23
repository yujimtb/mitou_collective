from __future__ import annotations


def test_proposal_create_get_and_review(client, contributor_auth_header, reviewer_auth_header) -> None:
    create_response = client.post(
        "/api/v1/proposals",
        headers=contributor_auth_header,
        json={
            "proposal_type": "create_claim",
            "target_entity_type": "claim",
            "payload": {"statement": "Entropy grows", "claim_type": "theorem"},
            "rationale": "Seed a claim",
        },
    )
    proposal_id = create_response.json()["id"]

    list_response = client.get("/api/v1/proposals", headers=reviewer_auth_header)
    detail_response = client.get(f"/api/v1/proposals/{proposal_id}", headers=reviewer_auth_header)
    review_response = client.post(
        f"/api/v1/proposals/{proposal_id}/review",
        headers=reviewer_auth_header,
        json={"proposal_id": proposal_id, "decision": "reject", "comment": "Needs work"},
    )

    assert create_response.status_code == 201
    assert list_response.status_code == 200
    assert detail_response.status_code == 200
    assert detail_response.json()["reviews"] == []
    assert isinstance(detail_response.json()["created_at"], str)
    assert detail_response.json()["proposed_by"]["trust_level"] == "contributor"
    assert review_response.status_code == 201
    assert review_response.json()["decision"] == "reject"
