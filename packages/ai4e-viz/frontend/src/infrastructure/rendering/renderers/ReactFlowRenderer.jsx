import { Background, Controls, MiniMap, ReactFlow } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

export default function ReactFlowRenderer({ payload }) {
  const data = payload.data;
  const params = payload.resolved_spec?.params ?? {};
  const nodes = (data.nodes ?? []).map((node, index) => ({
    id: String(node.id), data: { label: node.name ?? node.label ?? node.id },
    position: { x: Number(node.x ?? node.stage * 180 ?? index * 140), y: Number(node.y ?? (index % 3) * 110) },
    style: { width: Math.max(100, (params.node_size ?? 28) * 4), borderColor: '#1677ff' }
  }));
  const edges = (data.links ?? []).map((edge, index) => {
    const [source, target] = Array.isArray(edge) ? edge : [edge.source, edge.target];
    return { id: `edge-${index}`, source: String(source), target: String(target), style: { strokeWidth: params.edge_width ?? 1.5 } };
  });
  return <div className="react-flow-renderer" style={{ height: params.height ?? 440 }}>
    <ReactFlow nodes={nodes} edges={edges} fitView nodesDraggable zoomOnScroll={params.zoom !== false} aria-label={payload.artifact.takeaway}>
      <Background /><MiniMap pannable zoomable /><Controls showInteractive />
    </ReactFlow>
  </div>;
}

