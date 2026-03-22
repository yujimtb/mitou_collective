import Link from "next/link";

import { CIRDisplay } from "@/components/cir/CIRDisplay";
import { TrustBadge } from "@/components/common/TrustBadge";
import { EvidenceCard } from "@/components/evidence/EvidenceCard";
import type { ClaimDetailData } from "@/lib/api";

export function ClaimDetail({ data }: { data: ClaimDetailData }) {
  const { claim, concepts, contexts, evidence, pendingProposals, history } = data;

  return (
    <div className="detail-grid">
      <section className="section-stack">
        <article className="card">
          <div className="badge-row">
            <span className="type-pill">{claim.claim_type}</span>
            <TrustBadge status={claim.trust_status} />
            <span className="chip">Version {claim.version}</span>
          </div>
          <h2 className="hero-title" style={{ fontSize: "2rem", marginTop: 18 }}>
            {claim.statement}
          </h2>

          <div className="section-stack" style={{ marginTop: 20 }}>
            <div>
              <p className="eyebrow">Related Concepts</p>
              <div className="chip-row">
                {concepts.map((concept) => (
                  <Link className="chip" href={`/concepts/${concept.id}`} key={concept.id}>
                    {concept.label} · {concept.field}
                  </Link>
                ))}
              </div>
            </div>

            <div>
              <p className="eyebrow">Contexts</p>
              <div className="chip-row">
                {contexts.map((context) => (
                  <Link className="chip" href={`/contexts/${context.id}`} key={context.id}>
                    {context.name}
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </article>

        {claim.cir ? <CIRDisplay cir={claim.cir} /> : null}

        <section className="card-stack">
          <div className="card">
            <p className="eyebrow">Evidence</p>
            <div className="card-stack" style={{ marginTop: 14 }}>
              {evidence.map((item) => (
                <EvidenceCard evidence={item} key={item.id} />
              ))}
            </div>
          </div>
        </section>
      </section>

      <section className="section-stack">
        <div className="card">
          <p className="eyebrow">AI Suggestions</p>
          {pendingProposals.length ? (
            <div className="proposal-stack" style={{ marginTop: 14 }}>
              {pendingProposals.map((proposal) => {
                const confidence = Number(proposal.payload.confidence ?? 0);
                return (
                  <article className="proposal-card" key={proposal.id}>
                    <div className="badge-row">
                      <span className="status-pill status-pending">Pending</span>
                      <span className="chip">{String(proposal.payload.connection_type)}</span>
                    </div>
                    <p className="supporting-text" style={{ margin: 0 }}>
                      {proposal.rationale}
                    </p>
                    <div className="confidence-bar">
                      <span style={{ width: `${Math.round(confidence * 100)}%` }} />
                    </div>
                    <p className="small">Confidence {Math.round(confidence * 100)}%</p>
                    <div className="actions-row">
                      <Link className="button" href="/review">
                        Review
                      </Link>
                    </div>
                  </article>
                );
              })}
            </div>
          ) : (
            <div className="empty-state" style={{ marginTop: 14 }}>
              No pending AI connection proposals for this claim.
            </div>
          )}
        </div>

        <div className="card">
          <p className="eyebrow">History</p>
          <div className="timeline" style={{ marginTop: 12 }}>
            {history.map((event) => (
              <article className="timeline-item" key={event.id}>
                <strong>{event.title}</strong>
                <p className="supporting-text">{event.summary}</p>
                <p className="small">
                  {event.actorName} · {new Date(event.timestamp).toLocaleString()}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
