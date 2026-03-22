from __future__ import annotations


def test_concept_create_get_and_list(client, reviewer_auth_header) -> None:
    term_response = client.post(
        "/api/v1/terms",
        headers=reviewer_auth_header,
        json={"surface_form": "entropy", "language": "en"},
    )
    term_id = term_response.json()["id"]

    create_response = client.post(
        "/api/v1/concepts",
        headers=reviewer_auth_header,
        json={"label": "Entropy", "description": "Meaning", "field": "physics", "term_ids": [term_id]},
    )
    concept_id = create_response.json()["id"]

    list_response = client.get("/api/v1/concepts?search=Entropy", headers=reviewer_auth_header)
    detail_response = client.get(f"/api/v1/concepts/{concept_id}", headers=reviewer_auth_header)
    connections_response = client.get(f"/api/v1/concepts/{concept_id}/connections", headers=reviewer_auth_header)

    assert create_response.status_code == 201
    assert list_response.status_code == 200
    assert detail_response.json()["term_ids"] == [term_id]
    assert connections_response.json() == []