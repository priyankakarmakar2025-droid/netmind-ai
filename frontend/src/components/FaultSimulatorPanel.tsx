import React, { useState } from 'react';
import { Play, RotateCcw, GitCompare, ShieldCheck, Zap } from 'lucide-react';
import { Scenario, StrategyComparison, api } from '../services/api';

interface Props {
  scenarios: Scenario[];
  onSimulationComplete: () => void;
}

export const FaultSimulatorPanel: React.FC<Props> = ({ scenarios, onSimulationComplete }) => {
  const [selectedScenario, setSelectedScenario] = useState<string>(scenarios[0]?.id || 'dns_failure');
  const [loading, setLoading] = useState(false);
  const [comparisons, setComparisons] = useState<StrategyComparison[]>([]);
  const [recommendation, setRecommendation] = useState<string>('');
  const [rationale, setRationale] = useState<string>('');
  const [message, setMessage] = useState<string>('');

  const handleInjectFault = async () => {
    setLoading(true);
    setMessage('');
    try {
      await api.runSimulation({ fault_type: selectedScenario, severity: 1.0 });
      setMessage(`Fault successfully simulated! Topology state and incident graph recalculated.`);
      onSimulationComplete();
      
      // Auto-fetch counterfactual comparison
      const compRes = await api.compareRecovery(selectedScenario);
      setComparisons(compRes.data.strategies);
      setRecommendation(compRes.data.recommended_strategy_id);
      setRationale(compRes.data.rationale);
    } catch (e: any) {
      setMessage(`Simulation error: ${e.response?.data?.detail || e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    setLoading(true);
    try {
      await api.resetNetwork();
      setComparisons([]);
      setRecommendation('');
      setRationale('');
      setMessage('Network restored to pristine 100% baseline.');
      onSimulationComplete();
    } catch (e: any) {
      setMessage(`Reset error: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
              <Zap className="w-5 h-5 text-amber-400" /> Fault Injection Laboratory
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Select and execute controlled network failure modes in the virtual digital twin.
            </p>
          </div>
          <button
            onClick={handleReset}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
          >
            <RotateCcw className="w-3.5 h-3.5" /> Restore Baseline
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Simulation Scenario</label>
            <select
              value={selectedScenario}
              onChange={(e) => setSelectedScenario(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
            >
              {scenarios.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={handleInjectFault}
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 text-xs font-semibold rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white transition shadow-lg shadow-cyan-950/50"
            >
              <Play className="w-4 h-4 fill-current" /> {loading ? 'Computing Simulation...' : 'Inject Fault Scenario'}
            </button>
          </div>
        </div>

        {message && (
          <div className="mt-3 text-xs px-3 py-2 rounded-lg bg-cyan-950/50 border border-cyan-800/60 text-cyan-200">
            {message}
          </div>
        )}
      </div>

      {comparisons.length > 0 && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
          <div className="flex items-center gap-2 mb-3">
            <GitCompare className="w-5 h-5 text-indigo-400" />
            <h3 className="text-base font-semibold text-slate-100">Counterfactual Recovery Strategy Comparison</h3>
          </div>
          <p className="text-xs text-slate-400 mb-4">
            Deterministic evaluations executed across isolated clones of the simulated network.
          </p>

          {rationale && (
            <div className="mb-4 p-3 rounded-lg bg-indigo-950/40 border border-indigo-800/60 flex items-start gap-2.5">
              <ShieldCheck className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
              <div>
                <span className="text-xs font-semibold text-indigo-200">System Recommendation: </span>
                <span className="text-xs text-indigo-300">{rationale}</span>
              </div>
            </div>
          )}

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border border-slate-800 rounded-lg">
              <thead className="bg-slate-950/80 text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-3 font-medium">Strategy</th>
                  <th className="py-2.5 px-3 font-medium">Availability Recovery</th>
                  <th className="py-2.5 px-3 font-medium">Est. Latency</th>
                  <th className="py-2.5 px-3 font-medium">Est. Recovery Time</th>
                  <th className="py-2.5 px-3 font-medium">Trade-offs &amp; Side Effects</th>
                  <th className="py-2.5 px-3 font-medium">Confidence Score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {comparisons.map((c) => {
                  const isRec = c.strategy_id === recommendation;
                  return (
                    <tr key={c.strategy_id} className={`hover:bg-slate-800/40 ${isRec ? 'bg-cyan-950/20' : ''}`}>
                      <td className="py-2.5 px-3 font-medium text-slate-200">
                        {c.name}
                        {isRec && (
                          <span className="ml-2 text-[10px] bg-cyan-900/60 text-cyan-300 border border-cyan-700/60 px-1.5 py-0.5 rounded">
                            Recommended
                          </span>
                        )}
                      </td>
                      <td className="py-2.5 px-3">
                        <span className="text-rose-400 font-mono">{c.availability_before}%</span>
                        <span className="mx-1 text-slate-500">→</span>
                        <span className="text-emerald-400 font-mono font-bold">{c.availability_after}%</span>
                      </td>
                      <td className="py-2.5 px-3 font-mono text-slate-300">{c.latency_ms}ms</td>
                      <td className="py-2.5 px-3 font-mono text-slate-300">{c.recovery_time_est_s}s</td>
                      <td className="py-2.5 px-3 text-slate-400 max-w-xs">{c.tradeoffs}</td>
                      <td className="py-2.5 px-3 font-mono text-cyan-400 font-semibold">{Math.round(c.score * 100)}%</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
