export const dynamic = "force-dynamic";

import { notFound } from "next/navigation";

import { ClaimDetail } from "@/components/claims/ClaimDetail";
import { Header } from "@/components/layout/Header";
import { ApiError, getClaimDetail, listClaims } from "@/lib/api";

export default async function ClaimDetailPage({ params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const [data, claimPage] = await Promise.all([getClaimDetail(id), listClaims({}, 1, 100)]);

    return (
      <>
        <Header
          title="Claim detail"
          subtitle="Review evidence, structured representation, history, and AI-suggested bridges around one statement."
        />
        <ClaimDetail availableClaims={claimPage.items} data={data} />
      </>
    );
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) {
      notFound();
    }
    throw e;
  }
}
