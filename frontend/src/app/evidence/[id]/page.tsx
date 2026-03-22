export const dynamic = "force-dynamic";

import Link from "next/link";
import { notFound } from "next/navigation";

import { Header } from "@/components/layout/Header";
import { ApiError, getEvidence } from "@/lib/api";

function sourceHref(source: string) {
  try {
    const url = new URL(source);
    return url.toString();
  } catch {
    return null;
  }
}

function reliabilityPercent(reliability: string) {
  if (reliability === "high") return 100;
  if (reliability === "medium") return 68;
  if (reliability === "low") return 38;
  return 18;
}

export default async function EvidenceDetailPage({ params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const evidence = await getEvidence(id);
    const href = sourceHref(evidence.source);
    const percent = reliabilityPercent(evidence.reliability);

    return (
      <>
        <Header
          title="Evidence detail"
          subtitle="Inspect provenance, excerpted support, and the claims linked to this evidence record."
        />

        <section className="detail-grid">
          <article className="card section-stack">
            <div className="badge-row">
              <span className="type-pill">{evidence.evidence_type}</span>
              <span className="chip">Reliability: {evidence.reliability}</span>
            </div>

            <div>
              <p className="eyebrow">Title</p>
              <h2 className="hero-title" style={{ fontSize: "2rem" }}>
                {evidence.title}
              </h2>
            </div>

            <div>
              <p className="eyebrow">Source</p>
              {href ? (
                <a className="ghost-button" href={href} rel="noreferrer" target="_blank">
                  Open source
                </a>
              ) : (
                <p className="supporting-text">{evidence.source}</p>
              )}
            </div>

            {evidence.excerpt ? (
              <blockquote
                className="mini-card"
                style={{ borderLeft: "4px solid var(--amber-400)", margin: 0, fontStyle: "italic" }}
              >
                {evidence.excerpt}
              </blockquote>
            ) : null}
          </article>

          <article className="card section-stack">
            <div>
              <p className="eyebrow">Reliability indicator</p>
              <div className="confidence-bar" style={{ marginTop: 10 }}>
                <span style={{ width: `${percent}%` }} />
              </div>
              <p className="small" style={{ marginTop: 10 }}>
                Confidence signal for this evidence: {evidence.reliability}
              </p>
            </div>

            <div>
              <p className="eyebrow">Related claims</p>
              <div className="card-stack" style={{ marginTop: 12 }}>
                {evidence.related_claims.length ? (
                  evidence.related_claims.map((claim) => (
                    <Link className="card" href={`/claims/${claim.claim_id}`} key={claim.claim_id}>
                      <div className="badge-row">
                        <span className="chip">{claim.relationship}</span>
                        <span className={`trust-badge trust-${claim.trust_status}`}>{claim.trust_status}</span>
                      </div>
                      <h3 className="card-title" style={{ marginTop: 12 }}>
                        {claim.statement}
                      </h3>
                    </Link>
                  ))
                ) : (
                  <div className="empty-state">No claims are linked to this evidence yet.</div>
                )}
              </div>
            </div>
          </article>
        </section>
      </>
    );
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) {
      notFound();
    }
    throw e;
  }
}
