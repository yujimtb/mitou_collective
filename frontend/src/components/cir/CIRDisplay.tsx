import type { CIRRead } from "@/lib/types";

export function CIRDisplay({ cir }: { cir: CIRRead }) {
  return (
    <section className="card-stack">
      <div className="card">
        <p className="eyebrow">CIR</p>
        <h3 className="card-title">Structured Claim Representation</h3>
        <div className="list-stack" style={{ marginTop: 16 }}>
          <div className="mini-card">
            <strong>Context Ref</strong>
            <p className="supporting-text">{cir.context_ref}</p>
          </div>
          <div className="mini-card">
            <strong>Triple</strong>
            <p className="supporting-text">
              {cir.subject} {cir.relation} {cir.object ?? "(implicit object)"}
            </p>
          </div>
          <div className="mini-card">
            <strong>Conditions</strong>
            <div className="chip-row" style={{ marginTop: 10 }}>
              {cir.conditions.map((condition) => (
                <span className="chip" key={`${condition.predicate}-${condition.argument}`}>
                  {condition.negated ? "not " : ""}
                  {condition.predicate}: {condition.argument}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
