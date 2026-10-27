---
title: "Smart Fab Edge-AI: Predictive Maintenance and Autonomous Decision Agent System"
date: 2026-10-18
draft: false
math: true
tags:
  - Edge AI
  - 預測性維護
  - Fab Domain
  - 系統設計
  - AI Agent
description: "An engineering guide to edge deployment, predictive maintenance, Edge Agents, Industrial RAG, MLOps, and autonomous decision systems for smart factories."
cover:
  image: "https://jiejiefu.github.io/blog/projects/fab-predictive-maintenance-ppt169/images/cover.jpg"
  alt: "Terminal running the sentinel-07 PHM pipeline: 2 kHz sensor stream, two-stage anomaly detection, RUL, canary rollout and a governed agent"
  hidden: false
---

{{< tldr >}}
- Six-layer architecture: sensing → streaming → signal processing → PHM → Edge Agent → MES/EAP safety integration.
- Two-stage detection (Isolation Forest → Autoencoder) plus RUL prediction turns raw signals into maintenance planning; figures are project-specific.
- Models ship through shadow deployment, canary rollout (5% → 20% → 100%), then monitoring and rollback.
- Edge Agent, Industrial RAG, and MLOps connect evidence to workflows, but safety-critical control stays outside the LLM.

Make each layer observable, verifiable, and recoverable before expanding autonomy.
{{< /tldr >}}

## Introduction

This article expands an 11-slide interview deck into a technical reference on the Smart Fab Edge AI architecture. The appendix explains how to read the figures.

It covers real-time processing, anomaly detection, Remaining Useful Life (RUL) prediction, edge deployment, industrial knowledge retrieval, and AI agent boundaries. The real question is not how to deploy models, but how to run them under constrained resources — balancing latency, compute, reliability, and operating cost — while integrating with existing controls, maintenance workflows, and factory systems.

{{< audio src="audio/morty-introduction.m4a" caption="Introduction — narrated by Morty" >}}

> **Intellectual Property and Usage Notice:** This article is for technical exchange, architecture discussion, and demonstration of personal capability. The content has been de-identified. It contains no confidential customer data, trade secrets, or non-public project information. Use and redistribution of the text and diagrams are subject to the author's published licensing terms.

---

## 01. System Objectives and Design Assumptions

![Cover: Smart Fab Edge-AI Predictive Maintenance and Autonomous Decision Agent System](images/01_cover.png)

Semiconductor lines have many equipment types, high-frequency sensor data, expensive downtime, and strict latency and reliability requirements for some control loops. The architecture therefore pairs edge computing with centralized management: latency-sensitive work stays in the factory, while centralized services handle management. Firewall and audit rules also make sending data off-site for real-time analysis impractical.

- **Data governance and security:** Classify and control access to sensor data, equipment information, and maintenance records; process sensitive data in-factory and follow internal rules for cross-system transfers.
- **Edge resources:** Choose model size, inference frequency, and buffering against each device's CPU, memory, and accelerators.
- **Detection usability:** Beyond accuracy, evaluate false-positive and false-negative rates, alert volume, and on-site workload.
- **Safety and fault isolation:** AI assesses anomalies and recommends maintenance; safety-critical control stays with validated control systems and safety mechanisms.

---

## 02. End-to-End Technical Architecture

![End-to-end technical architecture map](images/02_architecture.png)

The architecture has six layers. The first three answer where data comes from, how it is organized, and how it becomes a judgment; the last three answer who receives that judgment, under what permissions, and how it connects to existing systems.

| Layer | Name | Key Technologies and Responsibilities |
| --- | --- | --- |
| 01 | Sensing and Data Acquisition | MCUs, IO-Link, vibration/current/pressure sensors |
| 02 | Streaming and Time-Series Data | Kafka, InfluxDB, ring buffers, timestamps, and synchronization |
| 03 | Signal Processing | FFT, wavelet transforms, time-domain and frequency-domain feature extraction |
| 04 | AI Analytics and PHM | Isolation Forest, Autoencoders, LSTM/Transformer, and RUL prediction |
| 05 | Edge Agent and Task Orchestration | State management, tool routing, workflow orchestration, and model selection |
| 06 | Integration and Safety Control | SECS/GEM, MES/EAP APIs, authorization, and safety middleware |

Edge devices handle low-latency processing and inference. The central platform manages models, runs cross-equipment analytics and training, and coordinates deployment.

These components need not form a linear pipeline; the right combination depends on data frequency, latency, and deployment environment.

Even if a model returns in milliseconds, end-to-end latency must include acquisition, signal processing, inference, communication, and controller execution.

---

## 03. High-Throughput Data Streaming and Signal Processing

![High-throughput data streaming and signal processing](images/03_streaming.png)

In high-frequency sensing, the first challenge is rarely model accuracy — it is processing a continuous stream of incoming data.

