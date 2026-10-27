import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Network, 
  Zap, 
  FileSearch, 
  ShieldAlert, 
  History, 
  Settings, 
  Upload, 
  RotateCcw,
  CheckCircle,
  AlertTriangle,
  XCircle,
  ArrowUpRight,
  Server
} from 'lucide-react';
import { api, TopologyData, Scenario, Incident, AnomalyRecord, NetworkNode } from './services/api';
import { NetworkGraphView } from './components/NetworkGraphView';
import { FaultSimulatorPanel } from './components/FaultSimulatorPanel';
import { RootCauseAnalysisView } from './components/RootCauseAnalysisView';
import { AnomalyDetectionView } from './components/AnomalyDetectionView';
import { LogIngestionView } from './components/LogIngestionView';
import { IncidentHistoryView } from './components/IncidentHistoryView';

export function App() {
  const [activeTab, setActiveTab] = useState<'overview' | 'live' | 'simulator' | 'rca' | 'anomalies' | 'logs' | 'history' | 'settings'>('overview');
  const [topology, setTopology] = useState<TopologyData | null>(null);
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [anomalies, setAnomalies] = useState<AnomalyRecord[]>([]);
  const [metricHistory, setMetricHistory] = useState<any[]>([]);
  const [selectedNode, setSelectedNode] = useState<NetworkNode | null>(null);
  const [configStatus, setConfigStatus] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchData = async () => {
    try {
      const [topRes, scenRes, incRes, anomRes, histRes, cfgRes] = await Promise.all([
        api.getTopology(),
        api.getScenarios(),
        api.getIncidents(),
        api.getAnomalies(),
        api.getMetricHistory(),
        api.getConfigStatus()
      ]);
      setTopology(topRes.data);
      setScenarios(scenRes.data);
      setIncidents(incRes.data);
      setAnomalies(anomRes.data);
      setMetricHistory(histRes.data);
      setConfigStatus(cfgRes.data);
    } catch (e) {
      console.error('Error fetching data:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(() => {
      api.getTopology().then(res => setTopology(res.data)).catch(() => {});
    }, 6000);
    return () => clearInterval(interval);
  }, []);

  const totalNodes = topology?.nodes.length || 0;
  const healthyCount = topology?.nodes.filter(n => n.status === 'healthy').length || 0;
  const degradedCount = topology?.nodes.filter(n => n.status === 'degraded').length || 0;
  const failedCount = topology?.nodes.filter(n => n.status === 'failed' || n.status === 'impacted').length || 0;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Top Navigation Bar */}
      <header className="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-md sticky top-0 z-50 px-6 py-3.5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-900/40">
            <Activity className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-base tracking-wide bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-300 bg-clip-text text-transparent">
                NetMind AI
              </span>
              <span className="text-[10px] bg-cyan-950 text-cyan-400 border border-cyan-800/60 px-2 py-0.5 rounded-full font-mono">
                Digital Twin NOC v1.0
              </span>
            </div>
            <p className="text-[11px] text-slate-400">Autonomous Fault Diagnosis &amp; Counterfactual Recovery Lab</p>
          </div>
        </div>

        {/* Global Quick Metrics */}
        <div className="hidden lg:flex items-center gap-4 text-xs font-mono">
          <div className="bg-slate-950 px-3 py-1.5 rounded-lg border border-slate-800 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-slate-400">Availability:</span>
            <span className="font-bold text-emerald-400">{topology?.availability_pct || 100}%</span>
          </div>
          <div className="bg-slate-950 px-3 py-1.5 rounded-lg border border-slate-800 flex items-center gap-2">
            <span className="text-slate-400">Avg RTT:</span>
            <span className="text-cyan-400 font-bold">{topology?.avg_latency_ms || 1.8}ms</span>
          </div>
          <div className="bg-slate-950 px-3 py-1.5 rounded-lg border border-slate-800 flex items-center gap-2">
            <span className="text-slate-400">Drop Rate:</span>
            <span className={`font-bold ${(topology?.avg_packet_loss_pct || 0) > 0 ? 'text-rose-400' : 'text-slate-200'}`}>
              {topology?.avg_packet_loss_pct || 0}%
            </span>
          </div>
        </div>

        {/* Quick Reset Action */}
        <button
          onClick={async () => {
            await api.resetNetwork();
            await fetchData();
          }}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
        >
          <RotateCcw className="w-3.5 h-3.5" /> Reset Topology
        </button>
      </header>

      {/* Main Navigation Tabs */}
      <nav className="border-b border-slate-800/80 bg-slate-900/30 px-6 flex items-center gap-1 overflow-x-auto">
        {[
          { id: 'overview', label: 'Command Overview', icon: Activity },
          { id: 'live', label: 'Live Digital Twin', icon: Network },
          { id: 'simulator', label: 'Fault Simulator & What-If', icon: Zap },
          { id: 'rca', label: 'Root-Cause Analysis', icon: FileSearch },
          { id: 'anomalies', label: 'Anomaly Detection', icon: ShieldAlert },
          { id: 'logs', label: 'Log Ingestion', icon: Upload },
          { id: 'history', label: 'Incident History', icon: History },
          { id: 'settings', label: 'System Settings', icon: Settings },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-3 text-xs font-medium border-b-2 transition whitespace-nowrap ${
                isActive
                  ? 'border-cyan-400 text-cyan-400 bg-cyan-950/20'
                  : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/20'
              }`}
            >
              <Icon className="w-4 h-4" /> {tab.label}
            </button>
          );
        })}
      </nav>

      {/* Main Content Area */}
      <main className="flex-1 p-6 max-w-7xl w-full mx-auto space-y-6">
        {loading ? (
          <div className="h-64 flex items-center justify-center text-slate-400 text-sm animate-pulse">
            Loading NetMind Virtual Environment...
          </div>
        ) : (
          <>
            {/* OVERVIEW TAB */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {/* Metric Summary Cards */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl shadow-lg">
                    <span className="text-xs text-slate-400 block mb-1">Total Network Nodes</span>
                    <div className="flex items-baseline justify-between">
                      <span className="text-2xl font-bold font-mono text-slate-100">{totalNodes}</span>
                      <Server className="w-4 h-4 text-cyan-400" />
                    </div>
                    <span className="text-[10px] text-slate-500 mt-2 block">11 hosts, routers, switches &amp; daemons</span>
                  </div>

                  <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl shadow-lg">
                    <span className="text-xs text-slate-400 block mb-1">Healthy Nodes</span>
                    <div className="flex items-baseline justify-between">
                      <span className="text-2xl font-bold font-mono text-emerald-400">{healthyCount}</span>
                      <CheckCircle className="w-4 h-4 text-emerald-400" />
                    </div>
                    <span className="text-[10px] text-emerald-500/80 mt-2 block">Normal operating baseline</span>
                  </div>

                  <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl shadow-lg">
                    <span className="text-xs text-slate-400 block mb-1">Degraded / Jitter Nodes</span>
                    <div className="flex items-baseline justify-between">
                      <span className="text-2xl font-bold font-mono text-amber-400">{degradedCount}</span>
                      <AlertTriangle className="w-4 h-4 text-amber-400" />
                    </div>
                    <span className="text-[10px] text-amber-500/80 mt-2 block">Elevated latency or drop</span>
                  </div>

                  <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl shadow-lg">
                    <span className="text-xs text-slate-400 block mb-1">Failed / Impacted Nodes</span>
                    <div className="flex items-baseline justify-between">
                      <span className="text-2xl font-bold font-mono text-rose-400">{failedCount}</span>
                      <XCircle className="w-4 h-4 text-rose-400" />
                    </div>
                    <span className="text-[10px] text-rose-500/80 mt-2 block">Requires recovery failover</span>
                  </div>
                </div>

                {/* Digital Twin Snapshot */}
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-sm font-semibold text-slate-100">Interactive Digital Twin Canvas</h3>
                    <button
                      onClick={() => setActiveTab('live')}
                      className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-medium"
                    >
                      Expand View <ArrowUpRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  <NetworkGraphView topology={topology} onSelectNode={(node) => setSelectedNode(node)} />
                </div>
              </div>
            )}

            {/* LIVE DIGITAL TWIN TAB */}
            {activeTab === 'live' && (
              <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                <div className="lg:col-span-3">
                  <NetworkGraphView topology={topology} onSelectNode={(node) => setSelectedNode(node)} />
                </div>

                {/* Node Details Inspector */}
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
                  <h3 className="text-sm font-semibold text-slate-100 mb-3 border-b border-slate-800 pb-2">
                    Node Telemetry Inspector
                  </h3>
                  {selectedNode ? (
                    <div className="space-y-3 text-xs">
                      <div>
                        <span className="text-slate-400 block">Node ID:</span>
                        <span className="font-mono text-cyan-400 font-semibold">{selectedNode.id}</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block">Display Name:</span>
                        <span className="text-slate-100 font-medium">{selectedNode.name}</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block">IP Address:</span>
                        <span className="font-mono text-slate-200">{selectedNode.ip_address || 'Layer 2 Device'}</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block">Role / Type:</span>
                        <span className="capitalize text-slate-200">{selectedNode.node_type}</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block">Health Status:</span>
                        <span className="capitalize font-semibold text-emerald-400">{selectedNode.status}</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block">Round-Trip Latency:</span>
                        <span className="font-mono text-slate-200">{selectedNode.latency} ms</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block">Packet Loss Rate:</span>
                        <span className="font-mono text-rose-400">{selectedNode.packet_loss} %</span>
                      </div>
                      {selectedNode.active_fault && (
                        <div className="p-2.5 rounded bg-rose-950/60 border border-rose-800 text-rose-300">
                          <span className="font-semibold block mb-0.5">Active Injected Fault:</span>
                          {selectedNode.active_fault}
                        </div>
                      )}
                      <div>
                        <span className="text-slate-400 block">Specifications:</span>
                        <p className="text-slate-400 mt-1 leading-relaxed">{selectedNode.details}</p>
                      </div>
                    </div>
                  ) : (
                    <div className="py-12 text-center text-xs text-slate-500">
                      Click any node on the digital twin canvas to inspect runtime telemetry, packet drop, and link statistics.
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* FAULT SIMULATOR TAB */}
            {activeTab === 'simulator' && (
              <FaultSimulatorPanel
                scenarios={scenarios}
                onSimulationComplete={async () => {
                  await fetchData();
                }}
              />
            )}

            {/* ROOT CAUSE ANALYSIS TAB */}
            {activeTab === 'rca' && (
              <RootCauseAnalysisView
                incidents={incidents}
                onRefresh={async () => {
                  await fetchData();
                }}
              />
            )}

            {/* ANOMALY DETECTION TAB */}
            {activeTab === 'anomalies' && (
              <AnomalyDetectionView
                anomalies={anomalies}
                history={metricHistory}
                onRefresh={async () => {
                  await fetchData();
                }}
              />
            )}

            {/* LOG INGESTION TAB */}
            {activeTab === 'logs' && (
              <LogIngestionView
                onUploadSuccess={async () => {
                  await fetchData();
                  setActiveTab('rca');
                }}
              />
            )}

            {/* INCIDENT HISTORY TAB */}
            {activeTab === 'history' && (
              <IncidentHistoryView
                incidents={incidents}
                onSelectIncident={() => setActiveTab('rca')}
              />
            )}

            {/* SETTINGS TAB */}
            {activeTab === 'settings' && (
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-6 max-w-2xl">
                <div>
                  <h3 className="text-base font-semibold text-slate-100 flex items-center gap-2">
                    <Settings className="w-5 h-5 text-cyan-400" /> System &amp; AI Provider Configuration
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Telemetry, AI adapters, and persistent database runtime status.
                  </p>
                </div>

                <div className="space-y-3 text-xs">
                  <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 flex justify-between">
                    <span className="text-slate-400">Database Engine</span>
                    <span className="text-slate-200 font-mono">SQLite (Local Persistent)</span>
                  </div>
                  <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 flex justify-between">
                    <span className="text-slate-400">AI Diagnostic Mode</span>
                    <span className="text-cyan-400 font-mono">
                      {configStatus?.ai_assistant?.mode || 'Deterministic Local Fallback Engine'}
                    </span>
                  </div>
                  <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 flex justify-between">
                    <span className="text-slate-400">LLM Provider</span>
                    <span className="text-slate-200 font-mono">
                      {configStatus?.ai_assistant?.provider || 'local_deterministic'}
                    </span>
                  </div>
                  <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 flex justify-between">
                    <span className="text-slate-400">Virtual Network Graph Model</span>
                    <span className="text-slate-200 font-mono">NetworkX 3.6.1 + React Flow</span>
                  </div>
                </div>

                <div className="p-4 rounded-lg bg-cyan-950/30 border border-cyan-800/60 text-xs text-cyan-300">
                  NetMind AI runs completely offline and deterministically without requiring third-party API keys. 
                  Optional Gemini API keys can be passed via the `GEMINI_API_KEY` environment variable.
                </div>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}

export default App;
