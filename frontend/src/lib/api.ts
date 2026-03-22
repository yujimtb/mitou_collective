import type {
  ClaimRead,
  ConceptRead,
  ConnectionType,
  ContextRead,
  CrossFieldConnectionRead,
  EvidenceRead,
  PaginatedResponse,
  ProposalRead,
  ProposalStatus,
  ReviewDecision,
  SearchResultItem,
  TermRead,
  TrustStatus,
} from "@/lib/types";

/* ------------------------------------------------------------------ */
/*  Public interface types (unchanged from the original mock API)      */
/* ------------------------------------------------------------------ */

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

/* ------------------------------------------------------------------ */
/*  HTTP helpers                                                       */
/* ------------------------------------------------------------------ */

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const V1 = `${API_BASE}/api/v1`;

function authHeaders(): Record<string, string> {
  const token = process.env.CS_API_TOKEN;
  if (token) {
    return { Authorization: `Bearer ${token}` };
  }
  return {};
}

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${V1}${path}`;
  const res = await fetch(url, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...init?.headers,
    },
    next: { revalidate: 30 },
  });
  if (!res.ok) {
    throw new Error(`API ${res.status}: ${url}`);
  }
  return res.json() as Promise<T>;
}

function qs(params: Record<string, string | number | boolean | undefined | null>): string {
  const entries = Object.entries(params).filter(
    (pair): pair is [string, string | number | boolean] => pair[1] != null && pair[1] !== "",
  );
  if (entries.length === 0) return "";
  return "?" + new URLSearchParams(entries.map(([k, v]) => [k, String(v)])).toString();
}

/* ------------------------------------------------------------------ */
/*  Dashboard                                                          */
/* ------------------------------------------------------------------ */

export async function getDashboardData(): Promise<DashboardData> {
  const [claims, concepts, contexts, evidence, proposals] = await Promise.all([
    api<PaginatedResponse<ClaimRead>>("/claims?per_page=1"),
    api<PaginatedResponse<ConceptRead>>("/concepts?per_page=1"),
    api<PaginatedResponse<ContextRead>>("/contexts?per_page=1"),
    api<PaginatedResponse<EvidenceRead>>("/evidence?per_page=1"),
    api<PaginatedResponse<ProposalRead>>("/proposals?status=pending&per_page=1"),
  ]);

  return {
    totals: {
      claims: claims.total_count,
      concepts: concepts.total_count,
      contexts: contexts.total_count,
      evidence: evidence.total_count,
      pendingProposals: proposals.total_count,
    },
    recentActivity: [],
  };
}

/* ------------------------------------------------------------------ */
/*  Claims                                                             */
/* ------------------------------------------------------------------ */

export async function listClaims(
  filters: ClaimListFilters = {},
  page = 1,
  perPage = 4,
): Promise<PaginatedResponse<ClaimRead>> {
  const params = qs({
    context: filters.contextId,
    field: filters.field,
    trust_status: filters.trustStatus || undefined,
    search: filters.query,
    page,
    per_page: perPage,
  });
  return api<PaginatedResponse<ClaimRead>>(`/claims${params}`);
}

export async function getClaimDetail(claimId: string): Promise<ClaimDetailData> {
  const claim = await api<ClaimRead>(`/claims/${encodeURIComponent(claimId)}`);

  const [conceptRes, contextRes, evidenceRes, proposalRes, historyRes] = await Promise.all([
    claim.concept_ids.length
      ? Promise.all(claim.concept_ids.map((id) => api<ConceptRead>(`/concepts/${encodeURIComponent(id)}`).catch(() => null)))
      : Promise.resolve([]),
    claim.context_ids.length
      ? Promise.all(claim.context_ids.map((id) => api<ContextRead>(`/contexts/${encodeURIComponent(id)}`).catch(() => null)))
      : Promise.resolve([]),
    claim.evidence_ids.length
      ? Promise.all(claim.evidence_ids.map((id) => api<EvidenceRead>(`/evidence/${encodeURIComponent(id)}`).catch(() => null)))
      : Promise.resolve([]),
    api<PaginatedResponse<ProposalRead>>("/proposals?status=pending&per_page=100"),
    api<Array<Record<string, unknown>>>(`/claims/${encodeURIComponent(claimId)}/history`).catch(() => []),
  ]);

  const concepts = conceptRes.filter(Boolean) as ConceptRead[];
  const contexts = contextRes.filter(Boolean) as ContextRead[];

  const evidenceItems = (evidenceRes.filter(Boolean) as EvidenceRead[]).map((ev) => ({
    ...ev,
    relationship: ev.claim_links.find((l) => l.claim_id === claim.id)?.relationship ?? null,
  }));

  const pendingProposals = proposalRes.items.filter((p) => {
    const payload = p.payload as Record<string, unknown>;
    return payload.source_claim_id === claim.id || payload.target_claim_id === claim.id || p.target_entity_id === claim.id;
  });

  const history: ActivityItem[] = (historyRes as Array<Record<string, string>>).map((h, i) => ({
    id: h.id ?? `hist-${i}`,
    kind: (h.kind ?? "claim_created") as ActivityItem["kind"],
    title: h.title ?? "",
    summary: h.summary ?? "",
    actorName: h.actor_name ?? "",
    timestamp: h.timestamp ?? h.created_at ?? "",
    href: h.href ?? `/claims/${claimId}`,
  }));

  return { claim, concepts, contexts, evidence: evidenceItems, pendingProposals, history };
}

/* ------------------------------------------------------------------ */
/*  Concepts                                                           */
/* ------------------------------------------------------------------ */

export async function listConcepts(): Promise<ConceptRead[]> {
  const res = await api<PaginatedResponse<ConceptRead>>("/concepts?per_page=100");
  return res.items.sort((a, b) => a.label.localeCompare(b.label));
}

export async function getConceptDetail(conceptId: string): Promise<ConceptDetailData> {
  const [concept, connections] = await Promise.all([
    api<ConceptRead>(`/concepts/${encodeURIComponent(conceptId)}`),
    api<CrossFieldConnectionRead[]>(`/concepts/${encodeURIComponent(conceptId)}/connections`).catch(() => []),
  ]);

  const termsRes = concept.term_ids.length
    ? await Promise.all(concept.term_ids.map((id) => api<TermRead>(`/terms/${encodeURIComponent(id)}`).catch(() => null)))
    : [];

  const claimsRes = await api<PaginatedResponse<ClaimRead>>("/claims?per_page=100");
  const claimsForConcept = claimsRes.items.filter((c) => c.concept_ids.includes(concept.id));

  const allConcepts = await api<PaginatedResponse<ConceptRead>>("/concepts?per_page=100");
  const relatedConcepts = allConcepts.items.filter(
    (c) =>
      c.id !== concept.id &&
      (c.field !== concept.field || c.label.includes("Entropy")) &&
      c.label.split(" ").some((token) => concept.label.includes(token)),
  );

  return {
    concept,
    terms: termsRes.filter(Boolean) as TermRead[],
    claims: claimsForConcept,
    relatedConcepts,
    connections,
  };
}

/* ------------------------------------------------------------------ */
/*  Contexts                                                           */
/* ------------------------------------------------------------------ */

export async function listContexts(): Promise<ContextListItem[]> {
  const [contextRes, claimRes] = await Promise.all([
    api<PaginatedResponse<ContextRead>>("/contexts?per_page=100"),
    api<PaginatedResponse<ClaimRead>>("/claims?per_page=100"),
  ]);
  const ctxs = contextRes.items;
  const allClaims = claimRes.items;

  return ctxs.map((context) => ({
    context,
    claimCount: allClaims.filter((c) => c.context_ids.includes(context.id)).length,
    childCount: ctxs.filter((c) => c.parent_context_id === context.id).length,
  }));
}

export async function getContextDetail(contextId: string): Promise<ContextDetailData> {
  const [context, contextRes, claimRes] = await Promise.all([
    api<ContextRead>(`/contexts/${encodeURIComponent(contextId)}`),
    api<PaginatedResponse<ContextRead>>("/contexts?per_page=100"),
    api<PaginatedResponse<ClaimRead>>(`/claims?context=${encodeURIComponent(contextId)}&per_page=100`),
  ]);

  return {
    context,
    children: contextRes.items.filter((c) => c.parent_context_id === context.id),
    claims: claimRes.items,
  };
}

/* ------------------------------------------------------------------ */
/*  Proposals & Reviews                                                */
/* ------------------------------------------------------------------ */

export async function listProposals(filters: ProposalListFilters = {}): Promise<ProposalRead[]> {
  const params = qs({
    status: filters.status && filters.status !== "all" ? filters.status : undefined,
    per_page: 100,
  });
  const res = await api<PaginatedResponse<ProposalRead>>(`/proposals${params}`);
  return res.items;
}

export async function submitReview(submission: ReviewSubmission): Promise<ProposalRead> {
  if (submission.decision === "reject" && !submission.comment.trim()) {
    throw new Error("A rejection comment is required.");
  }

  await api<unknown>(`/proposals/${encodeURIComponent(submission.proposalId)}/review`, {
    method: "POST",
    body: JSON.stringify({
      proposal_id: submission.proposalId,
      decision: submission.decision,
      comment: submission.comment || null,
      confidence: submission.confidence ?? null,
    }),
  });

  return api<ProposalRead>(`/proposals/${encodeURIComponent(submission.proposalId)}`);
}

/* ------------------------------------------------------------------ */
/*  Graph                                                              */
/* ------------------------------------------------------------------ */

export async function getGraphData(filters: {
  contextId?: string;
  field?: string;
} = {}): Promise<GraphData> {
  const claimParams = qs({
    context: filters.contextId,
    field: filters.field,
    per_page: 100,
  });

  const [claimRes, conceptRes, contextRes] = await Promise.all([
    api<PaginatedResponse<ClaimRead>>(`/claims${claimParams}`),
    api<PaginatedResponse<ConceptRead>>("/concepts?per_page=100"),
    api<PaginatedResponse<ContextRead>>("/contexts?per_page=100"),
  ]);

  const allClaims = claimRes.items;
  const allConcepts = conceptRes.items;
  const contextMap = new Map(contextRes.items.map((c) => [c.id, c]));
  const conceptMap = new Map(allConcepts.map((c) => [c.id, c]));

  const claimNodes: GraphNode[] = allClaims.map((claim) => ({
    id: claim.id,
    kind: "claim",
    label: claim.statement,
    field: contextMap.get(claim.context_ids[0])?.field ?? "Unknown",
    href: `/claims/${claim.id}`,
    contextIds: claim.context_ids,
  }));

  const visibleClaimIds = new Set(claimNodes.map((n) => n.id));
  const usedConceptIds = new Set(allClaims.flatMap((c) => c.concept_ids));

  const conceptNodes: GraphNode[] = allConcepts
    .filter((c) => usedConceptIds.has(c.id))
    .map((c) => ({
      id: c.id,
      kind: "concept" as const,
      label: c.label,
      field: c.field,
      href: `/concepts/${c.id}`,
      contextIds: [],
    }));

  const edges: GraphEdge[] = [];

  for (const claim of allClaims) {
    for (const cid of claim.concept_ids) {
      if (conceptMap.has(cid)) {
        edges.push({
          id: `edge-${claim.id}-${cid}`,
          source: claim.id,
          target: cid,
          kind: "association",
        });
      }
    }
  }

  // Fetch connections for each visible concept to find cross-field edges
  const connectionSets = await Promise.all(
    allConcepts
      .filter((c) => usedConceptIds.has(c.id))
      .map((c) => api<CrossFieldConnectionRead[]>(`/concepts/${encodeURIComponent(c.id)}/connections`).catch(() => [])),
  );
  const seenConnIds = new Set<string>();
  for (const conns of connectionSets) {
    for (const conn of conns) {
      if (
        !seenConnIds.has(conn.id) &&
        visibleClaimIds.has(conn.source_claim_id) &&
        visibleClaimIds.has(conn.target_claim_id)
      ) {
        seenConnIds.add(conn.id);
        edges.push({
          id: conn.id,
          source: conn.source_claim_id,
          target: conn.target_claim_id,
          kind: "connection",
          connectionType: conn.connection_type,
        });
      }
    }
  }

  return { nodes: [...claimNodes, ...conceptNodes], edges };
}

/* ------------------------------------------------------------------ */
/*  Search                                                             */
/* ------------------------------------------------------------------ */

export async function searchKnowledge(query: string, entityType = "all"): Promise<SearchGroup[]> {
  const trimmed = query.trim();
  if (!trimmed) return [];

  const params = qs({ q: trimmed, scope: entityType === "all" ? undefined : entityType, per_page: 50 });
  const result = await api<{ total_count: number; items: SearchResultItem[] }>(`/search${params}`);

  const grouped = new Map<string, SearchResultItem[]>();
  for (const item of result.items) {
    const group = grouped.get(item.entity_type) ?? [];
    group.push(item);
    grouped.set(item.entity_type, group);
  }

  return Array.from(grouped.entries()).map(([entityType, items]) => ({
    entityType,
    items,
  }));
}

/* ------------------------------------------------------------------ */
/*  Reference data                                                     */
/* ------------------------------------------------------------------ */

export async function getReferenceData() {
  const res = await api<PaginatedResponse<ContextRead>>("/contexts?per_page=100");
  const contexts = res.items;
  return {
    contexts,
    fields: Array.from(new Set(contexts.map((c) => c.field))),
  };
}

export async function getEntityHref(item: SearchResultItem): Promise<string> {
  if (item.entity_type === "claim") return `/claims/${item.entity_id}`;
  if (item.entity_type === "concept") return `/concepts/${item.entity_id}`;
  if (item.entity_type === "context") return `/contexts/${item.entity_id}`;
  if (item.entity_type === "evidence") return `/claims`;
  return "/search";
}

export function resetMockState() {
  // No-op: no longer using mock state
}
