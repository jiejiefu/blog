---
title: "半導體設備 Edge AI 平台：從感測器資料到智慧決策的端到端系統"
tags: ["Edge AI", "預測性維護", "MLOps", "AI Agent", "Backend Engineering"]
draft: false
date: 2026-10-18
cover:
    image: "images/01_project_overview.png"
    alt: "Semiconductor Equipment Edge AI Platform Cover"
    relative: true
    hidden: false
---
## 前言

這篇文章是將我面試用的 10 張簡報內容整理成的文字版。簡報受限於篇幅通常只能呈現最終結論，因此這裡特別補充了每個技術模組選型的背後思維，以及過程中被權衡（Trade-off）掉的替代方案。
特別是最後一張關於「SQLite 單機架構天花板」的討論，那正是整套系統設計的起點：唯有先誠實釐清邊緣端的物理與架構限制，才能精準畫出後續架構演進的路線圖。

本文歡迎轉載，但請務必註明出處與原作者。文中簡報的所有公司名稱與敏感資訊皆已移除，相關數據亦經過虛擬化處理，閱讀時建議聚焦於系統架構與設計邏輯即可。

> ⚠️ **智慧財產權與免責聲明**
本文圖表版權歸作者所有，僅供個人技術能力展示與面試參考。內容已全面進行去識別化與虛擬化處理，未包含任何未公開之營業秘密、真實客戶名稱、具體半導體製程節點或內部專案代號。未經授權，請勿將圖表進行商業下載、二次改作或未註明來源之轉載。

---

## 01. 專案總覽：半導體設備 Edge AI 平台

![專案總覽：半導體設備 Edge AI 平台](images/01_project_overview.png)

本平台定位為「半導體設備 Edge AI 平台」，副標題為「邊緣 AI 與故障預測健康管理（PHM）」，從感測器資料到智慧決策，將碎片化 Sensor + ML 流程整合為可執行的工程閉環。

### 端到端執行管線（End-to-End Execution Pipeline）

五個階段串聯：

| 階段 | 名稱 | 內容摘要 |
|---|---|---|
| 1 | Sensor Data 感測器資料採集 | 2kHz 振動 / 溫度 |
| 2 | Feature & ML 特徵工程與模型 | FFT / One-Class SVM |
| 3 | Edge Inference 設備端即時推論 | Low Latency < 5ms |
| 4 | Monitoring 即時健康度監控 | Health Score & Alert |
| 5 | AI Agent 智慧代理決策 | LLM Root Cause Analysis |

### 核心工程能力（Core Engineering Capabilities）

四大核心模組：

1. **IoT Data Ingestion 感測資料鏈結 (IoT)**：deque 記憶體削峰環狀緩衝區、500 筆 / 5s 批次 Flush 寫入、SQLite 雙資料庫滾動隔離與備份
2. **ML & PHM Engine 健康度推論**：One-Class SVM 異常偵測、PCA 降維特徵萃取與漂移分析、無監督退化趨勢指標量化、馬氏距離與離群值精準偵測
3. **Edge Deployment 邊緣端架構 (Edge AI)**：PyInstaller 獨立二進位檔打包、離線環境零依賴即插即用、版本發佈與檢查更新機制
4. **GenAI & RAG Agent 智慧維護 Agent**：LLM 自動化產生修復工單、RAG 檢索歷史維護知識庫、閉環式故障根因診斷與派工

### 系統技術棧（System Tech Stack）

- Frontend: React UI
- Backend: Flask / SSE
- Database: SQLite 雙庫
- ML: scikit-learn / PCA
- Infra: Docker Compose
- GenAI: LLM Agent / RAG

---

## 02. 為什麼需要 Edge AI 平台？（Before / After 對比）

![為什麼需要 Edge AI 平台](images/02_why.png)

### Before：6 個零散工具與資料孤島

1. CSV Files：感測器原始資料紀錄，手動 Export 導出
2. Python Scripts：臨時 / 一次性資料清理腳本，缺乏版本控制
3. ML Notebooks：離線模型實驗與訓練，無法即時推論
4. Config Files：靜態 JSON/YAML 設定，門檻固定缺乏彈性
5. Edge C++ Runtime：設備端單體執行檔，孤立更新困難
6. Web Dashboard：獨立前端監控介面，狀態無法同步

### Critical System Pain Points（關鍵系統痛點）

