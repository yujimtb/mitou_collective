from __future__ import annotations


def test_claim_endpoints_require_authentication(client) -> None:
    response = client.get("/api/v1/claims")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


def test_claim_crud_and_history(client, reviewer_auth_header) -> None:
    context_response = client.post(
        "/api/v1/contexts",
        headers=reviewer_auth_header,
        json={"name": "Thermodynamics", "description": "Heat", "field": "physics", "assumptions": []},
    )
    context_id = context_response.json()["id"]

    create_response = client.post(
        "/api/v1/claims",
        headers=reviewer_auth_header,
        json={"statement": "Entropy increases", "claim_type": "theorem", "context_ids": [context_id]},
    )
    claim_id = create_response.json()["id"]

    get_response = client.get(f"/api/v1/claims/{claim_id}", headers=reviewer_auth_header)
    update_response = client.put(
        f"/api/v1/claims/{claim_id}",
        headers=reviewer_auth_header,
        json={"statement": "Entropy does not decrease", "trust_status": "established"},
    )
    history_response = client.get(f"/api/v1/claims/{claim_id}/history", headers=reviewer_auth_header)

    assert create_response.status_code == 201
    assert get_response.status_code == 200
    assert update_response.status_code == 200
    assert update_response.json()["version"] == 2
    assert [item["event_type"] for item in history_response.json()] == ["ClaimCreated", "ClaimUpdated", "ClaimTrustChanged"]