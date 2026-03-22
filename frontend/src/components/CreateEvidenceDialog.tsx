"use client";

import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";
import type { ChangeEvent } from "react";

import { useToast } from "@/components/Toast";
import { createEvidence } from "@/lib/api";
import type { ClaimRead, EvidenceRelationship, EvidenceType, Reliability } from "@/lib/types";

function readSelectedValues(event: ChangeEvent<HTMLSelectElement>) {
  return Array.from(event.target.selectedOptions, (option) => option.value);
}

export function CreateEvidenceDialog({
  claims,
  initialClaimId,
  triggerLabel = "Evidence追加",
}: {
  claims: ClaimRead[];
  initialClaimId?: string;
  triggerLabel?: string;
}) {
  const router = useRouter();
  const { pushToast } = useToast();
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [source, setSource] = useState("");
  const [excerpt, setExcerpt] = useState("");
  const [evidenceType, setEvidenceType] = useState<EvidenceType>("paper");
  const [reliability, setReliability] = useState<Reliability>("medium");
  const [relationship, setRelationship] = useState<EvidenceRelationship>("supports");
  const [claimIds, setClaimIds] = useState<string[]>(initialClaimId ? [initialClaimId] : []);
  const [isPending, startTransition] = useTransition();

  const resetForm = () => {
    setTitle("");
    setSource("");
    setExcerpt("");
    setEvidenceType("paper");
    setReliability("medium");
    setRelationship("supports");
    setClaimIds(initialClaimId ? [initialClaimId] : []);
  };

  const submit = () => {
    if (!title.trim() || !source.trim()) {
      pushToast({ kind: "error", message: "Title and source are required." });
      return;
    }

    startTransition(async () => {
      try {
        await createEvidence({
          title: title.trim(),
          source: source.trim(),
          excerpt: excerpt.trim() || null,
          evidence_type: evidenceType,
          reliability,
          claim_links: claimIds.map((claimId) => ({
            claim_id: claimId,
            relationship,
          })),
        });
        resetForm();
        setOpen(false);
        pushToast({ kind: "success", message: "Evidence created successfully." });
        router.refresh();
      } catch (error) {
        pushToast({
          kind: "error",
          message: error instanceof Error ? error.message : "Failed to create evidence.",
        });
      }
    });
  };

  return (
    <>
      <button className="button" onClick={() => setOpen(true)} type="button">
        {triggerLabel}
      </button>

      {open ? (
        <div className="dialog-overlay" role="dialog" aria-modal="true">
          <div className="dialog-card card-stack dialog-form">
            <div>
              <p className="eyebrow">Create Evidence</p>
              <h3 className="card-title">Attach supporting material</h3>
              <p className="dialog-helper">Link evidence to one or more claims and describe its reliability.</p>
            </div>

            <label>
              Title
              <input onChange={(event) => setTitle(event.target.value)} placeholder="Foundations of Statistical Mechanics" value={title} />
            </label>

            <label>
              Evidence type
              <select onChange={(event) => setEvidenceType(event.target.value as EvidenceType)} value={evidenceType}>
                <option value="textbook">textbook</option>
                <option value="paper">paper</option>
                <option value="experiment">experiment</option>
                <option value="proof">proof</option>
                <option value="expert_opinion">expert_opinion</option>
              </select>
            </label>

            <label>
              Source
              <input onChange={(event) => setSource(event.target.value)} placeholder="Book, DOI, URL, or lab notebook" value={source} />
            </label>

            <label>
              Excerpt
              <textarea
                onChange={(event) => setExcerpt(event.target.value)}
                placeholder="Optional excerpt or quotation"
                rows={4}
                value={excerpt}
              />
            </label>

            <label>
              Reliability
              <select onChange={(event) => setReliability(event.target.value as Reliability)} value={reliability}>
                <option value="high">high</option>
                <option value="medium">medium</option>
                <option value="low">low</option>
                <option value="unverified">unverified</option>
              </select>
            </label>

            <label>
              Claim relationship
              <select onChange={(event) => setRelationship(event.target.value as EvidenceRelationship)} value={relationship}>
                <option value="supports">supports</option>
                <option value="contradicts">contradicts</option>
                <option value="partially_supports">partially_supports</option>
              </select>
            </label>

            <label>
              Linked claims
              <select multiple onChange={(event) => setClaimIds(readSelectedValues(event))} value={claimIds}>
                {claims.map((claim) => (
                  <option key={claim.id} value={claim.id}>
                    {claim.statement}
                  </option>
                ))}
              </select>
            </label>

            <div className="actions-row">
              <button className="ghost-button" onClick={() => !isPending && setOpen(false)} type="button">
                Cancel
              </button>
              <button className="button" disabled={isPending} onClick={submit} type="button">
                {isPending ? "Creating..." : "Create evidence"}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}
