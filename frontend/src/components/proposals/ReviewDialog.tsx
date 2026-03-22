"use client";

import { useState, useTransition } from "react";

import { useToast } from "@/components/Toast";
import { submitReview } from "@/lib/api";
import type { ProposalRead, ReviewDecision } from "@/lib/types";

export function ReviewDialog({
  proposal,
  decision,
  onClose,
  onSuccess,
}: {
  proposal: ProposalRead;
  decision: Extract<ReviewDecision, "approve" | "reject">;
  onClose: () => void;
  onSuccess: (decision: Extract<ReviewDecision, "approve" | "reject">) => void;
}) {
  const { pushToast } = useToast();
  const [comment, setComment] = useState("");
  const [confidence, setConfidence] = useState(String(Math.round(Number(proposal.payload.confidence ?? 0.6) * 100)));
  const [isPending, startTransition] = useTransition();

  const submit = () => {
    startTransition(async () => {
      try {
        await submitReview({
          proposalId: proposal.id,
          decision,
          comment,
          confidence: Math.max(0, Math.min(1, Number(confidence) / 100)),
        });
        onSuccess(decision);
      } catch (submissionError) {
        pushToast({
          kind: "error",
          message: submissionError instanceof Error ? submissionError.message : "Review failed.",
        });
      }
    });
  };

  return (
    <div className="dialog-overlay" role="dialog" aria-modal="true">
      <div className="dialog-card card-stack">
        <div>
          <p className="eyebrow">Review Proposal</p>
          <h3 className="card-title">{decision === "approve" ? "Approve proposal" : "Reject proposal"}</h3>
          <p className="supporting-text">{proposal.rationale}</p>
        </div>

        <label>
          Comment{decision === "reject" ? " (required)" : ""}
          <textarea
            onChange={(event) => setComment(event.target.value)}
            placeholder={decision === "approve" ? "Why this link is acceptable" : "Why this proposal should be rejected"}
            rows={5}
            value={comment}
          />
        </label>

        <label>
          Confidence (%)
          <input
            max={100}
            min={0}
            onChange={(event) => setConfidence(event.target.value)}
            type="number"
            value={confidence}
          />
        </label>

        <div className="actions-row">
          <button className="ghost-button" onClick={onClose} type="button">
            Cancel
          </button>
          <button className={decision === "approve" ? "button" : "danger-button"} disabled={isPending} onClick={submit} type="button">
            {isPending ? "Submitting..." : decision === "approve" ? "Submit approval" : "Submit rejection"}
          </button>
        </div>
      </div>
    </div>
  );
}
