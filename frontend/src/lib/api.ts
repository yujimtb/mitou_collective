import type {
  ActorRef,
  CIRRead,
  ClaimRead,
  ConnectionType,
  ContextRead,
  ConceptRead,
  CrossFieldConnectionRead,
  EvidenceRead,
  PaginatedResponse,
  ProposalRead,
  ProposalStatus,
  ReviewDecision,
  ReviewRead,
  SearchResultItem,
  TermRead,
  TrustStatus,
} from "@/lib/types";

export interface DashboardData {
  totals: {
    claims: number;
    concepts: number;
    contexts: number;
    evidence: number;
    pendingProposals: number;
  };
  recentActivity: ActivityItem[];
}

export interface ActivityItem {
  id: string;
  kind: "claim_created" | "proposal_created" | "review_completed" | "connection_added";
  title: string;
  summary: string;
  actorName: string;
  timestamp: string;
  href: string;
}

export interface ClaimListFilters {
  contextId?: string;
  field?: string;
  trustStatus?: TrustStatus | "";
  query?: string;
}

export interface ClaimEvidenceView extends EvidenceRead {
  relationship: string | null;
}

export interface ClaimDetailData {
  claim: ClaimRead;
  concepts: ConceptRead[];
  contexts: ContextRead[];
  evidence: ClaimEvidenceView[];
  pendingProposals: ProposalRead[];
  history: ActivityItem[];
}

export interface ConceptDetailData {
  concept: ConceptRead;
  terms: TermRead[];
  claims: ClaimRead[];
  relatedConcepts: ConceptRead[];
  connections: CrossFieldConnectionRead[];
}

export interface ContextListItem {
  context: ContextRead;
  claimCount: number;
  childCount: number;
}

export interface ContextDetailData {
  context: ContextRead;
  children: ContextRead[];
  claims: ClaimRead[];
}

