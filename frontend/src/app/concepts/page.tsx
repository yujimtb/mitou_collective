export const dynamic = "force-dynamic";

import Link from "next/link";

import { CreateConceptDialog } from "@/components/CreateConceptDialog";
import { Header } from "@/components/layout/Header";
import { getReferenceData, listConcepts } from "@/lib/api";

export default async function ConceptsPage() {
  const [concepts, referenceData] = await Promise.all([listConcepts(), getReferenceData()]);

  return (
    <>
      <Header
        title="Concept map"
        subtitle="Trace the vocabulary that lets thermodynamics, information theory, and algorithmic descriptions talk to each other."
      />

      <div className="actions-row" style={{ marginBottom: 16 }}>
        <CreateConceptDialog fields={referenceData.fields} terms={referenceData.terms} />
      </div>

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
