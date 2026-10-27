import React from 'react';
import { Handle, Position } from 'reactflow';
import { 
  Laptop, 
  Server, 
  Router, 
  Database, 
  Globe, 
  Network, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  Clock 
} from 'lucide-react';
import { NetworkNode } from '../services/api';

const getNodeIcon = (type: string) => {
  switch (type) {
    case 'client':
      return <Laptop className="w-5 h-5 text-sky-400" />;
    case 'switch':
      return <Network className="w-5 h-5 text-indigo-400" />;
    case 'router':
      return <Router className="w-5 h-5 text-emerald-400" />;
    case 'dns':
      return <Server className="w-5 h-5 text-purple-400" />;
    case 'dhcp':
      return <Clock className="w-5 h-5 text-amber-400" />;
    case 'web':
      return <Globe className="w-5 h-5 text-blue-400" />;
    case 'db':
      return <Database className="w-5 h-5 text-rose-400" />;
    default:
      return <Server className="w-5 h-5 text-slate-400" />;
  }
};

const getStatusBadge = (status: string) => {
  switch (status) {
    case 'healthy':
      return (
        <span className="flex items-center gap-1 text-[10px] bg-emerald-950/80 text-emerald-400 border border-emerald-800/60 px-1.5 py-0.5 rounded-full font-medium">
          <CheckCircle className="w-3 h-3" /> ONLINE
        </span>
      );
    case 'degraded':
      return (
        <span className="flex items-center gap-1 text-[10px] bg-amber-950/80 text-amber-400 border border-amber-800/60 px-1.5 py-0.5 rounded-full font-medium">
          <AlertTriangle className="w-3 h-3" /> DEGRADED
        </span>
      );
    case 'failed':
      return (
        <span className="flex items-center gap-1 text-[10px] bg-rose-950/80 text-rose-400 border border-rose-800/60 px-1.5 py-0.5 rounded-full font-medium animate-pulse">
          <XCircle className="w-3 h-3" /> DOWN
        </span>
      );
    case 'impacted':
      return (
        <span className="flex items-center gap-1 text-[10px] bg-purple-950/80 text-purple-400 border border-purple-800/60 px-1.5 py-0.5 rounded-full font-medium">
          <AlertTriangle className="w-3 h-3" /> IMPACTED
        </span>
      );
    default:
      return null;
  }
};

export const CustomNodeComponent: React.FC<{ data: NetworkNode }> = ({ data }) => {
  const isFailed = data.status === 'failed';
  const isDegraded = data.status === 'degraded';
  const isImpacted = data.status === 'impacted';

  return (
    <div 
      className={`px-3.5 py-2.5 rounded-xl border backdrop-blur-md transition-all duration-200 min-w-[190px] shadow-lg ${
        isFailed 
          ? 'bg-rose-950/40 border-rose-600 shadow-rose-950/50 ring-1 ring-rose-500' 
          : isDegraded 
          ? 'bg-amber-950/30 border-amber-500 shadow-amber-950/50' 
          : isImpacted
          ? 'bg-purple-950/30 border-purple-500'
          : 'bg-slate-900/90 border-slate-800 hover:border-slate-700 shadow-slate-950/50'
      }`}
    >
      <Handle type="target" position={Position.Left} className="w-2.5 h-2.5 bg-slate-500 border-2 border-slate-900" />

      <div className="flex items-center justify-between gap-2 mb-1.5">
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-slate-800/80 rounded-lg border border-slate-700/50">
            {getNodeIcon(data.node_type)}
          </div>
          <div>
            <div className="text-xs font-semibold text-slate-100 leading-tight">{data.name}</div>
            <div className="text-[10px] text-slate-400 font-mono">{data.ip_address || 'L2 Switch'}</div>
          </div>
        </div>
        {getStatusBadge(data.status)}
      </div>

      <div className="mt-2 pt-2 border-t border-slate-800/80 grid grid-cols-2 gap-1 text-[10px] text-slate-400">
        <div>RTT: <span className="text-slate-200 font-mono">{data.latency}ms</span></div>
        <div>Loss: <span className={`font-mono ${data.packet_loss > 0 ? 'text-rose-400' : 'text-slate-200'}`}>{data.packet_loss}%</span></div>
      </div>

      {data.active_fault && (
        <div className="mt-1.5 text-[10px] text-rose-300 bg-rose-950/60 border border-rose-800/40 px-1.5 py-0.5 rounded truncate">
          {data.active_fault}
        </div>
      )}

      <Handle type="source" position={Position.Right} className="w-2.5 h-2.5 bg-slate-500 border-2 border-slate-900" />
    </div>
  );
};
