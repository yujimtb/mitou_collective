"use client";

import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";
import type { ChangeEvent } from "react";

import { useToast } from "@/components/Toast";
import { createConcept } from "@/lib/api";
import type { TermRead } from "@/lib/types";

function readSelectedValues(event: ChangeEvent<HTMLSelectElement>) {
  return Array.from(event.target.selectedOptions, (option) => option.value);
}

export function CreateConceptDialog({
  terms,
  fields,
  triggerLabel = "新規Concept作成",
}: {
  terms: TermRead[];
  fields: string[];
  triggerLabel?: string;
}) {
  const router = useRouter();
  const { pushToast } = useToast();
  const [open, setOpen] = useState(false);
  const [label, setLabel] = useState("");
  const [description, setDescription] = useState("");
  const [field, setField] = useState(fields[0] ?? "");
  const [termIds, setTermIds] = useState<string[]>([]);
  const [isPending, startTransition] = useTransition();

  const resetForm = () => {
    setLabel("");
    setDescription("");
    setField(fields[0] ?? "");
    setTermIds([]);
  };

  const submit = () => {
    if (!label.trim() || !description.trim() || !field.trim()) {
      pushToast({ kind: "error", message: "Label, description, and field are required." });
      return;
    }

    startTransition(async () => {
      try {
        await createConcept({
          label: label.trim(),
          description: description.trim(),
          field: field.trim(),
          term_ids: termIds,
          referent_id: null,
        });
        resetForm();
        setOpen(false);
        pushToast({ kind: "success", message: "Concept created successfully." });
        router.refresh();
      } catch (error) {
        pushToast({
          kind: "error",
          message: error instanceof Error ? error.message : "Failed to create concept.",
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
              <p className="eyebrow">Create Concept</p>
              <h3 className="card-title">Add a cross-field concept</h3>
              <p className="dialog-helper">Describe the concept and connect any existing terms that express it.</p>
            </div>

            <label>
              Label
              <input onChange={(event) => setLabel(event.target.value)} placeholder="Entropy" value={label} />
            </label>

            <label>
              Description
              <textarea
                onChange={(event) => setDescription(event.target.value)}
                placeholder="Explain how this concept is used across fields"
                rows={4}
                value={description}
              />
            </label>

            <label>
              Field
              <input list="concept-field-options" onChange={(event) => setField(event.target.value)} value={field} />
              <datalist id="concept-field-options">
                {fields.map((fieldOption) => (
                  <option key={fieldOption} value={fieldOption} />
                ))}
              </datalist>
            </label>

            <label>
              Terms
              <select multiple onChange={(event) => setTermIds(readSelectedValues(event))} value={termIds}>
                {terms.map((term) => (
                  <option key={term.id} value={term.id}>
                    {term.surface_form} ({term.language})
                  </option>
                ))}
              </select>
            </label>

            <div className="actions-row">
              <button className="ghost-button" onClick={() => !isPending && setOpen(false)} type="button">
                Cancel
              </button>
              <button className="button" disabled={isPending} onClick={submit} type="button">
                {isPending ? "Creating..." : "Create concept"}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}
