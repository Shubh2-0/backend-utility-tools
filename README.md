# 📊 Backend Telemetry & Feed Utility Tools

A collection of utility tools designed to parse, synchronize, and execute telemetry telemetry data nodes, RSS feed orchestration, and automated browser connectivity profiling.

---

## ⚙️ Core Modules

*   **`sync_feed_orchestrator.py`**: Handles structured RSS feed generation, validates XML telemetry formats, and updates publication history.
*   **`browser_node_telemetry.py`**: Executes simulated browser node telemetry requests utilizing Playwright browser profiles to check endpoint latency, connection handshakes, and UI responsiveness.

---

## 🛠️ Stack & Technologies

*   **Language**: Python 3.11
*   **Emulation Engine**: Playwright
*   **Orchestration**: GitHub Actions

---

## 🚀 Execution & Setup

### 1. Install Dependencies
```bash
pip install playwright
playwright install chromium
```

### 2. Local Telemetry Simulation
```bash
python browser_node_telemetry.py
```

### 3. Sync Feeds
```bash
python sync_feed_orchestrator.py
```
