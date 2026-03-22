import { describe, expect, it, vi } from "vitest";

// Mock the underlying api module before importing actions
vi.mock("@/lib/api", () => ({
  ApiError: class ApiError extends Error {
    status: number;
    constructor(status: number, message: string) {
      super(message);
      this.status = status;
      this.name = "ApiError";
    }
  },
  createClaim: vi.fn(),
  submitReview: vi.fn(),
  triggerAgentSuggestions: vi.fn(),
}));

import { createClaim, submitReview, triggerAgentSuggestions } from "@/lib/api";
import { createClaimAction, submitReviewAction, suggestConnectionsAction } from "@/lib/actions";

describe("Server Actions", () => {
  it("createClaimAction delegates to createClaim", async () => {
    const mockResult = { id: "claim-1", statement: "test" };
    vi.mocked(createClaim).mockResolvedValue(mockResult as never);

    const input = {
      statement: "test",
      claim_type: "definition" as const,
      trust_status: "tentative" as const,
      context_ids: [],
      concept_ids: [],
      evidence_ids: [],
      cir_id: null,
    };
    const result = await createClaimAction(input);
    expect(createClaim).toHaveBeenCalledWith(input);
    expect(result).toBe(mockResult);
  });

  it("submitReviewAction delegates to submitReview", async () => {
    const mockResult = { id: "proposal-1" };
    vi.mocked(submitReview).mockResolvedValue(mockResult as never);

    const submission = {
      proposalId: "proposal-1",
      decision: "approve" as const,
      comment: "LGTM",
      confidence: 0.9,
    };
    const result = await submitReviewAction(submission);
    expect(submitReview).toHaveBeenCalledWith(submission);
    expect(result).toBe(mockResult);
  });

  it("suggestConnectionsAction delegates to triggerAgentSuggestions", async () => {
    const mockResult = { job_id: "job-1", items: [] };
    vi.mocked(triggerAgentSuggestions).mockResolvedValue(mockResult as never);

    const result = await suggestConnectionsAction("claim", "claim-1", "physics");
    expect(triggerAgentSuggestions).toHaveBeenCalledWith("claim", "claim-1", "physics");
    expect(result).toBe(mockResult);
  });

  it("createClaimAction propagates errors from createClaim", async () => {
    vi.mocked(createClaim).mockRejectedValue(new Error("Auth failed"));

    const input = {
      statement: "test",
      claim_type: "definition" as const,
      trust_status: "tentative" as const,
      context_ids: [],
      concept_ids: [],
      evidence_ids: [],
      cir_id: null,
    };

    await expect(createClaimAction(input)).rejects.toThrow("Auth failed");
  });
});
