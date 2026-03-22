export const dynamic = "force-dynamic";

import { Header } from "@/components/layout/Header";
import { ProposalCard } from "@/components/proposals/ProposalCard";
import { listProposals } from "@/lib/api";

export default async function ReviewPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const status = typeof params.status === "string" ? params.status : "pending";
  const proposals = await listProposals({ status: status as "all" | "pending" | "approved" | "rejected" | "in_review" | "withdrawn" });

  return (
    <>
      <Header
        title="Review queue"
        subtitle="Resolve AI linking proposals and trust updates before they land in the graph."
      />

      <form className="filter-bar" method="get">
        <label>
          Status
          <select defaultValue={status} name="status">
            <option value="pending">Pending</option>
            <option value="all">All</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
        </label>
        <button className="button" type="submit">
          Refresh view
        </button>
      </form>

      <section className="proposal-stack">
        {proposals.length ? (
          proposals.map((proposal) => <ProposalCard key={proposal.id} proposal={proposal} />)
        ) : (
          <div className="empty-state">No proposals match this status filter.</div>
        )}
      </section>
    </>
  );
}
