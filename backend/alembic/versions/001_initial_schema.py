from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


actor_type_enum = sa.Enum("human", "ai_agent", name="actor_type_enum", native_enum=False)
trust_level_enum = sa.Enum("admin", "reviewer", "contributor", "observer", name="trust_level_enum", native_enum=False)
claim_type_enum = sa.Enum("definition", "theorem", "empirical", "conjecture", "meta", name="claim_type_enum", native_enum=False)
trust_status_enum = sa.Enum("established", "tentative", "disputed", "ai_suggested", name="trust_status_enum", native_enum=False)
evidence_type_enum = sa.Enum("textbook", "paper", "experiment", "proof", "expert_opinion", name="evidence_type_enum", native_enum=False)
reliability_enum = sa.Enum("high", "medium", "low", "unverified", name="reliability_enum", native_enum=False)
proposal_type_enum = sa.Enum("create_claim", "link_claims", "update_trust", "add_evidence", "connect_concepts", name="proposal_type_enum", native_enum=False)
proposal_status_enum = sa.Enum("pending", "in_review", "approved", "rejected", "withdrawn", name="proposal_status_enum", native_enum=False)
review_decision_enum = sa.Enum("approve", "reject", "request_changes", name="review_decision_enum", native_enum=False)
connection_type_enum = sa.Enum("equivalent", "analogous", "generalizes", "contradicts", "complements", name="connection_type_enum", native_enum=False)
evidence_relationship_enum = sa.Enum("supports", "contradicts", "partially_supports", name="evidence_relationship_enum", native_enum=False)
connection_status_enum = sa.Enum("pending", "in_review", "approved", "rejected", "withdrawn", name="connection_status_enum", native_enum=False)


