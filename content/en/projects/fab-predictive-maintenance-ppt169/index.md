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

{{< audio src="audio/morty-too-long-dont-read.m4a" caption="TL;DR — narrated by Morty" >}}

## Introduction

This article turns an 11-slide interview deck into a technical reference on the Smart Fab Edge AI architecture: real-time processing, anomaly detection, remaining useful life (RUL) prediction, edge deployment, industrial knowledge retrieval, and AI agent boundaries. The hard part is not deployment but running models under tight latency, compute, and cost constraints while meeting reliability requirements and integrating with existing controls, maintenance workflows, and factory systems.

> **Intellectual Property and Usage Notice:** This article is for technical exchange, architecture discussion, and demonstration of personal capability. The content has been de-identified. It contains no confidential customer data, trade secrets, or non-public project information. Use and redistribution of the text and diagrams are subject to the author's published licensing terms.

---

## 01. System Objectives and Design Assumptions

![Cover: Smart Fab Edge-AI Predictive Maintenance and Autonomous Decision Agent System](images/01_cover.png)

Semiconductor lines combine many equipment types, high-rate sensors, expensive downtime, and strict latency and reliability requirements on some control loops. The architecture therefore pairs edge computing with centralized management: latency-sensitive work stays in the factory, while centralized services handle model management, cross-equipment analytics, and deployment. Firewall and audit rules make off-site real-time analysis impractical.

- **Data governance and security:** Classify sensor data, equipment information, and maintenance records; process sensitive data in-factory and follow internal rules for transfers.
- **Edge resources:** Size models, inference frequency, and buffering against each device's CPU, memory, and accelerators.
- **Detection usability:** Beyond accuracy, weigh false-positive/negative rates, alert volume, and on-site workload.
- **Safety and fault isolation:** AI assesses anomalies and recommends maintenance; safety-critical control stays with validated systems and safety mechanisms.

---

## 02. End-to-End Technical Architecture

![End-to-end technical architecture map](images/02_architecture.png)

The architecture has six layers. The first three handle acquisition, streaming, and feature extraction; the fourth forms a judgment; the fifth turns it into tasks; the sixth handles system integration and safety control.

| Layer | Name | Key Technologies and Responsibilities |
| --- | --- | --- |
| 01 | Sensing and Data Acquisition | MCUs, IO-Link, vibration/current/pressure sensors |
| 02 | Streaming and Time-Series Data | Kafka, InfluxDB, ring buffers, timestamps, and synchronization |
| 03 | Signal Processing | FFT, wavelet transforms, time-domain and frequency-domain feature extraction |
| 04 | AI Analytics and PHM | Isolation Forest, Autoencoders, LSTM/Transformer, and RUL prediction |
| 05 | Edge Agent and Task Orchestration | State management, tool routing, workflow orchestration, and model selection |
| 06 | Integration and Safety Control | SECS/GEM, MES/EAP APIs, authorization, and safety middleware |

Edge devices handle low-latency processing and inference; the central platform manages models, cross-equipment analytics, and deployment. Kafka handles messaging, InfluxDB stores time series, and ring buffers cap memory for continuous streams. These components need not form one path; the mix follows data rate, latency, and deployment constraints. Even if a model returns in milliseconds, end-to-end latency must include acquisition, signal processing, inference, communication, and controller execution.

---

## 03. High-Throughput Data Streaming and Signal Processing

![High-throughput data streaming and signal processing](images/03_streaming.png)

In high-frequency sensing, the challenge is rarely accuracy — it is the continuous stream.

### Data Volume and Scope

Assume 20 machines, three channels each, 2 kHz continuous sampling, and 4 bytes per sample.

Per second:

$$
20 \times 3 \times 2{,}000 \times 4 = 480{,}000\ \text{bytes/s}
$$

Per day:

$$
480{,}000 \times 86{,}400 = 41{,}472{,}000{,}000\ \text{bytes/day}
$$

That is about **41.47 GB/day** in decimal units (1 GB = \(10^9\) bytes). This counts raw values only — not timestamps, packet overhead, indexes, storage formats, or metadata. With those costs, 50 GB/day is a reasonable planning figure; the exact number depends on format and retention.

The 20-machine figure is illustrative, not a scale claim. **Managed fleet size** (machines connected) and **high-frequency processing scale** (machines streaming raw waveforms at 2 kHz) are different metrics; the latter depends on how many machines sample at high frequency, channel count, sampling rate, and retention policy. Managing 500+ machines does not mean all stream at that rate.