### Data Volume and Scope

Take 20 machines, three sensor channels each, sampled continuously at 2 kHz, with each sample stored as 4 bytes.

Per second:

$$
20 \times 3 \times 2{,}000 \times 4 = 480{,}000\ \text{bytes/s}
$$

Per day:

$$
480{,}000 \times 86{,}400 = 41{,}472{,}000{,}000\ \text{bytes/day}
$$

That is about **41.47 GB/day** in decimal units (1 GB = \(10^9\) bytes). This counts raw values only — not timestamps, packet overhead, indexes, storage formats, or other metadata. With those, real traffic or storage can approach 50 GB/day.

The 20-machine figure is an illustrative calculation, not a scale claim. **Managed fleet size** (how many machines the system can connect to) and **high-frequency processing scale** (how many actually stream raw waveforms at 2 kHz) are different metrics. Managing 500+ machines does not mean all of them stream raw waveforms at that rate.

### Signal Processing Pipeline

1. **Acquisition:** Capture vibration, current, and pressure signals, handling timestamps, missing values, and data quality.
2. **Windowing:** Split continuous signals into fixed-length windows; length and overlap follow equipment characteristics and analysis needs.
3. **Feature extraction:** Apply FFT, wavelet transforms, and statistics to compute RMS, spectral entropy, and band energy.
4. **Output:** Emit fixed-format feature vectors for anomaly detection and health models.

A model might consume a 64-dimensional feature vector instead of the full waveform, cutting downstream compute. Suitability still depends on the anomaly pattern — information lost during extraction cannot be recovered later.

### Edge Optimization

- Process in batches or windows instead of sample by sample.
- Use preallocated ring buffers to cut allocation and copying.
- Separate high-frequency signal processing from lower-frequency state analysis.
- Apply different retention and transmission policies to raw data, features, and events.
- Monitor queue length, data loss, CPU usage, and end-to-end latency.

---

## 04. Two-Stage Anomaly Detection

![Two-stage anomaly detection](images/04_anomaly_detection.png)

Equipment failure datasets are heavily imbalanced: normal data is easy to collect, real failures are rare. Pure supervised learning therefore lacks enough labeled failures.

False alarms are the other practical problem. Most come from material changeover or warm-up, when the vibration spectrum briefly departs from its usual distribution. The model scores it as anomalous and fires repeatedly while the machine is fine — enough noise for on-site staff to start ignoring the system.

This architecture therefore separates cheap initial screening from deeper assessment.

### Stage 1: Rapid Screening

Isolation Forest flags samples that differ from observed data. It is lightweight enough for some resource-constrained edge environments. Its job is to shortlist data for investigation, not to declare failure.

### Stage 2: In-Depth Assessment

An Autoencoder measures reconstruction error against learned normal patterns. Thresholds can be set per equipment type, operating state, and sensor channel, so normal process transitions and load changes are not classified as failures.

### Alert Consolidation

Alert management cannot rely on model output alone. It must also consider repeated alerts from the same machine, alert duration and severity, the machine's operating and maintenance state, and whether an alert is already acknowledged or tied to a work order. A five-minute duplicate-suppression window per equipment and anomaly type is a reasonable starting point, with exceptions preserved for severity escalation and safety events.

---

## 05. Equipment Health Management and Remaining Useful Life Prediction

![PHM and remaining useful life prediction](images/05_rul_prediction.png)

Anomaly detection answers "is the equipment deviating from normal?" Predictive maintenance goes further: "how is health changing?" and "when will maintenance be needed?"

Equipment health management (PHM) combines sensor features, equipment history, failure modes, and maintenance records. With enough data, an RUL model estimates time to a defined failure condition.

### RUL Model Design

- **Statistical / survival analysis:** e.g. Weibull distributions, given appropriate assumptions.
- **Time-series models:** LSTM or Transformer, tracking how health indicators evolve.
- **Domain features:** band energy, spectral entropy, vibration amplitude, and load, to sharpen recognition of real failure modes.

A Weibull distribution alone does not make a single machine's RUL accurate; per-machine prediction still needs observations and validation.

### From Prediction to Planning

RUL matters because it lets maintenance teams plan people, spare parts, and downtime in advance.

- **Routine monitoring:** RUL > 30 days — keep tracking at the established cadence.
- **Advance preparation:** 7–30 days — verify spare parts and maintenance resources.
- **Priority assessment:** < 7 days — schedule an engineering inspection and evaluate the maintenance window.

These thresholds are illustrative. Real ones depend on failure consequences, spare-part lead times, prediction uncertainty, and production scheduling. For safety-critical equipment, continued operation must not rest on the RUL estimate alone.

Root Mean Squared Error (RMSE) is an aggregate metric: it weights large misses more heavily and is not a per-prediction guarantee.

---

## 06. Edge Deployment and Model Lifecycle Management