export interface GraphNode {
  id: string;
  kind: "claim" | "concept";
  label: string;
  field: string;
  href: string;
  contextIds: string[];
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  kind: "association" | "connection";
  connectionType?: ConnectionType;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface ProposalListFilters {
  status?: ProposalStatus | "all";
}

export interface ReviewSubmission {
  proposalId: string;
  decision: ReviewDecision;
  comment: string;
  confidence?: number;
}

export interface SearchGroup {
  entityType: string;
  items: SearchResultItem[];
}

interface MockState {
  actors: ActorRef[];
  contexts: ContextRead[];
  terms: TermRead[];
  concepts: ConceptRead[];
  claims: ClaimRead[];
  evidence: EvidenceRead[];
  proposals: ProposalRead[];
  reviews: ReviewRead[];
  connections: CrossFieldConnectionRead[];
  activities: ActivityItem[];
  claimHistories: Record<string, ActivityItem[]>;
}

const iso = (value: string) => new Date(value).toISOString();

const actors: ActorRef[] = [
  {
    id: "actor-human-1",
    actor_type: "human",
    name: "Dr. Rei Mori",
    trust_level: "reviewer",
    agent_model: null,
  },
  {
    id: "actor-human-2",
    actor_type: "human",
    name: "Aiko Tan",
    trust_level: "contributor",
    agent_model: null,
  },
  {
    id: "actor-ai-1",
    actor_type: "ai_agent",
    name: "Atlas Linking Agent",
    trust_level: "reviewer",
    agent_model: "gpt-5.4",
  },
];

const contexts: ContextRead[] = [
  {
    id: "ctx-thermo",
    name: "Classical Thermodynamics",
    description: "Macroscopic energy exchange under equilibrium assumptions.",
    field: "Thermodynamics",
    assumptions: ["Closed system", "Quasi-static transitions"],
    parent_context_id: null,
    created_at: iso("2026-03-01T09:00:00Z"),
    created_by: actors[0],
  },
  {
    id: "ctx-statmech",
    name: "Statistical Mechanics",
    description: "Microscopic ensembles linked to macroscopic observables.",
    field: "Statistical Mechanics",
    assumptions: ["Large state spaces", "Ensemble averaging"],
    parent_context_id: "ctx-thermo",
    created_at: iso("2026-03-01T10:00:00Z"),
    created_by: actors[0],
  },
  {
    id: "ctx-shannon",
    name: "Shannon Information Theory",
    description: "Communication limits under noisy coding channels.",
    field: "Information Theory",
    assumptions: ["Discrete symbols", "Probabilistic source model"],
    parent_context_id: null,
    created_at: iso("2026-03-01T11:00:00Z"),
    created_by: actors[1],
  },
  {
    id: "ctx-blackhole",
    name: "Black Hole Thermodynamics",
    description: "Thermodynamic analogies for horizon geometry and quantum gravity.",
    field: "Astrophysics",
    assumptions: ["Event horizon exists", "Semi-classical regime"],
    parent_context_id: null,
    created_at: iso("2026-03-02T08:00:00Z"),
    created_by: actors[0],
  },
  {
    id: "ctx-algorithmic",
    name: "Algorithmic Information Theory",
    description: "Complexity measured by shortest effective descriptions.",
    field: "Algorithmic Information Theory",
    assumptions: ["Universal Turing machine", "Finite description language"],
    parent_context_id: null,
    created_at: iso("2026-03-02T09:30:00Z"),
    created_by: actors[1],
  },
];

const terms: TermRead[] = [
  {
    id: "term-entropy",
    surface_form: "entropy",
    language: "en",
    field_hint: "cross-domain",
    concept_ids: ["concept-thermo-entropy", "concept-info-entropy", "concept-bh-entropy"],
    created_at: iso("2026-03-03T08:00:00Z"),
    created_by: actors[0],
  },
  {
    id: "term-microstate",
    surface_form: "microstate",
    language: "en",
    field_hint: "statistical mechanics",
    concept_ids: ["concept-microstate"],
    created_at: iso("2026-03-03T08:30:00Z"),
    created_by: actors[0],
  },
  {
    id: "term-information",
    surface_form: "information content",
    language: "en",
    field_hint: "information theory",
    concept_ids: ["concept-info-entropy"],
    created_at: iso("2026-03-03T08:40:00Z"),
    created_by: actors[1],
  },
  {
    id: "term-complexity",
    surface_form: "Kolmogorov complexity",
    language: "en",
    field_hint: "algorithmic information theory",
    concept_ids: ["concept-kolmogorov"],
    created_at: iso("2026-03-03T09:00:00Z"),
    created_by: actors[1],
  },
  {
    id: "term-horizon",
    surface_form: "event horizon",
    language: "en",
    field_hint: "astrophysics",
    concept_ids: ["concept-bh-entropy"],
    created_at: iso("2026-03-03T09:10:00Z"),
    created_by: actors[0],
  },
  {
    id: "term-compression",
    surface_form: "lossless compression",
    language: "en",
    field_hint: "information theory",
    concept_ids: ["concept-compression"],
    created_at: iso("2026-03-03T09:20:00Z"),
    created_by: actors[1],
  },
];

const concepts: ConceptRead[] = [
  {
    id: "concept-thermo-entropy",
    label: "Thermodynamic Entropy",
    description: "State variable measuring unavailable energy in macroscopic systems.",
    field: "Thermodynamics",
    term_ids: ["term-entropy"],
    referent_id: null,
    created_at: iso("2026-03-03T12:00:00Z"),
    created_by: actors[0],
  },
  {
    id: "concept-info-entropy",
    label: "Information Entropy",
    description: "Expected uncertainty over a probabilistic message source.",
    field: "Information Theory",
    term_ids: ["term-entropy", "term-information"],
    referent_id: null,
    created_at: iso("2026-03-03T12:10:00Z"),
    created_by: actors[1],
  },
  {
    id: "concept-bh-entropy",
    label: "Black Hole Entropy",
    description: "Entropy proportional to horizon area in gravitational systems.",
    field: "Astrophysics",
    term_ids: ["term-entropy", "term-horizon"],
    referent_id: null,
    created_at: iso("2026-03-03T12:20:00Z"),
    created_by: actors[0],
  },
  {
    id: "concept-kolmogorov",
    label: "Kolmogorov Complexity",
    description: "Shortest description length required to generate a string.",
    field: "Algorithmic Information Theory",
    term_ids: ["term-complexity"],
    referent_id: null,
    created_at: iso("2026-03-03T12:30:00Z"),
    created_by: actors[1],
  },
  {
    id: "concept-microstate",
    label: "Microstate Ensemble",
    description: "Fine-grained configurations underlying macroscopic observables.",
    field: "Statistical Mechanics",
    term_ids: ["term-microstate"],
    referent_id: null,
    created_at: iso("2026-03-03T12:40:00Z"),
    created_by: actors[0],
  },
  {
    id: "concept-compression",
    label: "Lossless Compression",
    description: "Encoding strategy approaching entropy-defined limits without data loss.",
    field: "Information Theory",
    term_ids: ["term-compression"],
    referent_id: null,
    created_at: iso("2026-03-03T12:45:00Z"),
    created_by: actors[1],
  },
];

const cirEntropy: CIRRead = {
  id: "cir-entropy",
  claim_id: "claim-entropy-increase",
  context_ref: "IsolatedSystem",
  subject: "entropy",
  relation: "non_decreasing_in",
  object: "spontaneous_process",
  conditions: [
    { predicate: "system_type", argument: "isolated", negated: false },
    { predicate: "time_reversal", argument: "macroscopic", negated: true },
  ],
  units: null,
  definition_refs: ["term-entropy"],
  created_at: iso("2026-03-05T07:00:00Z"),
};

const claims: ClaimRead[] = [
  {
    id: "claim-entropy-increase",
    statement: "In an isolated macroscopic system, entropy does not decrease over time.",
    claim_type: "theorem",
    trust_status: "established",
    context_ids: ["ctx-thermo", "ctx-statmech"],
    concept_ids: ["concept-thermo-entropy", "concept-microstate"],
    evidence_ids: ["evidence-clausius", "evidence-boltzmann"],
    cir: cirEntropy,
    created_at: iso("2026-03-05T08:00:00Z"),
    created_by: actors[0],
    version: 3,
  },
  {
    id: "claim-shannon-uncertainty",
    statement: "Shannon entropy quantifies the expected uncertainty of a discrete message source.",
    claim_type: "definition",
    trust_status: "established",
    context_ids: ["ctx-shannon"],
    concept_ids: ["concept-info-entropy"],
    evidence_ids: ["evidence-shannon"],
    cir: null,
    created_at: iso("2026-03-05T08:15:00Z"),
    created_by: actors[1],
    version: 2,
  },
  {
    id: "claim-bh-area",
    statement: "Black hole entropy scales with the area of the event horizon rather than its volume.",
    claim_type: "theorem",
    trust_status: "tentative",
    context_ids: ["ctx-blackhole"],
    concept_ids: ["concept-bh-entropy"],
    evidence_ids: ["evidence-bekenstein"],
    cir: null,
    created_at: iso("2026-03-05T08:30:00Z"),
    created_by: actors[0],
    version: 1,
  },
  {
    id: "claim-kolmogorov-randomness",
    statement: "A string is algorithmically random when no substantially shorter program can generate it.",
    claim_type: "definition",
    trust_status: "tentative",
    context_ids: ["ctx-algorithmic"],
    concept_ids: ["concept-kolmogorov"],
    evidence_ids: ["evidence-li-vitanyi"],
    cir: null,
    created_at: iso("2026-03-05T08:45:00Z"),
    created_by: actors[1],
    version: 1,
  },
  {
    id: "claim-maxent-inference",
    statement: "Maximum entropy inference selects the least biased distribution consistent with known constraints.",
    claim_type: "meta",
    trust_status: "ai_suggested",
    context_ids: ["ctx-statmech", "ctx-shannon"],
    concept_ids: ["concept-thermo-entropy", "concept-info-entropy"],
    evidence_ids: ["evidence-jaynes"],
    cir: null,
    created_at: iso("2026-03-05T09:00:00Z"),
    created_by: actors[2],
    version: 1,
  },
  {
    id: "claim-compression-limit",
    statement: "No lossless code can compress every message below the Shannon entropy bound on average.",
    claim_type: "theorem",
    trust_status: "established",
    context_ids: ["ctx-shannon"],
    concept_ids: ["concept-info-entropy", "concept-compression"],
    evidence_ids: ["evidence-shannon"],
    cir: null,
    created_at: iso("2026-03-05T09:15:00Z"),
    created_by: actors[1],
    version: 2,
  },
];

const evidence: EvidenceRead[] = [
  {
    id: "evidence-clausius",
    evidence_type: "textbook",
    title: "Clausius formulation in classical thermodynamics",
    source: "Thermodynamics textbook, chapter 7",
    excerpt: "Entropy of an isolated system tends not to decrease for irreversible processes.",
    reliability: "high",
    claim_links: [{ claim_id: "claim-entropy-increase", relationship: "supports" }],
    created_at: iso("2026-03-04T09:00:00Z"),
    created_by: actors[0],
  },
  {
    id: "evidence-boltzmann",
    evidence_type: "proof",
    title: "Boltzmann counting argument",
    source: "Statistical mechanics note set",
    excerpt: "Higher multiplicity macro-states dominate spontaneous evolution.",
    reliability: "high",
    claim_links: [{ claim_id: "claim-entropy-increase", relationship: "supports" }],
    created_at: iso("2026-03-04T09:20:00Z"),
    created_by: actors[0],
  },
  {
    id: "evidence-shannon",
    evidence_type: "paper",
    title: "A Mathematical Theory of Communication",
    source: "Bell System Technical Journal (1948)",
    excerpt: "Entropy is the expected information produced by a stochastic source.",
    reliability: "high",
    claim_links: [
      { claim_id: "claim-shannon-uncertainty", relationship: "supports" },
      { claim_id: "claim-compression-limit", relationship: "supports" },
    ],
    created_at: iso("2026-03-04T09:30:00Z"),
    created_by: actors[1],
  },
  {
    id: "evidence-bekenstein",
    evidence_type: "paper",
    title: "Black holes and entropy",
    source: "Physical Review D (1973)",
    excerpt: "Black hole entropy scales with horizon area up to physical constants.",
    reliability: "medium",
    claim_links: [{ claim_id: "claim-bh-area", relationship: "supports" }],
    created_at: iso("2026-03-04T09:40:00Z"),
    created_by: actors[0],
  },
  {
    id: "evidence-li-vitanyi",
    evidence_type: "textbook",
    title: "An Introduction to Kolmogorov Complexity and Its Applications",
    source: "Springer",
    excerpt: "Randomness is characterized through incompressibility relative to a fixed universal machine.",
    reliability: "high",
    claim_links: [{ claim_id: "claim-kolmogorov-randomness", relationship: "supports" }],
    created_at: iso("2026-03-04T09:50:00Z"),
    created_by: actors[1],
  },
  {
    id: "evidence-jaynes",
    evidence_type: "paper",
    title: "Information Theory and Statistical Mechanics",
    source: "Physical Review (1957)",
    excerpt: "Entropy maximization provides a bridge between inference and thermodynamics.",
    reliability: "medium",
    claim_links: [{ claim_id: "claim-maxent-inference", relationship: "supports" }],
    created_at: iso("2026-03-04T10:00:00Z"),
    created_by: actors[2],
  },
];

const connections: CrossFieldConnectionRead[] = [
  {
    id: "conn-entropy-bridge",
    source_claim_id: "claim-entropy-increase",
    target_claim_id: "claim-shannon-uncertainty",
    connection_type: "analogous",
    description: "Both claims formalize uncertainty with entropy, one in physical ensembles and one in symbol distributions.",
    confidence: 0.88,
    proposal_id: "proposal-entropy-bridge",
    status: "approved",
    created_at: iso("2026-03-06T08:20:00Z"),
  },
  {
    id: "conn-bh-entropy",
    source_claim_id: "claim-bh-area",
    target_claim_id: "claim-entropy-increase",
    connection_type: "generalizes",
    description: "The black hole case extends thermodynamic reasoning into gravitational horizons.",
    confidence: 0.67,
    proposal_id: "proposal-bh-bridge",
    status: "pending",
    created_at: iso("2026-03-06T09:00:00Z"),
  },
];

const proposals: ProposalRead[] = [
  {
    id: "proposal-entropy-bridge",
    proposal_type: "connect_concepts",
    proposed_by: actors[2],
    target_entity_type: "claim",
    target_entity_id: "claim-shannon-uncertainty",
    payload: {
      source_claim_id: "claim-entropy-increase",
      target_claim_id: "claim-shannon-uncertainty",
      connection_type: "analogous",
      confidence: 0.88,
      rationale: "Both statements define entropy as a monotonic summary of uncertainty, with different underlying state spaces.",
      caveats: ["Thermodynamic entropy is constrained by physical state variables."],
    },
    rationale:
      "Both statements define entropy as a monotonic summary of uncertainty, with different underlying state spaces.",
    status: "approved",
    created_at: iso("2026-03-06T08:00:00Z"),
    reviewed_at: iso("2026-03-06T08:15:00Z"),
    reviewed_by: actors[0],
  },
  {
    id: "proposal-bh-bridge",
    proposal_type: "connect_concepts",
    proposed_by: actors[2],
    target_entity_type: "claim",
    target_entity_id: "claim-entropy-increase",
    payload: {
      source_claim_id: "claim-bh-area",
      target_claim_id: "claim-entropy-increase",
      connection_type: "generalizes",
      confidence: 0.67,
      rationale: "Area-scaling black hole entropy looks like a gravitational extension of the second-law style reasoning in thermodynamics.",
      caveats: ["Semi-classical assumptions may not hold in full quantum gravity."],
    },
    rationale:
      "Area-scaling black hole entropy looks like a gravitational extension of the second-law style reasoning in thermodynamics.",
    status: "pending",
    created_at: iso("2026-03-06T09:00:00Z"),
    reviewed_at: null,
    reviewed_by: null,
  },
  {
    id: "proposal-maxent-review",
    proposal_type: "connect_concepts",
    proposed_by: actors[2],
    target_entity_type: "claim",
    target_entity_id: "claim-compression-limit",
    payload: {
      source_claim_id: "claim-maxent-inference",
      target_claim_id: "claim-compression-limit",
      connection_type: "complements",
      confidence: 0.52,
      rationale: "Constraint-based inference and coding limits both expose entropy as an optimization boundary.",
      caveats: ["One is inferential, the other operational."],
    },
    rationale:
      "Constraint-based inference and coding limits both expose entropy as an optimization boundary.",
    status: "pending",
    created_at: iso("2026-03-06T09:30:00Z"),
    reviewed_at: null,
    reviewed_by: null,
  },
  {
    id: "proposal-trust-maxent",
    proposal_type: "update_trust",
    proposed_by: actors[1],
    target_entity_type: "claim",
    target_entity_id: "claim-maxent-inference",
    payload: {
      claim_id: "claim-maxent-inference",
      from_status: "ai_suggested",
      to_status: "tentative",
      confidence: 0.61,
    },
    rationale: "Jaynes evidence warrants moving the claim from AI-suggested to tentative.",
    status: "pending",
    created_at: iso("2026-03-06T09:45:00Z"),
    reviewed_at: null,
    reviewed_by: null,
  },
];

const reviews: ReviewRead[] = [
  {
    id: "review-entropy-bridge",
    proposal_id: "proposal-entropy-bridge",
    reviewer: actors[0],
    decision: "approve",
    comment: "The mapping is well-scoped and caveated.",
    confidence: 0.89,
    created_at: iso("2026-03-06T08:15:00Z"),
  },
];

const activities: ActivityItem[] = [
  {
    id: "activity-1",
    kind: "proposal_created",
    title: "AI bridge proposed",
    summary: "Atlas suggested a bridge between black hole entropy and thermodynamic entropy.",
    actorName: actors[2].name,
    timestamp: iso("2026-03-06T09:00:00Z"),
    href: "/review",
  },
  {
    id: "activity-2",
    kind: "proposal_created",
    title: "Inference proposal queued",
    summary: "A cross-field proposal links maximum entropy inference with coding limits.",
    actorName: actors[2].name,
    timestamp: iso("2026-03-06T09:30:00Z"),
    href: "/review",
  },
  {
    id: "activity-3",
    kind: "review_completed",
    title: "Connection approved",
    summary: "A reviewer approved the thermodynamics to information-theory entropy bridge.",
    actorName: actors[0].name,
    timestamp: iso("2026-03-06T08:15:00Z"),
    href: "/claims/claim-entropy-increase",
  },
  {
    id: "activity-4",
    kind: "claim_created",
    title: "Algorithmic randomness claim added",
    summary: "A new claim about incompressibility entered the graph.",
    actorName: actors[1].name,
    timestamp: iso("2026-03-05T08:45:00Z"),
    href: "/claims/claim-kolmogorov-randomness",
  },
  {
    id: "activity-5",
    kind: "connection_added",
    title: "Cross-field connection materialized",
    summary: "Approved entropy bridge now appears in the graph view.",
    actorName: actors[0].name,
    timestamp: iso("2026-03-06T08:20:00Z"),
    href: "/graph",
  },
];

const claimHistories: Record<string, ActivityItem[]> = {
  "claim-entropy-increase": [
    {
      id: "hist-1",
      kind: "claim_created",
      title: "Claim created",
      summary: "Initial thermodynamic second-law statement entered the graph.",
      actorName: actors[0].name,
      timestamp: iso("2026-03-05T08:00:00Z"),
      href: "/claims/claim-entropy-increase",
    },
    {
      id: "hist-2",
      kind: "proposal_created",
      title: "AI suggestion linked to Shannon entropy",
      summary: "Atlas proposed an analogous relation to communication entropy.",
      actorName: actors[2].name,
      timestamp: iso("2026-03-06T08:00:00Z"),
      href: "/review",
    },
    {
      id: "hist-3",
      kind: "review_completed",
      title: "Reviewer approved cross-field link",
      summary: "The entropy bridge is now visible in graph mode.",
      actorName: actors[0].name,
      timestamp: iso("2026-03-06T08:15:00Z"),
      href: "/graph",
    },
  ],
  "claim-maxent-inference": [
    {
      id: "hist-4",
      kind: "claim_created",
      title: "Claim proposed by AI",
      summary: "Maximum entropy inference was added as an AI-suggested cross-context claim.",
      actorName: actors[2].name,
      timestamp: iso("2026-03-05T09:00:00Z"),
      href: "/claims/claim-maxent-inference",
    },
    {
      id: "hist-5",
      kind: "proposal_created",
      title: "Trust update awaiting review",
      summary: "A contributor requested moving the claim to tentative status.",
      actorName: actors[1].name,
      timestamp: iso("2026-03-06T09:45:00Z"),
      href: "/review",
    },
  ],
};

let state: MockState = createState();

function createState(): MockState {
  return clone({
    actors,
    contexts,
    terms,
    concepts,
    claims,
    evidence,
    proposals,
    reviews,
    connections,
    activities,
    claimHistories,
  });
}

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}

