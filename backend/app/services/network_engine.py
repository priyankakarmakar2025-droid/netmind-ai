import copy
import uuid
import networkx as nx
from typing import Dict, Any, List, Tuple
from app.models.schemas import FaultInjectionRequest, SimulationResult, StrategyComparisonResult

DEFAULT_NODES = [
    {"id": "client-1", "name": "Workstation Alpha", "node_type": "client", "ip_address": "192.168.1.101", "status": "healthy", "latency": 1.2, "packet_loss": 0.0, "pos_x": 50, "pos_y": 100, "details": "Finance Dept PC"},
    {"id": "client-2", "name": "Workstation Beta", "node_type": "client", "ip_address": "192.168.1.102", "status": "healthy", "latency": 1.1, "packet_loss": 0.0, "pos_x": 50, "pos_y": 250, "details": "Engineering PC"},
    {"id": "client-3", "name": "Workstation Gamma", "node_type": "client", "ip_address": "192.168.1.103", "status": "healthy", "latency": 1.4, "packet_loss": 0.0, "pos_x": 50, "pos_y": 400, "details": "HR Dept PC"},
    {"id": "switch-1", "name": "Core Access Switch", "node_type": "switch", "ip_address": "192.168.1.2", "status": "healthy", "latency": 0.4, "packet_loss": 0.0, "pos_x": 280, "pos_y": 250, "details": "Layer 2 Managed Switch"},
    {"id": "router-pri", "name": "Edge Router Primary", "node_type": "router", "ip_address": "192.168.1.1", "status": "healthy", "latency": 2.1, "packet_loss": 0.0, "pos_x": 500, "pos_y": 180, "details": "BGP/OSPF Gateway 1Gbps"},
    {"id": "router-bak", "name": "Edge Router Backup", "node_type": "router", "ip_address": "192.168.1.254", "status": "healthy", "latency": 2.5, "packet_loss": 0.0, "pos_x": 500, "pos_y": 320, "details": "Standby VRRP Router"},
    {"id": "dns-pri", "name": "Primary DNS Server", "node_type": "dns", "ip_address": "192.168.1.53", "status": "healthy", "latency": 1.8, "packet_loss": 0.0, "pos_x": 750, "pos_y": 80, "details": "BIND9 DNS Authoritative"},
    {"id": "dns-sec", "name": "Secondary DNS Server", "node_type": "dns", "ip_address": "192.168.1.54", "status": "healthy", "latency": 2.2, "packet_loss": 0.0, "pos_x": 750, "pos_y": 180, "details": "Secondary Recursive Resolver"},
    {"id": "dhcp-srv", "name": "DHCP Server", "node_type": "dhcp", "ip_address": "192.168.1.5", "status": "healthy", "latency": 1.0, "packet_loss": 0.0, "pos_x": 280, "pos_y": 450, "details": "Kea DHCP Daemon"},
    {"id": "web-srv", "name": "Web Application Server", "node_type": "web", "ip_address": "10.0.1.10", "status": "healthy", "latency": 3.5, "packet_loss": 0.0, "pos_x": 750, "pos_y": 300, "details": "Nginx + React/Node App"},
    {"id": "db-srv", "name": "Production Database", "node_type": "db", "ip_address": "10.0.2.20", "status": "healthy", "latency": 4.1, "packet_loss": 0.0, "pos_x": 950, "pos_y": 300, "details": "PostgreSQL Primary Cluster"}
]

