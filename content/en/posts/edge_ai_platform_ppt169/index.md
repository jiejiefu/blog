---
title: "Semiconductor Equipment Edge AI Platform: From Sensor Data to Intelligent Decisions"
tags: ["Edge AI", "Predictive Maintenance", "MLOps", "AI Agent", "Backend Engineering"]
draft: true
date: 2026-10-17
cover:
    image: "01_project_overview.png"
    alt: "Semiconductor Equipment Edge AI Platform Cover"
    relative: true
    hidden: false
---
## Introduction

This article is based on an interview presentation deck (10 slides) showcasing the complete engineering practice of a Semiconductor Equipment Edge AI Platform, covering real-time health inference from sensor data ingestion to AI Agent and MLOps operations across the full stack. All images have been de-identified; company names and sensitive information have been removed, and data and technical parameters are logical illustrations only, for architecture and visual reference purposes.

> ⚠️ **Intellectual Property Notice**: All images in this article are copyrighted by their respective original companies. Unauthorized download, reproduction, or modification is prohibited. This article is for personal technical demonstration and interview reference only. All images have been de-identified and virtualized and do not contain any undisclosed trade secrets, real customer names, specific process nodes, or internal project codenames.

---

## 01. Project Overview: Semiconductor Equipment Edge AI Platform

![Project Overview: Semiconductor Equipment Edge AI Platform](images/01_project_overview.png)

The platform is positioned as a "Semiconductor Equipment Edge AI Platform," subtitled "Edge AI and Fault Prediction Health Management," integrating fragmented Sensor + ML workflows into executable engineering closed loops from sensor data to intelligent decisions.

### End-to-End Execution Pipeline

Five stages connected:

| Stage | Name | Summary |
|---|---|---|
| 1 | Sensor Data | Sensor data collection · 2kHz vibration / temperature |
| 2 | Feature & ML | Feature engineering and models · FFT / One-Class SVM |
| 3 | Edge Inference | Device-side real-time inference · Low latency < 5ms |
| 4 | Monitoring | Real-time health monitoring · Health Score & Alert |
| 5 | AI Agent | Intelligent agent decision · LLM Root Cause Analysis |

### Core Engineering Capabilities

Four core modules:

1. **IoT Data Ingestion**: deque memory ring buffer · 500 entries/s batch flush write-in · SQLite dual-database isolation and backup
2. **ML & PHM Engine**: One-Class SVM anomaly detection · PCA dimensionality reduction feature extraction and anomaly analysis · unsupervised degradation trend cumulative quantification
3. **Edge Deployment**: PyInstaller standalone binary packaging · offline environment level software ready-to-use · version delivery and inspection update mechanism
4. **GenAI & RAG Agent**: LLM automated maintenance tool generation · RAG retrieval of historical maintenance knowledge base · open-loop fault root cause diagnosis and dispatch

### System Tech Stack

- Frontend: React UI
- Backend: Flask / SSE
- Database: SQLite Dual
- ML: scikit-learn / PCA
- Infra: Docker Compose
- GenAI: LLM Agent / RAG

---

## 02. Why Edge AI Platform? (Before / After Comparison)

![Why Edge AI Platform](images/02_why.png)

### Before: 6 Fragmented Tools and Data Silos

1. CSV Files: Sensor original data records, manual Export
2. Python Scripts: Ad-hoc / one-time data cleaning scripts, lack version control
3. ML Notebooks: Offline model experimentation and training, no real-time inference
4. Config Files: Static JSON/YAML configuration, fixed thresholds
5. Edge C++ Runtime: Device-side monolithic executable, isolated updates difficult
6. Web Dashboard: Independent frontend monitoring interface, status cannot sync

### Critical System Pain Points

- **High Friction Glue Code**: Steps heavily dependent on manual conversion and custom scripts, prone to crash due to format mismatch
- **Broken Data Lineage**: Inference results cannot be traced back to original sensor parameter versions and training datasets
- **High Time-to-Market Latency**: Model updates require weeks of manual re-implementation and verification

### After: 1 Executable Engineering Loop

1. Sensor Data Ingestion: Automatic data streaming
2. Feature & ML Pipeline: Feature standardization + PHM
3. Edge AI Inference Engine: One-click device deployment
4. Continuous Health Monitor: Real-time health monitoring alerts
5. AI Agent Diagnostics: Intelligent root cause diagnosis
6. Closed-Loop Feedback: Data model continuous adjustment

### Engineering Impact

| Metric | Before | After | Benefit |
|---|---|---|---|
| Model Deployment Cycle | 28 days (manual) | 1 day (automated pipeline) | → shortened 96% time |
| Glue Code Reduction | — | -85% | Significantly reduce repetitive development |
| Data Lineage Integrity | — | 100% Sync | End-to-end automatic alignment |

