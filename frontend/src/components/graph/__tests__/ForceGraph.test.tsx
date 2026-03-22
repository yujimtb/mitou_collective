import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

type MockNode = {
  id: string;
  x?: number;
  y?: number;
  [key: string]: unknown;
};

type MockGraphProps = {
  graphData?: {
    nodes?: MockNode[];
  };
  onNodeClick?: (node: MockNode) => void;
};

const zoomToFitMock = vi.fn();
const centerAtMock = vi.fn();
const zoomMock = vi.fn();

vi.mock("react-force-graph-2d", async () => {
  const React = await import("react");

  return {
    __esModule: true,
    default: React.forwardRef<unknown, MockGraphProps>(function MockForceGraph(props, ref) {
      React.useImperativeHandle(ref, () => ({
        zoomToFit: zoomToFitMock,
        centerAt: centerAtMock,
        zoom: zoomMock,
      }));

      return React.createElement(
        "button",
        {
          type: "button",
          "data-testid": "graph-canvas",
          onClick: () => {
            const firstNode = props.graphData?.nodes?.[0];
            if (firstNode) {
              props.onNodeClick?.({ ...firstNode, x: 128, y: 96 });
            }
          },
        },
        `Graph nodes: ${props.graphData?.nodes?.length ?? 0}`,
      );
    }),
  };
});

vi.mock("next/dynamic", async () => {
  const graphModule = await import("react-force-graph-2d");

  return {
    __esModule: true,
    default: () => graphModule.default,
  };
});

import { ForceGraph } from "@/components/graph/ForceGraph";
import type { GraphData } from "@/lib/api";

const graphData: GraphData = {
  nodes: [
    {
      id: "claim-1",
      kind: "claim",
      label: "Entropy grows in isolated systems",
      field: "Physics",
      href: "/claims/claim-1",
      contextIds: ["ctx-1"],
    },
    {
      id: "concept-1",
      kind: "concept",
      label: "Entropy",
      field: "Physics",
      href: "/concepts/concept-1",
      contextIds: [],
    },
  ],
  edges: [
    {
      id: "edge-1",
      source: "claim-1",
      target: "concept-1",
      kind: "association",
    },
  ],
};

describe("ForceGraph", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("renders the graph surface with supplied graph data", () => {
    render(<ForceGraph data={graphData} />);

    expect(screen.getByText("Claim node")).toBeInTheDocument();
    expect(screen.getByText("Concept node")).toBeInTheDocument();
    expect(screen.getByTestId("graph-canvas")).toHaveTextContent("Graph nodes: 2");
  });

  it("shows a tooltip when a node is clicked", async () => {
    render(<ForceGraph data={graphData} />);

    fireEvent.click(screen.getByTestId("graph-canvas"));

    expect(await screen.findByText("Entropy grows in isolated systems")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Open detail" })).toHaveAttribute(
      "href",
      "/claims/claim-1",
    );
    expect(centerAtMock).toHaveBeenCalledWith(128, 96, 350);
    expect(zoomMock).toHaveBeenCalledWith(2.2, 350);
  });
});
