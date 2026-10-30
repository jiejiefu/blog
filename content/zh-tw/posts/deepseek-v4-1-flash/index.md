---
draft: false
date: 2026-10-27
title: "DeepSeek-V4.1-Flash：把 global KV 壓到 890 bytes/token，骨幹反而大了近一倍"
description: "DeepSeek-V4.1-Flash 用 CED 把 decoder 的 global KV 從 encoder 長出來、用 CSA2 跨層共享 KV 與 index、再把 global KV 壓到 FP4，做到 890 bytes/token。本文拆解 40 層配置、FP4 位元帳、SWA Bounded Replay 的近似代價，以及 1017 更新後與 Anthropic Opus-5 的 4 勝 4 負。"
tags: ["ai", "llm", "deepseek", "kv-cache", "model-architecture", "system-design"]
ShowToc: true
TocOpen: false
math: true
cover:
    image: "images/cover.jpg"
    alt: "DeepSeek 鯨魚標誌與 890 bytes/token 的 global KV 壓縮示意封面"
    caption: "封面為自製終端機／藍圖風格示意圖；DeepSeek 鯨魚標誌 © DeepSeek，僅用於識別；數字取自 DeepSeek-V4.1-Flash 論文與 1017 模型卡。"
    relative: true
---

{{< tldr >}}
V4.1-Flash 把 global KV 壓到 **890 bytes**。
這是每個 token 的用量。
大約是 V4-Flash 的 1/4，V1 的 1/437。
同期 backbone 從 284B 長到 552B，接近一倍。
這個反差比 benchmark 更說明問題。

壓縮分三層。
CED 讓 decoder 的 global KV 從 encoder 投影。
來源是最後一層。
prefill 的 global 分支只跑一半的層。
CSA2 讓相鄰層共用 main KV、indexer K 與 Top-K。
但它們不共用 query。
FP4 再把 KV 從 FP8 砍一半。
部署時用 SWA Bounded Replay 把短期窗口移出 SSD。
persistent KV 降到 1/8。

代價論文有寫。
SWA 重建是近似的。
sparse selection 可能選錯。
1M prefill 也不便宜。
下面把「可以省」與「不能假設」分開講。
{{< /tldr >}}

2026 年 9 月 10 日，DeepSeek 發布 V4.1-Flash。
新聞稿主打「smarter, faster, more efficient」。
技術報告的標題是 Pushing the Limits of KV Cache Compression。
兩句話擺在一起，重點就換了。
長 context 的競爭不再問「模型能吃多長」。
現在問同一份 1M context 要佔多少記憶體。
還要問它重算幾次。
以及每次 cache miss 付多少錢。

但它在壓 KV 的同時，把 backbone 從 284B 拉到 552B。
骨幹變大、cache 變小，怎麼同時成立？

## 1. 先把規格講清楚：748B、763B，與那張 1M 的帳單

2026 年 9 月 10 日的論文版寫的是：

- 552B backbone parameters
- 196B Engram parameters
- 兩者相加 748B
- prefill 每 token 啟用 8B，decode 每 token 啟用 16B
- context 上限 1M，最大輸出 384K

10 月 17 日換成 `DeepSeek-V4.1-Flash-1017`。
數字不一樣。
Hugging Face 上的 safetensors 張量加總約 **763B**。
精確數字是 763,205,315,794。

15B 的差額，官方沒有給明細。
不能解讀成 backbone 又大了 15B。
比較合理的理解是口徑不同。
763B 是 1017 checkpoint 的張量總和。
748B 是論文用「backbone + Engram」描述的帳。

兩代規格如下：

| 項目 | DeepSeek-V4-Flash | DeepSeek-V4.1-Flash |
|---|---:|---:|
| Backbone 參數 | 284B | 552B |
| 每 token 啟用 | 13B | 8B（prefill）/ 16B（decode） |
| Global KV / token | 約 3.5 KB | **890 bytes** |
| Persistent KV | 100% | **約 12.5%** |

> 本文參數用 `B` 代表 billion；KV 大小一律寫 `bytes`，例如 `890 bytes/token`，避免和參數的 B 混淆。

骨幹長了 1.94 倍，prefill 每 token 啟用反而降到 8B。
這是 CED 的直接結果。
global 分支只跑 20 層。

763B 的總量還是巨獸。
890 bytes/token 省的是 KV，不是權重。
把 checkpoint 塞進單機，是一個問題。
把 1M context 的 KV 放進 HBM（GPU 的高頻寬記憶體），是另一個問題。

## 2. 為什麼此刻要壓 KV：agent 把工作負載變成 input-heavy

Agent 改變了 inference 的形狀。

一般聊天是短輸入、長輸出。
agent 是長輸入、多次工具呼叫。
每次工具呼叫都可能 cache miss。
一輪任務裡，模型反覆讀工具輸出。
重送 context，再生成下一步。
輸入可以遠長於輸出。
prefill 不是跑一次，是跑很多次。

論文的原話是：

> prefill remains computationally expensive, and large KV caches continue to strain HBM and SSD capacity and data-transfer bandwidth.

瓶頸有三個，而且互相牽連：

