"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import type { ForceGraphMethods } from "react-force-graph-2d";

import type { GraphData, GraphEdge, GraphNode } from "@/lib/api";

const GraphCanvas = dynamic(() => import("react-force-graph-2d"), {
  ssr: false,
  loading: () => <div className="graph-loading">Loading graph…</div>,
});

const edgeStyles: Record<string, string> = {
  equivalent: "#5f8da3",
  analogous: "#c78838",
  generalizes: "#5f8f5d",
  contradicts: "#ca6b55",
  complements: "#173033",
};

const nodeStyles = {
  claim: "#c78838",
  concept: "#5f8da3",
} satisfies Record<GraphNode["kind"], string>;

type VisualNode = GraphNode & {
  color: string;
  val: number;
  x?: number;
  y?: number;
  fx?: number;
  fy?: number;
};

type VisualLink = GraphEdge & {
  color: string;
};

function truncateLabel(label: string, maxLength: number) {
  return label.length > maxLength ? `${label.slice(0, maxLength - 1)}…` : label;
}

export function ForceGraph({ data }: { data: GraphData }) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const graphRef = useRef<
    ForceGraphMethods<Record<string, unknown>, Record<string, unknown>> | undefined
  >(undefined);
  const [dimensions, setDimensions] = useState({ width: 960, height: 620 });
  const [selectedNode, setSelectedNode] = useState<VisualNode | null>(null);
  const [hoveredNode, setHoveredNode] = useState<VisualNode | null>(null);

  const graphData = useMemo(
    () => ({
      nodes: data.nodes.map((node) => ({
        ...node,
        color: nodeStyles[node.kind],
        val: node.kind === "claim" ? 1.9 : 1.5,
      })),
      links: data.edges.map((edge) => ({
        ...edge,
        color: edge.connectionType ? edgeStyles[edge.connectionType] : "#8aa0a3",
      })),
    }),
    [data],
  );

  const activeNode = selectedNode ?? hoveredNode;

  const relatedEdges = useMemo(() => {
    if (!activeNode) {
      return [];
    }

    return graphData.links.filter((edge) => edge.source === activeNode.id || edge.target === activeNode.id).slice(0, 6);
  }, [activeNode, graphData.links]);

  useEffect(() => {
    const element = containerRef.current;
    if (!element) {
      return;
    }

    const resizeObserver = new ResizeObserver((entries) => {
      const entry = entries[0];
      if (!entry) {
        return;
      }

      const width = Math.max(320, Math.floor(entry.contentRect.width));
      const height = Math.max(420, Math.floor(width * 0.58));
      setDimensions({ width, height });
    });

    resizeObserver.observe(element);
    return () => resizeObserver.disconnect();
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      graphRef.current?.zoomToFit(400, 60);
    }, 180);

    return () => window.clearTimeout(timer);
  }, [graphData]);

  return (
    <section className="graph-surface">
      <div className="legend-row" style={{ marginBottom: 18 }}>
        <span className="chip">Claim node</span>
        <span className="chip">Concept node</span>
        <span className="chip">Drag, zoom, and pan to inspect local structure</span>
      </div>

      <div className="graph-shell">
        <div className="graph-stage" ref={containerRef}>
          <GraphCanvas
            ref={graphRef}
            backgroundColor="rgba(255,255,255,0)"
            cooldownTicks={120}
            enableNodeDrag
            graphData={graphData}
            height={dimensions.height}
            linkColor={(link) => (link as VisualLink).color}
            linkDirectionalParticles={(link) =>
              (link as VisualLink).kind === "connection" ? 2 : 0
            }
            linkDirectionalParticleColor={(link) => (link as VisualLink).color}
            linkWidth={(link) => ((link as VisualLink).kind === "connection" ? 2.2 : 1.2)}
            nodeCanvasObject={(node, ctx, globalScale) => {
              const visualNode = node as VisualNode;
              const radius = visualNode.kind === "claim" ? 8 : 6;
              const fontSize = visualNode.kind === "claim" ? 13 : 11;
              const label = truncateLabel(
                visualNode.label,
                visualNode.kind === "claim" ? 32 : 22,
              );
              const isActive = visualNode.id === activeNode?.id;

              ctx.beginPath();
              ctx.arc(visualNode.x ?? 0, visualNode.y ?? 0, radius, 0, 2 * Math.PI, false);
              ctx.fillStyle = visualNode.color;
              ctx.fill();

              ctx.lineWidth = isActive ? 3 : 1.2;
              ctx.strokeStyle = isActive ? "#173033" : "rgba(23, 48, 51, 0.24)";
              ctx.stroke();

              const visibleFont = fontSize / globalScale;
              ctx.font = `${visibleFont}px Inter, Arial, sans-serif`;
              ctx.textAlign = "center";
              ctx.textBaseline = "middle";

              const textWidth = ctx.measureText(label).width;
              const padding = 6 / globalScale;
              const boxHeight = visibleFont + padding * 2;
              const boxWidth = textWidth + padding * 2;
              const x = (visualNode.x ?? 0) - boxWidth / 2;
              const y = (visualNode.y ?? 0) + radius + 8 / globalScale;

              ctx.fillStyle = "rgba(255, 255, 255, 0.92)";
              ctx.fillRect(x, y, boxWidth, boxHeight);
              ctx.strokeStyle = "rgba(23, 48, 51, 0.12)";
              ctx.strokeRect(x, y, boxWidth, boxHeight);

              ctx.fillStyle = "#112022";
              ctx.fillText(label, visualNode.x ?? 0, y + boxHeight / 2);
            }}
            nodeLabel=""
            nodeRelSize={7}
            onBackgroundClick={() => setSelectedNode(null)}
            onNodeClick={(node) => {
              const visualNode = node as VisualNode;
              setSelectedNode(visualNode);
              if (typeof visualNode.x === "number" && typeof visualNode.y === "number") {
                graphRef.current?.centerAt(visualNode.x, visualNode.y, 350);
                graphRef.current?.zoom(2.2, 350);
              }
            }}
            onNodeDragEnd={(node) => {
              const visualNode = node as VisualNode;
              visualNode.fx = visualNode.x;
              visualNode.fy = visualNode.y;
            }}
            onNodeHover={(node) => setHoveredNode((node as VisualNode | null) ?? null)}
            showPointerCursor
            width={dimensions.width}
          />

          {activeNode ? (
            <aside className="graph-tooltip">
              <div className="badge-row">
                <span className="type-pill">{activeNode.kind}</span>
                <span className="chip">{activeNode.field}</span>
              </div>
              <h3 className="card-title" style={{ marginTop: 10 }}>
                {activeNode.label}
              </h3>
              <div className="chip-row" style={{ marginTop: 14 }}>
                {relatedEdges.length ? (
                  relatedEdges.map((edge) => (
                    <span
                      className="edge-pill"
                      key={edge.id}
                      style={{ borderLeft: `4px solid ${edge.color}` }}
                    >
                      {edge.connectionType ?? edge.kind}
                    </span>
                  ))
                ) : (
                  <span className="chip">No visible relations in this slice</span>
                )}
              </div>
              <div className="actions-row" style={{ marginTop: 14 }}>
                <Link className="ghost-button" href={activeNode.href}>
                  Open detail
                </Link>
                <button className="ghost-button" onClick={() => setSelectedNode(null)} type="button">
                  Dismiss
                </button>
              </div>
            </aside>
          ) : null}
        </div>
      </div>
    </section>
  );
}
