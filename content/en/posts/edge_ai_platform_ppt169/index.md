---
title: "Semiconductor Equipment Edge AI Platform: From Sensor Data to Intelligent Decisions"
tags: ["Edge AI", "Predictive Maintenance", "MLOps", "AI Agent", "Backend Engineering"]
draft: false
date: 2026-10-17
cover:
    image: "https://jiejiefu.github.io/blog/posts/edge_ai_platform_ppt169/images/01_project_overview.png"
    alt: "Semiconductor Equipment Edge AI Platform Cover"
    hidden: false
---
## Introduction

This is the written version of an interview deck — 10 slides. Slides can only show conclusions, so here I've written out why each piece was chosen the way it was and what got traded away. The last slide in particular (the limits of a single-node SQLite architecture) is where the whole design started: you can't pick a direction until you're honest about where the ceiling is.

All diagrams have been de-identified — company names and sensitive details removed, numbers are illustrative. Attribution required when reposting.

> ⚠️ **Intellectual Property Notice**: All images in this article are copyrighted by the blog author. Unauthorized download, reproduction, or modification is prohibited. This article is for personal technical demonstration and interview reference only. All images have been de-identified and virtualized and do not contain any undisclosed trade secrets, real customer names, specific process nodes, or internal project codenames.

---

## 01. Project Overview: Semiconductor Equipment Edge AI Platform

![Project Overview: Semiconductor Equipment Edge AI Platform](images/01_project_overview.png)

The platform is positioned as a "Semiconductor Equipment Edge AI Platform," subtitled "Edge AI and Fault Prediction Health Management (PHM)," integrating fragmented Sensor + ML workflows into executable engineering closed loops from sensor data to intelligent decisions.

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

1. **IoT Data Ingestion**: deque in-memory peak-shaving buffer · 500 entries / 5s batch flush · SQLite dual-database rolling isolation and backup
2. **ML & PHM Engine**: One-Class SVM anomaly detection · PCA dimensionality reduction, feature extraction and drift analysis · unsupervised degradation trend metric quantification · Mahalanobis distance / outlier detection
3. **Edge Deployment**: PyInstaller standalone binary packaging · zero-dependency, ready-to-use in offline environments · version release and update check mechanism
4. **GenAI & RAG Agent**: LLM-generated repair work orders · RAG retrieval over the historical maintenance knowledge base · closed-loop fault root cause diagnosis and dispatch

### System Tech Stack

- Frontend: React UI
- Backend: Flask / SSE
- Database: SQLite (dual DB)
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
5. Edge C++ Runtime: Device-side monolithic executable, difficult to update in isolation
6. Web Dashboard: Independent frontend monitoring interface, status cannot sync

### Critical System Pain Points

- **High Friction Glue Code**: Steps heavily dependent on manual conversion and custom scripts, prone to crash due to format mismatch
- **Broken Data Lineage**: Inference results cannot be traced back to original sensor parameter versions and training datasets
- **High Time-to-Market Latency**: Model updates require weeks of manual re-implementation and verification

> **Core cost**: engineers shift from manual hand-off to system maintenance and exception handling.

### After: 1 Executable Engineering Loop

1. Sensor Data Ingestion: Automatic data streaming
2. Feature & ML Pipeline: Feature standardization + PHM
3. Edge AI Inference Engine: One-click device deployment
4. Continuous Health Monitor: Real-time health monitoring alerts
5. AI Agent Diagnostics: Intelligent root cause diagnosis
6. Closed-Loop Feedback: Data model closed-loop continuous tuning

### Engineering Impact

| Metric | Before | After | Benefit |
|---|---|---|---|
| Model Deployment Cycle | 28 days (manual) | 1 day (automated pipeline) | → 96% reduction |
| Glue Code Reduction | — | -85% | Significant reduction in repetitive development |
| Data Lineage Integrity | — | 100% Sync | End-to-end automatic alignment |

---

