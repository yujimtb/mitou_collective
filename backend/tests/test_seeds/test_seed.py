from __future__ import annotations

from sqlalchemy import select

from app.models import CIR, Claim, Context, CrossFieldConnection, Evidence, Term
from app.seeds import seed_entropy_dataset


def test_entropy_dataset_seed_is_idempotent(db_session) -> None:
    first = seed_entropy_dataset(db_session)
    second = seed_entropy_dataset(db_session)

    assert first == second
    assert first.contexts >= 5
    assert first.claims >= 100
    assert first.evidence >= 30
    assert first.connections >= 4
    assert 3 <= first.cir <= 5


def test_entropy_dataset_links_expected_entities(db_session) -> None:
    seed_entropy_dataset(db_session)

    contexts = db_session.scalars(select(Context)).all()
    terms = db_session.scalars(select(Term)).all()
    second_law = db_session.scalar(select(Claim).where(Claim.statement == "Isolated systems exhibit non-decreasing entropy over time."))
    evidence = db_session.scalar(select(Evidence).where(Evidence.title == "Thermodynamics and an Introduction to Thermostatistics"))
    cir = db_session.scalar(select(CIR).where(CIR.subject == "entropy(system)"))
    connections = db_session.scalars(select(CrossFieldConnection)).all()

    assert any(context.name == "Classical Thermodynamics" for context in contexts)
    assert any(term.surface_form == "entropy" and term.language == "en" for term in terms)
    assert second_law is not None
    assert len(second_law.context_links) >= 1
    assert evidence is not None
    assert len(evidence.claim_links) >= 1
    assert cir is not None
    assert len(connections) >= 4