1. HBM 容量：global KV 必須隨時可讀。放不下就排隊或降 batch。
2. SSD 容量與頻寬：persistent KV 用來做 prefix reuse。放不下就 cache miss。
3. 傳輸頻寬：KV 在 HBM、host memory、SSD 之間搬。搬越多，延遲越難藏。

換成 1M context，差距很具體：

- V1：約 **389 GB**
- V4-Flash：約 **3.5 GB**
- V4.1-Flash：約 **890 MB**

{{< figure src="images/01_kv_generations.webp" alt="三個世代的 global KV 對照：V1 每個 token 389 KB、V4-Flash 3.5 KB、V4.1-Flash 890 bytes；換成 1M context 分別是 389 GB、3.5 GB、890 MB" caption="只計 global KV。SWA 的 128-token 窗口、weights、activation 與其他啟動記憶體另計；890 MB 不是「1M context 的總記憶體」。倍數依論文 Fig. 1b 的 437× / 約 4× 回推。" loading="lazy" >}}

圖用 log scale。
這裡只算 KV。
對 serving 來說，這比 benchmark 多兩分更值錢。

## 3. KV 的三個乘法維度

KV 的壓縮只有三個維度。
三者相乘。

| 維度 | 問題 | 常見手法 |
|---|---|---|
| Entry size | 每個 KV entry 多大？ | GQA 減少 KV heads；MLA 把 heads 壓進 shared latent |
| Sequence | 多少 token 共用一個 entry？ | CSA / HCA 把每 \(m\) 個 token 壓成一個 entry |
| Layer | 多少層可以共用？ | IndexCache 重用 Top-K；YOIO 共享 routing；HySparse 讓 sparse layer 用 dense layer 的 KV |

多數方法只動其中一個。
CSA2 三個一起動。
它跨層共用 main KV 與 indexer K。
也允許跨層重用 Top-K。
再用 hierarchical indexer 縮小候選池。

論文對既有做法的批評：

- IndexCache 只省 index 計算，不省 main KV。
- YOIO 全層共用一組 routing，表達力受限。
- HySparse 的 hybrid 設計仍保留 full attention layer。
- 沒有人同時覆蓋三個維度。

省 index 不等於省 KV。
省 KV 也不等於省 prefill。
三個成本要分開算。

## 4. CED：decoder 的 global KV 從第 20 層長出來

V4.1-Flash 最反直覺的設計是 CED。
全名 Causal Encoder-Decoder。

一般 decoder-only 模型每層自己算 KV。
KV 來自該層的 hidden state。
CED 把 40 層切成兩半。
前 20 層是 causal encoder。
後 20 層是 decoder。
global attention 的 KV 改由 encoder 最後一層投影：

$$
C_l = H_{L/2} W_l^{KV}, \qquad Z_l = H_{L/2} W_l^{Z}, \qquad l > \frac{L}{2}
$$

\(C_l\) 是第 \(l\) 層的 KV entry。
\(Z_l\) 是對應的壓縮權重。
\(W_l^{KV}\) 與 \(W_l^{Z}\) 每層不同。

- KV 來源相同：都是 encoder 最後一層的 \(H_{20}\)。
- 每層投影不同：decoder 仍能學到自己的 KV 子空間。
- decoder 不必重跑 20 層：prefill 跑完 encoder，就能長出 global KV。

{{< mermaid >}}
flowchart TB
    P[Prompt tokens] --> E[Encoder layers 1-20]
    E --> H[Encoder output H20]
    H --> G[Decoder layers 21-40<br/>每層自己的 global KV = H20 × W_l]
    E --> S[Replay last 128 tokens<br/>for decoder SWA]
    G --> D[Decode step<br/>global KV from cache]
    S --> D
{{< /mermaid >}}

Prefill 的複雜度因此從 \(O(NL)\) 降到：

$$
O\left(\frac{NL}{2} + n_{\mathrm{win}}\frac{L}{2}\right) \approx O\left(\frac{NL}{2}\right)
$$

第二項是 SWA 的 replay。
decoder 的 SWA KV 仍由自己的 hidden state 算出。
它不能從 encoder 投影。
prefill 還是要為 SWA 跑一小段。
論文只跑最後 \(n_{\mathrm{win}}=128\) 個 token。

CED 只讓 global 分支變淺。
local attention 仍逐層跑完 40 層。
論文說這是 YOCO 的加強版，補上 KV 容量與生成深度。

代價有三個。

- 表徵深度鎖在第 20 層。decoder 不能用 hidden state 豐富 global KV。
- SWA 仍逐層。prefill 不能真的只跑 20 層，還要補 128 個 token 的 replay。
- 短 prompt、多輪對話最敏感。uncached suffix 可能很短，decoder 還是要 replay。

論文只說它「nearly halves prefill computation」。
它沒說 global attention 變免費。

## 5. CSA2：共享 KV、共享 index，但不共享 query

CED 解決 prefill 的計算。
CSA2 解決 KV 儲存與 decode 的 index 計算。

CSA2 的每一層固定是三種模式之一：

| 模式 | Main KV | Indexer K | Top-K | 這一層還算什麼？ |
|---|---|---|---|---|
| Full | 自己算 | 從 main KV 投影 | 自己選 | 完整的 CSA2 路徑：global Q、main KV、indexer Q/K、Top-K |
| Reindex | 重用前一層 | 重用前一層 | 自己重選 | 自己的 indexer Q，對共享的 indexer K 重新打分 |
| Reuse | 重用前一層 | 重用前一層 | 重用前一層 | 只算 global Q + SWA KV，直接做 sparse attention |

