"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", title: "Dashboard", caption: "Live system pulse" },
  { href: "/claims", title: "Claims", caption: "Filter and inspect" },
  { href: "/concepts", title: "Concepts", caption: "Cross-field vocabulary" },
  { href: "/contexts", title: "Contexts", caption: "Theory scaffolds" },
  { href: "/graph", title: "Graph", caption: "Visual relations" },
  { href: "/review", title: "Review", caption: "Pending proposals" },
  { href: "/search", title: "Search", caption: "Traverse everything" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="sidebar panel">
      <p className="eyebrow">CollectiveScience</p>
      <h2 className="hero-title" style={{ fontSize: "2rem" }}>
        Claim Atlas
      </h2>
      <p className="hero-subtitle">
        A research cockpit for browsing claims, reviewing AI links, and tracing theory across
        domains.
      </p>

      <nav className="sidebar-nav" aria-label="Primary">
        {links.map((link) => {
          const active = pathname === link.href || pathname.startsWith(`${link.href}/`);
          return (
            <Link key={link.href} className={`nav-link${active ? " active" : ""}`} href={link.href}>
              <span>{link.title}</span>
              <span className="nav-caption">{link.caption}</span>
            </Link>
          );
        })}
      </nav>

      <div className="card" style={{ marginTop: 22 }}>
        <p className="eyebrow">Autonomy</p>
        <p className="section-title">Level 0</p>
        <p className="supporting-text">
          AI can suggest links and trust changes, but approvals remain reviewer-driven.
        </p>
      </div>
    </aside>
  );
}
