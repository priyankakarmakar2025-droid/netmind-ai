# NetMind AI — Known Limitations & Future Improvements

## Known Limitations
1. **Simplified Packet Semantics**: The simulation models network behavior through graph reachability, statistical latency distributions, and packet-loss percentages rather than emulating full real-time kernel TCP/IP stacks (such as NS-3 or Mininet).
2. **Simplified Routing Protocols**: Router failover uses simplified VRRP heartbeat simulation rather than dynamic convergence algorithms (e.g. BGP full routing tables or full OSPF link-state advertisements).
3. **Local In-Memory Isolation**: Counterfactual recovery simulations run in isolated in-memory Python clones rather than containerized virtual network namespaces.

## Future Improvements
1. **Mininet / GNS3 Integration**: Connect the digital twin to real Mininet virtual switches for hybrid physical/simulated topologies.
2. **Continuous PCAP Ingestion**: Stream live Wireshark/tcpdump packet streams into the anomaly detection module.
3. **Multi-Tenant Topologies**: Support concurrent virtual enterprise networks with custom subnetting.