三種模式有一個共同點。
每個 layer 都保留自己的 global Q 與 SWA KV。
共享的是被查詢的 cache 與索引。
不共享 query 本身。

{{< mermaid >}}
flowchart LR
    F[Full] -->|產生| KV[Main KV + indexer K]
    F -->|計算| IDX[Top-K indices]
    R[Reindex] -->|重用| KV
    R -->|自己的 Q 重新打分| IDX
    U[Reuse] -->|重用| KV
    U -->|重用| IDX
    Q[每一層自己的 global Q] --> A[Sparse attention]
    KV --> A
    IDX --> A
{{< /mermaid >}}

關鍵在於把 cache 共享與 index 共享解耦。

- 只共享 cache，每層都要重跑 indexer。decode 的 index 成本仍是 \(O(N)\)。
- 只共享 index，KV 儲存完全沒省。
- Reindex 共享 cache、重選 index。
- Reuse 兩者都共享。
- 儲存與計算因此能分開調。

### 40 層的實際配置

論文給的 40 層配置：

| 區塊 | 層數 | 配置 |
|---|---:|---|
| 前 2 層（encoder） | 2 | 純 SWA，沒有 global attention |
| Encoder 其餘 18 層 | 18 | CSA2，\(m=2\)；3 組 × 6 層，每組 1 層 Full + 5 層 Reuse |
| Decoder | 20 | CSA2，\(m=1\)；5 組 × 4 層，第 1 組 1 層 Full + 3 層 Reuse，其餘 4 組 1 層 Reindex + 3 層 Reuse |

- 40 層 = 20 encoder + 20 decoder，hidden dim \(d=5120\)。
- 所有 CSA2 layer：indexer 32 heads × 128 dim，sparse attention 取 Top-512。
- Query 端：64 heads × 512 dim，query compression dim 1280；輸出投影 8 組，每組 intermediate 1024。
- SWA window \(n_{\mathrm{win}}=128\)。
- MoE：1 shared expert + 384 routed experts，每 token 啟用 6 個 routed，expert intermediate dim 2304。

{{< figure src="images/03_layer_layout.webp" alt="DeepSeek-V4.1-Flash 的 40 層配置：encoder 前 2 層純 SWA，其餘 18 層分成 3 組 Full 加 5 次 Reuse；decoder 20 層分成 5 組，第一組 Full 加 3 次 Reuse，其餘四組 Reindex 加 3 次 Reuse" caption="同一組內，main KV、indexer K 與 Top-K 由 1 層 Full 算完，後面 3 或 5 層直接 Reuse；Reindex 只重跑 indexer，不重算 main KV。" loading="lazy" >}}

灰色只代表沒有 global attention，不代表沒有 SWA。
每一層都有 SWA，前 2 層只是少了 global。

### 為什麼 encoder 用 \(m=2\)、decoder 用 \(m=1\)？

兩邊的任務不同。

- encoder 建立 global KV。每 2 個 token 壓成 1 個 entry，sequence 維度直接減半。encoder 只需記得住，不必每個位置都細查。
- decoder 逐 token 生成與檢索。\(m=1\) 不做 sequence 壓縮，每個位置保留一個 entry。節省來自跨層共享與 FP4。

encoder 用壓縮換容量。
decoder 用共享換精細度。
這解釋了 890 bytes/token 的來源。
它也解釋 attention 為何還能選到 Top-512。

### 與 V4 的差別：拿掉 HCA

V4 用的是 CSA + HCA 的 hybrid。
CSA 負責壓縮的 sparse attention。
HCA 負責重度壓縮的 global 通道。
V4.1-Flash 改成 pure CSA2，拿掉 HCA。

簡化不一定會變好。
SWA 的 local processing 留著。
好處是：

- 少一種 layer type，實作與 kernel 都簡單。
- 不需要在 CSA 與 HCA 之間做 routing / 混合。
- 跨層共享的規則可以統一。

代價是表達力下降。
global 通道要靠 Full/Reindex/Reuse 的配置補回來。
論文說效能沒掉，甚至更好。
但這是整體訓練與資料的結果。
不能單獨歸因於拿掉 HCA。

## 6. Hierarchical Sparse Indexer：把 decode 的 index 成本關進候選池

CSA2 讓很多層不用重算 index。
Reindex 層還是要重新打分。
1M context 下，每層若掃過所有 main KV，成本仍是 \(O(N)\)。
這會變成 decode 的 bottleneck。

Hierarchical Sparse Indexer 把 index 成本拆成三階段：

1. Full：第一個 Full 層掃過所有 main KV，選出 Top-512。同時用 blockwise max 選出高分 block。
2. Reindex：把選中 block 的位置收成 candidate pool。後續 Reindex 層只在 pool 裡打分。
3. Reuse：不做 index，直接沿用最新的 Top-K。

候選池上限是 2,048 × 8。
也就是 16,384 個 candidate positions。
最後的 attention 仍只讀 Top-512。