- **High Friction Glue Code**：步驟間高度依賴人工轉換與客製腳本，極易因格式不符而崩潰
- **Broken Data Lineage**：推論結果無法回溯至原始感測器參數版本與訓練資料集
- **High Time-to-Market Latency**：模型每次更新需要數週的人工重新實作與驗證流程

> **核心代價**：工程師的時間從人工串接，轉向系統維護與例外判斷。

### After：1 個可執行工程閉環

1. Sensor Data Ingestion：自動資料串流
2. Feature & ML Pipeline：特徵標準化 + PHM
3. Edge AI Inference Engine：一鍵設備部署
4. Continuous Health Monitor：即時健康度監控告警
5. AI Agent Diagnostics：智慧根因診斷
6. Closed-Loop Feedback：資料模型持續閉環

### 工程影響（Engineering Impact）

| 指標 | Before | After | 效益 |
|---|---|---|---|
| Model Deployment Cycle | 28 天（人工串接） | 1 天（自動化管線） | → 縮短 96% 時間 |
| Glue Code Reduction | — | -85% | 大幅減少重複開發 |
| Data Lineage Integrity | — | 100% Sync | 端到端自動對齊 |

---

## 03. 系統組裝與架構設計（5 層整合架構）

![系統組裝與架構設計](images/03_system_architecture.png)

### 五層系統技術棧

| 層級 | 名稱 | 技術細節 |
|---|---|---|
| 1 | 使用者與前端介面 (User & Frontend) | React 18 · MUI · React Flow · 31 組路由 · 監控儀表板 UI |
| 2 | 後端核心服務 (Backend Core / REST & SSE Hub) | Flask · 15 個 Blueprints · JWT 驗證 · Agent Tool 協同派發 |
| 3 | 機器學習與分析引擎 (ML & Analytics) | scikit-learn · 特徵擷取 · One-Class SVM 異常偵測 · 批次推論 |
| 4 | 設備端執行層 (Edge Execution) | 感測器資料接入 → Edge.exe 引擎 → 即時健康度分數 (Health Score) |
| 5 | 資料持久化與儲存層 (Data & Persistence) | SQLite（雙資料庫）、模型檔與特徵檔管理 (Model Registry) |

### AI Agent 協同架構

**可控的 Tool Calling 架構設計**：
- 嚴格的邊界控制（Strict Boundary Control）：Agent 不繞過後端邏輯，僅能透過已驗證的 Tool API 執行操作
- 即時 SSE 上下文注入（Context Ingestion）：將設備即時 Alert 訊號串流注入 LLM 推理上下文
- 可執行的診斷閉環（Actionable Insights）：將根因分析與維護建議自動回傳至前端 UI 顯示

### 性能指標

| 指標 | 數值 |
|---|---|
| 模組數 | 15 個模組（Flask Blueprints） |
| Edge 資料接入 | 8 ms |
| 後端 Tool 執行 | 35 ms |
| SSE 串流廣播 | 15 ms |
| Agent 推理決策 | 120 ms |

核心架構價值：AI Agent 僅透過 Tool Calling 扮演智慧協調者，完整保留後端系統的確定性與安全性。

---

## 04. 端到端資料流（End-to-End Data Flow）

![端到端資料流](images/04_end_to_end_data_flow.png)

### Stage 1：資料投入與蓄流（Ingestion）

- 執行緒安全佇列（deque maxlen=5k）
- 每 5 秒批次寫入（max 500 筆）
- 資料庫容量上限：10,000 筆紀錄
- 突發高頻訊號下防止 I/O 阻塞

**蓄流與批次寫入機制**：
- 記憶體邊界佇列（Bounded Queue）：collections.deque(maxlen=5000)，有效吸收高頻感測器突發訊號，避免阻塞系統主執行緒
- 非同步 SQLite Flush：500 筆 / 5 秒，資料庫容量硬性限制 10,000 筆，確保查詢維持極低延遲

### Stage 2：預處理與 ML 推論（Scoring）

- 時域與頻域特徵擷取（Time/Freq）
- One-Class SVM 批次推論引擎
- 即時健康度分數歸一化（Health Score）
- 將原始振動資料轉為量化指標

### Stage 3：監控告警與 AI 聯防（Action）

- 前端 10 秒輪詢機制（10s Polling）
- GET /api/vibration/latest 端點
- SSE 事件串流驅動 AI Agent 推論
- 自動化根因診斷與維修處置建議