---

## 03. System Architecture (5-Layer Integrated Architecture)

![System Architecture](images/03_system_architecture.png)

### Five-Layer System Tech Stack

| Layer | Name | Technical Details |
|---|---|---|
| 1 | User & Frontend | React 18 · MUI · React Flow · 31 routes, monitoring dashboard UI |
| 2 | Backend Core / REST & SSE Hub | Flask · 15 Blueprints · JWT authentication · Agent Tool collaborative dispatch |
| 3 | ML & Analytics | scikit-learn · feature extraction · One-ClassSVM anomaly detection · batch inference |
| 4 | Edge Execution | Sensor data ingestion → Edge.exe engine → real-time health score (Health Score) |
| 5 | Data & Persistence | SQLite (dual database), model storage and feature storage management (Model Registry) |

### AI Agent Collaborative Architecture

**Controllable Tool Calling Architecture Design**:
- Strict Boundary Control: Agent does not bypass backend logic; only executes via validated Tool APIs
- Real-time SSE Context Ingestion: Device real-time Alert signals streamed into LLM reasoning context
- Actionable Insights: Root cause analysis and maintenance suggestions automatically returned to frontend UI

### Performance Metrics

| Metric | Value |
|---|---|
| Module Count | 15 modules (Flask Blueprints) |
| Edge Carrier Execution | 8 ms |
| Backend Tool Execution | 35 ms |
| SSE Event Transmission | 15 ms |
| Agent Reasoning Decision | 85 ms |

Core architecture value: AI Agent acts only as an intelligent coordinator through Tool Calling, fully retaining backend system determinism and security.

---

## 04. End-to-End Data Flow

![End-to-End Data Flow](images/04_end_to_end_data_flow.png)

### Stage 1: Data Ingestion and Streaming

- Thread-safe queue (deque maxlen=5k)
- Batch write every 5 seconds (max 500 entries)
- Database capacity limit: 10,000 records
- Prevent I/O blocking under high-frequency signal bursts

**Buffer and Batch Write Mechanism**:
- Bounded Queue: collections.deque(maxlen=5000), effectively absorbs high-frequency sensor burst signals, avoiding blocking system main thread
- Asynchronous SQLite Flush: 500 entries / 5 seconds, flexible database capacity limit 10,000 records, ensuring frontend maintains extremely low latency

### Stage 2: Preprocessing and ML Scoring

- Time-domain and frequency-domain feature extraction
- One-Class SVM batch inference engine
- Real-time health score optimization
- Converts original vibration data into quantified metrics

### Stage 3: Monitoring Alert and AI Response

- Frontend 10-second polling mechanism
- GET /api/vibration/latest snapshot
- SSE event stream drives AI Agent inference
- Automated root cause diagnosis and maintenance recommendations

**Buffer Queue and DB Write Simulation**:
- Sensor anomaly signal (2,500 pts/s)
- DB asynchronous write-in (500 pts/s)
- I/O load control < 5%

Core architecture value: Asynchronous buffering isolates high-frequency signal burst impact on the database, ensuring stable system operation during abnormal bursts.

---

## 05. ML & PHM Pipeline

![ML & PHM Pipeline](images/05_ml_phm_pipeline.png)

### Preprocessing and Feature Processing Pipeline

1. Signal Ingestion: High-frequency vibration acceleration, acceleration data x(t), continuous sensor streaming
2. Time Slicing: Time-domain sliding window slicing, overlapping coverage, fixed-length signal frames
3. Feature Matrix Extraction: accRMS · peak · kurtosis, time-domain and frequency-domain feature metrics, input to downstream ML model

### Anomaly Detection

**One-Class SVM**: Applicable to production lines lacking fault labels, learns normal behavior boundary → marks anomaly deviation

### Feature Alignment

**DTW Sequence Alignment**: Overcomes rotational speed fluctuation and time axis phase misalignment, non-linear time series dynamic alignment

### Trend and Drift

**PCA and Feature Drift**: Current operation data vs historical Baseline comparison, quantifies long-term equipment wear and degradation

### Algorithm Selection Criteria

Based on physical signal characteristics → lacking fault labels → **OCSVM** → rotational phase misalignment → **DTW** → long-term wear degradation → **PCA feature drift**

---

## 06. Backend Engineering

![Backend Engineering](images/06_backend_engineering.png)

### Flask Core Architecture

