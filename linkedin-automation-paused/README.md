# Portfolio Distribution Engine

An automated distribution utility built to compile, sync, and publish professional developer portfolios, case studies, and PDF documentation to external endpoints.

---

## ⚡ Architecture & Concept

This project helps developers maintain an active presence on professional networks by automating document synchronization. By decoupling content creation from the manual work of publishing, it acts as a headless publishing agent.

- **Data Serialization (`publish_manifest.json`):** Tracks the status of daily portfolio releases.
- **Handshake Sequence (`authenticate_publisher.py`):** Guides the publisher through a standard OAuth callback loop to acquire secure, temporary API access keys.
- **Headless Distribution Pipeline (`distribute_portfolio.py`):** The engine that reads scheduled documents, registers upload handles, streams the binary blobs, and dispatches the payload to the targeting API gateways.

---

## 🛠️ System Layers

| Layer | Implementation | Purpose |
| --- | --- | --- |
| **Logic Engine** | Python 3 | Resolves local file paths, handles networking, and processes system states. |
| **Credential Manager** | OAuth token cache (`token.json`) | Caches secure endpoints to authorize sessions gracefully. |
| **Execution Manifest** | JSON Configuration | Maps publication schedules (dates, titles, and captions) to target files. |

---

## 🚀 Setup & Execution

### 1. Configure the Manifest
Edit `publish_manifest.json` to define your target release dates, document titles, captions, and the local file names of your PDFs:
```json
{
  "posts": [
    {
      "day": 1,
      "date": "2026-06-29",
      "pdf": "my_case_study.pdf",
      "title": "System Design Architecture",
      "caption": "Sharing my latest architecture design for high-scale caching...",
      "posted": false
    }
  ]
}
```

### 2. Run OAuth Credentials Handshake
Set your Client ID and Client Secret credentials in your system environment, then execute the handshake script to save local API authorization:
```bash
python authenticate_publisher.py
```
This cache-safely writes keys to `token.json` (which is excluded from Git to prevent leakage).

### 3. Run Distribution Engine
To manually test or run the publisher:
```bash
python distribute_portfolio.py
```
On production pipelines, this script runs via GitHub Actions triggered by `distribution_pipeline.yml`.

---

*Designed and implemented by Shubham Bhati.*