![Edge deployment and low-code platform](images/06_edge_deployment.png)

After training, the next problem is deploying reliably across devices and lines — and restoring the previous version when an update fails. In a factory this is more than packaging a container: OS, hardware architecture, drivers, inference-engine versions, and equipment protocols all affect whether the model runs.

### 1. Standardized Packaging

Bundle the model, inference application, dependencies, and config into a versioned, traceable artifact. Run compatibility tests per hardware platform.

### 2. Shadow Deployment

Run the new model alongside the current model or rules without affecting production control. Compare outputs, latency, resource use, and representative failure cases. Cover a representative range of operating conditions; two weeks is a reference, not a rule for equipment with rare failures.

### 3. Canary Release

Deploy to a small subset, then expand — for example 5%, 20%, then 100%, with explicit acceptance criteria at each stage.

### 4. Monitoring and Rollback

Track inference failure rate, latency, resource use, and output distribution. If a threshold is crossed, stop the rollout and revert to a validated version.

On top of this, a self-service interface lets production engineers with the right permissions select versions, inspect deployment status, and roll back without touching model internals.

---

## 07. Edge Agent: Task Orchestration and Decision Boundaries

![Edge Agent](images/07_edge_agent.png)

An Edge Agent turns sensor data, model inference, equipment states, and maintenance procedures into an executable, traceable workflow.

It does not need an LLM for every decision. For tasks with strict latency and well-defined inputs and outputs, conventional logic or lightweight models are easier to test and validate. Agents fit cross-tool coordination, information integration, and multi-step execution.

### Task Allocation at the Edge

- **Real-time signal processing:** Acquisition, feature extraction, and necessary low-latency inference at the edge.
- **State assessment and orchestration:** Combine anomaly scores, RUL, equipment state, and maintenance records to decide whether further inspection or a work order is needed.
- **Equipment control and safety:** Executed by systems with explicit control logic and validated safety mechanisms. Free-form text or unvalidated model output must never become a high-risk control command.

Workflow frameworks such as LangGraph manage agent state, tool calls, retries, and branches. A model router can pick a model or rule engine based on task complexity, latency, and available compute. Neither guarantees real-time behavior or safety — execution time, error handling, resource limits, and exceptional paths still need testing.

### Handling Disconnections

The network is down. Should the Agent keep working or stop?

Essential monitoring and local state assessment keep running on predefined rules when upstream is lost. If the system cannot confirm its own state, it enters a predefined degraded mode — and what each device does in that mode comes from equipment-specific risk analysis, not from a general-purpose Agent.

Keep three concepts distinct:

1. **Offline availability:** Can local monitoring or inference continue during an outage?
2. **Task success:** Can the Agent complete tool calls, state updates, and work orders?
3. **Equipment safety:** Do existing controllers still protect the equipment during failures?

Task success cannot substitute for safety validation. For OHT and other high-risk equipment, safety must rest on independent mechanisms and verification.

---

## 08. Industrial RAG: Making Equipment Knowledge Searchable and Traceable

![Industrial RAG](images/08_industrial_rag.png)

Factory knowledge lives beyond equipment manuals — in maintenance logs, fault analysis reports, engineering notes, and historical work orders. Formats, naming, and quality are inconsistent. Dumping documents into a vector database can produce fluent answers that are neither correct nor applicable to the equipment's current state.

Industrial RAG is therefore about traceability first: connecting questions, retrieved evidence, and source documents.

### Knowledge Pipeline

1. **Document preparation and access control:** Convert formats, remove duplicates, identify versions, handle sensitive data, and preserve provenance and permissions.
2. **Semantic chunking and indexing:** Split documents by structure and content, then generate vector representations.
3. **Hybrid retrieval:** Combine BM25, vector search, and metadata filtering to cope with terminology, equipment IDs, and near-duplicate documents.
4. **Reranking:** Reassess candidate relevance to the question.
5. **Answer generation and citations:** Generate from retrieved evidence and cite original documents, versions, and pages so users can verify.

### Enterprise Constraints

Deploying RAG in a factory raises questions about document-level permissions in retrieval results, whether the model can reach unauthorized data, and how conflicting or outdated documents are handled.

Maintenance recommendations should clearly separate what the source documents state from what the model inferred. When evidence is insufficient, the system should say so rather than invent a complete-looking procedure.

Indexes and query logs need retention periods, auditing, and access permissions matched to data sensitivity.

---

## 09. MLOps: Continuous Monitoring After Model Deployment

![MLOps and continuous learning](images/09_mlops.png)

The model performs well on the test set. Then what?

Component wear, maintenance activity, load changes, or process changes can shift the data distribution away from training. Deployed models therefore need continuous monitoring and a workflow connecting detection, evaluation, and version updates.

### Drift Monitoring