### Signal Processing Pipeline

1. **Acquisition:** Capture vibration, current, and pressure signals, handling timestamps, missing values, and data quality.
2. **Windowing:** Split continuous signals into fixed-length windows; length and overlap follow equipment characteristics and analysis needs.
3. **Feature extraction:** Apply FFT, wavelet transforms, and statistics to compute RMS, spectral entropy, and band energy.
4. **Output:** Emit fixed-format feature vectors for anomaly detection and health models.

A 64-dimensional feature vector can replace the full waveform and cut downstream compute, but suitability depends on anomaly type and model requirements; lost information cannot be recovered.

### Edge Optimization

- Process in batches or windows; use preallocated ring buffers to cut allocation and copying.
- Separate high-frequency signal processing from lower-frequency state analysis.
- Apply different retention and transmission policies to raw data, features, and events.
- Monitor queue length, data loss, CPU usage, and end-to-end latency.

---

## 04. Two-Stage Anomaly Detection

![Two-stage anomaly detection](images/04_anomaly_detection.png)

Equipment failure datasets are heavily imbalanced: normal data is easy to collect, real failures are rare, so supervised learning lacks enough labeled failures.

False alarms are the other practical problem. Most come from material changeover or warm-up, when the vibration spectrum briefly departs from normal. The model fires repeatedly while the machine is fine — enough noise for staff to start ignoring it.

The architecture therefore separates cheap initial screening from deeper assessment.

### Stage 1: Rapid Screening

Isolation Forest flags samples that differ from observed data. It is lightweight enough for constrained edge environments; its job is to shortlist data, not declare failure.

### Stage 2: In-Depth Assessment

An Autoencoder measures reconstruction error against learned normal patterns. Thresholds can be set per equipment type, operating state, and sensor channel, so normal process transitions and load changes are not classified as failures.

### Alert Consolidation and Suppression

Alert management cannot rely on model output alone: consider repeated alerts, duration and severity, operating and maintenance state, and whether an alert is already acknowledged or tied to a work order. A five-minute duplicate-suppression window per equipment and anomaly type is a reasonable start, with exceptions for severity escalation and safety events; do not hide new risks just to reduce notifications.

---

## 05. Equipment Health Management and Remaining Useful Life Prediction

![PHM and remaining useful life prediction](images/05_rul_prediction.png)

Anomaly detection answers "is the equipment deviating from normal?" Predictive maintenance goes further: "how is health changing?" and "when will maintenance be needed?"

Equipment health management (PHM) combines sensor features, equipment history, failure modes, and maintenance records. With enough data, an RUL model estimates time to a defined failure condition.

### RUL Model Design

- **Statistical / survival analysis:** e.g. Weibull survival distributions under suitable assumptions to describe time to failure.
- **Time-series models:** LSTM or Transformer, tracking how health indicators evolve.
- **Domain features:** band energy, spectral entropy, vibration amplitude, and load to sharpen failure-mode recognition.

Each approach fits different conditions. A Weibull distribution alone cannot guarantee an accurate RUL for one machine; prediction still needs observations and validation.

### From Prediction to Maintenance Planning

RUL is for planning labor, spare parts, and downtime, not just a time value.

- **Routine monitoring:** RUL > 30 days — keep tracking at the established cadence.
- **Advance preparation:** 7–30 days — verify spare parts and maintenance resources.
- **Priority assessment:** < 7 days — schedule an engineering inspection and evaluate the maintenance window.

These thresholds are illustrative; real ones depend on failure consequences, spare-part lead times, prediction uncertainty, and production scheduling. Safety-critical equipment must not keep running on the RUL estimate alone. RUL is an estimate, not a guarantee; keep human review in the maintenance window and never turn it directly into a shutdown command.

---

## 06. Edge Deployment and Model Lifecycle Management

![Edge deployment and low-code platform](images/06_edge_deployment.png)

After training, the next problem is deploying reliably across devices and lines — and restoring the previous version when an update fails. In a factory this is more than packaging a container: OS, hardware architecture, drivers, inference-engine versions, and equipment protocols all affect whether the model runs. The process has four stages.

### 1. Standardized Packaging

Bundle the model, inference application, dependencies, and config into a versioned, traceable artifact, with compatibility tests per hardware platform.

### 2. Shadow Deployment

