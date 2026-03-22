export const dynamic = "force-dynamic";

import Link from "next/link";

import { CreateContextDialog } from "@/components/CreateContextDialog";
import { Header } from "@/components/layout/Header";
import { getReferenceData, listContexts } from "@/lib/api";

export default async function ContextsPage() {
  const [items, referenceData] = await Promise.all([listContexts(), getReferenceData()]);

  return (
    <>
      <Header
        title="Context registry"
        subtitle="Browse theory frames, assumptions, and the claim density inside each context."
      />

      <div className="actions-row" style={{ marginBottom: 16 }}>
        <CreateContextDialog contexts={referenceData.contexts} fields={referenceData.fields} />
      </div>

      <section className="cards-grid">
        {items.map((item) => (
          <Link className="context-node" href={`/contexts/${item.context.id}`} key={item.context.id}>
            <div className="badge-row">
              <span className="type-pill">{item.context.field}</span>
              {item.context.parent_context_id ? <span className="chip">Child context</span> : null}
            </div>
            <h2 className="card-title" style={{ marginTop: 14 }}>{item.context.name}</h2>
            <p className="supporting-text">{item.context.description}</p>
            <div className="chip-row" style={{ marginTop: 14 }}>
              <span className="chip">{item.claimCount} claims</span>
              <span className="chip">{item.childCount} child contexts</span>
            </div>
          </Link>
        ))}
      </section>
    </>
  );
}