Depending on the data, use PSI, the KS test, or other distribution-difference measures against a baseline. PSI above 0.25 is a common warning threshold, but exceeding it does not mean the model has failed; thresholds should follow data distributions, feature behavior, and validation results.

Monitor missing data, sensor anomalies, inference latency, and output distribution too, so sensor failures are not misread as model drift. A seven-day rolling baseline must not slowly absorb developing anomalies. More robust: dynamic baselines by operating mode, plus anomaly checks and explicit baseline-update conditions.

### Model Update Workflow

- Periodically evaluate data quality and model performance.
- Build candidate models for confirmed issues.
- Validate against historical data and relevant simulated scenarios.
- Compare old and new in shadow mode.
- Release incrementally after required reviews.
- Preserve version, data provenance, parameters, and validation records for traceability and rollback.

Automation is not about replacing a model the moment drift appears. It is about shortening detection, evaluation, and deployment while keeping the process controlled and auditable.

---

## 10. System Integration and Future Development Directions

![Strategic impact and growth plan (2026–2027)](images/10_star_impact.png)

These components must be integrated through clear data interfaces, access control, and error handling. Wiring services together does not by itself create an autonomous decision system.

### Version 1.0: Observable, Predictable, Maintainable Foundation

The first phase gives every component defined inputs and outputs, measurable monitoring, and failure handling, then validates performance on a limited set of devices and lines.

| System | Phase 1 Focus | Evaluation Metrics |
| --- | --- | --- |
| Real-time streaming platform | Establish data acquisition and feature-processing pipelines | Throughput, data loss rate, end-to-end latency |
| Anomaly detection | Reduce invalid alerts while preserving important events | False positive rate, false negative rate, F1 score |
| RUL prediction | Estimate equipment health and remaining useful life | RMSE, prediction intervals, maintenance decision effectiveness |
| Edge Agent | Coordinate models, tools, and maintenance workflows | Task success rate, latency, failure recovery capability |
| Industrial RAG | Establish document retrieval and answer traceability | Retrieval quality, answer correctness, citation traceability |
| MLOps | Establish model versioning and release workflows | Deployment cycle, rollback time, version traceability completeness |

### Version 2.0: From Single-Equipment Analytics to Cross-Equipment Collaboration

Once data processing, model quality, and deployment are stable per device, explore collaboration across devices and lines:

- Extend real-time processing to more devices while evaluating bandwidth and compute for higher sampling rates.
- Combine multiple sensors to improve detection of complex, multi-factor anomalies.
- Integrate RUL with spare-parts management, maintenance scheduling, and work-order systems.
- Build an equipment knowledge graph for relationship queries across documents and devices.
- Let Edge Agents exchange states and task results within their authorized boundaries.

Longer term, an **Edge Agent Swarm** could let multiple agents collaborate across devices or tasks. That adds state consistency, task conflicts, communication failures, access control, and error propagation — so responsibilities, permitted actions, and failure handling must be defined before expanding autonomy.

---

## 11. Conclusion

![Thank You](images/11_thanks.png)

Building an Edge-AI system for a smart factory is more than combining sensors, machine-learning models, and an agent framework. The real work is system engineering: reliable data acquisition, models that run within constrained resources, anomaly results worth trusting, safe recovery from failed deployments, and AI recommendations that fit into equipment and maintenance workflows without breaking existing safety mechanisms.

Predictive maintenance and autonomous decision agents are not two separate capabilities. The former provides condition and risk information; the Agent turns it into traceable workflows. Data governance, model monitoring, and safety controls keep the whole system reliable over time.

The priority is not full autonomy from day one. Make each component observable, verifiable, and recoverable first, then expand the scope of AI-assisted decisions — because **AI capability and system responsibility boundaries must be defined together for the technology to work on the factory floor.**

---

## Appendix: How to Read the Numbers

Figures here come from past project experience and interview material. They explain design trade-offs; they are not performance promises.

- **Source and scope.** Some original test records are no longer retrievable, and none of these numbers has been independently revalidated. Company, customer, equipment, and system details are de-identified or generalized.
- **Measurement basis matters more than the number.** Latency and cold start depend on start and end points. A false-positive rate depends on whether the denominator is normal samples or all alerts. Availability depends on the window and criteria. Document counts and container image size are equally ambiguous: source documents, versions, or chunks; one service or the full runtime. Read averages with their distribution and tail.
- **Improvement is not attributable to a single cause.** Downtime, maintenance cost, abnormal-stop rate, and hours saved are shaped by workflows, spare-parts strategy, equipment upgrades, and staffing. If the model's contribution cannot be isolated, do not credit all of it to AI.
- **Not industry benchmarks.** These figures hold for specific equipment, loads, and deployment conditions. Another line or failure mode can produce entirely different results.

Nothing here is a basis for operating specific equipment, implementing safety controls, or making maintenance decisions.
