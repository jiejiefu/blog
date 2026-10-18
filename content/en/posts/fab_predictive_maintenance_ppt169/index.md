---
featured: true
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
  image: "https://jiejiefu.github.io/blog/posts/fab_predictive_maintenance_ppt169/images/01_cover.png"
  alt: "Smart Fab Edge-AI Predictive Maintenance Cover"
  hidden: false
---

## Introduction

This article documents the Smart Fab Edge AI system architecture I presented in an interview presentation, expanding the original 11-slide deck into a more comprehensive technical reference.

Starting with equipment sensor data, the article walks through real-time data processing, anomaly detection, Remaining Useful Life (RUL) prediction, edge deployment, industrial knowledge retrieval, and the decision-making capabilities and control boundaries of AI agents. Beyond the technical components, it discusses the design considerations at each layer and the trade-offs among latency, computational resources, reliability, and operational maintenance costs.

The central challenge is not simply deploying AI models in a factory. It is designing a system that can operate continuously under constrained computing resources while integrating with existing equipment controls, maintenance workflows, and factory information systems.

The equipment scale and selected performance figures described in this article are drawn from previous project experience and interview materials. Information concerning companies, customers, equipment configurations, and internal systems has been anonymized or generalized. Because some original test records are no longer available, the performance figures presented here are not claimed to have undergone independent revalidation. Readers should interpret each metric according to its definition and scope rather than treating it as an industry benchmark applicable to every factory.

> **Intellectual Property and Usage Notice:** This article is intended for technical knowledge sharing, system architecture discussions, and demonstration of personal technical capabilities. The content has been anonymized and adjusted where necessary. It should not contain confidential customer data, trade secrets, or non-public internal project information. The use and redistribution of the text and diagrams are subject to the licensing terms published by the author.

---

## 01. System Objectives and Design Assumptions

![Cover: Smart Fab Edge-AI Predictive Maintenance and Autonomous Decision Agent System](images/01_cover.png)

Production lines in semiconductor manufacturing share several operational characteristics: a wide variety of equipment, high-frequency sensor data, substantial downtime costs, and control processes with strict latency and reliability requirements.

Sending all data to the cloud for centralized analysis and decision-making can simplify management. However, it also increases network transmission overhead, data governance complexity, and system dependencies. This architecture therefore combines edge computing with centralized management, keeping latency-sensitive processing within the factory.

The overall design focuses on four key considerations:

- **Data governance and security:** Sensor data, equipment information, and maintenance records are handled according to data classification and access control policies. Sensitive data should, in principle, undergo necessary processing and management within the factory. Cross-system data transfers must comply with internal security requirements.
- **Edge computing resources:** Model size, inference frequency, and buffering strategies are selected according to the available CPU, memory, and accelerator resources of each edge device.
- **Anomaly detection usability:** Model accuracy alone is insufficient. False-positive rates, false-negative rates, alert frequency, and the resulting workload for on-site personnel must also be evaluated.
- **Equipment safety and fault isolation:** AI models can provide anomaly assessments and maintenance recommendations, but safety-critical control logic must remain under the responsibility of validated control systems and established safety mechanisms.

These assumptions directly influence the subsequent architectural layers, model selection, and permission design for AI agents.

---

## 02. End-to-End Technical Architecture

![End-to-end technical architecture map](images/02_architecture.png)

The overall architecture consists of six layers. The sensing and data acquisition layer captures equipment status, while the streaming and signal processing layers organize and transform incoming data. The AI analytics layer performs anomaly detection and health assessment. The upper layers coordinate decisions, maintenance workflows, and the necessary control interfaces.

| Layer | Name | Key Technologies and Responsibilities |
| --- | --- | --- |
| 01 | Sensing and Data Acquisition | MCUs, IO-Link, vibration/current/pressure sensors |
| 02 | Streaming and Time-Series Data | Kafka, InfluxDB, ring buffers, timestamps, and synchronization |
| 03 | Signal Processing | FFT, wavelet transforms, time-domain and frequency-domain feature extraction |
| 04 | AI Analytics and PHM | Isolation Forest, Autoencoders, LSTM/Transformer, and RUL prediction |
| 05 | Edge Agent and Task Orchestration | State management, tool routing, workflow orchestration, and model selection |
| 06 | Integration and Safety Control | SECS/GEM, MES/EAP APIs, authorization, and safety middleware |