function delay<T>(value: T): Promise<T> {
  return new Promise((resolve) => {
    setTimeout(() => resolve(clone(value)), 30);
  });
}

function getContextMap() {
  return new Map(state.contexts.map((context) => [context.id, context]));
}

function getConceptMap() {
  return new Map(state.concepts.map((concept) => [concept.id, concept]));
}

function getClaimMap() {
  return new Map(state.claims.map((claim) => [claim.id, claim]));
}

function includesText(haystack: string, needle: string) {
  return haystack.toLowerCase().includes(needle.toLowerCase());
}

function paginate<T>(items: T[], page: number, perPage: number): PaginatedResponse<T> {
  const start = (page - 1) * perPage;
  return {
    total_count: items.length,
    current_page: page,
    per_page: perPage,
    items: items.slice(start, start + perPage),
  };
}

function findFieldForClaim(claim: ClaimRead): string {
  const contextMap = getContextMap();
  return contextMap.get(claim.context_ids[0])?.field ?? "Unknown field";
}

function buildSearchSnippet(text: string, query: string) {
  if (!query) {
    return text;
  }

  const lower = text.toLowerCase();
  const index = lower.indexOf(query.toLowerCase());
  if (index === -1) {
    return text.slice(0, 120);
  }

  const start = Math.max(0, index - 36);
  const end = Math.min(text.length, index + query.length + 72);
  return `${start > 0 ? "..." : ""}${text.slice(start, end)}${end < text.length ? "..." : ""}`;
}

