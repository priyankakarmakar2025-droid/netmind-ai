import axios from 'axios';

const API_BASE = '/api';

export interface NetworkNode {
  id: string;
  name: string;
  node_type: string;
  ip_address?: string;
  status: 'healthy' | 'degraded' | 'failed' | 'impacted';
  latency: number;
  packet_loss: number;
  active_fault?: string;
  pos_x: number;
  pos_y: number;
  details?: string;
}

export interface NetworkLink {
  id: string;
  source: string;
  target: string;
  status: 'up' | 'degraded' | 'down';
  latency: number;
  packet_loss: number;
  bandwidth_mbps: number;
  is_backup: boolean;
}

export interface TopologyData {
  nodes: NetworkNode[];
  links: NetworkLink[];
  network_health: string;
  availability_pct: number;
  avg_latency_ms: number;
  avg_packet_loss_pct: number;
}

export interface Scenario {
  id: string;
  name: string;
  description: string;
  target: string;
  category: string;
}

export interface IncidentEvidence {
  evidence_type: string;
  description: string;
  weight: number;
}

export interface Incident {
  id: string;
  title: string;
  category: string;
  severity: string;
  status: string;
  suspected_root_cause: string;
  confidence_score: number;
  affected_nodes: string[];
  affected_services: string[];
  recommended_recovery?: string;
  explanation?: string;
  created_at: string;
  evidences: IncidentEvidence[];
}

export interface StrategyComparison {
  strategy_id: string;
  name: string;
  description: string;
  availability_before: number;
  availability_after: number;
  latency_ms: number;
  packet_loss_pct: number;
  recovered_services: string[];
  remaining_impacts: string[];
  recovery_time_est_s: number;
  tradeoffs: string;
  score: number;
}

export interface AnomalyRecord {
  id: number;
  timestamp: string;
  metric_name: string;
  value: number;
  expected_range: string;
  anomaly_score: number;
  severity: string;
  description: string;
}

export const api = {
  getHealth: () => axios.get(`${API_BASE}/health`),
  getConfigStatus: () => axios.get(`${API_BASE}/config/status`),
  getTopology: () => axios.get<TopologyData>(`${API_BASE}/network/topology`),
  getNetworkStatus: () => axios.get(`${API_BASE}/network/status`),
  resetNetwork: () => axios.post<TopologyData>(`${API_BASE}/network/reset`),
  getScenarios: () => axios.get<Scenario[]>(`${API_BASE}/simulations/scenarios`),
  runSimulation: (data: { fault_type: string; target_node?: string; severity?: number; params?: Record<string, any> }) =>
    axios.post(`${API_BASE}/simulations/run`, data),
  compareRecovery: (scenario_id: string) =>
    axios.post<{ scenario_id: string; strategies: StrategyComparison[]; recommended_strategy_id: string; rationale: string }>(
      `${API_BASE}/simulations/compare?scenario_id=${scenario_id}`
    ),
  getLogs: () => axios.get(`${API_BASE}/logs`),
  uploadLogs: (formData: FormData) =>
    axios.post(`${API_BASE}/logs/upload`, formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  getIncidents: () => axios.get<Incident[]>(`${API_BASE}/incidents`),
  getIncidentById: (id: string) => axios.get<Incident>(`${API_BASE}/incidents/${id}`),
  submitFeedback: (id: string, data: { confirmed_root_cause: string; actual_recovery_taken?: string; feedback_notes?: string; status: string }) =>
    axios.post(`${API_BASE}/incidents/${id}/feedback`, data),
  getAnomalies: () => axios.get<AnomalyRecord[]>(`${API_BASE}/anomalies`),
  getMetricHistory: () => axios.get(`${API_BASE}/metrics/history`),
  explainIncident: (id: string) => axios.post(`${API_BASE}/assistant/explain?incident_id=${id}`),
  chatAssistant: (question: string, incident_id?: string) =>
    axios.post(`${API_BASE}/assistant/chat`, { question, incident_id })
};
