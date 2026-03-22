from __future__ import annotations


def test_evidence_create_and_get(client, reviewer_auth_header) -> None:
    context_response = client.post(
        "/api/v1/contexts",
        headers=reviewer_auth_header,
        json={"name": "Experimental Physics", "description": "Lab", "field": "physics", "assumptions": []},
    )
    claim_response = client.post(
        "/api/v1/claims",
        headers=reviewer_auth_header,
        json={"statement": "Measured entropy rose", "claim_type": "empirical", "context_ids": [context_response.json()["id"]]},
    )
    create_response = client.post(
        "/api/v1/evidence",
        headers=reviewer_auth_header,
        json={
            "evidence_type": "paper",
            "title": "Lab paper",
            "source": "doi:test",
            "reliability": "high",
            "claim_links": [{"claim_id": claim_response.json()["id"], "relationship": "supports"}],
        },
    )
    evidence_id = create_response.json()["id"]
    get_response = client.get(f"/api/v1/evidence/{evidence_id}", headers=reviewer_auth_header)

    assert create_response.status_code == 201
    assert get_response.status_code == 200
    assert get_response.json()["claim_links"][0]["relationship"] == "supports"