import { ClaimCard } from "@/components/claims/ClaimCard";
import { ClaimTable } from "@/components/claims/ClaimTable";
import { FilterBar } from "@/components/common/FilterBar";
import { Pagination } from "@/components/common/Pagination";
import { Header } from "@/components/layout/Header";
import { getReferenceData, listClaims } from "@/lib/api";
import type { ClaimListFilters } from "@/lib/api";
import type { TrustStatus } from "@/lib/types";

export default async function ClaimsPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const page = Number(params.page ?? 1);
  const trustStatusValue =
    typeof params.trustStatus === "string"
      ? (params.trustStatus as TrustStatus | "")
      : undefined;
  const filters: ClaimListFilters = {
    query: typeof params.query === "string" ? params.query : "",
    contextId: typeof params.contextId === "string" ? params.contextId : undefined,
    field: typeof params.field === "string" ? params.field : undefined,
    trustStatus: trustStatusValue,
  };
  const [{ contexts, fields }, claimsPage] = await Promise.all([
    getReferenceData(),
    listClaims(filters, page, 4),
  ]);
  const contextMap = new Map(contexts.map((context) => [context.id, context]));

  return (
    <>
      <Header
        title="Claim registry"
        subtitle="Filter by context, field, trust state, or text to move through the graph as evidence changes."
      />

      <FilterBar contexts={contexts} fields={fields} filters={filters} />

      <ClaimTable claims={claimsPage.items} contextMap={contextMap} />

      <section className="cards-grid">
        {claimsPage.items.map((claim) => (
          <ClaimCard
            claim={claim}
            contexts={claim.context_ids.map((contextId) => contextMap.get(contextId)).filter(Boolean) as typeof contexts}
            key={claim.id}
          />
        ))}
      </section>

      <Pagination
        basePath="/claims"
        currentPage={claimsPage.current_page}
        perPage={claimsPage.per_page}
        query={{
          query: filters.query,
          contextId: filters.contextId,
          field: filters.field,
          trustStatus: filters.trustStatus,
        }}
        totalCount={claimsPage.total_count}
      />
    </>
  );
}
