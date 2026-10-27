import React, { useMemo } from 'react';
import ReactFlow, { 
  Background, 
  Controls, 
  Node, 
  Edge, 
  MarkerType 
} from 'reactflow';
import 'reactflow/dist/style.css';
import { TopologyData, NetworkNode } from '../services/api';
import { CustomNodeComponent } from './CustomNodeComponent';

interface Props {
  topology: TopologyData | null;
  onSelectNode: (node: NetworkNode) => void;
}

export const NetworkGraphView: React.FC<Props> = ({ topology, onSelectNode }) => {
  const nodeTypes = useMemo(() => ({ customNode: CustomNodeComponent }), []);

  if (!topology) {
    return (
      <div className="h-[550px] w-full flex items-center justify-center bg-slate-950/60 rounded-xl border border-slate-800">
        <span className="text-slate-400 text-sm animate-pulse">Loading Network Topology...</span>
      </div>
    );
  }

  const nodes: Node[] = topology.nodes.map((n) => ({
    id: n.id,
    type: 'customNode',
    position: { x: n.pos_x, y: n.pos_y },
    data: n
  }));

  const edges: Edge[] = topology.links.map((l) => {
    const isDown = l.status === 'down';
    const isDegraded = l.status === 'degraded';

    return {
      id: l.id,
      source: l.source,
      target: l.target,
      animated: !isDown && !l.is_backup,
      style: {
        stroke: isDown ? '#f43f5e' : isDegraded ? '#f59e0b' : l.is_backup ? '#64748b' : '#38bdf8',
        strokeWidth: isDown ? 3 : 2,
        strokeDasharray: l.is_backup ? '5,5' : undefined
      },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: isDown ? '#f43f5e' : isDegraded ? '#f59e0b' : '#38bdf8'
      }
    };
  });

  return (
    <div className="h-[560px] w-full bg-slate-950 rounded-xl border border-slate-800 relative overflow-hidden shadow-2xl">
      <div className="absolute top-3 left-3 z-10 flex items-center gap-2 bg-slate-900/80 backdrop-blur px-3 py-1.5 rounded-lg border border-slate-800 text-xs text-slate-300">
        <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
        <span>Virtual Digital Twin (React Flow &amp; NetworkX)</span>
      </div>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodeClick={(_, node) => onSelectNode(node.data)}
        fitView
      >
        <Background color="#1e293b" gap={18} size={1} />
        <Controls className="bg-slate-900 border-slate-800 text-slate-300 fill-slate-300" />
      </ReactFlow>
    </div>
  );
};