| Module | Content |
|---|---|
| Authentication | LDAP / AD enterprise authentication integration · JWT Token mechanism |
| RESTful API | 15 Domain Blueprints · Sensor / ML / Edge routes |
| Data Layer | SQLAlchemy ORM · Dual SQLite (vibration.db) |
| Background Jobs | APScheduler + Queue asynchronous Task Pipeline |
| AI Agent Collaborative Hub | LLM workflow orchestration · Tool Calling processor |
| Model Lifecycle | ModelBuildingHistory · automatic training state & metrics tracking |

### Data and Stream I/O

**Dual DB cross-library query and asynchronous buffering write-in mechanism**:
- edge_ai.db (configuration and model layer compression) + vibration.db (high-frequency time-domain database)
- SQLite ATTACH → high-efficiency single SQL join query
- High-frequency signal → deque queue maxlen=5000 → batch DB write (5s / 500 entries)

### Model Lifecycle

**ModelBuildingHistory**: Model state machine and history tracking
- building ↔ completed / failed
- Persisted metrics storage: Accuracy & Coverage, Anomaly Score threshold and anomaly log records

### 15 Domain Blueprints

Split by business domain for independent maintenance (Sensor / ML / Edge), avoiding large single Route file, improving modular extensibility.

**Authentication Flow**: LDAP / AD ↔ JWT Access ↔ Refresh (1-hour short token / 30-day refresh renewal)

### Key Metrics

| Metric | Value |
|---|---|
| Blueprints | 15 (modular architecture) |
| Databases | 2 (attached dual DB architecture) |
| Batch Interval | 5s (queue traffic control mechanism) |
| Model States | 3 (complete lifecycle tracking) |

---

## 07. AI Agent Architecture

![AI Agent Architecture](images/07_ai_agent_architecture.png)

### Agent Execution Flow

1. Client Layer: User input → React Agent UI conversation interface
2. Backend Gateway: POST /agent/chat/stream · SSE real-time streaming
3. Agent Orchestrator: OpenAI Agents SDK · automatic tool selection · ReAct reasoning chain
4. Platform Tools: Flask controller directly invoked controlled sandbox functions
   - get_health_score
   - get_vibration_data
   - run_sql_query_safe
   - anomaly_detection
   - read_file
   - export_report

### Reasoning Engine

- LLM focuses on understanding user intent, decomposes problem steps, selects appropriate Tool
- Eliminates hallucination, does not directly generate data; all physical data queried via Tools

### Deterministic Tool Execution

- Python encapsulated tools responsible for actual SQLite query execution, file reading, and algorithm computation
- High-precision execution results formatted and returned to LLM for comprehensive analysis and summarization

### Backend Protection and Security Governance

- Backend strictly controls API access and permission authentication; Unrestricted Shell strictly prohibited
- SQL query limited to Read-only mode with parameterized passing, preventing injection attacks
- Combined with JWT Token authentication, ensuring model sensitive data and business settings access security

### Agent Execution Latency Display

| Task | Latency |
|---|---|
| LLM reasoning | ~320 ms |
| Tool execution | ~35 ms |
| SSE event transmission | ~85 ms |

Deterministic data 0%, direct DB risk 100% (emphasizes all data accessed via controlled Tools).

---

## 08. Deployment & Monitoring

![Deployment & Monitoring](images/08_deployment_monitoring.png)

### Docker Compose Containerized Environment

| Service | Configuration |
|---|---|
| Frontend (:3000) | edgeai-frontend:latest, React UI + Nginx server |
| Backend API (:5000) | edgeai-backend:latest, Flask WSGI + APScheduler scheduling |
| Persistent Data Volume (Docker Volume) | SQLite dual database · ML model files (.pkl) · sensor logs, Volume mount, reducing data loss risk |

Key reconstruction application injection: entrypoint.sh → env.js → window.ENV → backend endpoint, same Image across environments (Deploy Once · Configure at Runtime)

### APScheduler: Proactive Health Detection and Rapid Recommendation

| Background Engine Task | Frequency |
|---|---|
| Health Detection | Every 5 minutes |
| Model Anomaly Inference | Every 5 minutes |
| Email Alert Notification | Event-triggered |

**State Buffer & Cache**: MonitorSnapshot state pool, RAM two-tier cache (API read value 0.2ms), disk fallback persistence

### Automated Schedule Timeline

- Daily database backup: 03:00 Daily
- Health detection: Every 5 minutes
- Model anomaly inference: Every 5 minutes
- Email alert delivery: Immediate event trigger
- High-frequency data write-in: 5s / 500 entries batch

### Frontend Visualization Panel

- Real-time health Gauge dashboard
- SSE proactive alert event push

---

## 09. Failure Handling & Scalability

![Failure Handling & Scalability](images/09_failure_scaling.png)

### Current Single-Machine Experience Flow

Sensor data → deque queue → batch write → SQLite DB

