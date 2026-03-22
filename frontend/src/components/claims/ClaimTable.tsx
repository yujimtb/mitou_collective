import Link from "next/link";

import { TrustBadge } from "@/components/common/TrustBadge";
import type { ClaimRead, ContextRead } from "@/lib/types";

interface ClaimTableProps {
  claims: ClaimRead[];
  contextMap: Map<string, ContextRead>;
}

export function ClaimTable({ claims, contextMap }: ClaimTableProps) {
  return (
    <div className="table-card">
      <table className="table">
        <thead>
          <tr>
            <th>Statement</th>
            <th>Type</th>
            <th>Trust</th>
            <th>Contexts</th>
          </tr>
        </thead>
        <tbody>
          {claims.map((claim) => (
            <tr key={claim.id}>
              <td>
                <Link href={`/claims/${claim.id}`}>{claim.statement}</Link>
              </td>
              <td>
                <span className="type-pill">{claim.claim_type}</span>
              </td>
              <td>
                <TrustBadge status={claim.trust_status} />
              </td>
              <td>
                <div className="chip-row">
                  {claim.context_ids.map((contextId) => (
                    <span className="chip" key={contextId}>
                      {contextMap.get(contextId)?.name ?? contextId}
                    </span>
                  ))}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
