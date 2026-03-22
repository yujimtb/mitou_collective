import Link from "next/link";

import type { GraphData } from "@/lib/api";

const edgeStyles: Record<string, string> = {
  equivalent: "#5f8da3",
  analogous: "#c78838",
  generalizes: "#5f8f5d",
  contradicts: "#ca6b55",
  complements: "#173033",
};

export function ForceGraph({ data }: { data: GraphData }) {
  return (
    <section className="graph-surface">
      <div className="legend-row" style={{ marginBottom: 18 }}>
        <span className="chip">Claim node</span>
        <span className="chip">Concept node</span>
        <span className="chip">Connection edge style encodes relation type</span>
      </div>

      <div className="graph-grid">
        {data.nodes.map((node) => (
          <article className={`graph-node ${node.kind}`} key={node.id}>
            <div className="badge-row">
              <span className="type-pill">{node.kind}</span>
              <span className="chip">{node.field}</span>
            </div>
            <h3 className="card-title" style={{ marginTop: 12 }}>
              {node.kind === "claim" ? `${node.label.slice(0, 88)}${node.label.length > 88 ? "..." : ""}` : node.label}
            </h3>
            <div className="chip-row" style={{ marginTop: 16 }}>
              {data.edges
                .filter((edge) => edge.source === node.id || edge.target === node.id)
                .slice(0, 4)
                .map((edge) => (
                  <span
                    className="edge-pill"
                    key={edge.id}
                    style={{ borderLeft: `4px solid ${edge.connectionType ? edgeStyles[edge.connectionType] : "#20464a"}` }}
                  >
                    {edge.connectionType ?? edge.kind}
                  </span>
                ))}
            </div>
            <div className="actions-row" style={{ marginTop: 18 }}>
              <Link className="ghost-button" href={node.href}>
                Open detail
              </Link>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