Within this architecture, edge devices primarily handle low-latency data processing and inference. The centralized platform manages models, performs cross-equipment analytics and training, and coordinates model deployment.

Responsibilities must also be clearly separated among individual components. Kafka is suitable for message delivery and decoupling data streams. InfluxDB supports time-series storage and querying. Ring buffers are useful for continuous data processing with predictable memory consumption.

These components do not necessarily need to be connected in a single linear pipeline. Their actual combination depends on data frequency, latency requirements, and the deployment environment.

Similarly, edge inference and equipment control are not the same thing. Even if a model produces a result within a few milliseconds, end-to-end latency must account for data acquisition, signal processing, inference, communication, and controller execution time.

---

## 03. High-Throughput Data Streaming and Signal Processing

![High-throughput data streaming and signal processing](images/03_streaming.png)

In high-frequency sensing scenarios, the first challenge is often not model accuracy but how to process a continuous stream of incoming data efficiently.

### Data Volume Estimation and Scope

Consider a representative data scenario with 20 machines, each equipped with three sensor channels. Each channel continuously samples at 2 kHz, and each sample is stored as a 4-byte value.

The raw numerical data generated per second is:

$$
20 \times 3 \times 2{,}000 \times 4 = 480{,}000\ \text{bytes/s}
$$

The corresponding daily data volume is:

$$
480{,}000 \times 86{,}400 = 41{,}472{,}000{,}000\ \text{bytes/day}
$$

This is approximately **41.47 GB per day**, using decimal units where 1 GB = \(10^9\) bytes.

This estimate includes only the raw sensor values. It excludes timestamps, communication packet overhead, indexes, database storage formats, and other metadata. Once these additional overheads are included, actual transmission or storage requirements could approach 50 GB per day, depending on the data format and system design.

The 20-machine scenario is an illustrative calculation, not a statement that the entire system manages only 20 machines. Nor should this figure be directly interpreted as the total data volume for a system managing 500 or more machines.

In practice, **the number of managed machines and the scale of high-frequency raw data processing are two distinct metrics**.

The managed equipment scale describes how many machines the system can connect to or manage. The high-frequency data processing scale depends on the number of machines actually using high-frequency sampling, the number of channels per machine, sampling rates, and data retention policies.

Consequently, a system managing more than 500 machines does not necessarily receive continuous raw waveforms from every machine at the same sampling frequency. When describing system scale, these two figures should not be conflated.

### Signal Processing Pipeline

The data pipeline can be divided into four stages:

1. **Raw data acquisition:** Capture sensor signals such as vibration, current, and pressure while handling timestamps, missing values, and data quality issues.
2. **Windowing:** Divide continuous signals into fixed-length data windows. Window length and overlap ratio are configured according to equipment characteristics and analytical requirements.
3. **Feature extraction:** Apply FFT, wavelet transforms, and statistical methods to calculate features such as RMS, spectral entropy, and energy within specific frequency bands.
4. **Feature output:** Convert the results into fixed-format feature vectors for downstream anomaly detection and equipment health models.

For example, a model might consume a 64-dimensional feature vector instead of receiving the complete raw waveform every time. This can reduce computational overhead in downstream processing, although its suitability depends on the anomaly patterns and model requirements. If feature extraction discards important information, downstream models cannot recover it.

### Edge Performance Optimization

Several optimization strategies can be applied at this layer:

- Process data in batches or windows to reduce the overhead of handling individual samples.
- Use preallocated ring buffers to reduce the frequency of memory allocation and data copying.
- Separate high-frequency signal processing from lower-frequency equipment state analysis.
- Apply different retention and transmission policies to raw data, extracted features, and event data instead of treating all data identically.
- Continuously monitor queue lengths, data loss rates, CPU utilization, and end-to-end latency.

The original presentation reported the following performance comparisons:

- Processing latency decreased from 45 ms to below 12 ms.
- CPU utilization decreased from 100% to 32%.
- Throughput increased by approximately 2.5 times.

Reducing latency from 45 ms to below 12 ms represents a latency reduction of at least approximately 73.3%.

However, latency and throughput are different metrics. The throughput improvement cannot be derived directly from the latency reduction. A meaningful throughput comparison requires measuring the amount of data actually processed per unit of time under identical or comparable input loads.