export async function getDashboardData(): Promise<DashboardData> {
  return delay({
    totals: {
      claims: state.claims.length,
      concepts: state.concepts.length,
      contexts: state.contexts.length,
      evidence: state.evidence.length,
      pendingProposals: state.proposals.filter((proposal) => proposal.status === "pending").length,
    },
    recentActivity: [...state.activities].sort((left, right) =>
      right.timestamp.localeCompare(left.timestamp),
    ).slice(0, 10),
  });
}

export async function listClaims(
  filters: ClaimListFilters = {},
  page = 1,
  perPage = 4,
): Promise<PaginatedResponse<ClaimRead>> {
  const contextMap = getContextMap();
  const conceptMap = getConceptMap();

  let items = [...state.claims];

  if (filters.contextId) {
    items = items.filter((claim) => claim.context_ids.includes(filters.contextId as string));
  }

  if (filters.field) {
    items = items.filter((claim) =>
      claim.context_ids.some((contextId) => contextMap.get(contextId)?.field === filters.field),
    );
  }

  if (filters.trustStatus) {
    items = items.filter((claim) => claim.trust_status === filters.trustStatus);
  }

  if (filters.query) {
    const query = filters.query.trim().toLowerCase();
    items = items.filter((claim) => {
      const conceptText = claim.concept_ids
        .map((conceptId) => conceptMap.get(conceptId)?.label ?? "")
        .join(" ");
      return includesText(`${claim.statement} ${conceptText}`, query);
    });
  }

  items.sort((left, right) => right.created_at.localeCompare(left.created_at));
  return delay(paginate(items, page, perPage));
}