**System concurrency bottleneck**: SQLite single-file write lock under high-frequency burst traffic

**Burst traffic peak shaving simulation**:
- Burst traffic peak: 2.5k
- 5s (burst point) → 15s (peak) → 25s (digestion complete)
- Smooth write-in limit 1000 req/s (Batch Flush)

**Bounded queue buffer**: deque(maxlen=5000) memory isolation
**Batch write strategy**: Every 5 seconds / 500 entries batch flush
**FIFO capacity retention limit**: Database record limit 10,000 entries
**Dual DB rolling backup mechanism**: Daily 03:00 automatic backup (retains 7 copies)

### Future Scale-Out Blueprint

MQTT Broker ↔ Message Queue ↔ Worker Cluster (N instances each)

**Persistence & Service Layer**:

| Component | Description |
|---|---|
| PostgreSQL | High availability HA mechanism, Write Sharding |
| Redis Cache | Memory-level cache, Real-time Snapshot |
| Flask API | Stateless elastic expansion, Load Balancer |

**Three expansion principles**:

1. **Ingress and compute node decoupling**: Message Queue (Kafka / RabbitMQ) fully absorbs high-frequency burst traffic, eliminating single-point lock
2. **Worker elastic horizontal expansion**: Stateless Worker nodes can be automatically scaled based on Queue backlog Auto-Scaling
3. **Enterprise-grade read/write separation**: PostgreSQL responsible for persistence, Redis provides high-speed API access, thoroughly separating read/write pressure

> Current SQLite is an engineering choice for current Edge Deployment scale; as scale grows, it will evolve into Scale-Out distributed architecture.

---

## 10. Engineering Trade-offs

![Engineering Trade-offs](images/10_engineering_tradeoffs.png)

### Current Solution vs. Bottleneck vs. Future Evolution per Component

| Component | Current Solution (TODAY) | Bottleneck & Limit | Future Evolution (NEXT) |
|---|---|---|---|
| Flask | Simple REST · ML integration easy | Architecture norm limits less | FastAPI (Service Split) |
| SQLite | Deployment simple, maintenance low | Single-file write concurrency lock | PostgreSQL HA Cluster |
| APScheduler | Background work built-in integrated | Single process limit | Worker Queue (Celery / RQ) |
| Local ML files | Edge direct load | Model version tracking weak | Model Registry (MLflow) |
| SSE | Unidirectional HTTP stream simple | No bidirectional communication | WebSocket (bidirectional demand) |
| One-Class SVM | No fault label threshold applicable | Over-parameterized boundary sensitive | Advanced PHM Model |
| React Context | Lightweight component state sharing | Large scale easy multi-render | Zustand / Redux |
| Queue | Memory queue buffer (deque) | Capacity limited by memory | Durable MQ (Kafka) |
| Docker Compose | Single-machine containerized deployment simple | Container orchestration capability limited | Kubernetes (K8s) |

### System Trade-off Radar Chart (Edge-Optimal vs. Scale-Out)

- **Deployment Difficulty**: Current architecture low, future Scale-Out increases with K8s introduction
- **Low Maintenance Cost**: Current solution better, distributed architecture maintenance complexity increases
- **Throughput**: Current single-machine limited, future Scale-Out significantly improves
- **Fault Tolerance**: Current single-point risk high, future distributed has high fault tolerance
- **Storage Capacity**: Current SQLite limited, future PostgreSQL + Redis significantly improves

### Architecture Evolution Blueprint

| Phase | Architecture Mode | Technology Stack |
|---|---|---|
| Phase 1 | Edge Monolith (current edge monolith) | SQLite · Flask · single process |
| Phase 2 | Decoupled Pipeline | Worker Queue · SSE Stream |
| Phase 3 | Cloud Scale-Out (cloud horizontal expansion) | K8s · PostgreSQL · Model Reg |

---

## Conclusion

The Semiconductor Equipment Edge AI Platform, from sensor data ingestion to AI Agent autonomous decision, has undergone transformation from "fragmented tools and data silos" to "unified executable engineering loop." Key achievements include:

- Model deployment cycle compressed from 28 days to 1 day (shortened 96%)
- Glue code reduced by 85%, data lineage integrity 100% synchronized
- Real-time inference latency < 5ms, offline autonomous operation supported
- 15 Domain Blueprints modular architecture, supporting future horizontal expansion to Kubernetes

Current SQLite single-machine architecture is an engineering choice for current Edge Deployment scale; as scale grows, it will evolve into Scale-Out distributed architecture.

---

> **Copyright and Terms of Use**: All images in this article are copyrighted by their respective original companies. Reproduction requires authorization. The image content has been de-identified and virtualized for logical and visual reference purposes only and does not constitute any trade secret disclosure.
