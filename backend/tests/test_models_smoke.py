from __future__ import annotations

from sqlalchemy import inspect


def test_core_tables_exist(engine) -> None:
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    expected = {
        "actors",
        "referents",
        "terms",
        "concepts",
        "contexts",
        "evidence",
        "claims",
        "proposals",
        "reviews",
        "cross_field_connections",
        "cir",
        "term_concepts",
        "claim_contexts",
        "claim_concepts",
        "claim_evidence",
    }

    assert expected.issubset(table_names)