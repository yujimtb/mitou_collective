"use server";

import { createClaim, submitReview, triggerAgentSuggestions } from "@/lib/api";
import type { ReviewSubmission, SuggestionTriggerResult } from "@/lib/api";
import type { ClaimCreateInput, ClaimRead, ProposalRead } from "@/lib/types";

export async function createClaimAction(data: ClaimCreateInput): Promise<ClaimRead> {
  return createClaim(data);
}

export async function submitReviewAction(submission: ReviewSubmission): Promise<ProposalRead> {
  return submitReview(submission);
}

export async function suggestConnectionsAction(
  entityType: string,
  entityId: string,
  targetField?: string,
): Promise<SuggestionTriggerResult> {
  return triggerAgentSuggestions(entityType, entityId, targetField);
}