{{< figure src="images/06_sparse_indexer_pool.webp" alt="Hierarchical Sparse Indexer 流程：1M context 經 Full 層掃描，以 blockwise max 選出 16,384 個 candidate positions，Reindex 只在候選池打分，Reuse 層直接沿用 Top-K" caption="Full 層仍掃全部 main KV；blockwise max 選出 block 後，候選池固定為 16,384 個位置。Reindex 只在 pool 裡打分，Reuse 層直接沿用 Top-K。圖為示意，區塊與位置非等比例。" loading="lazy" >}}

第一個 Full 層仍掃全 context。
後續 indexer 的每 query 成本變成常數。
候選池大小固定，與 context 長度無關。

兩個細節。

- pool 共享，Top-K 不共享。不同 Reindex 層仍可選到不同 entry。
- training-aware，post-training 才引入。訓練與推論用同一套 restriction。deeper indexer 在自己的搜尋範圍內最佳化。這套機制不能訓練完才外掛。

## 7. FP4 KV：4 bit 不是把 512 個 channel 隨便砍

CSA2 解決多少 entry。
FP4 解決每個 entry 幾 bit。

V4.1-Flash 的 global KV 用 MXFP4：

- E2M1：4-bit 浮點，1 sign、2 exponent、1 mantissa。
- 每 16 個 channel 一個 E4M3 scale。
- 省略 NVFP4 的第二層 global scale。

為什麼能省？關鍵是範圍。

- 訓練後最大 RMSNorm weight magnitude 約 11。
- RMS normalization 後，512-channel KV latent 的 L2 norm 上限約 \(\sqrt{512} \approx 22.6\)。
- RoPE 保留 norm，旋轉後的最大絕對值也綁在同樣量級。
- 訓練中觀測到的最大 magnitude 約 10。
- E2M1 最大值 6，E4M3 scale 最大值 448。相乘可表示到 2688。

因此省掉 global scale 不會 clip，也不掉精度。
這個論證只對 normalize 過的 KV latent 成立，不代表 FP4 對所有張量安全。

{{< figure src="images/07_fp4_budget_range.webp" alt="FP4 的位元帳與範圍：每 16 個 channel 用 64 bits E2M1 加 8 bits E4M3 scale，平均 4.5 bits/channel；訓練觀測最大 magnitude 10、RMSNorm L2 上限 22.6，而 E2M1 6 × E4M3 448 可表示到 2,688" caption="左：每個 16-channel group 的位元帳；512 channels 約 288 bytes/entry，這還不是 890 bytes/token 的完整 breakdown。右：可表示上限 2,688，對觀測最大 10 約 268 倍、對 L2 上限 22.6 約 119 倍。" loading="lazy" >}}

其他精度決策。

- Quantize after RoPE。before RoPE 只有邊際改善，還會增加 decode overhead。
- Non-RoPE 與 RoPE 元件用同一格式。
- SWA KV 維持 FP8。它對量化更敏感。
- 與 V4 的 FP8 main KV 相比，FP4 幾乎再砍一半。HBM 與 SSD offload 都一樣。

890 bytes/token 不是 256 bytes。
\(512 \times 4 \div 8\) 只得 256 bytes，而且只算單層、單一 entry。
真正的 890 bytes 還牽涉幾件事：

- encoder 的 \(m=2\) sequence compression。
- 跨層共享後，不是每層都存一份。
- indexer K、scale、對齊與 SWA 分支另計。
- 官方沒有公布完整 breakdown。

能確定的是三者必須同時成立。
跨層共享、sequence compression、FP4。
拿掉任何一個，都會回到 KB/token。

## 8. SWA Bounded Replay：把 approximate 寫進部署策略

CED 與 CSA2 是模型架構的壓縮。
SWA Bounded Replay 是部署策略的壓縮。

兩種 KV 要分清楚。

- Global KV：永遠在 HBM，供 global attention 使用。
- Persistent KV：存在 SSD 或 host memory，用來做 prefix reuse。它包含 global KV，也可能包含 SWA KV。

V4 的 persistent KV 同時存 global KV 與 SWA KV。
SWA KV 只存兩個時間點。
prompt 結束，與 output 結束。
多輪對話時從那裡恢復。
實際部署中，SWA KV 幾乎占 persistent KV 一半。

問題是 SWA KV 的重用窗口只有幾分鐘。
session 結束或下一輪開始，它就死了。
放在 SSD 上長期保留，又貴又慢。

V4.1-Flash 改了做法。

1. SWA KV 不再進 persistent KV cache。改放每台機器 10% host DRAM 的 memory pool，TTL 幾分鐘。
2. global KV 留在 persistent cache，至少 72 小時。
3. request 命中 global KV，但 SWA KV 已被 evict 時，用 SWA Bounded Replay 重建。

精確重建要把最後 2,560 個 token 跑過 20 層。
合計 51,200 個 layer-token passes。
Bounded Replay 只跑最後 128 個 token。
20 層乘下來是 2,560 個 passes。
重算量因此是 1/20。
SWA 截斷在 replay segment 內。