## 03. System Architecture (5-Layer Integrated Architecture)

![System Architecture](images/03_system_architecture.png)

### Five-Layer System Tech Stack

| Layer | Name | Technical Details |
|---|---|---|
| 1 | User & Frontend | React 18 · MUI · React Flow · 31 routes · monitoring dashboard UI |
| 2 | Backend Core / REST & SSE Hub | Flask · 15 Blueprints · JWT authentication · Agent Tool collaborative dispatch |
| 3 | ML & Analytics | scikit-learn · feature extraction · One-Class SVM anomaly detection · batch inference |
| 4 | Edge Execution | Sensor data ingestion → Edge.exe engine → real-time health score (Health Score) |
| 5 | Data & Persistence | SQLite (dual database), model file and feature file management (Model Registry) |

### AI Agent Collaborative Architecture

**Controllable Tool-Calling Architecture**:
- Strict Boundary Control: Agent does not bypass backend logic; only executes via validated Tool APIs
- Real-time SSE Context Ingestion: Device real-time Alert signals streamed into LLM reasoning context
- Actionable Insights: Root cause analysis and maintenance suggestions automatically returned to frontend UI

### Performance Metrics

| Metric | Value |
|---|---|
| Module Count | 15 modules (Flask Blueprints) |
| Edge Data Ingestion | 8 ms |
| Backend Tool Execution | 35 ms |
| SSE Broadcast | 15 ms |
| Agent Reasoning Decision | 120 ms |

Core architecture value: the AI Agent acts only as an intelligent coordinator through Tool Calling, preserving the determinism and security of the backend system.

---

## 04. End-to-End Data Flow

![End-to-End Data Flow](images/04_end_to_end_data_flow.png)

### Stage 1: Data Ingestion and Streaming

- Thread-safe queue (deque maxlen=5000)
- Batch write every 5 seconds (max 500 entries)
- Database capacity limit: 10,000 records
- Prevent I/O blocking under high-frequency signal bursts

**Buffering & Batch Write Mechanism**:
- Bounded Queue: collections.deque(maxlen=5000), effectively absorbs high-frequency sensor burst signals, avoiding blocking system main thread
- Asynchronous SQLite Flush: 500 entries / 5 seconds, hard database cap of 10,000 records, ensuring queries stay extremely low latency

### Stage 2: Preprocessing and ML Scoring

- Time-domain and frequency-domain feature extraction
- One-Class SVM batch inference engine
- Real-time health score normalization
- Converts original vibration data into quantified metrics

### Stage 3: Monitoring Alert and AI Response

- Frontend 10-second polling mechanism
- GET /api/vibration/latest endpoint
- SSE event stream drives AI Agent inference
- Automated root cause diagnosis and maintenance recommendations

**Buffering Queue & DB Write Simulation**:
- Sensor anomaly signal (2,500 pts/s)
- DB asynchronous write (500 pts / 5s)
- I/O load control < 5%

Core architecture value: Asynchronous buffering isolates high-frequency signal burst impact on the database, ensuring stable system operation during abnormal bursts.

---

## 05. ML & PHM Pipeline

![ML & PHM Pipeline](images/05_ml_phm_pipeline.png)

### Preprocessing and Feature Processing Pipeline

1. Signal Ingestion: High-frequency vibration acceleration signal x(t), continuous sensor streaming
2. Time Slicing: Time-domain sliding window slicing, overlapping windows, fixed-length signal frames
3. Feature Matrix Extraction: accRMS · peak · kurtosis, time-domain and frequency-domain feature metrics, input to downstream ML model

### Anomaly Detection

**One-Class SVM**: Applicable to production lines lacking fault labels, learns normal behavior boundary → marks anomaly deviation

### Feature Alignment

**DTW Sequence Alignment**: overcomes rotational speed fluctuation and time axis phase misalignment via non-linear time-series dynamic alignment

### Trend and Drift

