"use client";

import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";
import type { ChangeEvent } from "react";

import { useToast } from "@/components/Toast";
import { createClaimAction } from "@/lib/actions";
import type { ClaimType, ConceptRead, ContextRead } from "@/lib/types";

function readSelectedValues(event: ChangeEvent<HTMLSelectElement>) {
  return Array.from(event.target.selectedOptions, (option) => option.value);
}

export function CreateClaimDialog({
  contexts,
  concepts,
  triggerLabel = "新規Claim作成",
}: {
  contexts: ContextRead[];
  concepts: ConceptRead[];
  triggerLabel?: string;
}) {
  const router = useRouter();
  const { pushToast } = useToast();
  const [open, setOpen] = useState(false);
  const [statement, setStatement] = useState("");
  const [claimType, setClaimType] = useState<ClaimType>("definition");
  const [contextIds, setContextIds] = useState<string[]>([]);
  const [conceptIds, setConceptIds] = useState<string[]>([]);
  const [isPending, startTransition] = useTransition();

  const resetForm = () => {
    setStatement("");
    setClaimType("definition");
    setContextIds([]);
    setConceptIds([]);
  };

  const closeDialog = () => {
    if (isPending) return;
    setOpen(false);
  };

  const submit = () => {
    if (!statement.trim()) {
      pushToast({ kind: "error", message: "Claim statement is required." });
      return;
    }

    startTransition(async () => {
      try {
        await createClaimAction({
          statement: statement.trim(),
          claim_type: claimType,
          trust_status: "tentative",
          context_ids: contextIds,
          concept_ids: conceptIds,
          evidence_ids: [],
          cir_id: null,
        });
        resetForm();
        setOpen(false);
        pushToast({ kind: "success", message: "Claim created successfully." });
        router.refresh();
      } catch (error) {
        pushToast({
          kind: "error",
          message: error instanceof Error ? error.message : "Failed to create claim.",
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
              <p className="eyebrow">Create Claim</p>
              <h3 className="card-title">Add a new claim</h3>
              <p className="dialog-helper">Create a statement and connect it to the right contexts and concepts.</p>
            </div>

            <label>
              Statement
              <textarea
                onChange={(event) => setStatement(event.target.value)}
                placeholder="Describe the claim you want to register"
                rows={5}
                value={statement}
              />
            </label>

            <label>
              Claim type
              <select onChange={(event) => setClaimType(event.target.value as ClaimType)} value={claimType}>
                <option value="definition">definition</option>
                <option value="theorem">theorem</option>
                <option value="empirical">empirical</option>
                <option value="conjecture">conjecture</option>
                <option value="meta">meta</option>
              </select>
            </label>

            <label>
              Contexts
              <select multiple onChange={(event) => setContextIds(readSelectedValues(event))} value={contextIds}>
                {contexts.map((context) => (
                  <option key={context.id} value={context.id}>
                    {context.name} ({context.field})
                  </option>
                ))}
              </select>
            </label>

            <label>
              Concepts
              <select multiple onChange={(event) => setConceptIds(readSelectedValues(event))} value={conceptIds}>
                {concepts.map((concept) => (
                  <option key={concept.id} value={concept.id}>
                    {concept.label} ({concept.field})
                  </option>
                ))}
              </select>
            </label>

            <div className="actions-row">
              <button className="ghost-button" onClick={closeDialog} type="button">
                Cancel
              </button>
              <button className="button" disabled={isPending} onClick={submit} type="button">
                {isPending ? "Creating..." : "Create claim"}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}