{{< figure src="images/02_kv_budget.webp" alt="兩個儲存層的壓縮：HBM 的 global KV 從 100 降到 25，persistent SSD 從 100 降到 12.5；後者由 global KV 1/4 與 SWA 不落盤各貢獻一半" caption="V4.1 用 CSA2 與 FP4 把 global KV 壓到 1/4；再用 SWA Bounded Replay 把短期窗口整個移出 persistent storage，兩者相乘得到 1/8。SWA 條紋區為不落盤的短期 KV。" loading="lazy" >}}

圖裡的乘法關係是：

$$
\frac{1}{4}\ (\text{global KV}) \times \frac{1}{2}\ (\text{SWA 不再落盤}) = \frac{1}{8}
$$

論文說 bounded replay 的影響「negligible」。
他們在 post-training 就模擬同樣的 replay，讓模型適應。
這不是上線才補的 hack。

有三件事要盯。

- 重建不是數學等價。replay segment 起點 \(s\)，位置 \(i\) 的 query 只看得到 \([\max(s, i-W+1), i]\)。更早的 local 細節被截掉。
- session 越長、eviction 越頻繁，越容易踩到邊界。
- 它省 storage 與 recompute，不省語意。任務若依賴很早的 local 細節，這個近似就有成本。

## 9. 其他零件：mHC、Engram、DSpark、ViT

KV 之外還有幾個改動。

### Single-Pass mHC

V4 的 mHC 在 block 間維持 \(n\) 條 residual stream。
multi-pass 實作要跑三個 kernel。
residual update、coefficient prediction、input mixing。
activation memory traffic 是 \((4n+4)d\)。
V4.1 把 input mixing 的係數平移一個 block。
三個 kernel fuse 成一個 Mega-mHC。
traffic 降到理想的 \((2n+2)d\)。
論文設 \(n=4\)，等於從 \(20d\) 降到 \(10d\)。

這是 kernel-level 優化。
數學上只改了下標。
工程上少了一次完整的 residual read。

### Engram

Engram 是 conditional memory。
它把記憶從計算裡拆出來。
用 hash-based lookup 存取。

- 196B parameters，平均分給兩個 module。
- 放在 layer 1 與 layer 14（zero-indexed）。
- 每個 module 用 \(n\)-gram order \(\{2,3,4\}\)。
- 8 個 hash heads，每個 order 的 embedding dim 2048。
- 每個 head 一張約 16M entries 的表，大小取相異質數。
- Embedding table 與 key/value projection 都用 FP8。
- 推論時 deterministic addressing。
- 可從 host memory 透過 RDMA 背景 prefetch。
- 第一個 module 的 prefetch 能與第一個 Transformer block 重疊。

這對知識型能力有幫助。
但它讓部署更複雜。
196B 的 Engram 不在 GPU 上。
完整的 checkpoint 因此塞不進一張卡。

### DSpark

DSpark 是 speculative decoding 模組。
它先猜幾個 token，再讓主模型驗證。
模組有 3 個 Transformer block。
sliding window 是 128。
一次 forward 平行算 5 個 draft positions。
Markov head 建模 draft token 依賴。
confidence head 預測 acceptance probability。
scheduler 依 prefix survival 選 verification length。
它也看 engine throughput。

它與 V3 的 MTP 不同。
DSpark 在 pre-training 之後單獨訓練，backbone 凍結。
post-training 繼續訓練。
但 gradient 不傳回 backbone。

### DeepSeek-ViT

視覺編碼器是從頭訓練的。

- 32 層、dim 1024、16 heads、patch 14。
- 用 2D-RoPE 取代 absolute positional embedding，支援任意解析度。
- Patch embedding 用 linear projection，不用 convolution，為了與 Muon 相容。
- RMSNorm + SwiGLU。
- 進入 LLM 前做 3×3 pixel unshuffle，visual token 減少 9 倍。最高支援約 1344×1344。
- 2 層 MLP projector，hidden dim 5120。

3×3 unshuffle 的 9 倍不是小事。
visual token 數量與多模態 prefill 成本都由它決定。
這等於視覺端的 sequence compression，思路與 CSA2 一致。

## 10. 訓練：45T tokens，64K 起訓，34T 才拉到 1M

V4.1-Flash 的預訓練規模：

| 項目 | 設定 |
|---|---|
| Tokens | 45T multimodal tokens |
| Sequence | 64K 起訓；34T 時拉到 1M |
| Attention | 從第一步就用 sparse，沒有 dense warmup |
| Batch | 100.6M tokens |
| LR | 2000 steps warmup 到 \(2.6 \times 10^{-4}\)；維持到 28T；28T–40T cosine 到 \(2.6 \times 10^{-5}\)；40T–45T 維持 |

Optimizer 的分工：

| 參數 | Optimizer |
|---|---|
| Linear transformation、Engram projection、vision-language projector | Muon |
| Q/K | head-wise Muon |
| RMSNorm、非矩陣參數 | AdamW |
| Embedding、prediction head、Engram | momentum + Sinkhorn balancing |

Vision encoder 在 LR decay 前凍結。
decay 開始後才與 LLM 聯合訓練。

常見做法是先 dense 暖機，再切 sparse。
V4.1 跳過暖機，避開訓練看 dense、推論看 sparse 的 mismatch。
代價是訓練穩定性要求更高。