Run the new model alongside the current model or rules without affecting production control. The shadow period should cover representative equipment states and compare outputs, latency, resource use, and failure cases; two weeks is a reference period, not a fixed rule, and equipment with rare failures needs a longer shadow period.

### 3. Staged Canary Release

Deploy to a small subset, then expand — for example 5%, 20%, then 100%, with explicit acceptance criteria at each stage.

### 4. Monitoring and Rollback

Track inference failure rate, latency, resource use, and output distribution. If a threshold is crossed, stop the rollout and revert to a validated version following a predefined process.

---

## 07. Edge Agent: Task Orchestration and Decision Boundaries

![Edge Agent](images/07_edge_agent.png)

An Edge Agent turns sensor data, model inference, equipment states, and maintenance procedures into a traceable workflow. It does not need a large language model (LLM) for every decision: tasks with clear latency requirements and fixed inputs/outputs are easier to test with conventional logic or lightweight models. Agents fit cross-tool coordination and multi-step execution.

### Task Allocation at the Edge

- **Real-time signal processing:** Acquisition, feature extraction, and necessary low-latency inference at the edge.
- **State assessment and orchestration:** Combine anomaly scores, RUL, equipment state, and maintenance records to decide on inspection or a work order.
- **Equipment control and safety:** Execution belongs to systems with explicit control logic and validated safety mechanisms. Free-form text or unvalidated model output must never become a high-risk control command.

Workflow frameworks such as LangGraph manage state, tool calls, retries, and branches; a model router picks a model or rule engine by task complexity, latency, and compute. The framework itself does not guarantee real-time behavior or safety.

### Handling Disconnections

Essential monitoring and local state assessment keep running on predefined rules when upstream is lost. If the system cannot confirm its own state, it enters a predefined degraded mode; what each device does then comes from equipment-specific risk analysis, not a general-purpose Agent. Some equipment may need to derate; others should stop specific actions or hand control back to existing controllers.

Keep three concepts distinct:

1. **Offline availability:** Can local monitoring or inference continue during an outage?
2. **Task success:** Can the Agent complete tool calls, state updates, and work orders?
3. **Equipment safety:** Do existing controllers still protect the equipment during failures?

The three are evaluated differently; task success cannot substitute for safety validation. For overhead hoist transport (OHT) and other high-risk equipment, safety must rest on independent mechanisms and verification.

---

## 08. Industrial RAG: Making Equipment Knowledge Searchable and Traceable

![Industrial RAG](images/08_industrial_rag.png)

Factory knowledge lives in manuals, maintenance logs, fault reports, engineering notes, and work orders. Formats and quality vary, and dumping documents into a vector database can produce fluent answers that are neither correct nor applicable to the current equipment state. Industrial retrieval-augmented generation (RAG) is therefore about traceability: connecting questions, retrieved evidence, and source documents.

### Knowledge Pipeline

1. **Document preparation and access control:** Convert formats, remove duplicates, identify versions, handle sensitive data, and preserve provenance and permissions.
2. **Semantic chunking and indexing:** Split documents by structure and content, then generate vector representations.
3. **Hybrid retrieval:** Combine BM25, vector search, and metadata filtering to handle terminology, equipment IDs, and near-duplicate documents.
4. **Reranking:** Reassess candidate relevance to the question.
5. **Answer generation and citations:** Generate answers from retrieved evidence and cite documents, versions, and pages so users can verify.

### Enterprise Constraints

Deploying RAG in a factory means enforcing document-level permissions, preventing unauthorized data access, and handling conflicting or outdated documents.

Maintenance recommendations should separate source statements from model inference; when evidence is insufficient, the system should say so rather than invent a procedure. Retrieved documents and tool outputs must be treated as untrusted input; prompt injection or poisoned documents must not expand permissions or trigger control actions. Index and query logs also need retention periods, audits, and access controls matched to data sensitivity.

---

## 09. MLOps: Continuous Monitoring After Model Deployment

![MLOps and continuous learning](images/09_mlops.png)

The model performs well on the test set. Then what?

Component wear, maintenance activity, load changes, or process changes shift the input distribution away from the training set. Models therefore need continuous monitoring and a workflow connecting detection, evaluation, and updates.

### Drift Monitoring

Use PSI (Population Stability Index), the KS test, or other distribution-difference measures against a baseline. PSI above 0.25 is a common warning threshold, but exceeding it does not mean the model failed; set thresholds from data distributions, feature behavior, and validation results. Also monitor missing data, sensor anomalies, inference latency, and output distribution, so sensor failures are not misread as drift. A seven-day rolling baseline must not absorb developing anomalies; use dynamic baselines by operating mode, with anomaly checks and explicit update conditions.