CPU utilization must also be interpreted in the context of the measurement interval, core count, and test workload. The original figures of 100% and 32% are retained here as comparisons reported in the existing presentation. Without access to the original test records, they should not be interpreted as steady-state utilization levels that apply to every deployment environment.

---

## 04. Two-Stage Anomaly Detection

![Two-stage anomaly detection](images/04_anomaly_detection.png)

Equipment failure datasets are typically highly imbalanced. Normal operating data is relatively easy to collect, while actual failure cases are comparatively rare. As a result, purely supervised learning approaches often face a shortage of labeled failure data.

False alarms present another practical challenge. Even if a model can identify certain anomalies, generating large numbers of alerts that do not lead to actionable responses can undermine the confidence of on-site personnel.

This architecture therefore adopts a layered detection strategy that separates lightweight initial screening from more detailed anomaly assessment.

### Stage 1: Rapid Screening

Isolation Forest can identify samples that differ from the distribution of previously observed data. Because it is relatively lightweight, it can be suitable for some resource-constrained edge environments.

The objective of the first stage is to quickly identify data that warrants further investigation, rather than automatically interpreting every anomaly score as evidence of equipment failure.

### Stage 2: In-Depth Assessment

An Autoencoder can evaluate differences between incoming data and learned normal operating patterns through reconstruction error.

In practice, thresholds can be configured according to equipment type, operating state, and sensor channel. This helps prevent normal process transitions or load variations from being indiscriminately classified as failures.

### Alert Consolidation and Suppression

Alert management should not depend solely on model outputs. The system should also consider:

- Repeated alerts from the same machine within a short period.
- Alert duration and anomaly severity.
- The machine's current operating mode and maintenance status.
- Whether an alert has already been acknowledged or associated with a maintenance work order.

For example, the system could apply a five-minute duplicate-alert suppression window for the same equipment and anomaly type.

However, this mechanism must preserve exceptions for severity escalation and safety-related events. Reducing notifications must never conceal emerging risks.

The original presentation reported the following metrics:

- The false-positive rate decreased from 15% to 3.2%.
- The F1-score reached 0.94.
- The average fault detection time decreased by 40%.

These metrics describe different aspects of system performance.

- **False-positive rate:** The evaluation must first establish whether this refers to the proportion of normal samples incorrectly classified as anomalous (False Positive Rate, FPR) or the proportion of alerts that are false alarms. These metrics have different denominators and are not interchangeable.
- **F1-score:** The harmonic mean of precision and recall. It helps assess the balance between these two metrics but must still be interpreted in the context of the evaluation dataset and failure categories.
- **Fault detection time:** The starting point must be clearly defined. It could be the actual onset of a failure, the first appearance of anomalous features, or the first effective alert generated by the system.

Furthermore, if the reduction in false alarms resulted from a combination of model improvements, threshold tuning, and duplicate-alert suppression, the outcome should be understood as an improvement in the overall alerting workflow rather than attributed entirely to the model itself.

Because the original test data is unavailable, the figures in this article are retained as descriptions of previously reported project results. They are not presented as independently validated or universally applicable model performance benchmarks.

---

## 05. Equipment Health Management and Remaining Useful Life Prediction

![PHM and remaining useful life prediction](images/05_rul_prediction.png)

Anomaly detection primarily answers the question, "Is the equipment currently deviating from its normal operating condition?"

Predictive maintenance goes a step further by addressing two additional questions: "How is the equipment's health changing over time?" and "When might maintenance be required?"

Prognostics and Health Management (PHM) typically integrates sensor features, equipment history, failure modes, and maintenance records. When sufficient data is available, a Remaining Useful Life (RUL) model can estimate how much time remains before equipment reaches a defined failure condition.

### RUL Model Design

Different approaches can be selected according to the available data and prediction requirements:

- **Statistical methods and survival analysis:** Methods such as the Weibull distribution can characterize equipment failure-time distributions under appropriate assumptions.
- **Time-series models:** LSTM or Transformer architectures can analyze how equipment health indicators evolve over time.
- **Domain-specific features:** Frequency-band energy, spectral entropy, vibration amplitude, and equipment load can be combined to improve the model's ability to recognize actual failure modes.

These methods have different applicability conditions. A Weibull distribution alone does not guarantee accurate RUL predictions for an individual machine. Predicting the remaining life of a specific piece of equipment still requires appropriate observations and model validation.