DEFAULT_LINKS = [
    {"id": "link-c1-sw", "source": "client-1", "target": "switch-1", "status": "up", "latency": 1.0, "packet_loss": 0.0, "bandwidth_mbps": 1000.0, "is_backup": False},
    {"id": "link-c2-sw", "source": "client-2", "target": "switch-1", "status": "up", "latency": 1.0, "packet_loss": 0.0, "bandwidth_mbps": 1000.0, "is_backup": False},
    {"id": "link-c3-sw", "source": "client-3", "target": "switch-1", "status": "up", "latency": 1.0, "packet_loss": 0.0, "bandwidth_mbps": 1000.0, "is_backup": False},
    {"id": "link-sw-dhcp", "source": "switch-1", "target": "dhcp-srv", "status": "up", "latency": 0.5, "packet_loss": 0.0, "bandwidth_mbps": 1000.0, "is_backup": False},
    {"id": "link-sw-rpri", "source": "switch-1", "target": "router-pri", "status": "up", "latency": 1.5, "packet_loss": 0.0, "bandwidth_mbps": 1000.0, "is_backup": False},
    {"id": "link-sw-rbak", "source": "switch-1", "target": "router-bak", "status": "up", "latency": 2.0, "packet_loss": 0.0, "bandwidth_mbps": 1000.0, "is_backup": True},
    {"id": "link-rpri-dns1", "source": "router-pri", "target": "dns-pri", "status": "up", "latency": 2.0, "packet_loss": 0.0, "bandwidth_mbps": 1000.0, "is_backup": False},
    {"id": "link-rpri-dns2", "source": "router-pri", "target": "dns-sec", "status": "up", "latency": 2.0, "packet_loss": 0.0, "bandwidth_mbps": 1000.0, "is_backup": False},
    {"id": "link-rpri-web", "source": "router-pri", "target": "web-srv", "status": "up", "latency": 3.0, "packet_loss": 0.0, "bandwidth_mbps": 1000.0, "is_backup": False},
    {"id": "link-rbak-dns2", "source": "router-bak", "target": "dns-sec", "status": "up", "latency": 3.0, "packet_loss": 0.0, "bandwidth_mbps": 1000.0, "is_backup": True},
    {"id": "link-rbak-web", "source": "router-bak", "target": "web-srv", "status": "up", "latency": 4.0, "packet_loss": 0.0, "bandwidth_mbps": 1000.0, "is_backup": True},
    {"id": "link-web-db", "source": "web-srv", "target": "db-srv", "status": "up", "latency": 1.0, "packet_loss": 0.0, "bandwidth_mbps": 10000.0, "is_backup": False}
]

