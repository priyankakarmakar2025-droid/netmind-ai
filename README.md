# NetMind AI: AI-Powered Network Digital Twin for Predictive Fault Diagnosis, Root-Cause Analysis, and Counterfactual Recovery Simulation

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19+-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-6+-646CFF.svg?logo=vite&logoColor=white)](https://vitejs.dev)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-4.0+-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![NetworkX](https://img.shields.io/badge/NetworkX-3.6+-blue.svg)](https://networkx.org)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.9+-F7931E.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org)

NetMind AI is an intelligent network troubleshooting and simulation platform that helps administrators understand complex network failures, identify their precise root causes through deterministic evidence grounding, analyze failure propagation across dependent services, and safely test alternative recovery strategies in a virtual digital twin sandbox.

---

## 🌟 Key Features

1. **Interactive Virtual Digital Twin**: Real-time graph visualization using **React Flow** backed by **NetworkX** graph traversal.
2. **Deterministic Network Fault Simulation Engine**: Injects controlled DNS, DHCP, VRRP router, firewall ACL, congestion, and database dependency outages.
3. **Counterfactual Recovery Comparison**: Executes competing recovery strategies in isolated memory sandboxes to quantify availability, recovery time, latency, and side effects.
4. **Grounded Root-Cause Analysis (RCA)**: Multi-factor rule-based diagnostic engine producing traceable, evidence-backed incident reports.
5. **AI Diagnostic Copilot**: Grounded technical assistant explaining incidents in plain language with local deterministic fallback.
6. **Telemetry Anomaly Detection**: Unsupervised **Isolation Forest** ML model continuously inspecting latency and packet-loss distributions.
7. **Incident Memory & Feedback**: Persistent storage of incident history and administrator-confirmed root causes for historical learning.
8. **Network Log Ingestion**: Ingests, normalizes, and extracts structured events from `.log`, `.txt`, `.csv`, `.json`, and `.jsonl` formats.

---

## 🏗️ Architecture

```
netmind-ai/
├── backend/
│   ├── app/
│   │   ├── api/endpoints.py       # REST API endpoints
│   │   ├── core/                  # Database and configuration
│   │   ├── models/                # Pydantic schemas & SQLAlchemy DB models
│   │   └── services/
│   │       ├── network_engine.py  # NetworkX digital twin simulation engine
│   │       ├── rca_engine.py      # Rule-based root-cause analysis
│   │       ├── log_parser.py      # Multi-format log parsing service
│   │       ├── anomaly_detector.py# Isolation Forest ML anomaly model
│   │       ├── ai_assistant.py    # Grounded AI assistant adapter
│   │       └── incident_memory.py # Verified outcome history
│   ├── tests/test_backend.py      # Pytest unit & integration test suite
│   ├── requirements.txt
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── components/            # React Flow topology, RCA & Simulator panels
│   │   ├── services/api.ts        # Axios client
│   │   └── App.tsx                # Main NOC Command Dashboard
│   └── package.json
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── SIMULATION_MODEL.md
│   ├── TEAM_CONTRIBUTIONS.md
│   ├── DEMO_SCRIPT.md
│   └── KNOWN_LIMITATIONS.md
└── README.md
```

---

## 🚀 How to Run in VS Code

### 1. Open the Project in VS Code
Open the project directory in VS Code:
```bash
code C:\Users\35pri\.gemini\antigravity\scratch\netmind-ai
```
Or open the `netmind-ai.code-workspace` file directly.

### 2. Run the Backend (FastAPI)
In a VS Code terminal:
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload --port 8000
```
*API Swagger Documentation is available at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)*

### 3. Run the Frontend (React + Vite)
In a second VS Code terminal:
```powershell
cd frontend
npm run dev
```
*Access the Web Dashboard at: [http://localhost:5173](http://localhost:5173)*

---

## 🧪 Running Automated Tests

Run backend integration and unit tests:
```powershell
cd backend
$env:PYTHONPATH="."
.\venv\Scripts\pytest -v tests/test_backend.py
```
Build frontend production bundle:
```powershell
cd frontend
npm run build
```

---

## 📜 Academic Team Contributions

- **Member 1 (Network Simulation)**: Topology modeling, NetworkX integration, fault injection scenarios, counterfactual recovery simulator.
- **Member 2 (AI & Diagnostics)**: Log parser, structured events, rule-based RCA engine, Isolation Forest anomaly detection, AI assistant fallback.
- **Member 3 (Frontend & Integration)**: React Flow visualization, command center dashboard, charts, incident history, and end-to-end integration.
