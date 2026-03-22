export const dynamic = "force-dynamic";

import Link from "next/link";

import { CreateTermDialog } from "@/components/CreateTermDialog";
import { Header } from "@/components/layout/Header";
import { listConcepts, listTerms } from "@/lib/api";

function readParam(value: string | string[] | undefined) {
  return typeof value === "string" ? value : "";
}

export default async function TermsPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const search = readParam(params.search).trim().toLowerCase();
  const language = readParam(params.language);
  const [terms, concepts] = await Promise.all([listTerms(), listConcepts()]);

  const filteredTerms = terms.filter((term) => {
    const matchesSearch = !search || term.surface_form.toLowerCase().includes(search);
    const matchesLanguage = !language || term.language === language;
    return matchesSearch && matchesLanguage;
  });

  const languages = Array.from(new Set([...terms.map((term) => term.language), "en", "ja"])).sort();

  return (
    <>
      <Header
        title="Term registry"
        subtitle="Search the surface forms that anchor concepts across languages and research fields."
      />

      <div className="actions-row" style={{ marginBottom: 16, justifyContent: "space-between" }}>
        <form className="filter-bar" method="get" style={{ flex: 1 }}>
          <label>
            Search
            <input defaultValue={readParam(params.search)} name="search" placeholder="entropy, negentropy, ..." />
          </label>

          <label>
            Language
            <select defaultValue={language} name="language">
              <option value="">All languages</option>
              {languages.map((languageOption) => (
                <option key={languageOption} value={languageOption}>
                  {languageOption}
                </option>
              ))}
            </select>
          </label>

          <button className="button" type="submit">
            Apply filters
          </button>
        </form>

        <CreateTermDialog concepts={concepts} languages={languages} />
      </div>

      <article className="table-card">
        <table className="table">
          <thead>
            <tr>
              <th>Surface form</th>
              <th>Language</th>
              <th>Field hint</th>
              <th>Related Concepts</th>
            </tr>
          </thead>
          <tbody>
            {filteredTerms.map((term) => (
              <tr key={term.id}>
                <td>
                  <Link href={`/terms/${term.id}`}>{term.surface_form}</Link>
                </td>
                <td>{term.language}</td>
                <td>{term.field_hint ?? "—"}</td>
                <td>{term.concept_ids.length}</td>
              </tr>
            ))}
          </tbody>
        </table>

        {filteredTerms.length === 0 ? (
          <div className="empty-state" style={{ marginTop: 16 }}>
            No terms match the current filters.
          </div>
        ) : null}
      </article>
    </>
  );
}
