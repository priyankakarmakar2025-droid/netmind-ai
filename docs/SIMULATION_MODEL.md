# NetMind AI — Network Simulation Model & Assumptions

## Model Overview
The NetMind AI digital twin maintains a graph $G = (V, E)$ where:
- Nodes $V$ represent workstations, L2 switches, default gateways/routers, DNS resolvers, DHCP daemons, and application/database servers.
- Edges $E$ represent physical and logical links characterized by latency ($L_{e}$), packet loss ($\rho_{e}$), and active/backup status.

## Explicit Simulation Assumptions

1. **Reachability Traversal**:
   - Path reachability is determined by evaluating graph connectivity from client endpoints to designated service targets using Dijkstra's shortest path weighted by link latency.
   - When a primary router interface goes DOWN, alternate routes (such as VRRP standby paths) are engaged if configured.

2. **DNS vs. Direct-IP Semantics**:
   - Primary DNS failures cause FQDN resolution timeouts on dependent applications.
   - Direct-IP traffic routes remain functional as long as the underlying layer 2 and layer 3 paths are intact.

3. **DHCP Model**:
   - DHCP server outages halt dynamic address acquisition for new clients attempting lease discovery (`DHCPDISCOVER`).
   - Existing workstations with pre-allocated leases remain connected and operational.

4. **Service Dependency Cascading**:
   - Database outages (e.g. connection pool exhaustion) propagate cascading HTTP 500/502 errors to the web application tier, while the web server host remains physically reachable on the network.

5. **Counterfactual Recovery**:
   - Alternative remediation strategies are evaluated against deep-copied in-memory state clones.
   - Latency, recovery duration, and availability are calculated deterministically to prevent hallucinated recovery metrics.