export async function getClaimDetail(claimId: string): Promise<ClaimDetailData> {
  const claim = state.claims.find((item) => item.id === claimId);
  if (!claim) {
    throw new Error("Claim not found");
  }

  const conceptsById = getConceptMap();
  const contextsById = getContextMap();
  const claimEvidence = state.evidence
    .filter((item) => claim.evidence_ids.includes(item.id))
    .map((item) => ({
      ...item,
      relationship: item.claim_links.find((link) => link.claim_id === claim.id)?.relationship ?? null,
    }));

  const pendingProposals = state.proposals.filter((proposal) => {
    if (proposal.status !== "pending") {
      return false;
    }

    const payload = proposal.payload as Record<string, string | number | string[]>;
    return payload.source_claim_id === claim.id || payload.target_claim_id === claim.id;
  });

  return delay({
    claim,
    concepts: claim.concept_ids
      .map((conceptId) => conceptsById.get(conceptId))
      .filter(Boolean) as ConceptRead[],
    contexts: claim.context_ids
      .map((contextId) => contextsById.get(contextId))
      .filter(Boolean) as ContextRead[],
    evidence: claimEvidence,
    pendingProposals,
    history: state.claimHistories[claim.id] ?? [],
  });
}

export async function listConcepts(): Promise<ConceptRead[]> {
  return delay([...state.concepts].sort((left, right) => left.label.localeCompare(right.label)));
}

