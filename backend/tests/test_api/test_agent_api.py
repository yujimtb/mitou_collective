from __future__ import annotations


def test_agent_endpoints(client, reviewer_auth_header) -> None:
    suggest_response = client.post(
        "/api/v1/agent/suggest-connections",
        headers=reviewer_auth_header,
        json={"source_entity_type": "claim", "source_entity_id": "claim-1", "target_field": "biology"},
    )
    list_response = client.get("/api/v1/agent/suggestions?min_confidence=0.5", headers=reviewer_auth_header)

    assert suggest_response.status_code == 202
    assert "job_id" in suggest_response.json()
    assert suggest_response.json()["items"][0]["proposal_type"] == "connect_concepts"
    assert list_response.status_code == 200
    assert list_response.json()["total_count"] == 1