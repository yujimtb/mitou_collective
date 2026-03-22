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
    assert history_response.json()[0]["title"] == "Claim作成"
    assert history_response.json()[0]["summary"] == "「Entropy increases」を作成"
    assert history_response.json()[0]["actor_name"] == "Reviewer"
    assert "timestamp" in history_response.json()[0]


def test_claim_retract_endpoint_success(client, reviewer_auth_header) -> None:
    context_response = client.post(
        "/api/v1/contexts",
        headers=reviewer_auth_header,
        json={"name": "Retraction API Context", "description": "Heat", "field": "physics", "assumptions": []},
    )
    claim_response = client.post(
        "/api/v1/claims",
        headers=reviewer_auth_header,
        json={
            "statement": "Entropy can be retracted",
            "claim_type": "theorem",
            "context_ids": [context_response.json()["id"]],
        },
    )

    response = client.delete(f"/api/v1/claims/{claim_response.json()['id']}", headers=reviewer_auth_header)

    assert response.status_code == 200
    assert response.json()["trust_status"] == "retracted"


def test_claim_retract_endpoint_conflict(client, reviewer_auth_header) -> None:
    context_response = client.post(
        "/api/v1/contexts",
        headers=reviewer_auth_header,
        json={"name": "Retraction Conflict Context", "description": "Heat", "field": "physics", "assumptions": []},
    )
    claim_response = client.post(
        "/api/v1/claims",
        headers=reviewer_auth_header,
        json={
            "statement": "Entropy already retracted",
            "claim_type": "theorem",
            "context_ids": [context_response.json()["id"]],
        },
    )

    first = client.delete(f"/api/v1/claims/{claim_response.json()['id']}", headers=reviewer_auth_header)
    second = client.delete(f"/api/v1/claims/{claim_response.json()['id']}", headers=reviewer_auth_header)

    assert first.status_code == 200
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "conflict"


def test_claim_retract_endpoint_not_found(client, reviewer_auth_header) -> None:
    response = client.delete("/api/v1/claims/11111111-1111-1111-1111-111111111111", headers=reviewer_auth_header)

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_recent_events_endpoint_defaults_to_ten_and_returns_empty_list(client, reviewer_auth_header) -> None:
    response = client.get("/api/v1/events/recent", headers=reviewer_auth_header)

    assert response.status_code == 200
    assert response.json() == []


def test_recent_events_endpoint_supports_custom_limit(client, reviewer_auth_header) -> None:
    context_response = client.post(
        "/api/v1/contexts",
        headers=reviewer_auth_header,
        json={"name": "Recent Events Context", "description": "Heat", "field": "physics", "assumptions": []},
    )
    client.post(
        "/api/v1/claims",
        headers=reviewer_auth_header,
        json={
            "statement": "Entropy event one",
            "claim_type": "theorem",
            "context_ids": [context_response.json()["id"]],
        },
    )
    client.post(
        "/api/v1/claims",
        headers=reviewer_auth_header,
        json={
            "statement": "Entropy event two",
            "claim_type": "theorem",
            "context_ids": [context_response.json()["id"]],
        },
    )

    response = client.get("/api/v1/events/recent?limit=1", headers=reviewer_auth_header)

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Claim作成"
    assert response.json()[0]["actor_name"] == "Reviewer"
