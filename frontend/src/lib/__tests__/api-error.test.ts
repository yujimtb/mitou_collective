import { describe, expect, it } from "vitest";

import { ApiError } from "@/lib/api";

describe("ApiError", () => {
  it("stores status code and message", () => {
    const error = new ApiError(404, "Not found");
    expect(error.status).toBe(404);
    expect(error.message).toBe("Not found");
    expect(error.name).toBe("ApiError");
    expect(error).toBeInstanceOf(Error);
  });

  it("is distinguishable via instanceof", () => {
    const apiError = new ApiError(500, "Server error");
    const genericError = new Error("Generic error");
    expect(apiError instanceof ApiError).toBe(true);
    expect(genericError instanceof ApiError).toBe(false);
  });

  it("preserves status for 401 Unauthorized", () => {
    const error = new ApiError(401, "Unauthorized");
    expect(error.status).toBe(401);
  });

  it("preserves status for 403 Forbidden", () => {
    const error = new ApiError(403, "Forbidden");
    expect(error.status).toBe(403);
  });

  it("preserves status for 503 Service Unavailable", () => {
    const error = new ApiError(503, "Service unavailable");
    expect(error.status).toBe(503);
  });

  it("404 can be distinguished from other errors for notFound() logic", () => {
    const notFoundError = new ApiError(404, "Not found");
    const serverError = new ApiError(500, "Internal server error");
    const authError = new ApiError(401, "Unauthorized");

    // Only 404 should trigger notFound()
    expect(notFoundError instanceof ApiError && notFoundError.status === 404).toBe(true);
    expect(serverError instanceof ApiError && serverError.status === 404).toBe(false);
    expect(authError instanceof ApiError && authError.status === 404).toBe(false);
  });
});
