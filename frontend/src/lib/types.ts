export type ClaimType =
  | "definition"
  | "theorem"
  | "empirical"
  | "conjecture"
  | "meta";

export type TrustStatus =
  | "established"
  | "tentative"
  | "disputed"
  | "ai_suggested";

export type EvidenceType =
  | "textbook"
  | "paper"
  | "experiment"
  | "proof"
  | "expert_opinion";

export type Reliability = "high" | "medium" | "low" | "unverified";

export type ProposalType =
  | "create_claim"
  | "link_claims"
  | "update_trust"
  | "add_evidence"
  | "connect_concepts";

export type ProposalStatus =
  | "pending"
  | "in_review"
  | "approved"
  | "rejected"
  | "withdrawn";

export type ReviewDecision = "approve" | "reject" | "request_changes";

export type ConnectionType =
  | "equivalent"
  | "analogous"
  | "generalizes"
  | "contradicts"
  | "complements";

export type ActorType = "human" | "ai_agent";

export type TrustLevel = "admin" | "reviewer" | "contributor" | "observer";

export type EvidenceRelationship =
  | "supports"
  | "contradicts"
  | "partially_supports";

export type AutonomyLevel = "level_0" | "level_1" | "level_2" | "level_3";

export interface ActorRef {
  id: string;
  actor_type: ActorType;
  name: string;
  trust_level: TrustLevel;
  agent_model: string | null;
}

export interface AuthToken {
  access_token: string;
  token_type: "bearer";
  expires_at: string;
}

export interface ReferentRead {
  id: string;
  label: string;
  description: string;
  created_at: string;
  created_by: ActorRef | null;
}

export interface TermRead {
  id: string;
  surface_form: string;
  language: string;
  field_hint: string | null;
  concept_ids: string[];
  created_at: string;
  created_by: ActorRef | null;
}

export interface ConceptRead {
  id: string;
  label: string;
  description: string;
  field: string;
  term_ids: string[];
  referent_id: string | null;
  created_at: string;
  created_by: ActorRef | null;
}

export interface ContextRead {
  id: string;
  name: string;
  description: string;
  field: string;
  assumptions: string[];
  parent_context_id: string | null;
  created_at: string;
  created_by: ActorRef | null;
}

export interface ClaimEvidenceLink {
  claim_id: string;
  relationship: EvidenceRelationship;
}

export interface EvidenceRead {
  id: string;
  evidence_type: EvidenceType;
  title: string;
  source: string;
  excerpt: string | null;
  reliability: Reliability;
  claim_links: ClaimEvidenceLink[];
  created_at: string;
  created_by: ActorRef | null;
}

export interface ClaimCreateInput {
  statement: string;
  claim_type: ClaimType;
  trust_status?: TrustStatus;
  context_ids: string[];
  concept_ids: string[];
  evidence_ids?: string[];
  cir_id?: string | null;
}

export interface ConceptCreateInput {
  label: string;
  description: string;
  field: string;
  term_ids: string[];
  referent_id?: string | null;
}

export interface ContextCreateInput {
  name: string;
  description: string;
  field: string;
  assumptions: string[];
  parent_context_id?: string | null;
}

export interface EvidenceCreateInput {
  evidence_type: EvidenceType;
  title: string;
  source: string;
  excerpt?: string | null;
  reliability?: Reliability;
  claim_links: ClaimEvidenceLink[];
}

export interface Condition {
  predicate: string;
  argument: string;
  negated: boolean;
}

export interface CIRRead {
  id: string;
  claim_id: string;
  context_ref: string;
  subject: string;
  relation: string;
  object: string | null;
  conditions: Condition[];
  units: string | null;
  definition_refs: string[];
  created_at: string;
}

export interface ClaimRead {
  id: string;
  statement: string;
  claim_type: ClaimType;
  trust_status: TrustStatus;
  context_ids: string[];
  concept_ids: string[];
  evidence_ids: string[];
  cir: CIRRead | null;
  created_at: string;
  created_by: ActorRef | null;
  version: number;
}

export interface CrossFieldConnectionRead {
  id: string;
  source_claim_id: string;
  target_claim_id: string;
  connection_type: ConnectionType;
  description: string;
  confidence: number;
  proposal_id: string | null;
  status: ProposalStatus;
  created_at: string;
}

export interface ProposalRead {
  id: string;
  proposal_type: ProposalType;
  proposed_by: ActorRef;
  target_entity_type: string;
  target_entity_id: string | null;
  payload: Record<string, unknown>;
  rationale: string;
  status: ProposalStatus;
  created_at: string;
  reviewed_at: string | null;
  reviewed_by: ActorRef | null;
}

export interface ReviewRead {
  id: string;
  proposal_id: string;
  reviewer: ActorRef;
  decision: ReviewDecision;
  comment: string | null;
  confidence: number | null;
  created_at: string;
}

export interface SearchResultItem {
  entity_type: string;
  entity_id: string;
  title: string;
  snippet: string | null;
  score: number;
}

export interface SearchResult {
  total_count: number;
  items: SearchResultItem[];
}

export interface ErrorDetail {
  code: string;
  message: string;
  details: Record<string, unknown>;
}

export interface ErrorResponse {
  error: ErrorDetail;
}

export interface PaginatedResponse<T> {
  total_count: number;
  current_page: number;
  per_page: number;
  items: T[];
}