**蓄流佇列與 DB 寫入模擬**：
- 感測器異常訊號（2,500 pts/s）
- DB 非同步寫入（500 pts / 5s）
- I/O 負載控制在 < 5%

核心架構價值：非同步蓄流隔離高頻訊號寫入對資料庫的衝擊，確保系統在異常突發時依舊穩定運作。

---

## 05. ML & PHM Pipeline（機器學習與設備預測性維護管線）

![ML & PHM Pipeline](images/05_ml_phm_pipeline.png)

### 預處理與特徵處理管線

1. 原始訊號接入：高頻振動加速度訊號 x(t)，連續感測器串流
2. 時間切片：時域滑動視窗切片，Overlapping 蓄流，固定長度訊號幀
3. 特徵矩陣提取：accRMS · 峰值 · 峭度，時域與頻域特徵指標，餵入下游 ML 模型

### 異常偵測（Anomaly）

**One-Class SVM**：適用於生產線缺乏故障標籤情境，學習正常行為界線 → 標記異常偏離

### 模組對齊（Alignment）

**DTW 序列比對**：克服轉速波動與時間軸相位位移，非線性時間序列動態對齊演算

### 趨勢與漂移（Drift）

**PCA 與特徵漂移**：當前運轉資料 vs 歷史 Baseline 對比，量化追蹤設備長期磨損與退化

### 演算法選型準則

依物理訊號特性選用 — 缺乏故障標籤 → **OCSVM** → 轉速相位位移 → **DTW** → 長期磨損退化 → **PCA 特徵漂移**

---

## 06. 後端工程（Backend Engineering）

![後端工程](images/06_backend_engineering.png)

### Flask 核心架構

| 模組 | 內容 |
|---|---|
| 身分驗證 (Authentication) | LDAP / AD 企業驗證整合 · JWT Token 機制 |
| RESTful API 模組 | 15 個 Domain Blueprints · Sensor / ML / Edge 路由 |
| 資料存取層 (Data Layer) | SQLAlchemy ORM · 雙 SQLite（vibration.db） |
| 背景非同步任務 (Background Jobs) | APScheduler + Queue 非同步 Task Pipeline |
| AI Agent 協同中樞 | LLM 工作流編排 · Tool Calling 處理器 |
| 模型生命週期 (Model Lifecycle) | ModelBuildingHistory · 自動跟蹤訓練 State & Metrics |

### 資料與串流 I/O

**Dual DB 跨庫查詢與非同步蓄流寫入機制**：
- edge_ai.db（設定與模型歷程） + vibration.db（高頻時域資料庫）
- SQLite ATTACH → 高效率單一 SQL 聯表查詢
- API 讀取與高頻寫入解耦，前端查詢不被寫入尖峰阻塞
- 高頻訊號 → deque 佇列 maxlen=5000 → 批次交 DB（5s / 500 筆）

### Model Lifecycle

**ModelBuildingHistory**：模型狀態機與歷程追蹤
- building ↔ completed / failed
- 持久化跟蹤關鍵指標：Accuracy（準確度）與 Coverage（覆蓋率）、Anomaly Score 閾值與異常日誌紀錄

### 15 個 Domain Blueprints

依業務領域拆分獨立維護（Sensor / ML / Edge），避免單一 Route 檔案過大，提升模組化擴充性。

**Authentication 身分驗證流程**：LDAP / AD ↔ JWT Access ↔ Refresh（1 小時短期 Token / 30 天 Refresh 續期）

### 關鍵指標

| 指標 | 數值 |
|---|---|
| Blueprints | 15 個（模組化架構） |
| Databases | 2 個（Attached 雙 DB 架構） |
| Batch Interval | 5s（Queue 流量控制機制） |
| Model States | 3 個（完整 Lifecycle 追蹤） |

---

## 07. AI Agent 架構（AI Agent Architecture）

![AI Agent 架構](images/07_ai_agent_architecture.png)

### Agent 執行流程

1. **用戶端層（Client Layer）**：使用者輸入 → React Agent UI 對話介面
2. **後端網關（Backend Gateway）**：POST /agent/chat/stream · SSE 即時串流
3. **Agent 協同中樞（Orchestrator）**：OpenAI Agents SDK · 工具自動選擇 · ReAct 推理鏈
4. **平台可執行工具組（Platform Tools）**：由 Flask 控制器直接呼叫的受控沙箱函式（Sandboxed）
   - get_health_score
   - get_vibration_data
   - run_sql_query_safe
   - anomaly_detection
   - read_file
   - export_report

