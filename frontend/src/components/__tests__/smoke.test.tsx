import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { ClaimEvidenceView } from "@/lib/api";
import { ClaimCard } from "@/components/claims/ClaimCard";
import { FilterBar } from "@/components/common/FilterBar";
import { SearchBar } from "@/components/common/SearchBar";
import { TrustBadge } from "@/components/common/TrustBadge";
import { EvidenceCard } from "@/components/evidence/EvidenceCard";
import { Header } from "@/components/layout/Header";
import type { ClaimRead, ContextRead } from "@/lib/types";

const context: ContextRead = {
  id: "ctx-1",
  name: "Thermodynamics",
  description: "A physical context for entropy.",
  field: "Physics",
  assumptions: ["Closed system"],
  parent_context_id: null,
  created_at: "2026-03-22T00:00:00Z",
  created_by: null,
};

const claim: ClaimRead = {
  id: "claim-1",
  statement: "Entropy grows in isolated systems.",
  claim_type: "theorem",
  trust_status: "established",
  context_ids: ["ctx-1"],
  concept_ids: ["concept-1"],
  evidence_ids: ["evidence-1"],
  cir: null,
  created_at: "2026-03-22T00:00:00Z",
  created_by: null,
  version: 3,
};

const evidence: ClaimEvidenceView = {
  id: "evidence-1",
  evidence_type: "paper",
  title: "Foundations of Entropy",
  source: "Journal of Physics",
  excerpt: "Entropy is non-decreasing in an isolated system.",
  reliability: "high",
  claim_links: [{ claim_id: "claim-1", relationship: "supports" }],
  created_at: "2026-03-22T00:00:00Z",
  created_by: null,
  relationship: "supports",
};

describe("component smoke tests", () => {
  it("renders FilterBar with default filters and options", () => {
    render(
      <FilterBar
        contexts={[context]}
        fields={["Physics", "Information Theory"]}
        filters={{ query: "entropy", contextId: "ctx-1", field: "Physics", trustStatus: "established" }}
      />,
    );

    expect(screen.getByLabelText("Keyword")).toHaveValue("entropy");
    expect(screen.getByLabelText("Context")).toHaveValue("ctx-1");
    expect(screen.getByLabelText("Field")).toHaveValue("Physics");
    expect(screen.getByLabelText("Trust")).toHaveValue("established");
  });

  it("renders ClaimCard with statement, context, and destination link", () => {
    render(<ClaimCard claim={claim} contexts={[context]} />);

    expect(screen.getByText("Entropy grows in isolated systems.")).toBeInTheDocument();
    expect(screen.getByText("Thermodynamics")).toBeInTheDocument();
    expect(screen.getByRole("link")).toHaveAttribute("href", "/claims/claim-1");
  });

  it("renders Header with optional action content", () => {
    render(<Header action={<button type="button">Open review queue</button>} subtitle="Track the system pulse." title="Dashboard" />);

    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Track the system pulse.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Open review queue" })).toBeInTheDocument();
  });

  it("renders EvidenceCard with reliability, relationship, and excerpt", () => {
    render(<EvidenceCard evidence={evidence} />);

    expect(screen.getByText("Foundations of Entropy")).toBeInTheDocument();
    expect(screen.getByText("Reliability: high")).toBeInTheDocument();
    expect(screen.getByText("supports")).toBeInTheDocument();
    expect(screen.getByText("Entropy is non-decreasing in an isolated system.")).toBeInTheDocument();
  });

  it("renders SearchBar defaults and TrustBadge label", () => {
    render(
      <>
        <SearchBar entityType="concept" query="entropy" />
        <TrustBadge status="ai_suggested" />
      </>,
    );

    expect(screen.getByLabelText("Search")).toHaveValue("entropy");
    expect(screen.getByLabelText("Entity type")).toHaveValue("concept");
    expect(screen.getByText("AI Suggested")).toBeInTheDocument();
  });
});
