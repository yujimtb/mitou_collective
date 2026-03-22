"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { useToast } from "@/components/Toast";
import { ReviewDialog } from "@/components/proposals/ReviewDialog";
import type { ProposalRead, ReviewDecision } from "@/lib/types";

function previewStatement(statement: string) {
  return statement.length > 88 ? `${statement.slice(0, 87)}...` : statement;
}

export function SuggestionCard({
  proposal,
  sourceClaimLabel,
  targetClaimLabel,
}: {
  proposal: ProposalRead;
  sourceClaimLabel: string;
  targetClaimLabel: string;
}) {
  const router = useRouter();
  const { pushToast } = useToast();
  const [openDecision, setOpenDecision] = useState<"approve" | "reject" | null>(null);
  const [isClosing, setIsClosing] = useState(false);
  const [isHidden, setIsHidden] = useState(false);

  const confidence = Math.round(Number(proposal.payload.confidence ?? 0) * 100);
  const sourceClaimId = typeof proposal.payload.source_claim_id === "string" ? proposal.payload.source_claim_id : null;
  const targetClaimId = typeof proposal.payload.target_claim_id === "string" ? proposal.payload.target_claim_id : null;
  const connectionType =
    typeof proposal.payload.connection_type === "string" ? proposal.payload.connection_type : "unknown";

  const handleReviewSuccess = (decision: Extract<ReviewDecision, "approve" | "reject">) => {
    setOpenDecision(null);
    setIsClosing(true);
    pushToast({
      kind: "success",
      message: decision === "approve" ? "Suggestion approved." : "Suggestion rejected.",
    });

    window.setTimeout(() => {
      setIsHidden(true);
      router.refresh();
    }, 320);
  };

  if (isHidden) {
    return null;
  }

  return (
    <article className={`proposal-card card${isClosing ? " proposal-card-fading" : ""}`}>
      <div className="badge-row">
        <span className={`status-pill status-${proposal.status}`}>{proposal.status}</span>
        <span className="type-pill">{proposal.proposal_type}</span>
        <span className="chip">{connectionType}</span>
      </div>

      <div className="card-stack" style={{ gap: 10 }}>
        <div className="mini-card">
          <p className="eyebrow" style={{ marginBottom: 6 }}>
            Source claim
          </p>
          {sourceClaimId ? (
            <Link href={`/claims/${sourceClaimId}`}>{previewStatement(sourceClaimLabel)}</Link>
          ) : (
            <span>{previewStatement(sourceClaimLabel)}</span>
          )}
        </div>

        <div className="mini-card">
          <p className="eyebrow" style={{ marginBottom: 6 }}>
            Target claim
          </p>
          {targetClaimId ? (
            <Link href={`/claims/${targetClaimId}`}>{previewStatement(targetClaimLabel)}</Link>
          ) : (
            <span>{previewStatement(targetClaimLabel)}</span>
          )}
        </div>
      </div>

      <div>
        <h3 className="card-title">{proposal.rationale}</h3>
        <p className="supporting-text">
          Proposed by {proposal.proposed_by.name} · {new Date(proposal.created_at).toLocaleString()}
        </p>
      </div>

      <div className="confidence-bar">
        <span style={{ width: `${confidence}%` }} />
      </div>
      <p className="small">Confidence {confidence}%</p>

      {proposal.status === "pending" ? (
        <div className="actions-row">
          <button className="button" disabled={isClosing} onClick={() => setOpenDecision("approve")} type="button">
            Approve
          </button>
          <button className="danger-button" disabled={isClosing} onClick={() => setOpenDecision("reject")} type="button">
            Reject
          </button>
        </div>
      ) : null}

      {openDecision ? (
        <ReviewDialog
          decision={openDecision}
          onClose={() => setOpenDecision(null)}
          onSuccess={handleReviewSuccess}
          proposal={proposal}
        />
      ) : null}
    </article>
  );
}
