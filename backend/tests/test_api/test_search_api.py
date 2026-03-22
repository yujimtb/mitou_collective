from __future__ import annotations


def test_search_endpoint(client, reviewer_auth_header) -> None:
    context_response = client.post(
        "/api/v1/contexts",
        headers=reviewer_auth_header,
        json={"name": "Shannon Theory", "description": "entropy context", "field": "cs", "assumptions": []},
    )
    client.post(
        "/api/v1/terms",
        headers=reviewer_auth_header,
        json={"surface_form": "entropy", "language": "en"},
    )
    client.post(
        "/api/v1/claims",
        headers=reviewer_auth_header,
        json={"statement": "Entropy measures uncertainty", "claim_type": "definition", "context_ids": [context_response.json()["id"]]},
    )

    response = client.get("/api/v1/search?q=entropy", headers=reviewer_auth_header)

    assert response.status_code == 200
    assert response.json()["total_count"] >= 2
    assert {item["entity_type"] for item in response.json()["items"]} >= {"claim", "term", "context"}