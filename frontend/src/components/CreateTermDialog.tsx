"use client";

import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";
import type { ChangeEvent } from "react";

import { useToast } from "@/components/Toast";
import { createTerm } from "@/lib/api";
import type { ConceptRead } from "@/lib/types";

function readSelectedValues(event: ChangeEvent<HTMLSelectElement>) {
  return Array.from(event.target.selectedOptions, (option) => option.value);
}

export function CreateTermDialog({
  concepts,
  languages,
  triggerLabel = "新規Term作成",
}: {
  concepts: ConceptRead[];
  languages: string[];
  triggerLabel?: string;
}) {
  const router = useRouter();
  const { pushToast } = useToast();
  const [open, setOpen] = useState(false);
  const [surfaceForm, setSurfaceForm] = useState("");
  const [language, setLanguage] = useState(languages[0] ?? "en");
  const [fieldHint, setFieldHint] = useState("");
  const [conceptIds, setConceptIds] = useState<string[]>([]);
  const [isPending, startTransition] = useTransition();

  const resetForm = () => {
    setSurfaceForm("");
    setLanguage(languages[0] ?? "en");
    setFieldHint("");
    setConceptIds([]);
  };

  const submit = () => {
    if (!surfaceForm.trim() || !language.trim()) {
      pushToast({ kind: "error", message: "Surface form and language are required." });
      return;
    }

    startTransition(async () => {
      try {
        await createTerm({
          surface_form: surfaceForm.trim(),
          language: language.trim(),
          field_hint: fieldHint.trim() || null,
          concept_ids: conceptIds,
        });
        resetForm();
        setOpen(false);
        pushToast({ kind: "success", message: "Term created successfully." });
        router.refresh();
      } catch (error) {
        pushToast({
          kind: "error",
          message: error instanceof Error ? error.message : "Failed to create term.",
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
              <p className="eyebrow">Create Term</p>
              <h3 className="card-title">Add a term to the shared vocabulary</h3>
              <p className="dialog-helper">
                Capture a surface form, choose its language, and associate any related concepts.
              </p>
            </div>

            <label>
              Surface form
              <input
                onChange={(event) => setSurfaceForm(event.target.value)}
                placeholder="entropy"
                value={surfaceForm}
              />
            </label>

            <label>
              Language
              <select onChange={(event) => setLanguage(event.target.value)} value={language}>
                {languages.map((languageOption) => (
                  <option key={languageOption} value={languageOption}>
                    {languageOption}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Field hint
              <input
                onChange={(event) => setFieldHint(event.target.value)}
                placeholder="Information Theory"
                value={fieldHint}
              />
            </label>

            <label>
              Related concepts
              <select multiple onChange={(event) => setConceptIds(readSelectedValues(event))} value={conceptIds}>
                {concepts.map((concept) => (
                  <option key={concept.id} value={concept.id}>
                    {concept.label} ({concept.field})
                  </option>
                ))}
              </select>
            </label>

            <div className="actions-row">
              <button className="ghost-button" onClick={() => !isPending && setOpen(false)} type="button">
                Cancel
              </button>
              <button className="button" disabled={isPending} onClick={submit} type="button">
                {isPending ? "Creating..." : "Create term"}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}
