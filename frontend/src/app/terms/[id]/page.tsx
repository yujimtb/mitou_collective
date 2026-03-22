export const dynamic = "force-dynamic";

import Link from "next/link";
import { notFound } from "next/navigation";

import { Header } from "@/components/layout/Header";
import { ApiError, getTerm, listConcepts } from "@/lib/api";

export default async function TermDetailPage({ params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const [term, concepts] = await Promise.all([getTerm(id), listConcepts()]);
    const relatedConcepts = concepts.filter((concept) => term.concept_ids.includes(concept.id));

    return (
      <>
        <Header
          title="Term detail"
          subtitle="Inspect one term, its language, and the concepts that reuse the same expression."
        />

        <section className="detail-grid">
          <article className="card section-stack">
            <div className="badge-row">
              <span className="type-pill">{term.language}</span>
              {term.field_hint ? <span className="chip">{term.field_hint}</span> : null}
            </div>

            <div>
              <p className="eyebrow">Surface form</p>
              <h2 className="hero-title" style={{ fontSize: "2rem" }}>
                {term.surface_form}
              </h2>
            </div>

            <div>
              <p className="eyebrow">Created</p>
              <p className="supporting-text">
                {new Date(term.created_at).toLocaleString()}
                {term.created_by ? ` · ${term.created_by.name}` : ""}
              </p>
            </div>
          </article>

          <article className="card">
            <p className="eyebrow">Related concepts</p>
            <div className="chip-row" style={{ marginTop: 12 }}>
              {relatedConcepts.length ? (
                relatedConcepts.map((concept) => (
                  <Link className="chip" href={`/concepts/${concept.id}`} key={concept.id}>
                    {concept.label} · {concept.field}
                  </Link>
                ))
              ) : (
                <span className="supporting-text">No concepts are linked to this term yet.</span>
              )}
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
