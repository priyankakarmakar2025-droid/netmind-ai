import json
import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.models.db_models import (
    NetworkNodeModel, NetworkLinkModel, NetworkEventModel, IncidentModel,
    IncidentEvidenceModel, SimulationRunModel, AnomalyRecordModel, VerifiedFeedbackModel
)
from app.models.schemas import (
    TopologyResponse, FaultInjectionRequest, SimulationResult,
    RecoveryCompareResponse, StrategyComparisonResult, IncidentSchema,
    FeedbackRequest, ChatRequest, NetworkEventSchema, AnomalyRecordSchema
)
from app.services.network_engine import network_engine
from app.services.log_parser import log_parser
from app.services.rca_engine import rca_engine
from app.services.anomaly_detector import anomaly_service
from app.services.ai_assistant import ai_assistant
from app.services.incident_memory import incident_memory

router = APIRouter()

# ----------------- HEALTH & SYSTEM -----------------
@router.get("/health")
def get_health():
    return {"status": "ok", "app": settings.PROJECT_NAME, "version": settings.VERSION}

@router.get("/config/status")
def get_config_status():
    return {
        "project": settings.PROJECT_NAME,
        "database": "SQLite (Local Persistent)",
        "ai_assistant": ai_assistant.get_status(),
        "digital_twin_nodes": len(network_engine.current_nodes),
        "digital_twin_links": len(network_engine.current_links)
    }

# ----------------- NETWORK DIGITAL TWIN -----------------
@router.get("/network/topology", response_model=TopologyResponse)
def get_topology():
    return network_engine.get_current_topology()

@router.get("/network/status")
def get_network_status():
    avail, lat, loss = network_engine.calculate_metrics()
    nodes = network_engine.current_nodes
    return {
        "total_nodes": len(nodes),
        "healthy_nodes": sum(1 for n in nodes if n["status"] == "healthy"),
        "degraded_nodes": sum(1 for n in nodes if n["status"] == "degraded"),
        "failed_nodes": sum(1 for n in nodes if n["status"] in ["failed", "impacted"]),
        "availability_pct": avail,
        "avg_latency_ms": lat,
        "avg_packet_loss_pct": loss
    }

@router.get("/network/nodes/{node_id}")
def get_node_details(node_id: str):
    for node in network_engine.current_nodes:
        if node["id"] == node_id:
            # find connected links
            links = [l for l in network_engine.current_links if l["source"] == node_id or l["target"] == node_id]
            return {"node": node, "connected_links": links}
    raise HTTPException(status_code=404, detail="Node not found in virtual topology")

@router.post("/network/reset", response_model=TopologyResponse)
def reset_network(db: Session = Depends(get_db)):
    top = network_engine.reset_to_baseline()
    return top

# ----------------- FAULT SIMULATION & COUNTERFACTUAL -----------------
@router.get("/simulations/scenarios")
def get_scenarios():
    return [
        {
            "id": "dns_failure",
            "name": "1. Primary DNS Server Failure",
            "description": "Simulates BIND9 crash on 192.168.1.53. Downstream clients fail hostname lookups while IP routing remains intact.",
            "target": "dns-pri",
            "category": "DNS"
        },
        {
            "id": "dhcp_failure",
            "name": "2. DHCP Server Failure",
            "description": "Simulates DHCP daemon halt on 192.168.1.5. New clients cannot lease addresses; established clients retain valid leases.",
            "target": "dhcp-srv",
            "category": "DHCP"
        },
        {
            "id": "router_failure",
            "name": "3. Primary Router Failure (Blackhole)",
            "description": "Simulates complete loss of Edge Router Primary (192.168.1.1) without automatic failover enabled.",
            "target": "router-pri",
            "category": "ROUTING"
        },
        {
            "id": "router_backup",
            "name": "4. Router Failure with VRRP Failover",
            "description": "Simulates primary router failure with automatic dynamic switchover to Backup Router (192.168.1.254).",
            "target": "router-pri",
            "category": "ROUTING"
        },
        {
            "id": "link_congestion",
            "name": "5. Link Congestion & Packet Drop",
            "description": "Injects 65ms latency and 25% packet drop across router-to-web core transit link.",
            "target": "link-rpri-web",
            "category": "CONGESTION"
        },
        {
            "id": "web_failure",
            "name": "6. Web Server Crash (HTTP 502)",
            "description": "Simulates Nginx/Node.js worker process memory crash on 10.0.1.10.",
            "target": "web-srv",
            "category": "WEB"
        },
        {
            "id": "db_failure",
            "name": "7. Database Failure (Cascading Dependency)",
            "description": "Simulates PostgreSQL connection pool exhaustion on 10.0.2.20 causing cascading HTTP 500 in web tier.",
            "target": "db-srv",
            "category": "DATABASE_DEPENDENCY"
        },
        {
            "id": "firewall_block",
            "name": "8. Firewall Port Blocking (ACL Deny)",
            "description": "Injects an edge firewall ACL drop rule blocking inbound TCP Port 443.",
            "target": "web-srv",
            "category": "SECURITY_POLICY"
        }
    ]