{{< figure src="images/08_training_schedule.webp" alt="訓練排程：sequence length 從 64K 起訓，34T tokens 時拉到 1M；learning rate 先 warmup 2,000 steps 到 2.6×10⁻⁴，維持到 28T，28T 到 40T cosine 降到 2.6×10⁻⁵，40T 後持平" caption="上方是 sequence length，下方是 learning rate；28T 開始 cosine，40T 後持平。warmup 2,000 steps 以 batch 100.6M tokens 估算約 0.20T tokens。" loading="lazy" >}}

後訓練的原則更直接：不引入新演算法。
論文說：

> we refrain from introducing novel post-training algorithms... our efforts are concentrated almost entirely on *what* the model is trained on rather than *how* it is optimized.

流程是標準的 SFT → RL → OPD。
改進幾乎全來自資料。
自動化合成、可驗證任務、reference solution。
程式化建構的 agent 環境。
filtering、dedup、difficulty calibration。
最後的 full-vocabulary OPD 用了 40+ 個 teacher。
teacher 之間可以架構不同。
每個 domain 挑最適合的，不必是最強的那個。

## 11. Reasoning effort：1 到 100，但 API 只給你 50/75/100

V4.1-Flash 把思考長度變成純量 \(b\)。
範圍是 1 到 100。
它直接 prepend 到 system prompt：

```text
Reasoning Effort: {effort} (range 1--100; higher values request more thorough reasoning)
```

訓練時對每個 \((x,b)\) 取樣多個 response。
組內做 mean-centered advantage。
不同 effort level 的 response 不直接比較。
差異靠 reward 的 length penalty 誘導。
token penalty 係數隨 effort 指數下降：

$$
k(b) = k_0 e^{-(b-b_{\min})/\tau}
$$

effort 越高，對 reasoning token 的懲罰越輕。
模型自然寫更長。
好處是不用為每個 effort 訓練 reward model。
調一個純量就夠。

API 只暴露三個預設：

| API tier | effort \(b\) |
|---|---:|
| low | 50 |
| high | 75 |
| max | 100 |

effort 25→100 的變化：

- 8 個 reasoning benchmark 平均 Pass@1：**67.1 → 76.3**
- DeepSWE v1.1：**66.0 → 74.2**
- Terminal-Bench 2.1：**82.4 → 90.6**
- 代價：output token 約 **×2.5**

{{< figure src="images/04_effort_frontier.webp" alt="effort 從 25 拉到 100 的分數與 token 成本：Terminal-Bench 2.1 從 82.4 到 90.6、DeepSWE 66.0 到 74.2、推理平均 67.1 到 76.3，token 約 2.5 倍" caption="只畫兩個端點，中間不插值。API 的 low/high/max 對應 effort 50/75/100；25 是論文的最小值，不是 API 選項。" loading="lazy" >}}

論文對 max 的建議：

> The gains are front-loaded: the 60–80 range already recovers most of the accuracy of the maximum setting at less than half of its token budget, whereas the final step to effort 100 lengthens agent trajectories by 1.6–1.8× for only marginal improvements.

實務上：

- 日常 agent 用 60–80。大部分 accuracy 已到手，token 省一半以上。
- max 留給最難的任務。75 到 100 的軌跡長 1.6–1.8 倍，分數只多一點。
- low 不是笨，是快。延遲敏感場景用 50，換可預測的回應時間。

effort 的控制是學出來的。
它不是 inference-time 的 prompt hack。
論文說單輪 reasoning 的控制能轉移。
也能用在 multi-turn agentic trajectory。
如果成立，這比單純的 length penalty 更有價值。

## 12. 版本時間線與成績單：9/10 的論文版，10/17 的 1017

| 日期 | 事件 |
|---|---|
| 2026-04-24 | DeepSeek-V4 Preview |
| 2026-08-13 | DeepSeek-V4-Pro GA |
| 2026-08-21 | DeepSeek-V4-Flash-Vision-Exp |
| 2026-09-10 | DeepSeek-V4.1-Flash 發布，API 上線，技術報告釋出 |
| 2026-09-14 | 所有 `deepseek-v4-pro` 請求路由到 V4.1-Flash，直到 V4.1-Pro 上線 |
| 2026-10-17 | DeepSeek-V4.1-Flash-1017，benchmark 更新，開源（MIT） |
| 2026-10-31 | Search / Fetch 的 server-side tool 呼叫開始計費（16:00 UTC） |

官方稱 1017 是 minor update，降低任務執行時間與輸出長度。
benchmark 全面上升，架構規格沒變。
改動主要在後訓練與資料。
引用架構數字時，用 9/10 論文。
引用 benchmark 時，用 1017 模型卡。

下面是 1017 模型卡的 11 項對照，含 Anthropic Opus-5。
HLE 是知識密集問答。
TB4.0 是 terminal 長流程。
DeepSWE / NL2Repo / ProgramBench 測軟體工程與 repo 生成。
Automation / ALE / Apex 偏工具使用與 agentic 推理。
Chartography / BabyVision / ZeroBench 測視覺與圖表。

