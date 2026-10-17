+++
date = '2026-02-28T21:14:02+08:00'
tags = ['resume', 'personal']
draft = true
title = 'Resume'
+++

---

## 👨‍💻 About Me

Software engineer with a multidisciplinary background, specializing in **intelligent systems** and **edge AI technologies**. Currently working in the semiconductor industry, focused on building large-scale data processing platforms and smart analytics solutions.

**Core areas:** Machine Learning · Edge AI Deployment · Signal Processing & Data Analytics · Data Visualization Platforms

Read my technical write-ups in the **[Posts](/posts/)** section.

---

## 💼 Work Experience

### Software Engineer — [Company Name] (Semiconductor Industry)
**2021-11 – 2026-07** · Taipei, Taiwan

- Led edge AI platform development, reducing model deployment time from 4 hours to 30 minutes (**↓83%**) with support for 500+ production devices (Python, Docker)
- Developed LLM-powered natural-language interface for factory data visualization, cutting dashboard configuration time by **~50%**
- Built FFT spectral anomaly detection for wafer dicing saws with a TensorFlow AutoEncoder and dynamic thresholding, reaching **~80% Recall**; transfer learning cuts calibration to 1–2 hours
- Built virtual metrology for Underfill dispensing, estimating dispense volume from machine signals via time-series segmentation and physics-based features, accurate within **±1** dispense (R² > **0.95**)
- Integrated AI models with traditional signal processing and established standardized MLOps workflows

---

## 🧠 Projects

### Edge AI Platform

**Full-lifecycle edge AI solution** — end-to-end platform covering model development, optimization, and on-device deployment, serving semiconductor manufacturing environments for equipment monitoring and intelligent O&M.

[Read more →](/posts/edge-ai/)

#### Key Contributions
- **Distributed Inference Architecture** | Designed a cloud-edge collaborative architecture supporting independent edge inference and cloud-side model synchronization
- **Low-latency Inference Pipeline** | Integrated TensorRT quantization and model pruning, improving inference efficiency by **35%**
- **Automated Deployment System** | Developed Edge Runtime Pipeline, reducing deployment time from **>4 hours to <30 minutes** (↓83%)
- **PHM Predictive Maintenance Platform** | Built an equipment health management system supporting multi-machine status monitoring and remaining useful life prediction
- **AI Copilot Dashboard Assistant** | LLM-driven auto-charting tool reducing manual configuration time for new users by **60%**

#### Key Results
| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Model deployment time | > 4 hours | < 30 minutes | **↓83%** |
| Inference efficiency | baseline | +35% | **Significant gain** |
| Device support scale | Single device | > 500 devices | **Production-scale** |

---

### Edge AI Agent

**AI Agent with autonomous monitoring and anomaly detection** deployed on-device for 24/7 real-time equipment health diagnostics and root cause analysis, replacing traditional manual inspection workflows.

[Read more →](/posts/ai-agent/)

#### Key Contributions
- **AI Agent Architecture** | Built a perception-reasoning-action (ReAct) loop enabling autonomous on-device decision-making
- **Equipment Health Monitoring** | Integrated multi-source sensor data to build a health scoring model with trend-based early warning
- **Anomaly Detection Model** | Applied unsupervised learning (Isolation Forest / Autoencoder) to detect unknown anomaly patterns
- **Automated Event Analysis & Reporting** | Auto-generates diagnostic reports on anomaly detection, covering type, severity, and recommended actions
- **Multi-Agent System** | Designed a multi-agent collaboration architecture supporting cross-device cooperative diagnosis and task dispatch

#### Features
Real-time anomaly detection · Automated root cause analysis (RCA) · Intelligent alert tiering · Equipment health scoring

---

### Real-time Signal Analyzer

**Real-time signal analysis system** designed for high-speed industrial sensor data, supporting automatic extraction of time-domain and frequency-domain features, applied to anomaly identification in equipment vibration and current signals.

[Read more →](/posts/signal-processing/)

#### Key Contributions
- **High-speed Data Processing Pipeline** | Implemented a low-latency streaming architecture in C++, supporting real-time analysis of 20 devices at 2 kHz sampling rate
- **Automated Feature Extraction** | Integrated FFT, RMS, and Peak Detection algorithms to automatically output structured feature vectors
- **Real-time Anomaly Detection Module** | Combined signal features with threshold models to achieve millisecond-level anomaly triggering and alerting
- **Performance Optimization** | Improved signal processing throughput by **2.5×** through vectorized computation and multi-threaded scheduling

#### Supported Analysis Methods
FFT spectrum analysis · RMS · Peak detection · Frequency-domain feature extraction · Noise filtering

#### Key Results
- Signal processing throughput improved **2.5×**, supporting multi-channel parallel analysis
- Automated feature extraction replaces manual annotation, significantly reducing analysis lead time
- Anomaly detection accuracy improved over rule-based methods with a substantial reduction in false positives

---

## 🔓 Open Source

### Pokémon Algorithm — Interactive Algorithm Visualizer

**Zero-build vanilla JS/ES Modules web lab** visualizing 6 sorting algorithms, BFS/DFS pathfinding, and Conway's Game of Life across 1,025 sprites with Canvas rendering.

[Live demo →](https://pokemon-algorithm.jayfu0101.workers.dev/) · [Read more →](/posts/pokemon/)

#### Key Contributions
- Built a Python data pipeline generating 1,025 color palettes via MMCQ quantization with OKLab perceptual evaluation, plus a Node.js verification suite with content-hash caching
- Visualized sorting algorithms, pathfinding, and cellular automata with Canvas rendering

---

## 🎓 Education

### National Tsing Hua University
**B.S., Engineering and System Science** · 2013–2017 · Hsinchu, Taiwan
- Last 60 GPA: 3.89/4.3 (92%), Overall GPA: 3.63/4.3 (83%)

### The University of Texas at Dallas
**M.S., Computer Science** · 2018–2020 · Richardson, TX, USA
- CS6375 Machine Learning: 4.0/4.0 (A); Overall GPA: 3.23/4.0

---

## 🚀 Technical Skills

### Programming Languages
| Language | Use Cases |
|----------|-----------|
| **Python** | AI/ML, data analysis, automation scripts |
| **JavaScript/TypeScript** | Web applications, front-end development |
| **C++** | High-performance computing, low-level system development |
| **Java** | Enterprise systems, big data processing |

### Machine Learning & AI
PyTorch · TensorFlow/Keras · scikit-learn · Signal Processing · Time-series Forecasting · Unsupervised Anomaly Detection

### LLM & Agents
LLM Integration · ReAct Framework · Multi-agent Architecture · Prompt Engineering

### Infrastructure & DevOps
Edge Deployment · MLOps · Docker · CI/CD · Linux · Cloud-native Architecture

### Signal Processing
FFT / RMS / Spectral Analysis · Real-time Multi-threaded Pipelines

### Domain Knowledge
Semiconductor Manufacturing · Wafer Dicing Equipment · Equipment Health & RUL Prediction · Anomaly Detection

---

## 📫 Contact

- Email: jayfu0101@gmail.com
- GitHub: https://github.com/jiejiefu
- Website: https://jiejiefu.github.io/blog/
- LinkedIn: (optional)
