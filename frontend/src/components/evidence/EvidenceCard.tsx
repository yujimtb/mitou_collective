import type { ClaimEvidenceView } from "@/lib/api";

export function EvidenceCard({ evidence }: { evidence: ClaimEvidenceView }) {
  return (
    <article className="evidence-card">
      <div className="badge-row">
        <span className="type-pill">{evidence.evidence_type}</span>
        <span className="chip">Reliability: {evidence.reliability}</span>
        {evidence.relationship ? <span className="chip">{evidence.relationship}</span> : null}
      </div>
      <h3 className="card-title" style={{ marginTop: 12 }}>
        {evidence.title}
      </h3>
      <p className="supporting-text">{evidence.source}</p>
      {evidence.excerpt ? <p className="snippet">{evidence.excerpt}</p> : null}
    </article>
  );
}
