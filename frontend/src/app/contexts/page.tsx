import Link from "next/link";

import { Header } from "@/components/layout/Header";
import { listContexts } from "@/lib/api";

export default async function ContextsPage() {
  const items = await listContexts();

  return (
    <>
      <Header
        title="Context registry"
        subtitle="Browse theory frames, assumptions, and the claim density inside each context."
      />

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