export async function getConceptDetail(conceptId: string): Promise<ConceptDetailData> {
  const concept = state.concepts.find((item) => item.id === conceptId);
  if (!concept) {
    throw new Error("Concept not found");
  }

  const claimsForConcept = state.claims.filter((claim) => claim.concept_ids.includes(concept.id));
  const relatedConcepts = state.concepts.filter(
    (candidate) =>
      candidate.id !== concept.id &&
      (candidate.field !== concept.field || candidate.label.includes("Entropy")) &&
      candidate.label.split(" ").some((token) => concept.label.includes(token)),
  );

  const relatedConnections = state.connections.filter((connection) => {
    const sourceClaim = state.claims.find((claim) => claim.id === connection.source_claim_id);
    const targetClaim = state.claims.find((claim) => claim.id === connection.target_claim_id);
    return Boolean(
      sourceClaim?.concept_ids.includes(concept.id) || targetClaim?.concept_ids.includes(concept.id),
    );
  });

  return delay({
    concept,
    terms: state.terms.filter((term) => concept.term_ids.includes(term.id)),
    claims: claimsForConcept,
    relatedConcepts,
    connections: relatedConnections,
  });
}

export async function listContexts(): Promise<ContextListItem[]> {
  const items = state.contexts.map((context) => ({
    context,
    claimCount: state.claims.filter((claim) => claim.context_ids.includes(context.id)).length,
    childCount: state.contexts.filter((candidate) => candidate.parent_context_id === context.id).length,
  }));
  return delay(items);
}