### From Predictions to Maintenance Planning

The value of RUL is not simply the generation of a time estimate. It enables maintenance teams to plan personnel, spare parts, and equipment downtime in advance.

For example, predicted RUL can be divided into three maintenance planning intervals:

- **Routine monitoring:** Predicted RUL exceeds 30 days. Continue monitoring equipment condition at the established frequency.
- **Advance preparation:** Predicted RUL is between 7 and 30 days. Verify spare-part availability and maintenance resources.
- **Priority assessment:** Predicted RUL is below 7 days. Arrange an engineering inspection and evaluate the maintenance schedule.

These intervals are illustrative. Actual thresholds should be determined according to the consequences of equipment failure, spare-part lead times, prediction uncertainty, and production scheduling requirements.

For equipment involving safety risks, decisions about continued operation must not rely solely on the RUL estimate.

The original presentation reported the following metrics:

- RUL prediction RMSE of no more than 32 hours.
- A 42% reduction in unplanned downtime.
- A 28% reduction in maintenance costs.

RMSE (Root Mean Squared Error) measures the overall error between predicted and actual values. It is calculated as follows:

$$
\mathrm{RMSE} = \sqrt{\frac{1}{n}\sum_{i=1}^{n}(\hat{y}_i - y_i)^2}
$$

where \(\hat{y}_i\) represents the predicted value and \(y_i\) represents the actual value.

RMSE gives greater weight to larger prediction errors. Therefore, an RMSE of no more than 32 hours does not mean that every individual prediction is guaranteed to be within 32 hours of the actual value.

RUL evaluation must also account for the prediction time, equipment type, failure definition, and evaluation dataset selection methodology. Results from different equipment types or failure modes should not be combined or compared without considering these differences.

The reported reductions of 42% in unplanned downtime and 28% in maintenance costs should likewise be treated as overall improvement metrics within a specific project scope. If the contributions of the AI model cannot be separated from changes in maintenance workflows, spare-parts strategies, equipment upgrades, or other operational factors, the entire improvement should not be attributed directly to the AI model.

---

## 06. Edge Deployment and Model Lifecycle Management

![Edge deployment and low-code platform](images/06_edge_deployment.png)

Once a model has been trained, another critical challenge remains: how can it be deployed reliably across different devices and production lines, while ensuring that the existing service can be restored if an update fails?

In a factory environment, deployment involves much more than packaging an application into a container. The operating system, hardware architecture, device drivers, inference engine versions, and equipment communication protocols can all affect whether a model runs correctly.

A robust deployment workflow can therefore be divided into the following stages.

### 1. Standardized Packaging

Package the model, inference application, dependencies, and configuration files into a versioned and traceable release artifact. Compatibility testing should also be performed for different hardware platforms.

### 2. Shadow Deployment

Run the new model alongside the current model or existing rule-based system without allowing it to directly affect production control decisions.

Compare output differences, inference latency, resource utilization, and representative failure cases to determine whether the new version meets the requirements for production deployment.

Shadow deployment should cover a representative range of equipment operating conditions. Two weeks may serve as a reference period, but it may not be sufficient or appropriate for equipment where failures are rare.

### 3. Canary Release

Deploy the new version to a small subset of devices before gradually expanding deployment. For example, rollout may proceed through 5%, 20%, and finally 100% of the target fleet.

Each stage should have clearly defined acceptance criteria and thresholds that must be satisfied before proceeding.

### 4. Monitoring and Rollback

Continuously monitor inference failure rates, latency, resource utilization, and the distribution of model outputs.

If any metric exceeds its predefined threshold, the system should stop expanding the rollout and follow an established procedure to revert to a previously validated version.

On top of this workflow, a self-service management interface can be provided for production engineers. Depending on their access permissions, users can select model versions, inspect deployment status, and initiate rollbacks without directly modifying internal model parameters.

The original presentation lists several project metrics:

- Container image size below 300 MB.
- Cold-start time below 30 seconds.
- Deployment cycle reduced from six months to two weeks.

These figures should be interpreted with clearly defined measurement boundaries. Container image size should distinguish between an individual service image and the complete runtime environment. Cold-start time should separately account for container startup, model loading, and the time required for the service to become ready.

