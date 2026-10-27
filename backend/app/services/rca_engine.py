import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models.schemas import IncidentSchema, IncidentEvidenceSchema

class RootCauseAnalysisEngine:
    def analyze(self, events: List[Dict[str, Any]], current_topology: Dict[str, Any]) -> IncidentSchema:
        """Rule-based, deterministic RCA engine adhering to network engineering logic."""
        incident_id = f"INC-{uuid.uuid4().hex[:6].upper()}"
        evidences = []

        # Analyze events
        event_types = [e.get("event_type") for e in events]
        messages = [e.get("message", "") for e in events]
        full_text = " ".join(messages).lower()

        nodes = current_topology.get("nodes", [])
        failed_nodes = [n["id"] for n in nodes if n.get("status") in ["failed", "degraded"]]

        # 1. DNS Failure Rule
        if "DNS_LOOKUP_FAILURE" in event_types or "DNS_TIMEOUT" in event_types or "dns" in full_text:
            dns_pri_failed = any(n["id"] == "dns-pri" and n.get("status") == "failed" for n in nodes)
            evidences.append(IncidentEvidenceSchema(
                evidence_type="log",
                description="Repeated DNS resolution timeouts or NXDOMAIN response packets received.",
                weight=1.0
            ))
            if dns_pri_failed:
                evidences.append(IncidentEvidenceSchema(
                    evidence_type="topology",
                    description="Primary DNS Node (192.168.1.53) reports status: FAILED.",
                    weight=1.2
                ))
            
            return IncidentSchema(
                id=incident_id,
                title="Authoritative DNS Resolution Outage",
                category="DNS",
                severity="CRITICAL" if dns_pri_failed else "WARNING",
                status="active",
                suspected_root_cause="Primary DNS Server (BIND9) socket failure or unresponsive port 53 daemon.",
                confidence_score=0.94 if dns_pri_failed else 0.82,
                affected_nodes=["dns-pri", "client-1", "client-2", "client-3"],
                affected_services=["DNS Resolution (FQDN)", "Web Portal Hostname Mapping"],
                recommended_recovery="Trigger automatic DNS failover to Secondary Resolver (192.168.1.54) and restart BIND9 service.",
                explanation="Log correlation identifies recurring DNS client timeouts. Gateway and client-to-switch links remain fully functional, isolating the failure strictly to port 53 response generation on the primary DNS server.",
                is_ai_generated=False,
                created_at=datetime.utcnow(),
                evidences=evidences
            )

        # 2. Database Dependency Failure Rule
        if "DB_DEPENDENCY_FAILURE" in event_types or "DB_CONNECTION_FAIL" in event_types or "postgres" in full_text:
            evidences.append(IncidentEvidenceSchema(
                evidence_type="log",
                description="Database connection exhaustion or deadlock event logged on 10.0.2.20:5432.",
                weight=1.0
            ))
            evidences.append(IncidentEvidenceSchema(
                evidence_type="topology",
                description="Web server tier (10.0.1.10) reports downstream 500/502 errors due to backend database pool starvation.",
                weight=1.1
            ))
            return IncidentSchema(
                id=incident_id,
                title="Database Connection Pool Saturation & Web Tier Stall",
                category="DATABASE_DEPENDENCY",
                severity="CRITICAL",
                status="active",
                suspected_root_cause="PostgreSQL maximum client connections exceeded causing cascading HTTP 500 errors in web layer.",
                confidence_score=0.96,
                affected_nodes=["db-srv", "web-srv"],
                affected_services=["PostgreSQL Database", "Customer Web Application"],
                recommended_recovery="Scale connection pool pooler (PgBouncer), terminate idle backend queries, or failover to read replica.",
                explanation="While web-srv is reporting errors, network graph inspection shows switch-to-web route is healthy. The true root cause originates at db-srv connection limits.",
                is_ai_generated=False,
                created_at=datetime.utcnow(),
                evidences=evidences
            )

        # 3. Router Failure / Routing Error Rule
        if "ROUTING_ERROR" in event_types or "ROUTING_UNREACHABLE" in event_types or "LINK_DOWN" in event_types:
            evidences.append(IncidentEvidenceSchema(
                evidence_type="topology",
                description="Primary default gateway interface 192.168.1.1 link status DOWN.",
                weight=1.3
            ))
            return IncidentSchema(
                id=incident_id,
                title="Default Gateway Link Loss & Routing Blackhole",
                category="ROUTING",
                severity="CRITICAL",
                status="active",
                suspected_root_cause="Edge Router Primary link loss; default next-hop unreachable from core access switch.",
                confidence_score=0.95,
                affected_nodes=["router-pri", "web-srv", "dns-pri", "dns-sec"],
                affected_services=["External Internet Routing", "Cross-Subnet Traversal"],
                recommended_recovery="Engage VRRP Backup Router (192.168.1.254) priority preemption to restore egress paths.",
                explanation="All inter-VLAN and egress traffic dropped. Switch reports interface down on primary edge uplink. Activating VRRP standby restores routing within milliseconds.",
                is_ai_generated=False,
                created_at=datetime.utcnow(),
                evidences=evidences
            )

        # 4. Firewall Block Rule
        if "FIREWALL_DENIAL" in event_types or "firewall" in full_text:
            evidences.append(IncidentEvidenceSchema(
                evidence_type="log",
                description="Firewall ACL drop counter incremented on TCP SYN packets.",
                weight=1.0
            ))
            return IncidentSchema(
                id=incident_id,
                title="Firewall ACL Policy Traffic Drop",
                category="SECURITY_POLICY",
                severity="WARNING",
                status="active",
                suspected_root_cause="Access Control List policy misconfiguration dropping inbound service port packets.",
                confidence_score=0.91,
                affected_nodes=["web-srv"],
                affected_services=["Port 443 Web Services"],
                recommended_recovery="Audit and modify edge firewall filter rule #412 to permit authorized source subnets.",
                explanation="Physical and transport links are intact; packets are dropped intentionally by stateful firewall filter rules.",
                is_ai_generated=False,
                created_at=datetime.utcnow(),
                evidences=evidences
            )

        # 5. Packet Loss & Link Congestion
        if "PACKET_LOSS" in event_types or "latency" in full_text:
            evidences.append(IncidentEvidenceSchema(
                evidence_type="metric",
                description="Interface queue drops and RTT degradation > 50ms observed.",
                weight=0.9
            ))
            return IncidentSchema(
                id=incident_id,
                title="Transit Link Saturation & Packet Loss",
                category="CONGESTION",
                severity="WARNING",
                status="active",
                suspected_root_cause="Link bandwidth saturation causing tail drops and TCP retransmission bursts.",
                confidence_score=0.88,
                affected_nodes=["router-pri", "web-srv"],
                affected_services=["Interactive Web Latency"],
                recommended_recovery="Enable QoS traffic shaping and reroute bulk traffic to redundant link.",
                explanation="Elevated latency and drop rates isolated to uplink interface queue overflow.",
                is_ai_generated=False,
                created_at=datetime.utcnow(),
                evidences=evidences
            )

        # Default Generic or Uncertain Incident
        evidences.append(IncidentEvidenceSchema(
            evidence_type="log",
            description="General anomaly or baseline fluctuation detected across telemetry points.",
            weight=0.5
        ))
        return IncidentSchema(
            id=incident_id,
            title="Uncategorized Network Performance Deviation",
            category="UNKNOWN",
            severity="INFO",
            status="active",
            suspected_root_cause="Inconclusive: Telemetry indicates minor transient jitter or unclassified packet activity.",
            confidence_score=0.45,
            affected_nodes=failed_nodes if failed_nodes else ["switch-1"],
            affected_services=["Network Telemetry Stream"],
            recommended_recovery="Collect extended PCAP captures and verify switch counter statistics.",
            explanation="Evidence is currently insufficient to determine a deterministic single point of failure without speculation.",
            is_ai_generated=False,
            created_at=datetime.utcnow(),
            evidences=evidences
        )

rca_engine = RootCauseAnalysisEngine()
