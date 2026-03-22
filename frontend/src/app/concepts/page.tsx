export const dynamic = "force-dynamic";

import Link from "next/link";

import { Header } from "@/components/layout/Header";
import { listConcepts } from "@/lib/api";

export default async function ConceptsPage() {
  const concepts = await listConcepts();

  return (
    <>
      <Header
        title="Concept map"
        subtitle="Trace the vocabulary that lets thermodynamics, information theory, and algorithmic descriptions talk to each other."
      />

      <section className="concept-grid">
        {concepts.map((concept) => (
          <Link className="card" href={`/concepts/${concept.id}`} key={concept.id}>
            <div className="badge-row">
              <span className="type-pill">{concept.field}</span>
            </div>
            <h2 className="card-title" style={{ marginTop: 14 }}>{concept.label}</h2>
            <p className="supporting-text">{concept.description}</p>
          </Link>
        ))}
      </section>
    </>
  );
}