The deployment cycle also needs a clearly defined start and end point. For example, it could measure the time from candidate release readiness to production deployment, or the entire process from initial requirements to a completed production rollout.

These figures can be retained as project-specific targets from the original material, but they should not be treated as universal benchmarks that every edge device can achieve.

---

## 07. Edge Agent: Task Orchestration and Decision Boundaries

![Edge Agent](images/07_edge_agent.png)

The role of an Edge Agent is to integrate sensor data, model inference, equipment states, and maintenance procedures into an executable and traceable workflow.

An Edge Agent does not necessarily need to invoke a large language model for every decision. For tasks with strict latency requirements and well-defined inputs and outputs, conventional program logic or lightweight models are often easier to test and validate.

An Agent is better suited to tasks involving cross-tool coordination, information integration, or multi-step execution.

### Task Allocation at the Edge

Within this architecture, responsibilities can be divided into three categories:

- **Real-time signal processing:** Perform data acquisition, feature extraction, and necessary low-latency inference at the edge.
- **State assessment and task orchestration:** Combine anomaly scores, Remaining Useful Life (RUL) estimates, equipment states, and maintenance records to determine whether further inspection is needed or a maintenance work order should be created.
- **Equipment control and safety handling:** Execute control actions through systems with explicit control logic and validated safety mechanisms. Free-form generated text or unvalidated model outputs must never be translated directly into high-risk control commands.

Workflow frameworks such as LangGraph can help manage Agent state, tool calls, retries, and execution branches. A Model Router can select an appropriate model or rule engine based on task complexity, latency requirements, and available computing resources.

However, adopting these frameworks does not automatically guarantee real-time performance or safety. Execution time, error handling, resource constraints, and exceptional execution paths must still be tested and validated.

### Handling Network Disconnections

Edge systems must account for network outages, unavailable centralized services, and model-serving failures.

A reasonable design ensures that essential monitoring and local state-assessment functions can continue operating according to predefined rules when upstream connectivity is lost. If the system cannot reliably determine its own state, it should enter a predefined degraded operating mode.

However, degraded operation does not mean that every device should take the same action. Some equipment may need to reduce its operating load, while other devices may need to stop specific operations or hand control back to an existing controller.

The appropriate response must be determined through equipment-specific risk analysis and safety engineering, rather than inferred autonomously by a general-purpose Agent.

Three concepts must be distinguished:

1. **Offline service availability:** Whether the edge system can continue performing its designated local monitoring or inference tasks during a network outage.
2. **Task execution success rate:** Whether the Agent can complete tool calls, state updates, maintenance work-order creation, and other workflow steps.
3. **Equipment safety:** Whether existing controllers and safety mechanisms continue to protect the equipment during communication failures, model anomalies, or task execution errors.

These concepts require different evaluation methods. An Agent's task success rate cannot substitute for equipment safety validation.

The original presentation proposes a command round-trip latency below 20 ms and offline autonomous operation availability of 99.5%.

For command latency, the measurement boundaries must be explicitly defined, including whether network transmission, model inference, and tool execution are included. Offline availability also requires a defined measurement period, a description of the offline scenarios being evaluated, and clear criteria for determining whether the service is available.

For OHT systems, transport platforms, and other high-risk equipment, safety must continue to rely on independent safety mechanisms and appropriate verification procedures. Agent execution success alone is not sufficient evidence of equipment safety.

---

## 08. Industrial RAG: Making Equipment Knowledge Searchable and Traceable

![Industrial RAG](images/08_industrial_rag.png)

Knowledge in a factory exists in more than equipment manuals. It is also scattered across maintenance logs, fault analysis reports, engineering notes, and historical work orders.

These sources often have inconsistent formats, naming conventions, and data quality. Simply placing documents into a vector database may produce fluent answers, but fluent answers are not necessarily correct or applicable to the equipment's current operating conditions.

The primary objective of Industrial Retrieval-Augmented Generation (RAG) is therefore not merely to generate answers. It is to establish a traceable workflow connecting user questions, retrieved evidence, and original source documents.

### Knowledge Processing Pipeline