沙箱隔離執行，僅開放 Read-only API 權限。

**框架與基礎架構**：核心框架為 OpenAI Agents SDK（內建 20+ Function Tools）；備援機制為 LangGraph ReAct 架構；即時反饋透過 SSE Streaming 串流。

### 推理引擎（Reasoning）

- LLM 專注於理解使用者意圖，拆解問題步驟並選擇適當 Tool
- 避免幻覺產生，不直接生成資料，所有實體資料均交由 Tools 查詢

### 確定性工具執行（Execution）

- Python 封裝工具負責實際執行 SQLite 查詢、檔案讀取與演算法計算
- 將高精確度的執行結果格式化，再回傳給 LLM 進行綜合分析與摘要

### 後端防護與安全治理（Control）

- 後端嚴格管控 API 存取與權限驗證，禁止開啟 Unrestricted Shell
- SQL 查詢限定 Read-only 模式與參數化傳遞，防範注入攻擊
- 結合 JWT Token 身分驗證，確保機密感測資料與專案設定存取安全

### Agent 執行延遲顯示

| 任務 | 延遲 |
|---|---|
| LLM 邏輯推理 | ~320 ms |
| Tool 實體執行 | ~35 ms |
| SSE 串流傳輸 | ~85 ms |

100% 確定性資料，0% 直接 DB 風險（所有資料皆透過 Tool 受控存取）。

---

## 08. 部署與監控（Deployment & Monitoring）

![部署與監控](images/08_deployment_monitoring.png)

### Docker Compose 容器化環境

| 服務 | 設定 |
|---|---|
| 前端服務 Frontend (:3000) | edgeai-frontend:latest，React UI + Nginx 伺服器 |
| 後端 API 服務 Backend (:5000) | edgeai-backend:latest，Flask WSGI + APScheduler 排程 |
| 持久化資料卷 (Docker Volume) | SQLite 雙資料庫 · ML 模型檔 (.pkl) · 感測日誌，Volume 掛載，降低資料遺失風險 |

零重編譯動態注入：entrypoint.sh → env.js → window.ENV → 後端端點，同一 Image 跨環境部署（Deploy Once · Configure at Runtime）

### APScheduler：主動式健康檢測與快取推論

| 背景引擎任務 | 頻率 |
|---|---|
| 健康檢測 | 每 5 分鐘 |
| 模型異常推論 | 每 5 分鐘 |
| Email 告警通知 | 觸發制 |

**State Buffer & Cache**：MonitorSnapshot 狀態池，RAM 雙階快取（API 讀取僅 0.2ms），磁碟檔案 Fallback 容錯持久化

### 自動化排程時間軸

- 每日資料庫備份：03:00 Daily
- 健康度檢測：每 5 分鐘
- 模型異常推論：每 5 分鐘
- Email 告警發送：即時事件觸發
- 高頻資料寫入：5s / 500 筆 批次

### 前端視覺化面板

- 即時健康度 Gauge 儀表板
- SSE 主動推送告警事件

---

## 09. 故障處理與擴展性（Failure Handling & Scalability）

![故障處理與擴展性](images/09_failure_scaling.png)

### 現行單機體驗流程（單點佇列）

感測器資料 → deque 佇列 → 批次寫入 → SQLite DB

**系統併發瓶頸**：高頻突發流量時，SQLite 單一檔案寫入鎖定（Write Lock）

**突發流量削峰填谷模擬**：
- 突發流量峰值：2.5k
- 5s（突發點）→ 15s（峰值）→ 25s（消化完成）
- 平滑寫入上限 100 req/s（Batch Flush，即每 5 秒 500 筆）

**有界佇列緩衝區**：deque(maxlen=5000) 記憶體隔離
**批次寫入策略**：每 5 秒 / 滿 500 筆批次 Flush
**FIFO 容量保留限制**：資料庫紀錄上限 10,000 筆
**雙 DB 滾動備份機制**：每日 03:00 自動備份（保留 7 份）

### 未來橫向擴充藍圖（Scale-Out 調型）

MQTT Broker ↔ Message Queue ↔ Worker Cluster（各 N 個）

**持久化與服務層（Storage & Services）**：

