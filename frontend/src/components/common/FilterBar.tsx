import type { ClaimListFilters } from "@/lib/api";
import type { ContextRead, TrustStatus } from "@/lib/types";

interface FilterBarProps {
  filters: ClaimListFilters;
  contexts: ContextRead[];
  fields: string[];
}

export function FilterBar({ filters, contexts, fields }: FilterBarProps) {
  return (
    <form className="filter-bar" method="get">
      <label>
        Keyword
        <input defaultValue={filters.query ?? ""} name="query" placeholder="Search statements or concepts" />
      </label>

      <label>
        Context
        <select defaultValue={filters.contextId ?? ""} name="contextId">
          <option value="">All contexts</option>
          {contexts.map((context) => (
            <option key={context.id} value={context.id}>
              {context.name}
            </option>
          ))}
        </select>
      </label>

      <label>
        Field
        <select defaultValue={filters.field ?? ""} name="field">
          <option value="">All fields</option>
          {fields.map((field) => (
            <option key={field} value={field}>
              {field}
            </option>
          ))}
        </select>
      </label>

      <label>
        Trust
        <select defaultValue={filters.trustStatus ?? ""} name="trustStatus">
          <option value="">All states</option>
          {(["established", "tentative", "disputed", "ai_suggested"] as TrustStatus[]).map(
            (status) => (
              <option key={status} value={status}>
                {status.replace("_", " ")}
              </option>
            ),
          )}
        </select>
      </label>

      <div className="actions-row">
        <button className="button" type="submit">
          Apply filters
        </button>
      </div>
    </form>
  );
}
