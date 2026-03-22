"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useTransition } from "react";

import { useToast } from "@/components/Toast";
import { CreateEvidenceDialog } from "@/components/CreateEvidenceDialog";
import { CIRDisplay } from "@/components/cir/CIRDisplay";
import { TrustBadge } from "@/components/common/TrustBadge";
import { EvidenceCard } from "@/components/evidence/EvidenceCard";
import { ProposalCard } from "@/components/proposals/ProposalCard";
import { suggestConnectionsAction } from "@/lib/actions";
import type { ClaimDetailData } from "@/lib/api";
import type { ClaimRead } from "@/lib/types";

export function ClaimDetail({
  data,
  availableClaims,
}: {
  data: ClaimDetailData;
  availableClaims: ClaimRead[];
}) {
  const router = useRouter();
  const { pushToast } = useToast();
  const [isGenerating, startTransition] = useTransition();
  const { claim, concepts, contexts, evidence, pendingProposals, history } = data;

  const handleGenerateSuggestions = () => {
    startTransition(async () => {
      try {
        await suggestConnectionsAction("claim", claim.id, contexts[0]?.field);
        pushToast({ kind: "success", message: "AI connection suggestions generated." });
        router.refresh();
      } catch (error) {
        pushToast({
          kind: "error",
          message: error instanceof Error ? error.message : "Failed to generate AI suggestions.",
        });
      }
    });
  };

  return (
    <div className="detail-grid">
      <section className="section-stack">
        <article className="card">
          <div className="badge-row">
            <span className="type-pill">{claim.claim_type}</span>
            <TrustBadge status={claim.trust_status} />
            <span className="chip">Version {claim.version}</span>
          </div>
          <h2 className="hero-title" style={{ fontSize: "2rem", marginTop: 18 }}>
            {claim.statement}
          </h2>

          <div className="section-stack" style={{ marginTop: 20 }}>
            <div>
              <p className="eyebrow">Related Concepts</p>
              <div className="chip-row">
                {concepts.map((concept) => (
                  <Link className="chip" href={`/concepts/${concept.id}`} key={concept.id}>
                    {concept.label} · {concept.field}
                  </Link>
                ))}
              </div>
            </div>

            <div>
              <p className="eyebrow">Contexts</p>
              <div className="chip-row">
                {contexts.map((context) => (
                  <Link className="chip" href={`/contexts/${context.id}`} key={context.id}>
                    {context.name}
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </article>

        {claim.cir ? <CIRDisplay cir={claim.cir} /> : null}

        <section className="card-stack">
          <div className="card">
            <div className="actions-row" style={{ justifyContent: "space-between" }}>
              <p className="eyebrow" style={{ marginBottom: 0 }}>
                Evidence
              </p>
              <CreateEvidenceDialog claims={availableClaims} initialClaimId={claim.id} />
            </div>
            {evidence.length ? (
              <div className="card-stack" style={{ marginTop: 14 }}>
                {evidence.map((item) => (
                  <EvidenceCard evidence={item} key={item.id} />
                ))}
              </div>
            ) : (
              <div className="empty-state" style={{ marginTop: 14 }}>
                No evidence has been linked to this claim yet.
              </div>
            )}
          </div>
        </section>
      </section>

      <section className="section-stack">
        <div className="card">
          <div className="actions-row" style={{ justifyContent: "space-between" }}>
            <p className="eyebrow" style={{ marginBottom: 0 }}>
              AI Suggestions
            </p>
            <button className="button" disabled={isGenerating} onClick={handleGenerateSuggestions} type="button">
              {isGenerating ? "Generating..." : "AI接続候補を生成"}
            </button>
          </div>
          {pendingProposals.length ? (
            <div className="proposal-stack" style={{ marginTop: 14 }}>
              {pendingProposals.map((proposal) => (
                <ProposalCard key={proposal.id} onReviewed={() => router.refresh()} proposal={proposal} />
              ))}
            </div>
          ) : (
            <div className="empty-state" style={{ marginTop: 14 }}>
              No pending AI connection proposals for this claim.
            </div>
          )}
        </div>

        <div className="card">
          <p className="eyebrow">History</p>
          <div className="timeline" style={{ marginTop: 12 }}>
            {history.length ? (
              history.map((event) => (
                <article className="timeline-item" key={event.id}>
                  <div className="actions-row" style={{ justifyContent: "space-between", alignItems: "flex-start" }}>
                    <div>
                      <strong>{event.title}</strong>
                      <p className="supporting-text">{event.summary}</p>
                    </div>
                    <Link className="ghost-button" href={event.href}>
                      View claim
                    </Link>
                  </div>
                  <p className="small">
                    {event.actorName} · {new Date(event.timestamp).toLocaleString()}
                  </p>
                </article>
              ))
            ) : (
              <div className="empty-state">No history events have been recorded for this claim yet.</div>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
