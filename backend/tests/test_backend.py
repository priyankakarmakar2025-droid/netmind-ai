import pytest
from fastapi.testclient import TestClient
from main import app
from app.services.network_engine import network_engine
from app.models.schemas import FaultInjectionRequest

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "NetMind AI"

def test_topology_retrieval():
    response = client.get("/api/network/topology")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "links" in data
    assert len(data["nodes"]) == 11
    assert data["availability_pct"] == 100.0

def test_dns_fault_injection_and_recovery():
    # 1. Reset baseline
    reset_resp = client.post("/api/network/reset")
    assert reset_resp.status_code == 200

    # 2. Inject DNS fault
    fault_req = {
        "fault_type": "dns_failure",
        "target_node": "dns-pri",
        "severity": 1.0,
        "params": {}
    }
    sim_resp = client.post("/api/simulations/run", json=fault_req)
    assert sim_resp.status_code == 200
    sim_data = sim_resp.json()
    assert "dns-pri" in sim_data["affected_nodes"]
    assert sim_data["simulated_availability"] < 100.0

    # 3. Verify compare strategies counterfactual simulation
    comp_resp = client.post("/api/simulations/compare?scenario_id=dns_failure")
    assert comp_resp.status_code == 200
    comp_data = comp_resp.json()
    assert len(comp_data["strategies"]) > 0
    assert comp_data["strategies"][0]["availability_after"] == 100.0

    # 4. Check incidents list
    inc_resp = client.get("/api/incidents")
    assert inc_resp.status_code == 200
    inc_list = inc_resp.json()
    assert len(inc_list) > 0
    dns_inc = [i for i in inc_list if i["category"] == "DNS"][0]
    assert "dns-pri" in dns_inc["affected_nodes"]
    assert len(dns_inc["evidences"]) > 0

    # 5. Restore baseline
    restore_resp = client.post("/api/network/reset")
    assert restore_resp.status_code == 200
    assert restore_resp.json()["availability_pct"] == 100.0

def test_log_upload_parsing():
    sample_content = (
        "[2026-10-27 10:15:32] [CRITICAL] [dns-pri] named[1042]: resolution failed on 192.168.1.53\n"
        "[2026-10-27 10:15:35] [ERROR] [client-1] curl: connection timeout to 10.0.1.10\n"
    )
    files = {"file": ("test.log", sample_content.encode("utf-8"), "text/plain")}
    resp = client.post("/api/logs/upload", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert data["parsed_count"] == 2
    assert data["rejected_count"] == 0

def test_invalid_file_upload():
    files = {"file": ("malicious.exe", b"MZBinaryContent", "application/octet-stream")}
    resp = client.post("/api/logs/upload", files=files)
    assert resp.status_code == 400
