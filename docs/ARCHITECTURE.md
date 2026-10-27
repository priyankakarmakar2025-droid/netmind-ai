# NetMind AI — Architecture Specification

## Overview
NetMind AI integrates a graph-theoretic digital twin with an inference and anomaly detection engine to enable zero-risk network troubleshooting.

```
+-----------------------------------------------------------+
|               React 19 + React Flow Frontend              |
|  - Digital Twin Canvas     - RCA & Copilot Interface      |
|  - Fault Injection Console - Anomaly Recharts             |
+-----------------------------+-----------------------------+
                              | REST JSON (Axios)
+-----------------------------v-----------------------------+
|                FastAPI Backend (Uvicorn)                  |
|  - API Router               - Pydantic Validation         |
+--------------+------------------------------+--------------+
               |                              |
+--------------v---------------+ +------------v---------------+
|    Network Simulation Engine | | Diagnosis & Anomaly Engine  |
|  - NetworkX Graph Traversal  | | - Deterministic RCA Engine  |
|  - Mutex Topology State      | | - Isolation Forest Model    |
|  - Counterfactual Sandboxes  | | - Multi-format Log Parser   |
+--------------+---------------+ +------------+---------------+
               |                              |
               +--------------+---------------+
                              |
+-----------------------------v-----------------------------+
|               SQLite Persistent Storage                   |
|  - Nodes & Links    - Simulation Runs   - Incidents & RCA |
|  - Verified Ground-Truth Feedback       - Anomalies       |
+-----------------------------------------------------------+
```
