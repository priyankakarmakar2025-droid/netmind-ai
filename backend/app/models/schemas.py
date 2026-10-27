from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class NodeBase(BaseModel):
    id: str
    name: str
    node_type: str
    ip_address: Optional[str] = None
    status: str = "healthy"
    latency: float = 1.0
    packet_loss: float = 0.0
    active_fault: Optional[str] = None
    pos_x: float = 0.0
    pos_y: float = 0.0
    details: Optional[str] = None

class LinkBase(BaseModel):
    id: str
    source: str
    target: str
    status: str = "up"
    latency: float = 2.0
    packet_loss: float = 0.0
    bandwidth_mbps: float = 1000.0
    is_backup: bool = False

class TopologyResponse(BaseModel):
    nodes: List[NodeBase]
    links: List[LinkBase]
    network_health: str
    availability_pct: float
    avg_latency_ms: float
    avg_packet_loss_pct: float

class NetworkEventSchema(BaseModel):
    id: str
    timestamp: datetime
    source_ip: Optional[str] = None
    dest_ip: Optional[str] = None
    protocol: str = "TCP"
    event_type: str
    severity: str
    message: str
    hostname: Optional[str] = None
    service_name: Optional[str] = None
    raw_line: Optional[str] = None

class FaultInjectionRequest(BaseModel):
    fault_type: str  # dns_failure, dhcp_failure, router_failure, router_backup, link_latency, link_loss, web_failure, db_failure, firewall_block, link_congestion
    target_node: Optional[str] = None
    target_link: Optional[str] = None
    severity: float = 1.0
    params: Dict[str, Any] = Field(default_factory=dict)

class SimulationResult(BaseModel):
    scenario_id: str
    scenario_name: str
    initial_availability: float
    simulated_availability: float
    affected_nodes: List[str]
    affected_services: List[str]
    average_latency: float
    average_packet_loss: float
    generated_events: List[Dict[str, Any]]
    candidate_root_causes: List[str]
    recovery_strategies_available: List[str]

class RecoveryStrategyRequest(BaseModel):
    scenario_id: str
    strategy_id: str

class StrategyComparisonResult(BaseModel):
    strategy_id: str
    name: str
    description: str
    availability_before: float
    availability_after: float
    latency_ms: float
    packet_loss_pct: float
    recovered_services: List[str]
    remaining_impacts: List[str]
    recovery_time_est_s: int
    tradeoffs: str
    score: float

class RecoveryCompareResponse(BaseModel):
    incident_id: Optional[str] = None
    scenario_id: str
    strategies: List[StrategyComparisonResult]
    recommended_strategy_id: str
    rationale: str

class IncidentEvidenceSchema(BaseModel):
    id: Optional[int] = None
    evidence_type: str
    description: str
    weight: float = 1.0
    event_id: Optional[str] = None

class IncidentSchema(BaseModel):
    id: str
    title: str
    category: str
    severity: str
    status: str
    suspected_root_cause: str
    confidence_score: float
    affected_nodes: List[str]
    affected_services: List[str]
    recommended_recovery: Optional[str] = None
    explanation: Optional[str] = None
    is_ai_generated: bool = False
    created_at: datetime
    evidences: List[IncidentEvidenceSchema] = []

class AnomalyRecordSchema(BaseModel):
    id: int
    timestamp: datetime
    metric_name: str
    value: float
    expected_range: Optional[str] = None
    anomaly_score: float
    severity: str
    description: str

class FeedbackRequest(BaseModel):
    confirmed_root_cause: str
    actual_recovery_taken: Optional[str] = None
    feedback_notes: Optional[str] = None
    status: str = "confirmed"

class ChatRequest(BaseModel):
    incident_id: Optional[str] = None
    question: str