| Benchmark | V4.1-Flash-1017 | V4.1-Flash (9/10) | Opus-5 |
|---|---:|---:|---:|
| HLE w/o tools | 42.6 (44.0†) | 36.8 (39.1†) | **56.3** |
| Terminal-Bench 4.0 | 42.3 | 31.2 | **51.8** |
| DeepSWE v1.1 | **77.0** | 74.2 | 74.0 |
| ProgramBench | 29.1 | 20.3 | **37.0** |
| NL2Repo-Bench | 68.2 | 65.4 | **75.3** |
| Automation-Bench v1.0.6 | **60.5** | 54.8 | 50.3 |
| Agents' Last Exam | **35.4** | 31.8 | 28.6 |
| Apex Bench v1.1 | **72.1** | 64.6 | 65.8 |
| Chartography (w/tools) | 83.0 | 78.9 | **84.0** |
| BabyVision (w/tools) | 92.5 | 89.6 | **94.1** |
| ZeroBench-main (w/tools) | 51.0 | 49.0 | **52.0** |

† 是 HLE 的 text-only subset。

這些分數是 vendor-run，harness 也不同。
TB4.0 用 Claude Code harness。
DeepSWE 用 Mini-SWE-V2。
system prompt、tool schema、turn-taking 都會影響分數。
不能當成同條件下的絕對能力。

有三個地方容易被誤讀。

1. 同一個 benchmark，1017 的分數都比 9/10 高。TB4.0 +11.1、ProgramBench +8.8、Apex +7.5。
2. TB2.1 與 TB4.0 不是同一張考卷。9/10 論文用 TB2.1，1017 模型卡用 TB4.0。不能拿 90.6 比 42.3 說退步 48 分。
3. 視覺與圖表只差 1–2 分。BabyVision 92.5 對 94.1 是很好的成績。但它不是贏過 Opus。

### 成績單：4 勝 4 負，還有 3 場小輸

只數贏幾項，容易得到全面超車的結論。
把差距畫出來，形狀不一樣。

{{< figure src="images/05_benchmark_gap.webp" alt="V4.1-Flash-1017 與 Opus-5 的 8 項對照：Automation、Agents Last Exam、Apex、DeepSWE 贏；NL2Repo、ProgramBench、Terminal-Bench 4.0、HLE 輸" caption="只畫差距較大的 8 項。Chartography（-1.0）、BabyVision（-1.6）、ZeroBench（-1.0）差距在 2 分內，未畫入。綠點為 V4.1 較高，紅點為 Opus-5 較高。" loading="lazy" >}}

| 結果 | 項目（差距） |
|---|---|
| 贏 4 項 | Automation +10.2、Agents' Last Exam +6.8、Apex +6.3、DeepSWE +3.0 |
| 輸 4 項 | HLE -13.7、Terminal-Bench 4.0 -9.5、ProgramBench -7.9、NL2Repo -7.1 |
| 小輸 3 項 | Chartography -1.0、BabyVision -1.6、ZeroBench -1.0 |

拆開看：

> V4.1-Flash 贏在工具使用與自動化。
> 它輸在知識密集、repo 級長流程與較難的 terminal 任務。

這符合它的定位：在 agent 工作負載上把成本壓到可大規模部署。
官方新聞稿說它是「smallest model in our new architecture family」。
它沒有宣告 frontier intelligence。

## 13. 部署與帳單：890 bytes 到底省了什麼

把 890 bytes/token 放回 serving。
會看到三個影響。

### 13.1 HBM：同樣的預算，多放約 4 倍的 1M context

同樣 1M context，global KV 從 3.5 GB 降到 890 MB。

只算 KV。
實際還要算 weights、activation、CUDA workspace、Engram prefetch buffer。
所以不是線性 4 倍。

同樣的機器能接更多百萬 context 的並發。
論文把 890 bytes 放在摘要第一段。
它沒有埋進 appendix。

### 13.2 SSD：persistent KV 降到 1/8

Persistent KV 的 1/8 有兩個乘數：

- global KV 本身是 1/4。
- SWA KV 不再落盤，幾乎再砍一半。

結果是同樣的 SSD 保留 8 倍 prefix。
agent 工作負載常重複同一段 prompt、repo 與對話。
這直接影響 cache hit rate。

1/8 的 persistent KV 不只是容量問題。
它是帳單問題。

### 13.3 價格：cache hit 與 cache miss 差 50 倍

`deepseek-flash` 就是 V4.1-Flash-1017。
API 價格每 1M tokens：

| | Off-peak | Peak |
|---|---:|---:|
| Input（cache hit） | **$0.003** | $0.006 |
| Input（cache miss） | **$0.15** | $0.30 |
| Output | **$0.60** | $1.20 |

`deepseek-v4-pro`（V4-Pro-0813）對照：

| | Off-peak | Peak |
|---|---:|---:|
| Input（cache hit） | $0.022 | $0.044 |
| Input（cache miss） | $0.66 | $1.32 |
| Output | $1.98 | $3.96 |

Peak 是 UTC 週一至週五的 01:00–04:00 與 06:00–10:00。
其餘時段，含週末與中國國定假日，都是 off-peak。

$0.003 對 $0.15，不是筆誤。
persistent KV 留得住，比模型跑得快更影響成本。

一個具體例子：1M input + 100K output，off-peak：

| 情境 | Input | Output | 合計 |
|---|---:|---:|---:|
| V4.1-Flash，cache miss | $0.15 | $0.06 | **$0.21** |
| V4.1-Flash，cache hit | $0.003 | $0.06 | **$0.063** |
| V4-Pro，cache miss | $0.66 | $0.198 | **$0.858** |

