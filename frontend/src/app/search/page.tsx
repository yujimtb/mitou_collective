import Link from "next/link";

import { SearchBar } from "@/components/common/SearchBar";
import { Header } from "@/components/layout/Header";
import { getEntityHref, searchKnowledge } from "@/lib/api";

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const query = typeof params.q === "string" ? params.q : "entropy";
  const type = typeof params.type === "string" ? params.type : "all";
  const groups = await searchKnowledge(query, type);
  const hydratedGroups = await Promise.all(
    groups.map(async (group) => ({
      ...group,
      items: await Promise.all(
        group.items.map(async (item) => ({
          ...item,
          href: await getEntityHref(item),
        })),
      ),
    })),
  );

  return (
    <>
      <Header
        title="Cross-entity search"
        subtitle="Traverse claims, concepts, terms, contexts, and evidence from one query surface."
      />

      <SearchBar entityType={type} query={query} />

      <section className="search-grid">
        {hydratedGroups.map((group) => (
          <article className="card" key={group.entityType}>
            <p className="eyebrow">{group.entityType}</p>
            <div className="card-stack" style={{ marginTop: 14 }}>
              {group.items.map((item) => (
                <Link className="search-card" href={item.href} key={item.entity_id}>
                  <strong>{item.title}</strong>
                  <p className="supporting-text">{item.snippet}</p>
                  <p className="small">Score {item.score.toFixed(2)}</p>
                </Link>
              ))}
            </div>
          </article>
        ))}
      </section>
    </>
  );
}
