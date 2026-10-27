from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base

class NetworkNodeModel(Base):
    __tablename__ = "network_nodes"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    node_type = Column(String, nullable=False)  # client, switch, router, dns, dhcp, web, db
    ip_address = Column(String, nullable=True)
    status = Column(String, default="healthy")  # healthy, degraded, failed, impacted
    latency = Column(Float, default=1.0)
    packet_loss = Column(Float, default=0.0)
    active_fault = Column(String, nullable=True)
    pos_x = Column(Float, default=0.0)
    pos_y = Column(Float, default=0.0)
    details = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class NetworkLinkModel(Base):
    __tablename__ = "network_links"

    id = Column(String, primary_key=True, index=True)
    source = Column(String, ForeignKey("network_nodes.id"), nullable=False)
    target = Column(String, ForeignKey("network_nodes.id"), nullable=False)
    status = Column(String, default="up")  # up, degraded, down
    latency = Column(Float, default=2.0)
    packet_loss = Column(Float, default=0.0)
    bandwidth_mbps = Column(Float, default=1000.0)
    is_backup = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow)

class NetworkEventModel(Base):
    __tablename__ = "network_events"

    id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    source_ip = Column(String, nullable=True)
    dest_ip = Column(String, nullable=True)
    protocol = Column(String, default="TCP")
    event_type = Column(String, nullable=False)
    severity = Column(String, default="INFO")  # INFO, WARNING, ERROR, CRITICAL
    message = Column(Text, nullable=False)
    hostname = Column(String, nullable=True)
    service_name = Column(String, nullable=True)
    raw_line = Column(Text, nullable=True)

class IncidentModel(Base):
    __tablename__ = "incidents"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)
    severity = Column(String, default="WARNING")
    status = Column(String, default="active")  # active, resolved, confirmed, rejected
    suspected_root_cause = Column(Text, nullable=False)
    confidence_score = Column(Float, default=0.85)
    affected_nodes = Column(Text, default="[]")  # JSON encoded list
    affected_services = Column(Text, default="[]")  # JSON encoded list
    recommended_recovery = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)
    is_ai_generated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    evidences = relationship("IncidentEvidenceModel", back_populates="incident", cascade="all, delete-orphan")
    feedbacks = relationship("VerifiedFeedbackModel", back_populates="incident", cascade="all, delete-orphan")

class IncidentEvidenceModel(Base):
    __tablename__ = "incident_evidences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    incident_id = Column(String, ForeignKey("incidents.id"), nullable=False)
    event_id = Column(String, nullable=True)
    evidence_type = Column(String, nullable=False)  # log, topology, metric, anomaly
    description = Column(Text, nullable=False)
    weight = Column(Float, default=1.0)

    incident = relationship("IncidentModel", back_populates="evidences")

class SimulationRunModel(Base):
    __tablename__ = "simulation_runs"

    id = Column(String, primary_key=True, index=True)
    scenario_id = Column(String, nullable=False)
    scenario_name = Column(String, nullable=False)
    fault_type = Column(String, nullable=False)
    target_node = Column(String, nullable=True)
    target_link = Column(String, nullable=True)
    parameters = Column(Text, default="{}")
    results = Column(Text, default="{}")  # JSON result
    created_at = Column(DateTime, default=datetime.utcnow)

class AnomalyRecordModel(Base):
    __tablename__ = "anomaly_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metric_name = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    expected_range = Column(String, nullable=True)
    anomaly_score = Column(Float, default=0.0)
    severity = Column(String, default="WARNING")
    description = Column(Text, nullable=False)

class VerifiedFeedbackModel(Base):
    __tablename__ = "verified_feedbacks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    incident_id = Column(String, ForeignKey("incidents.id"), nullable=False)
    confirmed_root_cause = Column(String, nullable=False)
    actual_recovery_taken = Column(String, nullable=True)
    feedback_notes = Column(Text, nullable=True)
    status = Column(String, default="confirmed")  # confirmed, rejected
    timestamp = Column(DateTime, default=datetime.utcnow)

    incident = relationship("IncidentModel", back_populates="feedbacks")
