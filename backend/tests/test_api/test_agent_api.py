from __future__ import annotations

from fastapi.testclient import TestClient

from app.agent.config import LLMConfig
from app.main import create_app


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


def test_suggest_connections_returns_503_when_llm_is_unconfigured(
    api_services, reviewer_auth_header
) -> None:
    api_services["llm_config"] = LLMConfig(api_key="")

    with TestClient(create_app(api_services)) as client:
        response = client.post(
            "/api/v1/agent/suggest-connections",
            headers=reviewer_auth_header,
            json={"source_entity_type": "claim", "source_entity_id": "claim-1"},
        )

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "llm_unavailable",
            "message": "LLM service is not configured",
            "details": {},
        }
    }
