from __future__ import annotations

from app.events.formatting import event_href


class TestEventHref:
    def test_claim_href(self) -> None:
        assert event_href("claim", "abc-123") == "/claims/abc-123"

    def test_concept_href(self) -> None:
        assert event_href("concept", "abc-123") == "/concepts/abc-123"

    def test_context_href(self) -> None:
        assert event_href("context", "abc-123") == "/contexts/abc-123"

    def test_evidence_href(self) -> None:
        assert event_href("evidence", "abc-123") == "/evidence/abc-123"

    def test_proposal_href_points_to_review(self) -> None:
        assert event_href("proposal", "abc-123") == "/review"

    def test_cross_field_connection_with_proposal_id(self) -> None:
        assert event_href("cross_field_connection", "abc-123", proposal_id="prop-1") == "/review"

    def test_cross_field_connection_without_proposal_id(self) -> None:
        assert event_href("cross_field_connection", "abc-123") == "/suggestions"

    def test_unknown_aggregate_type(self) -> None:
        assert event_href("unknown", "abc-123") == "/"