**PCA and Feature Drift**: Current operation data vs historical Baseline comparison, quantifies long-term equipment wear and degradation

### Algorithm Selection Criteria

Selected based on physical signal characteristics — lacking fault labels → **OCSVM** → rotational phase misalignment → **DTW** → long-term wear degradation → **PCA feature drift**

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

**Dual DB cross-database query and asynchronous buffering write mechanism**:
- edge_ai.db (configuration and model history) + vibration.db (high-frequency time-domain database)
- SQLite ATTACH → high-efficiency single SQL join query
- API reads are decoupled from high-frequency writes, so queries are never blocked by write spikes
- High-frequency signal → deque queue maxlen=5000 → batch DB write (5s / 500 entries)

### Model Lifecycle

**ModelBuildingHistory**: Model state machine and history tracking
- building ↔ completed / failed
- Persisted metrics storage: Accuracy & Coverage, Anomaly Score threshold and anomaly log records

### 15 Domain Blueprints

Split by business domain for independent maintenance (Sensor / ML / Edge), avoiding monolithic Route files, improving modular extensibility.

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
4. Platform Tools: controlled sandbox functions invoked directly by the Flask controller
   - get_health_score
   - get_vibration_data
   - run_sql_query_safe
   - anomaly_detection
   - read_file
   - export_report

Sandboxed execution with Read-only API permissions only.

### Reasoning Engine

- Core framework: OpenAI Agents SDK (with 20+ built-in Function Tools); fallback: LangGraph ReAct; real-time feedback via SSE Streaming
- LLM focuses on understanding user intent, decomposing the problem into steps, and selecting the appropriate Tool
- Prevents hallucinations: the model never fabricates data, and all actual data is queried through Tools

### Deterministic Tool Execution

- Python encapsulated tools responsible for actual SQLite query execution, file reading, and algorithm computation
- High-precision execution results formatted and returned to LLM for comprehensive analysis and summarization

### Backend Protection and Security Governance

- Backend strictly controls API access and permission authentication; Unrestricted Shell strictly prohibited
- SQL query limited to Read-only mode with parameterized passing, preventing injection attacks
- Combined with JWT Token authentication, ensuring secure access to sensitive sensor data and project configuration

### Agent Execution Latency Display

| Task | Latency |
|---|---|
| LLM reasoning | ~320 ms |
| Tool execution | ~35 ms |
| SSE stream transmission | ~85 ms |

100% deterministic data, 0% direct DB risk (all data is accessed through controlled Tools).

---

## 08. Deployment & Monitoring

![Deployment & Monitoring](images/08_deployment_monitoring.png)

### Docker Compose Containerized Environment

| Service | Configuration |
|---|---|
| Frontend (:3000) | edgeai-frontend:latest, React UI + Nginx server |
| Backend API (:5000) | edgeai-backend:latest, Flask WSGI + APScheduler scheduling |
| Persistent Data Volume (Docker Volume) | SQLite dual database · ML model files (.pkl) · sensor logs, Volume mount, reducing data loss risk |

Zero-rebuild dynamic injection: entrypoint.sh → env.js → window.ENV → backend endpoint, same Image across environments (Deploy Once · Configure at Runtime)

### APScheduler: Proactive Health Detection and Cached Inference

| Background Engine Task | Frequency |
|---|---|
| Health Detection | Every 5 minutes |
| Model Anomaly Inference | Every 5 minutes |
| Email Alert Notification | Event-triggered |

**State Buffer & Cache**: MonitorSnapshot state pool, RAM two-tier cache (API reads in just 0.2ms), disk file fallback persistence

### Automated Schedule Timeline

- Daily database backup: 03:00 Daily
- Health detection: Every 5 minutes
- Model anomaly inference: Every 5 minutes
- Email alert delivery: Immediate event trigger
- High-frequency data writes: 5s / 500 entries batch

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
- 5s (burst start) → 15s (peak) → 25s (backlog fully absorbed)
- Smoothed write throughput 100 req/s (Batch Flush, i.e. 500 entries every 5 s)

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

