import type { TrustStatus } from "@/lib/types";

const labels: Record<TrustStatus, string> = {
  established: "Established",
  tentative: "Tentative",
  disputed: "Disputed",
  ai_suggested: "AI Suggested",
  retracted: "Retracted",
};

export function TrustBadge({ status }: { status: TrustStatus }) {
  return <span className={`trust-badge trust-${status}`}>{labels[status]}</span>;
}
