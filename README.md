# Backend Utility & Telemetry Suite (Java 17 / Spring Boot 3.3)

![Java 17](https://img.shields.io/badge/Java-17-orange.svg)
![Spring Boot 3.3](https://img.shields.io/badge/Spring%20Boot-3.3.0-brightgreen.svg)
![OpenAPI Swagger](https://img.shields.io/badge/OpenAPI-Swagger%20UI-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

Production-grade Spring Boot 3.3 utility suite providing enterprise **JVM Telemetry Analysis**, **RSS Feed Aggregation**, and **REST API Middleware Services**.

Designed and maintained by **Shubham Bhati** (Backend Engineer specializing in Java, Spring Boot, Microservices, Apache Kafka, and Distributed Caching).

---

## ⚡ Tech Stack & Architecture

* **Core Framework:** Java 17, Spring Boot 3.3.0 (Web, Actuator, Caching)
* **API Documentation:** SpringDoc OpenAPI 3 / Swagger UI (`/swagger-ui.html`)
* **Build Tool:** Apache Maven 3.x
* **Utility Modules:**
  * **Telemetry Suite:** Real-time JVM memory tracking, active thread counts, CPU processor load, and uptime diagnostics.
  * **Feed Orchestrator:** Cached REST endpoints for aggregated tech publications and RSS feed items.

---

## 🚀 Quick Start & API Endpoints

### 1. Build and Run
```bash
# Clone the repository
git clone https://github.com/Shubh2-0/backend-utility-tools.git
cd backend-utility-tools

# Run Spring Boot App
mvn spring-boot:run
```

### 2. Interactive Swagger UI
Once started, access the interactive API docs at:
👉 `http://localhost:8080/swagger-ui.html`

### 3. Sample Endpoints
* **JVM Telemetry Metrics:** `GET /api/v1/telemetry/metrics`
* **Aggregated Articles:** `GET /api/v1/feed/articles`
* **Health Check:** `GET /actuator/health`

---

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.
