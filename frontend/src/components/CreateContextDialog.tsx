"use client";

import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";

import { useToast } from "@/components/Toast";
import { createContext } from "@/lib/api";
import type { ContextRead } from "@/lib/types";

export function CreateContextDialog({
  contexts,
  fields,
  triggerLabel = "新規Context作成",
}: {
  contexts: ContextRead[];
  fields: string[];
  triggerLabel?: string;
}) {
  const router = useRouter();
  const { pushToast } = useToast();
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [field, setField] = useState(fields[0] ?? "");
  const [assumptions, setAssumptions] = useState("");
  const [parentContextId, setParentContextId] = useState("");
  const [isPending, startTransition] = useTransition();

  const resetForm = () => {
    setName("");
    setDescription("");
    setField(fields[0] ?? "");
    setAssumptions("");
    setParentContextId("");
  };

  const submit = () => {
    if (!name.trim() || !description.trim() || !field.trim()) {
      pushToast({ kind: "error", message: "Name, description, and field are required." });
      return;
    }

    startTransition(async () => {
      try {
        await createContext({
          name: name.trim(),
          description: description.trim(),
          field: field.trim(),
          assumptions: assumptions
            .split(",")
            .map((item) => item.trim())
            .filter(Boolean),
          parent_context_id: parentContextId || null,
        });
        resetForm();
        setOpen(false);
        pushToast({ kind: "success", message: "Context created successfully." });
        router.refresh();
      } catch (error) {
        pushToast({
          kind: "error",
          message: error instanceof Error ? error.message : "Failed to create context.",
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
              <p className="eyebrow">Create Context</p>
              <h3 className="card-title">Add a theoretical context</h3>
              <p className="dialog-helper">Capture the frame, assumptions, and optional parent context.</p>
            </div>

            <label>
              Name
              <input onChange={(event) => setName(event.target.value)} placeholder="Thermodynamic closed systems" value={name} />
            </label>

            <label>
              Description
              <textarea
                onChange={(event) => setDescription(event.target.value)}
                placeholder="Summarize the context and when it applies"
                rows={4}
                value={description}
              />
            </label>

            <label>
              Field
              <input list="context-field-options" onChange={(event) => setField(event.target.value)} value={field} />
              <datalist id="context-field-options">
                {fields.map((fieldOption) => (
                  <option key={fieldOption} value={fieldOption} />
                ))}
              </datalist>
            </label>

            <label>
              Assumptions
              <input
                onChange={(event) => setAssumptions(event.target.value)}
                placeholder="Comma-separated assumptions"
                value={assumptions}
              />
            </label>

            <label>
              Parent context
              <select onChange={(event) => setParentContextId(event.target.value)} value={parentContextId}>
                <option value="">No parent</option>
                {contexts.map((context) => (
                  <option key={context.id} value={context.id}>
                    {context.name}
                  </option>
                ))}
              </select>
            </label>

            <div className="actions-row">
              <button className="ghost-button" onClick={() => !isPending && setOpen(false)} type="button">
                Cancel
              </button>
              <button className="button" disabled={isPending} onClick={submit} type="button">
                {isPending ? "Creating..." : "Create context"}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}