1. **Complete decoupling of writes from compute**: the Message Queue (Kafka / RabbitMQ) fully absorbs ten-thousand-scale burst traffic, eliminating single-point locks
2. **Elastic horizontal scaling of Workers**: stateless Worker nodes can be auto-scaled based on queue backlog
3. **Enterprise-grade read/write separation**: PostgreSQL handles persistence while Redis serves high-speed API reads, fully separating read and write pressure

> Current SQLite is an engineering choice for current Edge Deployment scale; as scale grows, it will evolve into Scale-Out distributed architecture.

---

## 10. Engineering Trade-offs

![Engineering Trade-offs](images/10_engineering_tradeoffs.png)

### Current Solution vs. Bottleneck vs. Future Evolution per Component

| Component | Current Solution (TODAY) | Bottleneck & Limit | Future Evolution (NEXT) |
|---|---|---|---|
| Flask | Simple REST · ML integration easy | Few architectural constraints; hard to split services | FastAPI (Service Split) |
| SQLite | Deployment simple, low maintenance burden | Single-file write concurrency lock | PostgreSQL HA Cluster |
| APScheduler | Background work built-in integrated | Single process limit | Worker Queue (Celery / RQ) |
| Local ML files | Edge direct load | Model version tracking weak | Model Registry (MLflow) |
| SSE | Unidirectional HTTP stream simple | No bidirectional communication | WebSocket (bidirectional demand) |
| One-Class SVM | Applicable when fault labels are unavailable | Over-parameterized boundary sensitive | Advanced PHM Model |
| React Context | Lightweight component state sharing | Excessive re-renders at scale | Zustand / Redux |
| Queue | In-memory peak-shaving buffer (deque) | Capacity limited by memory | Durable MQ (Kafka) |
| Docker Compose | Single-machine containerized deployment simple | Container orchestration capability limited | Kubernetes (K8s) |

### System Trade-off Radar Chart (Edge-Optimal vs. Scale-Out)

- **Deployment Speed**: Fast for the current design; Scale-Out slows down once K8s is introduced
- **Low Ops Cost**: Lower for the current design; distributed architectures add significant ops complexity
- **Scalability**: Limited on a single machine; Scale-Out scales out substantially
- **Fault Tolerance**: High single-point risk today; the distributed design is highly fault tolerant
- **Throughput**: Limited on a single machine; Message Queue + Worker Cluster raise it substantially

Overall stance: design for today's edge constraints while leaving a clear evolution path for future scale-out.

### Architecture Evolution Blueprint

| Phase | Architecture Mode | Technology Stack |
|---|---|---|
| Phase 1 | Edge Monolith (current edge monolith) | SQLite · Flask · single process |
| Phase 2 | Decoupled Pipeline | Worker Queue · SSE Stream |
| Phase 3 | Cloud Scale-Out (cloud horizontal expansion) | K8s · PostgreSQL · Model Reg |

---

## Conclusion

Looking back, the most valuable part of this project wasn't any particular model — it was collapsing "fragmented tools + data silos" into one engineering loop that actually runs and can be handed off:

- Model deployment cycle compressed from 28 days to 1 day (shortened 96%)
- Glue code reduced by 85%, data lineage integrity 100% synchronized
- Real-time inference latency < 5 ms; supports offline autonomous operation
- 15 Domain Blueprints modular architecture, supporting future scale-out migration to Kubernetes

Not reaching for a heavier stack was deliberate: edge equipment has to keep running when the network drops, so the orchestrated architecture sits in Phase 3. Migrating later means you'll see exactly where the ceiling is, instead of guessing now.

---

> **Copyright and Terms of Use**: All images in this article are copyrighted by the blog author. Reproduction requires attribution. The image content has been de-identified and virtualized for logical and visual reference purposes only and does not constitute any trade secret disclosure.
