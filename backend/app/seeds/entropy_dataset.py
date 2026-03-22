from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.models import (
    Actor,
    Base,
    CIR,
    Claim,
    ClaimConcept,
    ClaimContext,
    ClaimEvidence,
    Concept,
    Context,
    CrossFieldConnection,
    Evidence,
    Referent,
    Term,
)
from app.schemas import ActorType, ClaimType, ConnectionType, EvidenceRelationship, EvidenceType, ProposalStatus, Reliability, TrustLevel, TrustStatus


DATA_DIR = Path(__file__).with_name("data")


@dataclass(frozen=True, slots=True)
class SeedSummary:
    contexts: int
    terms: int
    concepts: int
    claims: int
    evidence: int
    connections: int
    cir: int


def _load_json(name: str):
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


def _slug(prefix: str, index: int) -> str:
    return f"{prefix}_{index:02d}"


def _expand_claims(raw_claims: dict[str, object]) -> list[dict[str, object]]:
    claims = list(raw_claims["base_claims"])
    for group in raw_claims["generated_claim_groups"]:
        for index, topic in enumerate(group["topics"], start=1):
            claims.append(
                {
                    "slug": _slug(group["slug_prefix"], index),
                    "statement": group["template"].format(topic=topic, index=index),
                    "claim_type": group["claim_type"],
                    "trust_status": group["trust_status"],
                    "context_refs": list(group["context_refs"]),
                    "concept_refs": list(group["concept_refs"]),
                }
            )
    return claims


def _expand_evidence(raw_evidence: dict[str, object]) -> list[dict[str, object]]:
    evidence = list(raw_evidence["base_evidence"])
    for series in raw_evidence["generated_series"]:
        for index, topic in enumerate(series["topics"], start=1):
            evidence.append(
                {
                    "slug": _slug(series["slug_prefix"], index),
                    "title": series["title_template"].format(index=index),
                    "evidence_type": series["evidence_type"],
                    "source": series["source_template"].format(index=index),
                    "excerpt": series["excerpt_template"].format(index=index, topic=topic),
                    "reliability": series["reliability"],
                    "claim_refs": [_slug(series["claim_ref_prefix"], index)],
                }
            )
    return evidence


def _ensure_seed_actor(session: Session) -> Actor:
    actor = session.scalar(select(Actor).where(Actor.name == "Dataset Seeder"))
    if actor is None:
        actor = Actor(actor_type=ActorType.HUMAN, name="Dataset Seeder", trust_level=TrustLevel.ADMIN)
        session.add(actor)
        session.flush()
    return actor


def _upsert_context(session: Session, actor: Actor, item: dict[str, object], context_map: dict[str, Context]) -> None:
    context = session.scalar(select(Context).where(Context.name == item["name"]))
    if context is None:
        context = Context(name=item["name"], created_by_id=actor.id)
    context.description = item["description"]
    context.field = item["field"]
    context.assumptions = list(item["assumptions"])
    session.add(context)
    session.flush()
    context_map[item["key"]] = context


def _upsert_referent(session: Session, actor: Actor, item: dict[str, object], referent_map: dict[str, Referent]) -> Referent:
    referent = session.scalar(select(Referent).where(Referent.label == item["label"]))
    if referent is None:
        referent = Referent(label=item["label"], created_by_id=actor.id)
    referent.description = item["description"]
    session.add(referent)
    session.flush()
    referent_map[item["key"]] = referent
    return referent


def _upsert_concept(session: Session, actor: Actor, item: dict[str, object], referent_map: dict[str, Referent], concept_map: dict[str, Concept]) -> None:
    concept = session.scalar(select(Concept).where(Concept.label == item["label"], Concept.field == item["field"]))
    if concept is None:
        concept = Concept(label=item["label"], field=item["field"], created_by_id=actor.id)
    concept.description = item["description"]
    referent_item = item.get("referent")
    if referent_item is not None:
        referent = referent_map[referent_item["key"]]
        concept.referent_id = referent.id
    session.add(concept)
    session.flush()
    concept_map[item["key"]] = concept


def _upsert_term(session: Session, actor: Actor, item: dict[str, object], concept_map: dict[str, Concept], term_map: dict[str, Term]) -> None:
    term = session.scalar(select(Term).where(Term.surface_form == item["surface_form"], Term.language == item["language"]))
    if term is None:
        term = Term(surface_form=item["surface_form"], language=item["language"], created_by_id=actor.id)
    term.field_hint = item.get("field_hint")
    term.concepts = [concept_map[key] for key in item.get("concept_refs", [])]
    session.add(term)
    session.flush()
    term_map[item["key"]] = term


def _upsert_claim(session: Session, actor: Actor, item: dict[str, object], context_map: dict[str, Context], concept_map: dict[str, Concept], claim_map: dict[str, Claim]) -> None:
    claim = session.scalar(select(Claim).where(Claim.statement == item["statement"]))
    if claim is None:
        claim = Claim(statement=item["statement"], created_by_id=actor.id)
    claim.claim_type = ClaimType(item["claim_type"])
    claim.trust_status = TrustStatus(item["trust_status"])
    claim.context_links = [ClaimContext(claim_id=claim.id, context_id=context_map[key].id) for key in item.get("context_refs", [])]
    claim.concept_links = [ClaimConcept(claim_id=claim.id, concept_id=concept_map[key].id, role="related") for key in item.get("concept_refs", [])]
    session.add(claim)
    session.flush()
    claim_map[item["slug"]] = claim