class NetworkSimulationEngine:
    def __init__(self):
        self.baseline_nodes: List[Dict[str, Any]] = copy.deepcopy(DEFAULT_NODES)
        self.baseline_links: List[Dict[str, Any]] = copy.deepcopy(DEFAULT_LINKS)
        self.current_nodes: List[Dict[str, Any]] = copy.deepcopy(DEFAULT_NODES)
        self.current_links: List[Dict[str, Any]] = copy.deepcopy(DEFAULT_LINKS)
        self.active_faults: List[Dict[str, Any]] = []
        self.firewall_blocked_ports: List[int] = []

    def reset_to_baseline(self):
        self.current_nodes = copy.deepcopy(self.baseline_nodes)
        self.current_links = copy.deepcopy(self.baseline_links)
        self.active_faults = []
        self.firewall_blocked_ports = []
        return self.get_current_topology()

    def build_graph(self, include_backup: bool = True) -> nx.Graph:
        g = nx.Graph()
        for node in self.current_nodes:
            g.add_node(node["id"], **node)
        for link in self.current_links:
            if link["status"] != "down":
                if not link["is_backup"] or include_backup:
                    g.add_edge(link["source"], link["target"], weight=link["latency"], **link)
        return g

    def calculate_metrics(self) -> Tuple[float, float, float]:
        total_nodes = len(self.current_nodes)
        if total_nodes == 0:
            return 100.0, 0.0, 0.0
        healthy_or_degraded = sum(1 for n in self.current_nodes if n["status"] in ["healthy", "degraded"])
        availability_pct = round((healthy_or_degraded / total_nodes) * 100.0, 1)

        active_latencies = [n["latency"] for n in self.current_nodes if n["status"] != "failed"]
        avg_latency = round(sum(active_latencies) / len(active_latencies), 2) if active_latencies else 0.0

        active_losses = [n["packet_loss"] for n in self.current_nodes if n["status"] != "failed"]
        avg_loss = round(sum(active_losses) / len(active_losses), 2) if active_losses else 0.0
        return availability_pct, avg_latency, avg_loss

    def get_current_topology(self) -> Dict[str, Any]:
        avail, avg_lat, avg_loss = self.calculate_metrics()
        health = "HEALTHY"
        if avail < 70.0 or avg_loss > 10.0:
            health = "CRITICAL"
        elif avail < 95.0 or avg_loss > 2.0 or avg_lat > 15.0:
            health = "DEGRADED"

        return {
            "nodes": copy.deepcopy(self.current_nodes),
            "links": copy.deepcopy(self.current_links),
            "network_health": health,
            "availability_pct": avail,
            "avg_latency_ms": avg_lat,
            "avg_packet_loss_pct": avg_loss
        }

    def inject_fault(self, request: FaultInjectionRequest) -> SimulationResult:
        fault_type = request.fault_type
        events = []
        affected_nodes = []
        affected_services = []
        candidate_root_causes = []
        initial_avail, _, _ = self.calculate_metrics()

        # 1. Primary DNS failure
        if fault_type == "dns_failure":
            for n in self.current_nodes:
                if n["id"] == "dns-pri":
                    n["status"] = "failed"
                    n["active_fault"] = "Process Crash: BIND9 unhandled SIGSEGV"
                    n["packet_loss"] = 100.0
                    affected_nodes.append(n["id"])
            for l in self.current_links:
                if l["target"] == "dns-pri" or l["source"] == "dns-pri":
                    l["status"] = "down"

            # Downstream effect: clients experience resolution timeout unless failing over to dns-sec
            affected_services.append("DNS Resolution (FQDN queries)")
            candidate_root_causes.append("Primary DNS Daemon crashed (BIND9 socket reset)")
            events.append({
                "id": str(uuid.uuid4())[:8],
                "event_type": "SERVICE_FAIL",
                "severity": "CRITICAL",
                "message": "dns-pri daemon stopped responding on port 53. Connection refused.",
                "source_ip": "192.168.1.53"
            })
            events.append({
                "id": str(uuid.uuid4())[:8],
                "event_type": "DNS_TIMEOUT",
                "severity": "ERROR",
                "message": "Client Workstation Alpha DNS query for app.internal timed out after 3000ms",
                "source_ip": "192.168.1.101"
            })

        # 2. DHCP server failure
        elif fault_type == "dhcp_failure":
            for n in self.current_nodes:
                if n["id"] == "dhcp-srv":
                    n["status"] = "failed"
                    n["active_fault"] = "DHCP Pool Exhaustion / Daemon Offline"
                    n["packet_loss"] = 100.0
                    affected_nodes.append(n["id"])
            affected_services.append("DHCP Lease Allocation")
            candidate_root_causes.append("DHCP daemon halted; new host lease discovery packets unacknowledged")
            events.append({
                "id": str(uuid.uuid4())[:8],
                "event_type": "DHCP_NACK",
                "severity": "CRITICAL",
                "message": "dhcp-srv unreachable on UDP 67/68. DHCPDISCOVER broadcast expired.",
                "source_ip": "192.168.1.5"
            })

        # 3. Router failure without backup
        elif fault_type == "router_failure":
            for n in self.current_nodes:
                if n["id"] == "router-pri":
                    n["status"] = "failed"
                    n["active_fault"] = "Hardware PSU Failure / BGP link down"
                    n["packet_loss"] = 100.0
                    affected_nodes.append(n["id"])
            for l in self.current_links:
                if l["source"] == "router-pri" or l["target"] == "router-pri":
                    l["status"] = "down"
            # Without failover, web and dns are unreachable from clients
            for n in self.current_nodes:
                if n["id"] in ["web-srv", "dns-pri", "dns-sec"]:
                    n["status"] = "impacted"
                    affected_nodes.append(n["id"])
            affected_services.extend(["External Routing", "Web Portal", "DNS Resolution"])
            candidate_root_causes.append("Edge Router Primary power supply failure; gateway 192.168.1.1 down")
            events.append({
                "id": str(uuid.uuid4())[:8],
                "event_type": "LINK_DOWN",
                "severity": "CRITICAL",
                "message": "Interface GigabitEthernet0/1 to Edge Router Primary link down",
                "source_ip": "192.168.1.1"
            })
            events.append({
                "id": str(uuid.uuid4())[:8],
                "event_type": "ROUTING_UNREACHABLE",
                "severity": "ERROR",
                "message": "ICMP Host Unreachable: Destination network 10.0.1.0/24 via default gateway failed",
                "source_ip": "192.168.1.102"
            })

        # 4. Router failure WITH backup path activation (failover)
        elif fault_type == "router_backup":
            for n in self.current_nodes:
                if n["id"] == "router-pri":
                    n["status"] = "failed"
                    n["active_fault"] = "Primary gateway down - Failover active"
                    affected_nodes.append(n["id"])
                elif n["id"] == "router-bak":
                    n["status"] = "healthy"
                    n["details"] = "Active VRRP Master (Route switched)"
            for l in self.current_links:
                if l["source"] == "router-pri" or l["target"] == "router-pri":
                    l["status"] = "down"
                if l["is_backup"]:
                    l["status"] = "up"
            # Latency slightly rises via secondary path
            for n in self.current_nodes:
                if n["node_type"] == "client":
                    n["latency"] += 4.5
            affected_services.append("Primary Path (Suboptimal Backup Route engaged)")
            candidate_root_causes.append("VRRP failover initiated after router-pri heartbeat failure")
            events.append({
                "id": str(uuid.uuid4())[:8],
                "event_type": "VRRP_TRANSITION",
                "severity": "WARNING",
                "message": "router-bak transitioned from BACKUP to MASTER state for VIP 192.168.1.254",
                "source_ip": "192.168.1.254"
            })

        # 5. Increased link latency / packet loss
        elif fault_type in ["link_latency", "link_loss", "link_congestion"]:
            loss_val = request.params.get("packet_loss", 25.0) if fault_type != "link_latency" else 5.0
            lat_val = request.params.get("latency", 65.0)
            target = request.target_link or "link-rpri-web"
            for l in self.current_links:
                if l["id"] == target or target in [l["source"], l["target"]]:
                    l["status"] = "degraded"
                    l["latency"] = lat_val
                    l["packet_loss"] = loss_val
            for n in self.current_nodes:
                if n["id"] in ["web-srv", "client-1", "client-2"]:
                    n["status"] = "degraded"
                    n["latency"] += lat_val
                    n["packet_loss"] = loss_val
                    affected_nodes.append(n["id"])
            affected_services.append("HTTP Transaction Throughput")
            candidate_root_causes.append(f"Interface buffer queue congestion and link packet loss on {target}")
            events.append({
                "id": str(uuid.uuid4())[:8],
                "event_type": "PACKET_LOSS",
                "severity": "WARNING",
                "message": f"Link {target} reports drop rate of {loss_val}% and RTT {lat_val}ms",
                "source_ip": "192.168.1.1"
            })

        # 6. Web server failure
        elif fault_type == "web_failure":
            for n in self.current_nodes:
                if n["id"] == "web-srv":
                    n["status"] = "failed"
                    n["active_fault"] = "HTTP 502 Bad Gateway / Nginx Worker OOM"
                    n["packet_loss"] = 100.0
                    affected_nodes.append(n["id"])
            affected_services.append("Customer Web Portal (Port 80/443)")
            candidate_root_causes.append("Web application worker process terminated (Out of Memory error)")
            events.append({
                "id": str(uuid.uuid4())[:8],
                "event_type": "HTTP_502",
                "severity": "CRITICAL",
                "message": "Nginx upstream error: no live upstreams while connecting to 10.0.1.10:8000",
                "source_ip": "10.0.1.10"
            })

        # 7. Database server failure (causes cascading dependency failure to web server)
        elif fault_type == "db_failure":
            for n in self.current_nodes:
                if n["id"] == "db-srv":
                    n["status"] = "failed"
                    n["active_fault"] = "Database Connection Pool Saturated / Disk I/O Stall"
                    affected_nodes.append(n["id"])
                elif n["id"] == "web-srv":
                    n["status"] = "degraded"
                    n["active_fault"] = "Downstream Dependency Failure: DB Unavailable"
                    affected_nodes.append(n["id"])
            affected_services.extend(["PostgreSQL Engine", "Web Portal (API endpoints failing)"])
            candidate_root_causes.append("PostgreSQL deadlock / max connections limit exceeded on 10.0.2.20:5432")
            events.append({
                "id": str(uuid.uuid4())[:8],
                "event_type": "DB_CONNECTION_FAIL",
                "severity": "CRITICAL",
                "message": "FATAL: remaining connection slots are reserved for non-replication superuser connections",
                "source_ip": "10.0.2.20"
            })
            events.append({
                "id": str(uuid.uuid4())[:8],
                "event_type": "HTTP_500",
                "severity": "ERROR",
                "message": "web-srv API call /api/v1/user-data threw 500 Internal Error (DB unreachable)",
                "source_ip": "10.0.1.10"
            })

        # 8. Firewall blocking
        elif fault_type == "firewall_block":
            blocked_port = request.params.get("port", 443)
            self.firewall_blocked_ports.append(blocked_port)
            for n in self.current_nodes:
                if n["id"] == "web-srv":
                    n["status"] = "impacted"
                    n["active_fault"] = f"Egress/Ingress blocked on port {blocked_port}"
                    affected_nodes.append(n["id"])
            affected_services.append(f"TCP Port {blocked_port} Traffic")
            candidate_root_causes.append(f"Access Control List (ACL) drop rule blocking port {blocked_port}")
            events.append({
                "id": str(uuid.uuid4())[:8],
                "event_type": "FIREWALL_DENY",
                "severity": "WARNING",
                "message": f"Edge Firewall rule #412 DENY src:ANY dst:10.0.1.10 dport:{blocked_port} (TCP SYN dropped)",
                "source_ip": "192.168.1.1"
            })

        # Default fallback fault
        else:
            if request.target_node:
                for n in self.current_nodes:
                    if n["id"] == request.target_node:
                        n["status"] = "failed"
                        n["active_fault"] = f"Generic Fault: {fault_type}"
                        affected_nodes.append(n["id"])
                candidate_root_causes.append(f"Node fault injected on {request.target_node}")

        sim_avail, avg_lat, avg_loss = self.calculate_metrics()

        result = SimulationResult(
            scenario_id=fault_type,
            scenario_name=fault_type.replace("_", " ").title(),
            initial_availability=initial_avail,
            simulated_availability=sim_avail,
            affected_nodes=list(set(affected_nodes)),
            affected_services=list(set(affected_services)),
            average_latency=avg_lat,
            average_packet_loss=avg_loss,
            generated_events=events,
            candidate_root_causes=candidate_root_causes,
            recovery_strategies_available=self.get_strategies_for_fault(fault_type)
        )
        return result

    def get_strategies_for_fault(self, fault_type: str) -> List[str]:
        strategies_map = {
            "dns_failure": ["switch_secondary_dns", "restart_dns_daemon", "flush_local_dns_cache"],
            "dhcp_failure": ["restart_dhcp_service", "assign_static_fallback", "increase_dhcp_pool"],
            "router_failure": ["activate_vrrp_backup", "power_cycle_primary_router", "reroute_static_default_gw"],
            "router_backup": ["restore_primary_router", "optimize_backup_qos"],
            "link_latency": ["reroute_via_fiber_link", "enable_traffic_shaping", "reset_interface_buffers"],
            "link_loss": ["reroute_via_fiber_link", "enable_traffic_shaping", "reset_interface_buffers"],
            "link_congestion": ["reroute_via_fiber_link", "enable_traffic_shaping", "reset_interface_buffers"],
            "web_failure": ["restart_web_service", "spawn_canary_instance", "rollback_deployment"],
            "db_failure": ["scale_db_connection_pool", "failover_to_read_replica", "restart_postgres"],
            "firewall_block": ["revoke_blocking_acl_rule", "permit_port_in_firewall", "revert_security_group"]
        }
        return strategies_map.get(fault_type, ["restore_baseline", "reboot_node"])

    def compare_strategies(self, fault_type: str) -> List[StrategyComparisonResult]:
        """Calculates counterfactual recovery outcomes on isolated clones of current state."""
        strategies = self.get_strategies_for_fault(fault_type)
        results = []

        for strat in strategies:
            # Create isolated sandbox
            sandbox = copy.deepcopy(self)
            
            # Apply simulated recovery action
            recovered_services = []
            remaining_impacts = []
            tradeoffs = ""
            recovery_time = 30
            score = 0.85

            if strat in ["switch_secondary_dns", "activate_vrrp_backup", "scale_db_connection_pool", "revoke_blocking_acl_rule", "restart_web_service"]:
                # High effectiveness strategy
                for n in sandbox.current_nodes:
                    if n["status"] in ["failed", "impacted", "degraded"]:
                        n["status"] = "healthy"
                        n["active_fault"] = None
                        n["packet_loss"] = 0.0
                recovered_services = ["All Services Operational"]
                tradeoffs = "Negligible service interruption; recommended as primary automated remediation."
                recovery_time = 15
                score = 0.96
            elif strat in ["restart_dns_daemon", "power_cycle_primary_router", "restart_postgres"]:
                # Medium strategy: causes temporary downtime before returning
                recovered_services = ["Primary Service Recovered"]
                remaining_impacts = ["30-60 second transient TCP disconnect during cold reboot"]
                tradeoffs = "Requires daemon shutdown and cold cache warm-up period."
                recovery_time = 75
                score = 0.78
            else:
                # Fallback / Partial strategy
                recovered_services = ["Partial Connectivity Restored"]
                remaining_impacts = ["Some clients or routes remain suboptimally configured"]
                tradeoffs = "Manual intervention or static overrides required on individual endpoints."
                recovery_time = 120
                score = 0.65

            avail, lat, loss = sandbox.calculate_metrics()
            curr_avail, _, _ = self.calculate_metrics()

            results.append(StrategyComparisonResult(
                strategy_id=strat,
                name=strat.replace("_", " ").title(),
                description=f"Automated recovery procedure implementing {strat.replace('_', ' ')}",
                availability_before=curr_avail,
                availability_after=avail,
                latency_ms=lat,
                packet_loss_pct=loss,
                recovered_services=recovered_services,
                remaining_impacts=remaining_impacts,
                recovery_time_est_s=recovery_time,
                tradeoffs=tradeoffs,
                score=score
            ))

        # Sort highest score first
        results.sort(key=lambda s: s.score, reverse=True)
        return results

network_engine = NetworkSimulationEngine()
