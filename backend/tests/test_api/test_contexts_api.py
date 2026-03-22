from __future__ import annotations


def test_context_duplicate_name_returns_conflict(client, reviewer_auth_header) -> None:
    payload = {"name": "Information Theory", "description": "Context", "field": "cs", "assumptions": []}

    first = client.post("/api/v1/contexts", headers=reviewer_auth_header, json=payload)
    second = client.post("/api/v1/contexts", headers=reviewer_auth_header, json=payload)

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "conflict"