@router.post("/simulations/run", response_model=SimulationResult)
def run_simulation(req: FaultInjectionRequest, db: Session = Depends(get_db)):
    result = network_engine.inject_fault(req)

    # Persist simulation run and generated events into DB
    sim_db = SimulationRunModel(
        id=f"SIM-{uuid.uuid4().hex[:6]}",
        scenario_id=result.scenario_id,
        scenario_name=result.scenario_name,
        fault_type=req.fault_type,
        target_node=req.target_node,
        target_link=req.target_link,
        parameters=json.dumps(req.params),
        results=json.dumps(result.model_dump())
    )
    db.add(sim_db)

    for ev in result.generated_events:
        db_ev = NetworkEventModel(
            id=ev["id"],
            source_ip=ev.get("source_ip"),
            event_type=ev["event_type"],
            severity=ev["severity"],
            message=ev["message"]
        )
        db.add(db_ev)

    # Automatically trigger RCA and create incident for dashboard tracking
    topology = network_engine.get_current_topology()
    incident = rca_engine.analyze(result.generated_events, topology)

    # Check for anomaly detection
    avail, lat, loss = network_engine.calculate_metrics()
    anomalies = anomaly_service.analyze_metrics({"latency": lat, "packet_loss": loss})
    for an in anomalies:
        db.add(AnomalyRecordModel(
            metric_name=an["metric_name"],
            value=an["value"],
            expected_range=an["expected_range"],
            anomaly_score=an["anomaly_score"],
            severity=an["severity"],
            description=an["description"]
        ))

    # Save incident
    inc_db = IncidentModel(
        id=incident.id,
        title=incident.title,
        category=incident.category,
        severity=incident.severity,
        status="active",
        suspected_root_cause=incident.suspected_root_cause,
        confidence_score=incident.confidence_score,
        affected_nodes=json.dumps(incident.affected_nodes),
        affected_services=json.dumps(incident.affected_services),
        recommended_recovery=incident.recommended_recovery,
        explanation=incident.explanation
    )
    db.add(inc_db)
    for ev_item in incident.evidences:
        db.add(IncidentEvidenceModel(
            incident_id=incident.id,
            evidence_type=ev_item.evidence_type,
            description=ev_item.description,
            weight=ev_item.weight
        ))

    db.commit()
    return result

@router.post("/simulations/compare", response_model=RecoveryCompareResponse)
def compare_recovery(scenario_id: str = Query(...)):
    strategies = network_engine.compare_strategies(scenario_id)
    best = strategies[0] if strategies else None
    return RecoveryCompareResponse(
        scenario_id=scenario_id,
        strategies=strategies,
        recommended_strategy_id=best.strategy_id if best else "none",
        rationale=f"Strategy '{best.name if best else 'N/A'}' achieves maximum availability with lowest recovery time and zero side-effects."
    )

