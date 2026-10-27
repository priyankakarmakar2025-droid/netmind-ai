import React, { useState } from 'react';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  LineChart, 
  Line 
} from 'recharts';
import { ShieldAlert, RefreshCw } from 'lucide-react';
import { AnomalyRecord, api } from '../services/api';

interface Props {
  anomalies: AnomalyRecord[];
  history: any[];
  onRefresh: () => void;
}

export const AnomalyDetectionView: React.FC<Props> = ({ anomalies, history, onRefresh }) => {
  const [loading, setLoading] = useState(false);

  const handleCheck = async () => {
    setLoading(true);
    try {
      await api.getAnomalies();
      onRefresh();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Latency History Chart */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-100">Telemetry Stream: Latency (ms)</h3>
              <p className="text-xs text-slate-400">Baseline expectation &lt; 10ms with statistical thresholding</p>
            </div>
            <button
              onClick={handleCheck}
              disabled={loading}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={history}>
                <defs>
                  <linearGradient id="latencyGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#020617', borderColor: '#334155', fontSize: '12px' }} />
                <Area type="monotone" dataKey="latency" stroke="#06b6d4" fillOpacity={1} fill="url(#latencyGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Packet Loss & Throughput Chart */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-slate-100">Packet Loss Rate (%)</h3>
              <p className="text-xs text-slate-400">Isolation Forest Contamination: 0.10</p>
            </div>
          </div>
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={history}>
                <XAxis dataKey="time" stroke="#64748b" fontSize={11} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#020617', borderColor: '#334155', fontSize: '12px' }} />
                <Line type="monotone" dataKey="packet_loss" stroke="#f43f5e" strokeWidth={2} dot={{ fill: '#f43f5e', r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Detected Anomalies Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
        <h3 className="text-sm font-semibold text-slate-100 mb-1 flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-rose-400" />
          Detected Statistical Anomalies ({anomalies.length})
        </h3>
        <p className="text-xs text-slate-400 mb-4">
          Unsupervised Isolation Forest alerts highlighting anomalous feature vectors across simulated network telemetry.
        </p>

        {anomalies.length === 0 ? (
          <div className="p-6 text-center text-xs text-slate-400 bg-slate-950 rounded-lg border border-slate-800">
            No active statistical anomalies detected. Telemetry streams conform to normal Gaussian baseline.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border border-slate-800 rounded-lg">
              <thead className="bg-slate-950/80 text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-3">Timestamp</th>
                  <th className="py-2.5 px-3">Metric</th>
                  <th className="py-2.5 px-3">Observed Value</th>
                  <th className="py-2.5 px-3">Expected Range</th>
                  <th className="py-2.5 px-3">Anomaly Score</th>
                  <th className="py-2.5 px-3">Severity</th>
                  <th className="py-2.5 px-3">Model Rationale</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {anomalies.map((an) => (
                  <tr key={an.id} className="hover:bg-slate-800/40">
                    <td className="py-2.5 px-3 font-mono text-slate-400">{new Date(an.timestamp).toLocaleTimeString()}</td>
                    <td className="py-2.5 px-3 font-semibold text-slate-200">{an.metric_name}</td>
                    <td className="py-2.5 px-3 font-mono text-rose-400 font-bold">{an.value}</td>
                    <td className="py-2.5 px-3 text-slate-400">{an.expected_range}</td>
                    <td className="py-2.5 px-3 font-mono text-cyan-400">{an.anomaly_score}</td>
                    <td className="py-2.5 px-3">
                      <span className="px-2 py-0.5 rounded text-[10px] bg-rose-950 text-rose-400 border border-rose-800">
                        {an.severity}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-slate-300 max-w-sm">{an.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