export async function getContextDetail(contextId: string): Promise<ContextDetailData> {
  const context = state.contexts.find((item) => item.id === contextId);
  if (!context) {
    throw new Error("Context not found");
  }

  return delay({
    context,
    children: state.contexts.filter((item) => item.parent_context_id === context.id),
    claims: state.claims.filter((claim) => claim.context_ids.includes(context.id)),
  });
}

export async function listProposals(filters: ProposalListFilters = {}): Promise<ProposalRead[]> {
  let items = [...state.proposals].sort((left, right) => right.created_at.localeCompare(left.created_at));
  if (filters.status && filters.status !== "all") {
    items = items.filter((proposal) => proposal.status === filters.status);
  }
  return delay(items);
}

export async function submitReview(submission: ReviewSubmission): Promise<ProposalRead> {
  const proposal = state.proposals.find((item) => item.id === submission.proposalId);
  if (!proposal) {
    throw new Error("Proposal not found");
  }

  if (submission.decision === "reject" && !submission.comment.trim()) {
    throw new Error("A rejection comment is required.");
  }

  proposal.status = submission.decision === "approve" ? "approved" : "rejected";
  proposal.reviewed_at = new Date().toISOString();
  proposal.reviewed_by = state.actors[0];

  state.reviews.unshift({
    id: `review-${state.reviews.length + 1}`,
    proposal_id: proposal.id,
    reviewer: state.actors[0],
    decision: submission.decision,
    comment: submission.comment,
    confidence: submission.confidence ?? null,
    created_at: new Date().toISOString(),
  });

  state.activities.unshift({
    id: `activity-${state.activities.length + 1}`,
    kind: "review_completed",
    title: submission.decision === "approve" ? "Proposal approved" : "Proposal rejected",
    summary: proposal.rationale,
    actorName: state.actors[0].name,
    timestamp: new Date().toISOString(),
    href: "/review",
  });

  const payload = proposal.payload as Record<string, string | number>;
  if (submission.decision === "approve" && payload.source_claim_id && payload.target_claim_id) {
    const exists = state.connections.some(
      (connection) =>
        connection.source_claim_id === payload.source_claim_id &&
        connection.target_claim_id === payload.target_claim_id,
    );
    if (!exists) {
      state.connections.push({
        id: `conn-${state.connections.length + 1}`,
        source_claim_id: String(payload.source_claim_id),
        target_claim_id: String(payload.target_claim_id),
        connection_type: String(payload.connection_type) as ConnectionType,
        description: String(payload.rationale ?? proposal.rationale),
        confidence: Number(payload.confidence ?? 0.5),
        proposal_id: proposal.id,
        status: "approved",
        created_at: new Date().toISOString(),
      });
    }
  }

  if (submission.decision === "approve" && proposal.proposal_type === "update_trust") {
    const claim = state.claims.find((item) => item.id === proposal.target_entity_id);
    const nextStatus = proposal.payload.to_status as TrustStatus | undefined;
    if (claim && nextStatus) {
      claim.trust_status = nextStatus;
    }
  }

  return delay(proposal);
}

