import "@testing-library/jest-dom/vitest";
import React from "react";
import { vi } from "vitest";

vi.mock("next/link", () => ({
  default: ({
    children,
    href,
    ...props
  }: {
    children: React.ReactNode;
    href: unknown;
  } & React.AnchorHTMLAttributes<HTMLAnchorElement>) =>
    React.createElement(
      "a",
      {
        href:
          typeof href === "string"
            ? href
            : typeof href === "object" && href !== null && "pathname" in href
              ? String((href as { pathname?: string }).pathname ?? "")
              : String(href ?? ""),
        ...props,
      },
      children,
    ),
}));

class MockResizeObserver {
  observe() {}

  unobserve() {}

  disconnect() {}
}

vi.stubGlobal("ResizeObserver", MockResizeObserver);