def upgrade() -> None:
    op.create_table(
        "actors",
        sa.Column("actor_type", actor_type_enum, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("trust_level", trust_level_enum, nullable=False),
        sa.Column("agent_model", sa.String(length=100), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_actors"),
    )

    op.create_table(
        "referents",
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(["created_by_id"], ["actors.id"], name="fk_referents_created_by_id_actors", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_referents"),
    )

    op.create_table(
        "terms",
        sa.Column("surface_form", sa.String(length=500), nullable=False),
        sa.Column("language", sa.String(length=10), nullable=False),
        sa.Column("field_hint", sa.String(length=100), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(["created_by_id"], ["actors.id"], name="fk_terms_created_by_id_actors", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_terms"),
    )
    op.create_index("ix_terms_surface_form", "terms", ["surface_form"], unique=False)
    op.create_index("ix_terms_language", "terms", ["language"], unique=False)

    op.create_table(
        "concepts",
        sa.Column("label", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("field", sa.String(length=100), nullable=False),
        sa.Column("referent_id", sa.Uuid(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(["created_by_id"], ["actors.id"], name="fk_concepts_created_by_id_actors", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["referent_id"], ["referents.id"], name="fk_concepts_referent_id_referents", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_concepts"),
    )
    op.create_index("ix_concepts_label", "concepts", ["label"], unique=False)
    op.create_index("ix_concepts_field", "concepts", ["field"], unique=False)

    op.create_table(
        "contexts",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("field", sa.String(length=100), nullable=False),
        sa.Column("assumptions", sa.JSON(), nullable=False),
        sa.Column("parent_context_id", sa.Uuid(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(["created_by_id"], ["actors.id"], name="fk_contexts_created_by_id_actors", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["parent_context_id"], ["contexts.id"], name="fk_contexts_parent_context_id_contexts", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_contexts"),
        sa.UniqueConstraint("name", name="uq_contexts_name"),
    )
    op.create_index("ix_contexts_field", "contexts", ["field"], unique=False)

    op.create_table(
        "evidence",
        sa.Column("evidence_type", evidence_type_enum, nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("excerpt", sa.Text(), nullable=True),
        sa.Column("reliability", reliability_enum, nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(["created_by_id"], ["actors.id"], name="fk_evidence_created_by_id_actors", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_evidence"),
    )
    op.create_index("ix_evidence_evidence_type", "evidence", ["evidence_type"], unique=False)
    op.create_index("ix_evidence_reliability", "evidence", ["reliability"], unique=False)

    op.create_table(
        "claims",
        sa.Column("statement", sa.Text(), nullable=False),
        sa.Column("claim_type", claim_type_enum, nullable=False),
        sa.Column("trust_status", trust_status_enum, nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_by_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(["created_by_id"], ["actors.id"], name="fk_claims_created_by_id_actors", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_claims"),
    )
    op.create_index("ix_claims_claim_type", "claims", ["claim_type"], unique=False)
    op.create_index("ix_claims_trust_status", "claims", ["trust_status"], unique=False)

    op.create_table(
        "proposals",
        sa.Column("proposal_type", proposal_type_enum, nullable=False),
        sa.Column("proposed_by_id", sa.Uuid(), nullable=False),
        sa.Column("target_entity_type", sa.String(length=50), nullable=False),
        sa.Column("target_entity_id", sa.Uuid(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("status", proposal_status_enum, nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by_id", sa.Uuid(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["proposed_by_id"], ["actors.id"], name="fk_proposals_proposed_by_id_actors", ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["reviewed_by_id"], ["actors.id"], name="fk_proposals_reviewed_by_id_actors", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_proposals"),
    )

    op.create_table(
        "reviews",
        sa.Column("proposal_id", sa.Uuid(), nullable=False),
        sa.Column("reviewer_id", sa.Uuid(), nullable=False),
        sa.Column("decision", review_decision_enum, nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["proposal_id"], ["proposals.id"], name="fk_reviews_proposal_id_proposals", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reviewer_id"], ["actors.id"], name="fk_reviews_reviewer_id_actors", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", name="pk_reviews"),
    )

    op.create_table(
        "cross_field_connections",
        sa.Column("source_claim_id", sa.Uuid(), nullable=False),
        sa.Column("target_claim_id", sa.Uuid(), nullable=False),
        sa.Column("connection_type", connection_type_enum, nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("proposal_id", sa.Uuid(), nullable=True),
        sa.Column("status", connection_status_enum, nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["proposal_id"], ["proposals.id"], name="fk_cross_field_connections_proposal_id_proposals", ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["source_claim_id"], ["claims.id"], name="fk_cross_field_connections_source_claim_id_claims", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_claim_id"], ["claims.id"], name="fk_cross_field_connections_target_claim_id_claims", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_cross_field_connections"),
    )

    op.create_table(
        "cir",
        sa.Column("claim_id", sa.Uuid(), nullable=False),
        sa.Column("context_ref", sa.String(length=255), nullable=False),
        sa.Column("subject", sa.String(length=500), nullable=False),
        sa.Column("relation", sa.String(length=255), nullable=False),
        sa.Column("object", sa.Text(), nullable=True),
        sa.Column("conditions", sa.JSON(), nullable=False),
        sa.Column("units", sa.String(length=100), nullable=True),
        sa.Column("definition_refs", sa.JSON(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["claim_id"], ["claims.id"], name="fk_cir_claim_id_claims", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_cir"),
        sa.UniqueConstraint("claim_id", name="uq_cir_claim_id"),
    )

    op.create_table(
        "term_concepts",
        sa.Column("term_id", sa.Uuid(), nullable=False),
        sa.Column("concept_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["concept_id"], ["concepts.id"], name="fk_term_concepts_concept_id_concepts", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["term_id"], ["terms.id"], name="fk_term_concepts_term_id_terms", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("term_id", "concept_id", name="pk_term_concepts"),
    )

    op.create_table(
        "claim_contexts",
        sa.Column("claim_id", sa.Uuid(), nullable=False),
        sa.Column("context_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["claim_id"], ["claims.id"], name="fk_claim_contexts_claim_id_claims", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["context_id"], ["contexts.id"], name="fk_claim_contexts_context_id_contexts", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("claim_id", "context_id", name="pk_claim_contexts"),
    )

    op.create_table(
        "claim_concepts",
        sa.Column("claim_id", sa.Uuid(), nullable=False),
        sa.Column("concept_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(["claim_id"], ["claims.id"], name="fk_claim_concepts_claim_id_claims", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["concept_id"], ["concepts.id"], name="fk_claim_concepts_concept_id_concepts", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("claim_id", "concept_id", name="pk_claim_concepts"),
    )

    op.create_table(
        "claim_evidence",
        sa.Column("claim_id", sa.Uuid(), nullable=False),
        sa.Column("evidence_id", sa.Uuid(), nullable=False),
        sa.Column("relationship", evidence_relationship_enum, nullable=False),
        sa.ForeignKeyConstraint(["claim_id"], ["claims.id"], name="fk_claim_evidence_claim_id_claims", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["evidence_id"], ["evidence.id"], name="fk_claim_evidence_evidence_id_evidence", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("claim_id", "evidence_id", name="pk_claim_evidence"),
    )


def downgrade() -> None:
    op.drop_table("claim_evidence")
    op.drop_table("claim_concepts")
    op.drop_table("claim_contexts")
    op.drop_table("term_concepts")
    op.drop_table("cir")
    op.drop_table("cross_field_connections")
    op.drop_table("reviews")
    op.drop_table("proposals")
    op.drop_index("ix_claims_trust_status", table_name="claims")
    op.drop_index("ix_claims_claim_type", table_name="claims")
    op.drop_table("claims")
    op.drop_index("ix_evidence_reliability", table_name="evidence")
    op.drop_index("ix_evidence_evidence_type", table_name="evidence")
    op.drop_table("evidence")
    op.drop_index("ix_contexts_field", table_name="contexts")
    op.drop_table("contexts")
    op.drop_index("ix_concepts_field", table_name="concepts")
    op.drop_index("ix_concepts_label", table_name="concepts")
    op.drop_table("concepts")
    op.drop_index("ix_terms_language", table_name="terms")
    op.drop_index("ix_terms_surface_form", table_name="terms")
    op.drop_table("terms")
    op.drop_table("referents")
    op.drop_table("actors")
