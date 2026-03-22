import type { Metadata } from "next";
import type { ReactNode } from "react";

import "@/app/globals.css";
import { Sidebar } from "@/components/layout/Sidebar";

export const metadata: Metadata = {
  title: "CollectiveScience",
  description: "Claim-centric knowledge graph interface for cross-domain research review.",
};

function MobileNav() {
  const links = [
    { href: "/", label: "Home" },
    { href: "/claims", label: "Claims" },
    { href: "/review", label: "Review" },
    { href: "/graph", label: "Graph" },
    { href: "/search", label: "Search" },
    { href: "/contexts", label: "Contexts" },
  ];

  return (
    <nav className="mobile-nav" aria-label="Mobile primary">
      {links.map((link) => (
        <a className="ghost-button" href={link.href} key={link.href}>
          {link.label}
        </a>
      ))}
    </nav>
  );
}

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <div className="shell">
          <div className="app-frame">
            <Sidebar />
            <main className="main-column">
              <MobileNav />
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}
