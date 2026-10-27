# NetMind AI — Live Demonstration Script for Viva / Presentation

## 1. Baseline Health Inspection (1 Minute)
1. Open [http://localhost:5173](http://localhost:5173).
2. Point out the **11 Network Nodes** and **12 Links** in the digital twin.
3. Note 100% availability, ~1.8ms average RTT, and 0% packet loss.
4. Click on any client or server node on the **Live Digital Twin** tab to inspect its IP, RTT, and status.

## 2. Ingesting Real / Synthetic Logs (1 Minute)
1. Navigate to the **Log Ingestion** tab.
2. Click **Load Synthetic Log Sample** (or select a `.log` or `.csv` file).
3. Click **Upload & Parse Logs**.
4. Show how the regex/JSON normalizer parses events and populates the telemetry log stream.

## 3. Injecting a Complex Fault (2 Minutes)
1. Switch to the **Fault Simulator & What-If** tab.
2. Select **"1. Primary DNS Server Failure"** (or **"7. Database Failure (Cascading Dependency)"**).
3. Click **Inject Fault Scenario**.
4. Observe the live digital twin:
   - Target node enters the `FAILED` or `IMPACTED` state.
   - Links turn red (down) or amber (degraded).
   - Global availability drops from 100% to degraded levels.

## 4. Grounded Root-Cause Analysis & AI Copilot (2 Minutes)
1. Navigate to the **Root-Cause Analysis** tab.
2. Highlight the suspected root cause and observe the deterministic confidence score.
3. Review the **Supporting Evidence** citing specific logs and topology graph statuses.
4. Click **"Explain Incident in Plain Language"** to see the AI Diagnostic Copilot generate a grounded explanation.
5. In the Copilot chat, ask: *"Why did the web tier fail?"* or *"What is the recommended recovery?"*
6. Click **Confirm** under "Administrator Ground-Truth Feedback" to save the verified incident into historical memory.

## 5. Counterfactual Recovery Comparison (2 Minutes)
1. Return to the **Fault Simulator** tab.
2. Inspect the **Counterfactual Recovery Strategy Comparison** table.
3. Explain that NetMind AI cloned the simulated state into isolated memory sandboxes to simulate competing recovery procedures without touching production.
4. Review the recommended strategy score, estimated recovery time, and availability recovery (e.g. 81.8% -> 100%).
5. Click **Restore Baseline** to return the entire network to its healthy baseline.
