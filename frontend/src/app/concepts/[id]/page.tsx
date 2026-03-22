export const dynamic = "force-dynamic";

import Link from "next/link";
import { notFound } from "next/navigation";

import { Header } from "@/components/layout/Header";
import { getConceptDetail } from "@/lib/api";

export default async function ConceptDetailPage({ params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const data = await getConceptDetail(id);

    return (
      <>
        <Header
          title="Concept detail"
          subtitle="Inspect term anchors, attached claims, and neighboring concepts across domains."
        />

        <section className="detail-grid">
          <article className="card-stack">
            <div className="card">
              <div className="badge-row">
                <span className="type-pill">{data.concept.field}</span>
                <span className="chip">{data.claims.length} attached claims</span>
              </div>
              <h2 className="hero-title" style={{ fontSize: "2rem", marginTop: 16 }}>
                {data.concept.label}
              </h2>
              <p className="supporting-text">{data.concept.description}</p>
              <div className="chip-row" style={{ marginTop: 16 }}>
                {data.terms.map((term) => (
                  <span className="chip" key={term.id}>
                    {term.surface_form}
                  </span>
                ))}
              </div>
            </div>

            <div className="card">
              <p className="eyebrow">Related claims</p>
              <div className="card-stack" style={{ marginTop: 14 }}>
                {data.claims.map((claim) => (
                  <Link className="mini-card" href={`/claims/${claim.id}`} key={claim.id}>
                    <strong>{claim.statement}</strong>
                    <p className="supporting-text">{claim.claim_type}</p>
                  </Link>
                ))}
              </div>
            </div>
          </article>

          <article className="card-stack">
            <div className="card">
              <p className="eyebrow">Neighboring concepts</p>
              <div className="card-stack" style={{ marginTop: 14 }}>
                {data.relatedConcepts.map((concept) => (
                  <Link className="mini-card" href={`/concepts/${concept.id}`} key={concept.id}>
                    <strong>{concept.label}</strong>
                    <p className="supporting-text">{concept.field}</p>
                  </Link>
                ))}
              </div>
            </div>

            <div className="card">
              <p className="eyebrow">Connections</p>
              <div className="card-stack" style={{ marginTop: 14 }}>
                {data.connections.map((connection) => (
                  <div className="mini-card" key={connection.id}>
                    <strong>{connection.connection_type}</strong>
                    <p className="supporting-text">{connection.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </article>
        </section>
      </>
    );
  } catch {
    notFound();
  }
}