1. **Document preparation and access control:** Convert document formats, remove duplicates, identify versions, and handle sensitive information while preserving document provenance and access permissions.
2. **Semantic chunking and indexing:** Divide documents into appropriate text chunks based on their structure and content, then generate vector representations.
3. **Hybrid retrieval:** Combine BM25 keyword search, vector retrieval, and metadata filtering to reduce retrieval problems caused by technical terminology, equipment identifiers, and similar documents.
4. **Reranking:** Use a reranker to reassess the relevance of candidate documents to the user's question.
5. **Answer generation and citations:** Generate answers based on retrieved evidence and provide references to original documents, versions, and page numbers so that users can verify the information.

### Constraints in Enterprise Environments

Deploying RAG in a factory requires careful consideration of whether document-level permissions are enforced in retrieval results, whether the model can access unauthorized information, and how the system handles conflicting or outdated documents.

For equipment maintenance recommendations, answers should clearly distinguish between information explicitly documented in the source material and inferences generated by the model.

If sufficient evidence cannot be found, the system should be allowed to respond that the available information is insufficient, rather than inventing additional operating procedures merely to provide a complete-looking answer.

Document indexes and query logs should also have retention periods, auditing procedures, and access permissions appropriate to the sensitivity of the underlying data.

The original presentation lists the following scale and performance metrics:

- 850,000 documents.
- More than 20,000 queries per month.
- Knowledge lookup time reduced from an average of three hours to 40 seconds.

When interpreting these figures, document counts should distinguish between original documents, document versions, and indexed chunks created through document segmentation. Query volume should distinguish between submitted requests and requests that successfully retrieve useful answers.

Knowledge lookup time should be defined as the time from a user's question to the identification of a relevant knowledge source. It should not automatically be equated with the time required to complete an entire troubleshooting or maintenance procedure.

If the original three-hour and 40-second figures were calculated using different measurement criteria, they should not be directly compared as equivalent metrics.

Because the historical test records are not currently available for re-examination, the figures from the original material are retained without making additional assumptions about their measurement methodology or treating them as guaranteed results for all RAG systems.

---

## 09. MLOps: Continuous Monitoring After Model Deployment

![MLOps and continuous learning](images/09_mlops.png)

Good performance on test data does not guarantee that a model will maintain the same quality after deployment.

Equipment may experience changes in component condition, maintenance activities, operating loads, or process conditions. These changes can produce data distributions that differ from the training data.

Consequently, deployed models require continuous monitoring and a complete workflow that connects issue detection, model evaluation, and version updates.

### Drift Monitoring

Depending on the characteristics of the data, metrics such as the Population Stability Index (PSI), the Kolmogorov–Smirnov (KS) test, or other distribution-difference measures can be used to identify deviations from an established baseline.

For example, a PSI value above 0.25 may serve as a warning threshold in certain scenarios. However, exceeding this threshold does not automatically mean that the model has failed.

Thresholds should be determined based on data distributions, feature characteristics, and actual validation results.

The monitoring system should also track missing data, sensor abnormalities, inference latency, and model output distributions. This helps prevent sensor failures from being incorrectly classified as model drift.

If a seven-day rolling baseline is used to track equipment conditions, care must be taken to prevent the baseline from continuously absorbing slowly developing anomalies.

A more robust approach is to establish dynamic baselines based on equipment operating modes and historical data, supported by anomaly-state checks and explicit baseline-update conditions. This reduces the risk of incorporating persistent faults into the definition of normal behavior.

### Model Update Workflow

A more complete MLOps workflow may include the following steps:

- Periodically evaluate data quality and model performance.
- Develop candidate models to address confirmed issues.
- Validate candidates against historical data and relevant simulated scenarios.
- Compare new and existing versions in shadow mode.
- Release validated versions incrementally after the required reviews.
- Preserve version information, data provenance, parameters, and validation records for traceability and rollback.

The purpose of automation is not to replace a model immediately whenever drift is detected. Instead, it is to shorten the time required to detect problems, evaluate candidate models, and deploy updates while keeping the process controlled and auditable.

The original presentation lists the following metrics:

- Automatic retraining cycle reduced from two months to two weeks.
- Abnormal equipment downtime reduced by 75%.
- 1,200 hours of manual effort saved annually.

The automatic retraining cycle should distinguish among data updates, model training, model validation, and production deployment. Increasing retraining frequency does not necessarily improve model quality; every candidate model must still satisfy the required validation criteria.

Abnormal downtime and manual effort are system-level or process-level metrics. If improvements also result from changes to data pipelines, automation tools, maintenance workflows, or workforce responsibilities, the entire benefit should not be attributed directly to the model retraining mechanism.

