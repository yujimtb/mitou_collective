import { notFound } from "next/navigation";

import { ClaimDetail } from "@/components/claims/ClaimDetail";
import { Header } from "@/components/layout/Header";
import { getClaimDetail } from "@/lib/api";

export default async function ClaimDetailPage({ params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const data = await getClaimDetail(id);

    return (
      <>
        <Header
          title="Claim detail"
          subtitle="Review evidence, structured representation, history, and AI-suggested bridges around one statement."
        />
        <ClaimDetail data={data} />
      </>
    );
  } catch {
    notFound();
  }
}
