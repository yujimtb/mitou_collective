export const dynamic = "force-dynamic";

import { ForceGraph } from "@/components/graph/ForceGraph";
import { FilterBar } from "@/components/common/FilterBar";
import { Header } from "@/components/layout/Header";
import { getGraphData, getReferenceData } from "@/lib/api";

export default async function GraphPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const field = typeof params.field === "string" ? params.field : undefined;
  const contextId = typeof params.contextId === "string" ? params.contextId : undefined;

  const [{ contexts, fields }, graph] = await Promise.all([
    getReferenceData(),
    getGraphData({ field, contextId }),
  ]);

  return (
    <>
      <Header
        title="Graph view"
        subtitle="Inspect claim and concept neighborhoods, then narrow the surface by context or field."
      />
      <FilterBar contexts={contexts} fields={fields} filters={{ contextId, field }} />
      <ForceGraph data={graph} />
    </>
  );
}