| 組件 | 說明 |
|---|---|
| PostgreSQL | 高可用 HA 機制，Write Sharding |
| Redis Cache | 記憶體級快取，Real-time Snapshot |
| Flask API | 無狀態彈性擴充，Load Balancer |

**三大擴充原則**：

1. **寫入與計算徹底解耦**：Message Queue（Kafka / RabbitMQ）完全吸收萬級突發流量，消除單點鎖定
2. **Worker 彈性橫向擴充**：無狀態 Worker 節點可根據 Queue 堆積量自動實施 Auto-Scaling
3. **企業級讀寫分離**：PostgreSQL 負責持久化，Redis 提供極速 API 讀取，徹底分離讀寫壓力

> **現有 SQLite 是針對目前 Edge Deployment scale 的工程選擇；規模成長時，再演進至 Scale-Out 分散式架構。**

---

## 10. 工程權衡（Engineering Trade-offs）

![工程權衡](images/10_engineering_tradeoffs.png)

### 各組件現行方案與未來演進

| 組件 | 現行方案 (TODAY) | 瓶頸與限制 | 未來演進 (NEXT) |
|---|---|---|---|
| Flask | Simple REST · ML 整合容易 | 架構約束少，難以拆分服務 | FastAPI（Service Split） |
| SQLite | 部署簡單，維運負擔較低 | 單檔寫入併發鎖定 | PostgreSQL HA Cluster |
| APScheduler | 背景工作內建整合 | 單行程限制 | Worker Queue（Celery / RQ） |
| Local ML files | 邊緣端直接載入 | 模型版本追蹤弱 | Model Registry（MLflow） |
| SSE | 單向 HTTP 串流簡單 | 不支援雙向通訊 | WebSocket（雙向需求） |
| One-Class SVM | 無故障標籤時適用 | 超參數與邊界敏感 | Advanced PHM Model |
| React Context | 輕量級元件狀態共用 | 規模大易多重渲染 | Zustand / Redux |
| Queue | 記憶體削峰緩衝（deque） | 容量受限於記憶體 | Durable MQ（Kafka） |
| Docker Compose | 單機容器化部署簡單 | 容器編排能力有限 | Kubernetes (K8s) |

### 系統權衡雷達圖（Edge-Optimal vs. Scale-Out）

- **部署速度**：現行方案快，未來 Scale-Out 隨著 K8s 引入而變慢
- **低維運成本**：現行方案較低，分散式架構維運複雜度明顯增加
- **擴充性**：現行單機受限，Scale-Out 顯著提升
- **容錯能力**：現行單點風險高，未來分散式具備高容錯
- **吞吐量**：現行單機受限，未來 Message Queue + Worker Cluster 顯著提升

整體定位：現階段「立足當前邊緣端限制」進行設計，同時為「未來擴充」預留演進路徑。

### 架構演進藍圖

| 階段 | 架構模式 | 技術組合 |
|---|---|---|
| Phase 1 | Edge Monolith（現行邊緣單體） | SQLite · Flask · 單行程 |
| Phase 2 | Decoupled Pipeline（解耦管線） | Worker Queue · SSE Stream |
| Phase 3 | Cloud Scale-Out（雲端橫向擴充） | K8s · PostgreSQL · Model Reg |

---

## 結語

回頭來看，這個專案最大的價值不在於疊了多麼高深的演算法，而是成功把「零散工具與資料孤島」收斂成一個真正能跑、能交接的工業級工程閉環：

* **部署週期極速壓縮**：模型上線週期從 28 天大幅壓縮至 1 天（縮短 96%）。
* **高工程純度**：膠水程式碼減少 85%，並確保資料血緣（Data Lineage）100% 同步。
* **極致即時性**：邊緣端推論延遲控制在 5ms 以內，完美支援斷網環境下的離線自主運作。
* **模組化擴充性**：透過 15 個 Domain Blueprints 模組化架構，為未來平滑遷移至 Kubernetes 預留彈性。

刻意不一開始就上重型架構是經過深思熟慮的：邊緣設備首重斷網獨立運作的能力，過度設計只會徒增維運負擔。先在簡單的單機架構下把核心打紮實，等業務規模真正撐不住的那一天，再往分散式演進——這時瓶頸在哪裡，會比閉門造車清楚得多。

---

> **版權與使用條款**：本文所有圖表版權歸作者所有，轉載請註明出處。內容已全面去識別化與虛擬化處理，僅供技術交流與架構展示使用，不構成任何營業秘密洩露。