同一段 input 命中 cache，帳單從 $0.21 降到 $0.063。
差 3.3 倍。
同樣工作負載改用 V4-Pro 的 miss 價，是 $0.858。
約 4.1 倍。
這解釋了時間線上的路由決定。
對大多數 agent 工作負載，便宜的那個已經夠好。

{{< figure src="images/09_cache_cost.webp" alt="Cache 成本拆解：左圖 input-only 價格，V4.1 的 cache hit 與 miss 差 50 倍、V4-Pro 差 30 倍；右圖 1M input 加 100K output 的總價，V4.1 miss 到 hit 只差 3.3 倍，V4-Pro miss 到 V4.1 miss 差 4.1 倍" caption="左：input-only 的 cache hit/miss 差距；右：加上 100K output 後，總帳單差距被 output 稀釋。價格皆為 off-peak。" loading="lazy" >}}

### 13.4 但 weights 沒有變小

被壓縮的只有 KV，權重沒有動。

完整的 checkpoint 仍然需要：

- 大規模的 GPU 記憶體（或跨節點 sharding）；
- 對應的儲存與載入頻寬；
- Engram 的 host memory 與 RDMA prefetch；
- 足夠的 CPU / 網路資源來支撐 sandbox 與工具呼叫。

所以「V4.1-Flash 很省」是相對它自己的規模。
它不是能在筆電上跑 1M context。
官方新聞稿說，要規劃 2,000 GPUs 與 storage cluster 的部署，歡迎來談。

## 14. 限制與未解問題

限制集中在幾件事。

1. 890 bytes/token 只計 global KV。SWA KV 仍存在，每層 128 window、FP8，只是被 bounded replay 近似重建。
2. SWA Bounded Replay 是近似的。論文說影響 negligible，但 limitation 仍點名 cache-resumption boundary 尚未完全 characterize。
3. CSA2 的 sparse selection 可能選錯。Top-512 從壓縮後的 entry 選出。壓縮、FP4、跨層共享三個近似疊在一起。long-context retrieval 的極端案例仍是風險。
4. 1M prefill 仍然不便宜。CED 把 \(O(NL)\) 降到約 \(O(NL/2)\)。這是砍半，但不等於零。
5. FP4 的 long-tail 風險未完全證明。範圍論證只保證最大 magnitude。它不保證每個 channel 的 quantization error 都不影響下游。QAT 與 post-training 吸收大部分。極端輸入仍可能踩到。
6. Engram 的部署複雜度被低估。196B embedding 在 host memory，靠 RDMA prefetch。它對 latency 與網路要求很高。不是每個團隊都有這種基礎設施。
7. 省 4 倍 HBM 不等於省 4 倍成本。weights、網路、儲存、維運、閒置容量都會吃掉一部分。890 bytes 是必要條件，不是充分條件。

## 15. 設計判斷

### 把 KV 當成一級公民

多數模型先定 attention，再順便處理 KV。
V4.1-Flash 反過來。
它先定 KV 預算，再設計 attention。

- CED 改寫層的職責：global KV 改由 encoder 輸出。
- CSA2 設計三種模式，讓 index 與 cache 分開共享。
- FP4 縮小每個 entry，連 scale 層數都重新論證。
- SWA Bounded Replay 把 SWA 移出 persistent KV，接受近似重建。

四個決策指向同一個目標。

### 共享 cache 與 index，不共享 query

CSA2 的關鍵是知道什麼不能共享。

如果連 query 都共享，每層就看同一個方向。
表達力會塌。
CSA2 把共享停在 cache 與 index。
查詢與 SWA KV 仍歸各層。
平衡點很細。
共享夠多，才有儲存效益。
共享夠少，才不犧牲深度。

### 用可接受的近似換 storage

SWA Bounded Replay 靠幾個現實條件成立。

- SWA 的重用窗口只有分鐘級。
- 精確重建要跑一整段，邊界重建只要一個窗口。
- 這個近似只發生在 cache miss 的邊界，不是每一步都發生。

重點是把最壞情況從 full replay 換成 bounded replay。
再用訓練吸收誤差。
代價沒有消失。
但它把一個不可用的設計變成可用。

---

V4.1-Flash 沒有全面超車 Opus-5。
HLE、ProgramBench、TB4.0 都還輸。
這些差距是真的。

但它在 Automation、Agents' Last Exam、Apex、DeepSWE 上贏。
它把 1M context 的 global KV 壓到 890 MB。
persistent KV 壓到 1/8。
兩件事同時成立，才是設計核心。

> 它沒有把骨幹變小。
> 它把長 context 的代價變小。
> 骨幹反而變大，因為省下的預算拿去換能力。

## 參考資料

- DeepSeek-V4.1-Flash 技術報告：<https://arxiv.org/abs/2609.19969>
- 官方公告（2026-09-10）：<https://www.deepseek.com/en/news/deepseek-v4-1-flash/>
- API 定價：<https://api-docs.deepseek.com/quick_start/pricing/>
- 1017 發布說明：<https://api-docs.deepseek.com/news/news261017>
- 1017 模型卡：<https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017>
- 9/10 模型卡：<https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash>
