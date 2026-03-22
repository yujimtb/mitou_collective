"use client";

import { useState } from "react";

import { ReviewDialog } from "@/components/proposals/ReviewDialog";
import type { ProposalRead } from "@/lib/types";

export function ProposalCard({ proposal }: { proposal: ProposalRead }) {
  const [openDecision, setOpenDecision] = useState<"approve" | "reject" | null>(null);

  const confidence = Number(proposal.payload.confidence ?? 0);

  return (
    <article className="proposal-card card">
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
          <button className="button" onClick={() => setOpenDecision("approve")} type="button">
            Approve
          </button>
          <button className="danger-button" onClick={() => setOpenDecision("reject")} type="button">
            Reject
          </button>
        </div>
      ) : null}

      {openDecision ? (
        <ReviewDialog
          decision={openDecision}
          onClose={() => setOpenDecision(null)}
          proposal={proposal}
        />
      ) : null}
    </article>
  );
}