# ----------------- LOGS & PARSING -----------------
@router.post("/logs/upload")
async def upload_logs(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith((".log", ".txt", ".csv", ".json", ".jsonl")):
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload .log, .txt, .csv, or .json")

    content_bytes = await file.read()
    content = content_bytes.decode("utf-8", errors="ignore")

    events, parsed, rejected, errors = log_parser.parse_content(file.filename, content)

    for ev in events:
        db_ev = NetworkEventModel(
            id=str(uuid.uuid4())[:8],
            source_ip=ev.get("source_ip"),
            dest_ip=ev.get("dest_ip"),
            protocol=ev.get("protocol", "TCP"),
            event_type=ev.get("event_type", "GENERAL"),
            severity=ev.get("severity", "INFO"),
            message=ev.get("message", ""),
            hostname=ev.get("hostname"),
            service_name=ev.get("service_name"),
            raw_line=ev.get("raw_line")
        )
        db.add(db_ev)
    db.commit()

    return {
        "filename": file.filename,
        "parsed_count": parsed,
        "rejected_count": rejected,
        "errors": errors[:5],
        "sample_parsed_events": events[:3]
    }

@router.get("/logs")
def get_logs(limit: int = 50, db: Session = Depends(get_db)):
    records = db.query(NetworkEventModel).order_by(NetworkEventModel.timestamp.desc()).limit(limit).all()
    return records

@router.get("/logs/sample")
def get_sample_logs():
    return {
        "sample_lines": [
            "[2026-10-27 14:02:11] [CRITICAL] [dns-pri] named[1042]: client @0x7f834c000c00 192.168.1.101#54122 (app.internal): query failed (SERVFAIL) for zone internal",
            "[2026-10-27 14:02:14] [ERROR] [client-1] curl: (6) Could not resolve host: app.internal; DNS query timed out after 3000ms",
            "[2026-10-27 14:02:22] [WARNING] [router-pri] kernel: GigabitEthernet0/1: carrier drop detected, interface transitioning to DOWN",
            "[2026-10-27 14:02:25] [CRITICAL] [db-srv] postgres[8819]: [3-1] FATAL: remaining connection slots are reserved for non-replication superuser connections"
        ]
    }

# ----------------- DIAGNOSIS & INCIDENTS -----------------
@router.post("/diagnosis/analyze", response_model=IncidentSchema)
def analyze_current_state(db: Session = Depends(get_db)):
    # Pull recent events
    recent_events = db.query(NetworkEventModel).order_by(NetworkEventModel.timestamp.desc()).limit(20).all()
    events_data = [{"event_type": e.event_type, "message": e.message} for e in recent_events]
    top = network_engine.get_current_topology()
    incident = rca_engine.analyze(events_data, top)
    return incident

@router.get("/incidents")
def get_incidents(db: Session = Depends(get_db)):
    incidents = db.query(IncidentModel).order_by(IncidentModel.created_at.desc()).all()
    result = []
    for inc in incidents:
        evs = db.query(IncidentEvidenceModel).filter(IncidentEvidenceModel.incident_id == inc.id).all()
        result.append({
            "id": inc.id,
            "title": inc.title,
            "category": inc.category,
            "severity": inc.severity,
            "status": inc.status,
            "suspected_root_cause": inc.suspected_root_cause,
            "confidence_score": inc.confidence_score,
            "affected_nodes": json.loads(inc.affected_nodes),
            "affected_services": json.loads(inc.affected_services),
            "recommended_recovery": inc.recommended_recovery,
            "explanation": inc.explanation,
            "created_at": inc.created_at.isoformat(),
            "evidences": [{"evidence_type": e.evidence_type, "description": e.description, "weight": e.weight} for e in evs]
        })
    return result

@router.get("/incidents/{incident_id}")
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    inc = db.query(IncidentModel).filter(IncidentModel.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    evs = db.query(IncidentEvidenceModel).filter(IncidentEvidenceModel.incident_id == inc.id).all()
    return {
        "id": inc.id,
        "title": inc.title,
        "category": inc.category,
        "severity": inc.severity,
        "status": inc.status,
        "suspected_root_cause": inc.suspected_root_cause,
        "confidence_score": inc.confidence_score,
        "affected_nodes": json.loads(inc.affected_nodes),
        "affected_services": json.loads(inc.affected_services),
        "recommended_recovery": inc.recommended_recovery,
        "explanation": inc.explanation,
        "created_at": inc.created_at.isoformat(),
        "evidences": [{"evidence_type": e.evidence_type, "description": e.description, "weight": e.weight} for e in evs]
    }

@router.post("/incidents/{incident_id}/feedback")
def submit_feedback(incident_id: str, req: FeedbackRequest, db: Session = Depends(get_db)):
    inc = db.query(IncidentModel).filter(IncidentModel.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    inc.status = req.status
    fb = VerifiedFeedbackModel(
        incident_id=incident_id,
        confirmed_root_cause=req.confirmed_root_cause,
        actual_recovery_taken=req.actual_recovery_taken,
        feedback_notes=req.feedback_notes,
        status=req.status
    )
    db.add(fb)
    db.commit()
    return {"message": "Feedback saved successfully. Outcome recorded into historical memory."}

# ----------------- AI ASSISTANT -----------------
@router.post("/assistant/explain")
def assistant_explain(incident_id: str, db: Session = Depends(get_db)):
    inc = db.query(IncidentModel).filter(IncidentModel.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    inc_data = {
        "id": inc.id,
        "title": inc.title,
        "category": inc.category,
        "suspected_root_cause": inc.suspected_root_cause,
        "affected_nodes": json.loads(inc.affected_nodes),
        "recommended_recovery": inc.recommended_recovery
    }
    return ai_assistant.explain_incident(inc_data)

@router.post("/assistant/chat")
def assistant_chat(req: ChatRequest, db: Session = Depends(get_db)):
    inc_data = None
    if req.incident_id:
        inc = db.query(IncidentModel).filter(IncidentModel.id == req.incident_id).first()
        if inc:
            inc_data = {
                "id": inc.id,
                "title": inc.title,
                "category": inc.category,
                "suspected_root_cause": inc.suspected_root_cause,
                "affected_nodes": json.loads(inc.affected_nodes),
                "recommended_recovery": inc.recommended_recovery
            }
    ans = ai_assistant.answer_chat(req.question, inc_data)
    return {"answer": ans, "provider": ai_assistant.provider}

# ----------------- ANOMALY DETECTION -----------------
@router.get("/anomalies")
def get_anomalies(db: Session = Depends(get_db)):
    return db.query(AnomalyRecordModel).order_by(AnomalyRecordModel.timestamp.desc()).limit(30).all()

@router.post("/anomalies/analyze")
def trigger_anomaly_check(db: Session = Depends(get_db)):
    avail, lat, loss = network_engine.calculate_metrics()
    anomalies = anomaly_service.analyze_metrics({"latency": lat, "packet_loss": loss})
    for an in anomalies:
        db.add(AnomalyRecordModel(
            metric_name=an["metric_name"],
            value=an["value"],
            expected_range=an["expected_range"],
            anomaly_score=an["anomaly_score"],
            severity=an["severity"],
            description=an["description"]
        ))
    db.commit()
    return {"anomalies_detected": anomalies}

@router.get("/metrics/history")
def get_metrics_history():
    return anomaly_service.generate_metric_history(points=24)

# ----------------- RECOVERY & SIMILAR INCIDENTS -----------------
@router.get("/recovery/strategies")
def get_all_recovery_strategies():
    return [
        {"id": "switch_secondary_dns", "name": "Failover to Secondary DNS (192.168.1.54)"},
        {"id": "activate_vrrp_backup", "name": "Activate VRRP Backup Router (192.168.1.254)"},
        {"id": "scale_db_connection_pool", "name": "Increase PostgreSQL Connection Limits & PgBouncer"},
        {"id": "revoke_blocking_acl_rule", "name": "Revoke Blocking Firewall Rule #412"},
        {"id": "reroute_via_fiber_link", "name": "Reroute Traffic via Redundant High-Capacity Link"}
    ]

@router.get("/history/similar")
def get_similar_history(category: str = "DNS", root_cause: str = "", db: Session = Depends(get_db)):
    return incident_memory.get_similar_incidents(category, root_cause, db)
