import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sklearn.ensemble import IsolationForest

class AnomalyDetectionService:
    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.is_fitted = False
        self._fit_baseline()

    def _fit_baseline(self):
        # Generate representative baseline observations (Latency, Packet Loss, Jitter, Request Failure Rate)
        np.random.seed(42)
        n_samples = 300
        normal_latency = np.random.normal(loc=2.5, scale=0.8, size=(n_samples, 1))
        normal_loss = np.random.exponential(scale=0.1, size=(n_samples, 1))
        normal_jitter = np.random.normal(loc=0.4, scale=0.1, size=(n_samples, 1))
        normal_err_rate = np.random.exponential(scale=0.01, size=(n_samples, 1))

        baseline_features = np.hstack([normal_latency, normal_loss, normal_jitter, normal_err_rate])
        self.model.fit(baseline_features)
        self.is_fitted = True

    def analyze_metrics(self, current_metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        anomalies = []
        now = datetime.utcnow()

        lat = current_metrics.get("latency", 2.0)
        loss = current_metrics.get("packet_loss", 0.0)
        jitter = current_metrics.get("jitter", 0.3)
        err_rate = current_metrics.get("error_rate", 0.0)

        feature_vector = np.array([[lat, loss, jitter, err_rate]])

        # Model-based anomaly score
        if self.is_fitted:
            score = float(self.model.decision_function(feature_vector)[0])
            is_anomaly = bool(self.model.predict(feature_vector)[0] == -1)

            if is_anomaly or lat > 20.0 or loss > 5.0:
                severity = "CRITICAL" if (lat > 50.0 or loss > 15.0) else "WARNING"
                trigger_metric = "Latency" if lat > 20.0 else ("Packet Loss" if loss > 5.0 else "Multi-metric Deviation")
                anomalies.append({
                    "timestamp": now.isoformat(),
                    "metric_name": trigger_metric,
                    "value": round(lat if trigger_metric == "Latency" else loss, 2),
                    "expected_range": "Latency < 10ms, Loss < 1.0%",
                    "anomaly_score": round(abs(score), 3),
                    "severity": severity,
                    "description": f"IsolationForest flagged statistical anomaly ({trigger_metric} significantly exceeding baseline distribution)."
                })

        return anomalies

    def generate_metric_history(self, points: int = 24) -> List[Dict[str, Any]]:
        history = []
        base_time = datetime.utcnow() - timedelta(minutes=points * 5)
        np.random.seed(123)

        for i in range(points):
            t = base_time + timedelta(minutes=i * 5)
            # Add occasional spike near end for realistic visualization
            spike = 35.0 if i == points - 2 else 0.0
            history.append({
                "time": t.strftime("%H:%M"),
                "latency": round(float(np.random.normal(2.5, 0.5) + spike), 2),
                "packet_loss": round(float(np.clip(np.random.normal(0.05, 0.05) + (spike * 0.1), 0, 100)), 2),
                "throughput_mbps": round(float(np.random.normal(450, 40)), 1),
                "cpu_load_pct": round(float(np.random.normal(22, 5)), 1)
            })
        return history

anomaly_service = AnomalyDetectionService()
