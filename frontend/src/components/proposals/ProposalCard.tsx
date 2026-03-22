"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { useToast } from "@/components/Toast";
import { ReviewDialog } from "@/components/proposals/ReviewDialog";
import type { ProposalRead, ReviewDecision } from "@/lib/types";

export function ProposalCard({
  proposal,
  onReviewed,
}: {
  proposal: ProposalRead;
  onReviewed?: () => void;
}) {
  const router = useRouter();
  const { pushToast } = useToast();
  const [openDecision, setOpenDecision] = useState<"approve" | "reject" | null>(null);
  const [isClosing, setIsClosing] = useState(false);
  const [isHidden, setIsHidden] = useState(false);

  const confidence = Number(proposal.payload.confidence ?? 0);

  const handleReviewSuccess = (decision: Extract<ReviewDecision, "approve" | "reject">) => {
    setOpenDecision(null);
    setIsClosing(true);
    pushToast({
      kind: "success",
      message: decision === "approve" ? "Proposal approved." : "Proposal rejected.",
    });

    window.setTimeout(() => {
      setIsHidden(true);
      if (onReviewed) {
        onReviewed();
        return;
      }
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
        <span className="chip">By {proposal.proposed_by.name}</span>
      </div>

      <div>
        <h3 className="card-title">{proposal.rationale}</h3>
        <p className="supporting-text">
          Target: {proposal.target_entity_type} · {proposal.target_entity_id ?? "new entity"}
        </p>
      </div>

      <div className="confidence-bar">
        <span style={{ width: `${Math.round(confidence * 100)}%` }} />
      </div>
      <p className="small">Confidence {Math.round(confidence * 100)}%</p>

      <div className="mini-card">
        <strong>Payload</strong>
        <pre style={{ whiteSpace: "pre-wrap", margin: "10px 0 0" }}>
          {JSON.stringify(proposal.payload, null, 2)}
        </pre>
      </div>

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