export async function getGraphData(filters: {
  contextId?: string;
  field?: string;
} = {}): Promise<GraphData> {
  const conceptsById = getConceptMap();
  const contextMap = getContextMap();

  const claimNodes = state.claims
    .filter((claim) => {
      if (filters.contextId && !claim.context_ids.includes(filters.contextId)) {
        return false;
      }
      if (filters.field) {
        return claim.context_ids.some((contextId) => contextMap.get(contextId)?.field === filters.field);
      }
      return true;
    })
    .map<GraphNode>((claim) => ({
      id: claim.id,
      kind: "claim",
      label: claim.statement,
      field: findFieldForClaim(claim),
      href: `/claims/${claim.id}`,
      contextIds: claim.context_ids,
    }));

  const visibleClaimIds = new Set(claimNodes.map((node) => node.id));
  const conceptIds = new Set(
    state.claims
      .filter((claim) => visibleClaimIds.has(claim.id))
      .flatMap((claim) => claim.concept_ids),
  );

  const conceptNodes = state.concepts
    .filter((concept) => conceptIds.has(concept.id))
    .map<GraphNode>((concept) => ({
      id: concept.id,
      kind: "concept",
      label: concept.label,
      field: concept.field,
      href: `/concepts/${concept.id}`,
      contextIds: [],
    }));

  const edges: GraphEdge[] = [];
  state.claims.forEach((claim) => {
    if (!visibleClaimIds.has(claim.id)) {
      return;
    }

    claim.concept_ids.forEach((conceptId) => {
      if (conceptsById.has(conceptId)) {
        edges.push({
          id: `edge-${claim.id}-${conceptId}`,
          source: claim.id,
          target: conceptId,
          kind: "association",
        });
      }
    });
  });

  state.connections.forEach((connection) => {
    if (visibleClaimIds.has(connection.source_claim_id) && visibleClaimIds.has(connection.target_claim_id)) {
      edges.push({
        id: connection.id,
        source: connection.source_claim_id,
        target: connection.target_claim_id,
        kind: "connection",
        connectionType: connection.connection_type,
      });
    }
  });

  return delay({ nodes: [...claimNodes, ...conceptNodes], edges });
}

export async function searchKnowledge(query: string, entityType = "all"): Promise<SearchGroup[]> {
  const trimmed = query.trim();
  if (!trimmed) {
    return delay([]);
  }

  const groups: SearchGroup[] = [];

  const addGroup = (type: string, items: SearchResultItem[]) => {
    if (items.length && (entityType === "all" || entityType === type)) {
      groups.push({ entityType: type, items });
    }
  };

  addGroup(
    "claim",
    state.claims
      .filter((claim) => includesText(claim.statement, trimmed))
      .map((claim) => ({
        entity_type: "claim",
        entity_id: claim.id,
        title: claim.statement,
        snippet: buildSearchSnippet(claim.statement, trimmed),
        score: 0.91,
      })),
  );

  addGroup(
    "concept",
    state.concepts
      .filter((concept) => includesText(`${concept.label} ${concept.description}`, trimmed))
      .map((concept) => ({
        entity_type: "concept",
        entity_id: concept.id,
        title: concept.label,
        snippet: buildSearchSnippet(concept.description, trimmed),
        score: 0.84,
      })),
  );

  addGroup(
    "term",
    state.terms
      .filter((term) => includesText(term.surface_form, trimmed))
      .map((term) => ({
        entity_type: "term",
        entity_id: term.id,
        title: term.surface_form,
        snippet: term.field_hint,
        score: 0.73,
      })),
  );

  addGroup(
    "context",
    state.contexts
      .filter((context) => includesText(`${context.name} ${context.description}`, trimmed))
      .map((context) => ({
        entity_type: "context",
        entity_id: context.id,
        title: context.name,
        snippet: buildSearchSnippet(context.description, trimmed),
        score: 0.69,
      })),
  );

  addGroup(
    "evidence",
    state.evidence
      .filter((item) => includesText(`${item.title} ${item.excerpt ?? ""}`, trimmed))
      .map((item) => ({
        entity_type: "evidence",
        entity_id: item.id,
        title: item.title,
        snippet: item.excerpt,
        score: 0.66,
      })),
  );

  return delay(groups);
}

export async function getReferenceData() {
  return delay({
    contexts: state.contexts,
    fields: Array.from(new Set(state.contexts.map((context) => context.field))),
  });
}

export async function getEntityHref(item: SearchResultItem): Promise<string> {
  if (item.entity_type === "claim") {
    return `/claims/${item.entity_id}`;
  }
  if (item.entity_type === "concept") {
    return `/concepts/${item.entity_id}`;
  }
  if (item.entity_type === "context") {
    return `/contexts/${item.entity_id}`;
  }
  if (item.entity_type === "evidence") {
    const linkedClaim = state.evidence
      .find((entry) => entry.id === item.entity_id)
      ?.claim_links.at(0)?.claim_id;
    return linkedClaim ? `/claims/${linkedClaim}` : "/claims";
  }
  return "/search";
}

export function resetMockState() {
  state = createState();
}
