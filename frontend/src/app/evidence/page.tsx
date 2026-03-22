export const dynamic = "force-dynamic";

import Link from "next/link";

import { Header } from "@/components/layout/Header";
import { listEvidence } from "@/lib/api";

const EVIDENCE_TYPES = ["textbook", "paper", "experiment", "proof", "expert_opinion"] as const;
const RELIABILITY_LEVELS = ["high", "medium", "low", "unverified"] as const;

function readParam(value: string | string[] | undefined) {
  return typeof value === "string" ? value : "";
}

export default async function EvidencePage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const evidenceType = readParam(params.evidence_type);
  const reliability = readParam(params.reliability);
  const items = await listEvidence({
    evidenceType: evidenceType || undefined,
    reliability: reliability || undefined,
  });

  return (
    <>
      <Header
        title="Evidence library"
        subtitle="Review supporting material, reliability, and how many claims each evidence record touches."
      />

      <form className="filter-bar" method="get">
        <label>
          Evidence type
          <select defaultValue={evidenceType} name="evidence_type">
            <option value="">All types</option>
            {EVIDENCE_TYPES.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </label>

        <label>
          Reliability
          <select defaultValue={reliability} name="reliability">
            <option value="">All levels</option>
            {RELIABILITY_LEVELS.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </label>

        <button className="button" type="submit">
          Apply filters
        </button>
      </form>

      <section className="cards-grid">
        {items.length ? (
          items.map((evidence) => (
            <Link className="evidence-card" href={`/evidence/${evidence.id}`} key={evidence.id}>
              <div className="badge-row">
                <span className="type-pill">{evidence.evidence_type}</span>
                <span className="chip">Reliability: {evidence.reliability}</span>
              </div>
              <h2 className="card-title" style={{ marginTop: 12 }}>
                {evidence.title}
              </h2>
              <p className="supporting-text">{evidence.source_summary}</p>
              <div className="chip-row" style={{ marginTop: 14 }}>
                <span className="chip">{evidence.claim_count} linked claims</span>
              </div>
            </Link>
          ))
        ) : (
          <div className="empty-state">No evidence matches the current filters.</div>
        )}
      </section>
    </>
  );
}