def _upsert_evidence(session: Session, actor: Actor, item: dict[str, object], claim_map: dict[str, Claim]) -> None:
    evidence = session.scalar(select(Evidence).where(Evidence.title == item["title"], Evidence.source == item["source"]))
    if evidence is None:
        evidence = Evidence(title=item["title"], source=item["source"], created_by_id=actor.id)
    evidence.evidence_type = EvidenceType(item["evidence_type"])
    evidence.excerpt = item.get("excerpt")
    evidence.reliability = Reliability(item["reliability"])
    session.add(evidence)
    session.flush()
    session.query(ClaimEvidence).filter(ClaimEvidence.evidence_id == evidence.id).delete(synchronize_session=False)
    session.add_all(
        [
            ClaimEvidence(
                claim_id=claim_map[claim_ref].id,
                evidence_id=evidence.id,
                relationship_type=EvidenceRelationship.SUPPORTS,
            )
            for claim_ref in item.get("claim_refs", [])
        ]
    )
    session.flush()


def _upsert_connection(session: Session, item: dict[str, object], claim_map: dict[str, Claim]) -> None:
    source_claim = claim_map[item["source_claim_ref"]]
    target_claim = claim_map[item["target_claim_ref"]]
    connection = session.scalar(
        select(CrossFieldConnection).where(
            CrossFieldConnection.source_claim_id == source_claim.id,
            CrossFieldConnection.target_claim_id == target_claim.id,
            CrossFieldConnection.connection_type == ConnectionType(item["connection_type"]),
        )
    )
    if connection is None:
        connection = CrossFieldConnection(
            source_claim_id=source_claim.id,
            target_claim_id=target_claim.id,
            connection_type=ConnectionType(item["connection_type"]),
            description=item["description"],
            confidence=item["confidence"],
        )
    connection.description = item["description"]
    connection.confidence = item["confidence"]
    connection.status = ProposalStatus(item["status"])
    session.add(connection)
    session.flush()


def _upsert_cir(session: Session, item: dict[str, object], claim_map: dict[str, Claim]) -> None:
    claim = claim_map[item["claim_ref"]]
    cir = session.scalar(select(CIR).where(CIR.claim_id == claim.id))
    if cir is None:
        cir = CIR(claim_id=claim.id, context_ref=item["context_ref"], subject=item["subject"], relation=item["relation"])
    cir.context_ref = item["context_ref"]
    cir.subject = item["subject"]
    cir.relation = item["relation"]
    cir.object = item.get("object")
    cir.conditions = list(item.get("conditions", []))
    cir.units = item.get("units")
    cir.definition_refs = list(item.get("definition_refs", []))
    session.add(cir)
    session.flush()


def seed_entropy_dataset(session: Session) -> SeedSummary:
    contexts = _load_json("contexts.json")
    terms = _load_json("terms.json")
    concepts = _load_json("concepts.json")
    claims = _expand_claims(_load_json("claims.json"))
    evidence = _expand_evidence(_load_json("evidence.json"))
    connections = _load_json("connections.json")
    cir_items = _load_json("cir.json")

    actor = _ensure_seed_actor(session)

    context_map: dict[str, Context] = {}
    referent_map: dict[str, Referent] = {}
    concept_map: dict[str, Concept] = {}
    term_map: dict[str, Term] = {}
    claim_map: dict[str, Claim] = {}

    for item in contexts:
        _upsert_context(session, actor, item, context_map)

    for item in concepts:
        referent_item = item.get("referent")
        if referent_item is not None and referent_item["key"] not in referent_map:
            _upsert_referent(session, actor, referent_item, referent_map)
        _upsert_concept(session, actor, item, referent_map, concept_map)

    for item in terms:
        _upsert_term(session, actor, item, concept_map, term_map)

    for item in claims:
        _upsert_claim(session, actor, item, context_map, concept_map, claim_map)

    for item in evidence:
        _upsert_evidence(session, actor, item, claim_map)

    for item in connections:
        _upsert_connection(session, item, claim_map)

    for item in cir_items:
        _upsert_cir(session, item, claim_map)

    session.commit()

    return SeedSummary(
        contexts=session.scalar(select(Context).count()) if False else session.query(Context).count(),
        terms=session.query(Term).count(),
        concepts=session.query(Concept).count(),
        claims=session.query(Claim).count(),
        evidence=session.query(Evidence).count(),
        connections=session.query(CrossFieldConnection).count(),
        cir=session.query(CIR).count(),
    )


def main() -> None:
    database_url = os.getenv("DATABASE_URL", "sqlite:///./entropy_demo.db")
    engine = create_engine(database_url, future=True)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    with session_factory() as session:
        summary = seed_entropy_dataset(session)
    print(
        json.dumps(
            {
                "contexts": summary.contexts,
                "terms": summary.terms,
                "concepts": summary.concepts,
                "claims": summary.claims,
                "evidence": summary.evidence,
                "connections": summary.connections,
                "cir": summary.cir,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()