---

## 10. System Integration and Future Development Directions

![Strategic impact and growth plan (2026–2027)](images/10_star_impact.png)

The components discussed in the preceding sections—stream processing, anomaly detection, RUL prediction, Edge Agents, Industrial RAG, and MLOps—address different layers of the overall system.

Stream processing ensures that data can be acquired and analyzed reliably. Anomaly detection and RUL models provide evidence for equipment condition assessment. Agents integrate information and coordinate tasks. RAG provides traceable document-based knowledge. MLOps manages the model lifecycle from validation through production deployment and ongoing operation.

These components must be integrated through clearly defined data interfaces, access-control mechanisms, and error-handling procedures. Simply connecting multiple services does not automatically create an autonomous decision-making system.

### Version 1.0: Establishing an Observable, Predictable, and Maintainable Foundation

The first phase focuses on ensuring that every component has well-defined inputs and outputs, measurable monitoring indicators, and appropriate failure-handling procedures. Performance should then be validated on a limited number of devices and production lines.

| System | Phase 1 Focus | Evaluation Metrics |
| --- | --- | --- |
| Real-time streaming platform | Establish data acquisition and feature-processing pipelines | Throughput, data loss rate, end-to-end latency |
| Anomaly detection | Reduce invalid alerts while preserving important events | False positive rate, false negative rate, F1 score |
| RUL prediction | Estimate equipment health and remaining useful life | RMSE, prediction intervals, maintenance decision effectiveness |
| Edge Agent | Coordinate models, tools, and maintenance workflows | Task success rate, latency, failure recovery capability |
| Industrial RAG | Establish document retrieval and answer traceability | Retrieval quality, answer correctness, citation traceability |
| MLOps | Establish model versioning and release workflows | Deployment cycle, rollback time, version traceability completeness |

### Version 2.0: From Individual Equipment Analytics to Cross-Equipment Collaboration

Once data processing, model quality, and deployment workflows are stable for individual devices, the system can begin exploring collaboration across multiple devices and production lines.

Potential development directions include:

- Extending real-time data processing to more devices while evaluating the bandwidth and computational requirements associated with higher sampling frequencies.
- Combining information from multiple sensors to improve the detection of complex, multi-factor anomalies.
- Integrating RUL estimates with spare-parts management, maintenance scheduling, and work-order systems.
- Building an equipment knowledge graph to support relationship-based queries across documents and devices.
- Enabling different Edge Agents to exchange equipment states and task results within their authorized access boundaries.

In the longer term, an **Edge Agent Swarm** architecture could be explored, in which multiple edge agents collaborate to handle different devices or tasks.

However, multi-agent collaboration introduces additional challenges, including state consistency, task conflicts, communication failures, access control, and error propagation.

Before expanding autonomous collaboration, the responsibilities of each Agent, its permitted actions, and its failure-handling procedures must be explicitly defined.

---

## 11. Conclusion

![Thank You](images/11_thanks.png)

Building an Edge-AI system for a smart factory requires much more than combining sensors, machine learning models, and an Agent framework.

The real challenge lies in engineering the entire system: ensuring reliable data acquisition, running models within constrained computing resources, determining whether anomaly results are trustworthy, recovering safely from deployment failures, and integrating AI recommendations into equipment operations and maintenance workflows without compromising existing safety mechanisms.

From this perspective, predictive maintenance and autonomous decision agents are not two independent capabilities.

Predictive maintenance provides equipment condition assessments and risk information. The Agent translates that information into traceable workflows. Data governance, model monitoring, and safety controls provide the essential foundation for keeping the entire system reliable over the long term.

For organizations seeking to advance these systems, the priority should not be achieving full autonomy from the outset. Instead, each component should first become observable, verifiable, and recoverable. The scope of AI-assisted decision-making can then be expanded incrementally.

This is the central design principle behind this architecture: **AI capabilities and system responsibility boundaries must be clearly defined together for the technology to operate reliably on the factory floor.**

---

> **Copyright and Terms of Use:** The use and reproduction of this article's text and figures are subject to the licensing terms published by the author. This article is intended for technical knowledge sharing and architectural discussion. Some information has been de-identified or adjusted and should not be used as the basis for operating specific equipment, implementing safety controls, or making maintenance decisions.