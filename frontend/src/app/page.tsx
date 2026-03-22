import Link from "next/link";

import { Header } from "@/components/layout/Header";
import { StatsCard } from "@/components/layout/StatsCard";
import { getDashboardData } from "@/lib/api";

export default async function DashboardPage() {
  const dashboard = await getDashboardData();

  return (
    <>
      <Header
        title="Research dashboard"
        subtitle="Monitor claim growth, pending reviews, and the newest cross-field movements."
        action={
          <Link className="button" href="/review">
            Open review queue
          </Link>
        }
      />

      <section className="hero panel">
        <p className="eyebrow">Overview</p>
        <h2 className="hero-title">A living atlas of entropy, uncertainty, and their neighboring ideas.</h2>
        <p className="hero-subtitle" style={{ maxWidth: 760 }}>
          This workspace keeps claims, evidence, contexts, and AI-generated bridges in one place,
          so reviewers can move from system pulse to individual proposal with minimal friction.
        </p>
      </section>

      <section className="stats-grid">
        <StatsCard href="/claims" label="Claims" note="Core statements under review" value={dashboard.totals.claims} />
        <StatsCard href="/concepts" label="Concepts" note="Vocabulary spanning domains" value={dashboard.totals.concepts} />
        <StatsCard href="/contexts" label="Contexts" note="Theory frames and assumptions" value={dashboard.totals.contexts} />
        <StatsCard label="Evidence" note="Sources grounding the graph" value={dashboard.totals.evidence} />
        <StatsCard href="/review" label="Pending proposals" note="Needs reviewer attention" value={dashboard.totals.pendingProposals} />
      </section>

      <section className="cards-grid">
        <article className="card">
          <p className="eyebrow">Recent activity</p>
          <div className="timeline" style={{ marginTop: 16 }}>
            {dashboard.recentActivity.map((event) => (
              <article className="timeline-item" key={event.id}>
                <strong>{event.title}</strong>
                <p className="supporting-text">{event.summary}</p>
                <p className="small">
                  {event.actorName} · {new Date(event.timestamp).toLocaleString()}
                </p>
              </article>
            ))}
          </div>
        </article>

        <article className="card">
          <p className="eyebrow">Reviewer shortcuts</p>
          <div className="card-stack" style={{ marginTop: 16 }}>
            <Link className="ghost-button" href="/claims?trustStatus=ai_suggested">
              Inspect AI-suggested claims
            </Link>
            <Link className="ghost-button" href="/graph?field=Information%20Theory">
              Focus graph on information theory
            </Link>
            <Link className="ghost-button" href="/search?q=entropy">
              Search for entropy-linked entities
            </Link>
          </div>
        </article>
      </section>
    </>
  );
}
