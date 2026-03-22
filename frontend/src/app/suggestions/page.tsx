export const dynamic = "force-dynamic";

import { Header } from "@/components/layout/Header";
import { SuggestionCard } from "@/components/suggestions/SuggestionCard";
import { listClaims, listSuggestions } from "@/lib/api";

function readParam(value: string | string[] | undefined) {
  return typeof value === "string" ? value : "";
}

export default async function SuggestionsPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const status = readParam(params.status) || "pending";
  const minConfidenceRaw = Number(readParam(params.min_confidence) || "0");
  const minConfidence = Number.isFinite(minConfidenceRaw) ? Math.max(0, Math.min(100, minConfidenceRaw)) : 0;

  const [proposals, claimPage] = await Promise.all([
    listSuggestions({
      status: status as "all" | "pending" | "approved" | "rejected" | "in_review" | "withdrawn",
      minConfidence: minConfidence / 100,
    }),
    listClaims({}, 1, 100),
  ]);

  const claimMap = new Map(claimPage.items.map((claim) => [claim.id, claim.statement]));

  return (
    <>
      <Header
        title="AI suggestions"
        subtitle="Filter linking proposals by review state and confidence, then approve or reject them inline."
      />

      <form className="filter-bar" method="get">
        <label>
          Status
          <select defaultValue={status} name="status">
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="all">All</option>
          </select>
        </label>

        <label>
          Minimum confidence: {minConfidence}%
          <input defaultValue={minConfidence} max={100} min={0} name="min_confidence" type="range" />
        </label>

        <button className="button" type="submit">
          Apply filters
        </button>
      </form>

      <section className="proposal-stack">
        {proposals.length ? (
          proposals.map((proposal) => {
            const sourceClaimId =
              typeof proposal.payload.source_claim_id === "string" ? proposal.payload.source_claim_id : "";
            const targetClaimId =
              typeof proposal.payload.target_claim_id === "string" ? proposal.payload.target_claim_id : "";

            return (
              <SuggestionCard
                key={proposal.id}
                proposal={proposal}
                sourceClaimLabel={claimMap.get(sourceClaimId) ?? "Unknown source claim"}
                targetClaimLabel={claimMap.get(targetClaimId) ?? "Unknown target claim"}
              />
            );
          })
        ) : (
          <div className="empty-state">No AI suggestions match the current filters.</div>
        )}
      </section>
    </>
  );
}