### Model Update Workflow

A more complete workflow includes:

- Periodically evaluate data quality and model performance.
- Build candidates for confirmed issues; validate on historical and simulated data.
- Compare old and new in shadow mode, then release incrementally after review.
- Preserve version, provenance, parameters, and validation records for traceability and rollback.

Automation does not replace a model the moment drift appears; it shortens detection, evaluation, and deployment while keeping the process controlled and auditable.

---

## 10. System Integration and Future Development Directions

![Strategic impact and growth plan (2026–2027)](images/10_star_impact.png)

The preceding sections cover streaming, anomaly detection and RUL, Agent coordination, RAG, and MLOps—each addressing a different layer.

These components must be integrated through clear data interfaces, access control, and error handling. Wiring services together does not create an autonomous decision system.

### Version 1.0: Observable, Predictable, Maintainable Foundation

Phase 1 gives every component defined inputs and outputs, measurable monitoring metrics, and failure handling, then validates on a limited set of devices and lines.

| System | Phase 1 Focus | Evaluation Metrics |
| --- | --- | --- |
| Real-time streaming platform | Establish data acquisition and feature-processing pipelines | Throughput, data loss rate, end-to-end latency |
| Anomaly detection | Reduce invalid alerts while preserving important events | False positive rate, false negative rate, F1 score |
| RUL prediction | Estimate equipment health and remaining useful life | RMSE (root mean squared error), prediction intervals, maintenance decision effectiveness |
| Edge Agent | Coordinate models, tools, and maintenance workflows | Task success rate, latency, failure recovery capability |
| Industrial RAG | Establish document retrieval and answer traceability | Retrieval quality, answer correctness, citation traceability |
| MLOps | Establish model versioning and release workflows | Deployment cycle, rollback time, version traceability completeness |

### Version 2.0: From Single-Equipment Analytics to Cross-Equipment Collaboration

Explore collaboration across devices and lines only after data processing, model quality, and deployment are stable per device:

- Extend processing to more devices and combine sensors to catch complex anomalies, while evaluating bandwidth and compute at higher sampling rates.
- Integrate RUL with spare-parts management, maintenance scheduling, and work-order systems.
- Build an equipment knowledge graph for relationship queries across documents and devices.
- Let Edge Agents exchange states and task results within their authorized boundaries.

Longer term, an **Edge Agent Swarm** could let agents collaborate across devices or tasks, but it introduces state-consistency problems, task conflicts, communication failures, access-control gaps, and error propagation; define responsibilities, permitted actions, and failure handling first.

---

## 11. Conclusion

![Thank You](images/11_thanks.png)

Building a smart-factory Edge AI system is more than combining sensors, models, and an agent framework. The real work is system engineering: reliable data, models that run within constrained resources, trustworthy anomaly results, safe recovery from failed deployments, and AI recommendations that do not break existing safety mechanisms.

Predictive maintenance and autonomous decision agents are not separate: the former provides condition and risk information, and the Agent turns it into traceable workflows. Data governance, model monitoring, and safety controls keep the system reliable. The priority is not full autonomy from day one — make each component observable, verifiable, and recoverable first, then expand AI-assisted decisions. That is also what it takes for AI to reach the factory floor.

---

## Appendix: A Minimum Checklist for Performance Figures

This article deliberately omits project-specific performance figures and keeps only reproducible estimates and design thresholds. If such figures are cited, the following four checks are the minimum.

- **Source and scope.** Confirm whether the original test records are retrievable and whether the numbers were independently validated. Company, customer, equipment, and system details should be de-identified or generalized.
- **Measurement basis matters more than the number.** The same metric can vary by an order of magnitude depending on definitions: latency and cold start on start and end points, false-positive rate on the denominator, availability on the measurement window and criteria, and document counts and image size on what is included. Pair averages with distributions and tail values.
- **Improvement is not attributable to a single cause.** Downtime, maintenance cost, abnormal-stop rate, and hours saved are shaped by workflows, spare-parts strategy, equipment upgrades, and staffing. If the model's contribution cannot be isolated, do not credit all of it to AI.
- **Not an industry benchmark.** Figures hold for specific equipment, load, and deployment conditions; another line or failure mode can produce very different results.

Nothing here is a basis for operating specific equipment, implementing safety controls, or making maintenance decisions.
