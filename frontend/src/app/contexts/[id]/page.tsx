export const dynamic = "force-dynamic";

import Link from "next/link";
import { notFound } from "next/navigation";

import { Header } from "@/components/layout/Header";
import { ApiError, getContextDetail } from "@/lib/api";

export default async function ContextDetailPage({ params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const data = await getContextDetail(id);

    return (
      <>
        <Header
          title="Context detail"
          subtitle="Expose assumptions, descendants, and claims that share one theoretical frame."
        />

        <section className="detail-grid">
          <article className="card-stack">
            <div className="card">
              <div className="badge-row">
                <span className="type-pill">{data.context.field}</span>
              </div>
              <h2 className="hero-title" style={{ fontSize: "2rem", marginTop: 16 }}>
                {data.context.name}
              </h2>
              <p className="supporting-text">{data.context.description}</p>
              <div className="chip-row" style={{ marginTop: 16 }}>
                {data.context.assumptions.map((assumption) => (
                  <span className="chip" key={assumption}>
                    {assumption}
                  </span>
                ))}
              </div>
            </div>

            <div className="card">
              <p className="eyebrow">Claims in context</p>
              <div className="card-stack" style={{ marginTop: 14 }}>
                {data.claims.map((claim) => (
                  <Link className="mini-card" href={`/claims/${claim.id}`} key={claim.id}>
                    <strong>{claim.statement}</strong>
                    <p className="supporting-text">{claim.claim_type} · v{claim.version}</p>
                  </Link>
                ))}
              </div>
            </div>
          </article>

          <article className="card">
            <p className="eyebrow">Child contexts</p>
            {data.children.length ? (
              <div className="card-stack" style={{ marginTop: 14 }}>
                {data.children.map((child) => (
                  <Link className="mini-card" href={`/contexts/${child.id}`} key={child.id}>
                    <strong>{child.name}</strong>
                    <p className="supporting-text">{child.description}</p>
                  </Link>
                ))}
              </div>
            ) : (
              <div className="empty-state" style={{ marginTop: 14 }}>
                No child contexts are currently attached.
              </div>
            )}
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
