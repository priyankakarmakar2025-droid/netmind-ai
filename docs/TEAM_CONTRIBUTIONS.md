# NetMind AI — Academic Team Contributions

## Member 1 — Network Simulation & Graph Theory
- **Primary Focus**: Digital twin network topology, graph algorithms, and simulation mechanics.
- **Key Modules**:
  - `backend/app/services/network_engine.py`: NetworkX graph representation, dynamic reachability traversal, fault injection logic.
  - Fault scenario specifications (DNS, DHCP, VRRP router failover, Link loss/congestion, ACL drop, DB dependency).
  - Counterfactual recovery comparison engine with isolated memory sandboxes.
  - Automated simulation test coverage (`backend/tests/test_backend.py`).

## Member 2 — AI, Diagnostics & Data Processing
- **Primary Focus**: Log parsing, rule-based root cause analysis, statistical anomaly detection, and AI assistant grounding.
- **Key Modules**:
  - `backend/app/services/log_parser.py`: Multi-format log parsing (syslog, JSON, CSV) and event normalization.
  - `backend/app/services/rca_engine.py`: Deterministic multi-factor rule-based diagnostic engine.
  - `backend/app/services/anomaly_detector.py`: Scikit-learn Isolation Forest ML model and synthetic telemetry generator.
  - `backend/app/services/ai_assistant.py`: Grounded AI explanation adapter with deterministic local fallback.
  - `backend/app/services/incident_memory.py`: Persistent historical learning and verified feedback storage.

## Member 3 — Frontend & System Integration
- **Primary Focus**: NOC Command Center interface, React Flow topology graph, live metric visualization, and API integration.
- **Key Modules**:
  - `frontend/src/components/NetworkGraphView.tsx` & `CustomNodeComponent.tsx`: Interactive React Flow digital twin.
  - `frontend/src/components/FaultSimulatorPanel.tsx`: Interactive fault injection console and counterfactual comparison matrix.
  - `frontend/src/components/RootCauseAnalysisView.tsx`: Evidence-backed RCA investigation console and Copilot chat.
  - `frontend/src/components/AnomalyDetectionView.tsx`: Telemetry charts (Recharts) and ML alert tables.
  - `frontend/src/components/IncidentHistoryView.tsx` & `LogIngestionView.tsx`: History audit and log ingestion.
  - System end-to-end integration and responsive dark NOC design.
