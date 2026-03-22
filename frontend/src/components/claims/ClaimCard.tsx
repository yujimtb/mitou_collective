import Link from "next/link";

import { TrustBadge } from "@/components/common/TrustBadge";
import type { ClaimRead, ContextRead } from "@/lib/types";

export function ClaimCard({ claim, contexts }: { claim: ClaimRead; contexts: ContextRead[] }) {
  return (
    <Link className="card" href={`/claims/${claim.id}`}>
      <div className="badge-row">
        <span className="type-pill">{claim.claim_type}</span>
        <TrustBadge status={claim.trust_status} />
      </div>
      <h3 className="card-title" style={{ marginTop: 14 }}>
        {claim.statement}
      </h3>
      <div className="chip-row" style={{ marginTop: 14 }}>
        {contexts.map((context) => (
          <span className="chip" key={context.id}>
            {context.name}
          </span>
        ))}
      </div>
      <p className="supporting-text" style={{ marginBottom: 0 }}>
        Version {claim.version} · {new Date(claim.created_at).toLocaleDateString()}
      </p>
    </Link>
  );
}
