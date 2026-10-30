# 投影片與文章對照

> `AGENTS.md` 的延伸文件。只在改投影片、去識別化或用詞時讀。
> 本機路徑、專案代號與禁用字串清單在 `AGENTS.local.md`（不進版控）。

`fab-predictive-maintenance-ppt169` 與 `edge-ai-platform-ppt169` 兩篇的圖片來自自製 SVG 簡報。
**投影片與文章是兩份獨立檔案**，改一邊時務必同步另一邊。

⚠️ 部落格文章 slug 與投影片專案資料夾名**刻意不同**。本地專案代號見 `AGENTS.local.md`。
對外 slug **不得含公司名稱或業態字樣**，因為它會出現在公開 URL、`og:url`、`canonical`、RSS 與 sitemap。

## 檔案位置

本地路徑、專案代號、備份與匯出位置見 `AGENTS.local.md`。這裡只記規則：

- 專案資料夾**不是 git repo**，改 SVG 前手動備份。
- SVG 有兩份序列化格式（`svg_output/` 與 `svg_final/`），改完要同步。
- 部分 SVG 以相對路徑引用外部 PNG；轉檔時來源圖必須與 SVG 同目錄，否則圖片會空白。
- 個別 SVG 內含 JS metadata 與靜態 `<text>` 兩份文字，改字時兩處都要改。

⚠️ **浮水印不會自動套用。** 已加浮水印的來源圖不放在部落格 repo 內，流程見下方。

## 圖片路徑：en 版與 zh 版共用（**這不是問題，不要修**）

`content/en/{posts,projects}/*/` **刻意沒有 `images/` 資料夾**，這是設計而非疏漏。

兩篇英文文章的 markdown 裡寫的路徑跟中文版**完全相同**（`images/01_cover.png`、`images/02_architecture.png` …）。Hugo 在當前 page bundle 找不到資源時會跨 bundle 解析，直接命中 `content/zh-tw/{posts,projects}/*/images/` 的同一個檔案。

- 圖片**只需要放在 `content/zh-tw/` 一份**，不需要複製到 `content/en/`。
- 產出的 HTML 會把 `src` 指向 **zh-tw 文章的 URL**，這是**預期行為**，不是壞連結。
- 投影片本來就是中文的，英文文章引用中文投影片是刻意的。
- 重製圖片時**只覆蓋 `content/zh-tw/{posts,projects}/*/images/*.png`**，英文版自動跟著更新。

⚠️ 若日後 `content/en/{posts,projects}/*/` 出現 `images/` 資料夾，英文頁的 `src` 會改指向 `/blog/en/...`，同一張圖會存兩份。

## 兩邊刻意不同（不要「修正」）

| 投影片 SVG | 部落格文章 | 原因 |
|---|---|---|
| 公司名稱（含簡稱） | `公司名稱` / `"company name"` | 去識別化 |
| `4.5 Yrs Domain Experience`（01 封面）<br>`4.5 Yrs Smart Manufacturing & Domain Expertise`（11 感謝頁） | **保留在封面，不得寫入內文** | Domain 年資是產業壁壘的標示，HR／LinkedIn 搜尋靠它；封面是 og:image 會外流，但這是有意為之 |
| `門檻僵硬`（edge 02） | `門檻固定缺乏彈性` | 藥丸寬 103px，字多會溢出 |
| `架構約束少`（edge 10） | `架構約束少，難以拆分服務` | 下一欄從 x=500 起 |
| `C2 管制級以下的邊緣自動化設備`（10） | `C2 管制層級（含 C2）以下的邊緣自動化設備` | 表格欄位到 x=1220 |
| `deque 記憶體削峰填谷` | `deque 記憶體削峰環狀緩衝區` | 文章補上「環狀緩衝區」語意 |
| `邊緣 AI 與故障預測健康管理` | 同上加 `(PHM)` | 文章補縮寫 |

英文版為意譯非逐字：`5s (突發點)` → `5s (burst start)`、`25s (消化完成)` → `25s (backlog fully absorbed)`。

## 業態去識別化（不只是公司名稱）

除了公司名稱，**具體業態**同樣會縮小識別範圍。

⚠️ **適用範圍：只套用在「履歷頁」與「投影片／由投影片衍生的那兩篇已發布文章」。**
其餘內容（首頁 Console、其他文章、程式註解）**不需要**自我審查。寫 `OHT`、`SECS/GEM`、`MES/EAP` 這類廠內術語是刻意的，那是能力證明與領域感。

| 不要寫 | 改用 |
|---|---|
| 公司全名、簡稱 | `公司名稱` / `[Company Name]` |
| 具體產線類型 | `產線`、`半導體製造` / `Semiconductor Manufacturing`、`production line` |
| 更細的產業分類 | `半導體製造` |

實際禁用字串見 `AGENTS.local.md`。

履歷「領域知識」與工作經歷裡的**設備級技術細節**（機台類型、數量）是**刻意保留**的，那是能力證明。刪掉反而會讓履歷失去可信度。

⚠️ 這些字眼若出現在**投影片 SVG** 裡，會被燒進 PNG 圖片，只改 markdown 沒用。改字時必須同步改 SVG 並重出圖片。

⚠️ **首頁 Console 不受此限。** `data/home.yaml` 的 `shared.console.stream` 直接使用廠內術語，是為了讓看過產線的人一眼認出「這是真的」，刻意保留。

## 兩邊必須一致的字詞

| 投影片／舊用詞 | 已統一為 |
|---|---|
| 數據 | 資料 |
| 智能 | 智慧 |
| 身份驗證 | 分身驗證 |
| 沙盒 | 沙箱 |
| 邊緣端直接加載 | 邊緣端直接載入 |
| 動態配置 | 動態設定 |
| CPU 100% 爆滿 | CPU 100% 滿載 |
| 資料偏移 / 特徵分布偏移 | 資料漂移 / 特徵分布漂移 |
| 異常下線率 | 異常停機率 |
| 緩存與回補 | 緩衝與回填 |
| 斷線保命機制 | 斷線保護機制 |
| 金絲雀灰度發佈 | 金絲雀分批發佈 |
| Weibull 生存分配 | Weibull 存活分布 |
| 平均故障偵測時間加速 40% | 縮短 40% |
| 年節省工時 | 每年節省工時 |
| AI 模型市場化 | AI 模型商品化 |
| 資料不落地雲端 | 資料不離開本地 |
| 版本發送 | 版本發佈 |
| 健康度分數優化 | 健康度分數歸一化 |
| 500 筆 / s、500 pts/s | 500 筆 / 5s、500 pts / 5s |
| 平滑寫入上限 1000 req/s | 100 req/s（= 每 5 秒 500 筆） |
| 產線良率的舊寫法（含縮寫） | 產線良率 / production line yield |

⚠️ **數據 → 資料 已在兩篇文章全面套用。** 注意 `content/zh-tw/resume/index.md` 與 TECH_TRENDS 系列是機器翻譯稿，仍保留 `數據`，那是刻意不動的（改動會牽動整篇）。

## 重新產生部落格圖片的流程

1. 改 `svg_output/*.svg`，並手動同步 `svg_final/`
2. **手動改 `<image href>`**：把外部 PNG 的 href 改成浮水印版檔名（來源圖與產出方式見 `AGENTS.local.md`；此步驟**不會自動完成**）
3. **去識別化**：另存一份副本，把公司名稱換成 `公司名稱`
4. 轉 PNG（指令見 `docs/image-conversion.md`）
5. 跑防盜浮水印 `scripts/anti_theft_watermark.py`
6. 覆蓋 `content/zh-tw/{posts,projects}/*/images/*.png`
7. `hugo -D --minify` 驗證

## 圖片格式與尺寸規範

TECH_TRENDS 系列原本把資訊圖存成 PNG，單檔最大 9.3 MB，六篇合計 204 MB。已全面改格式，**往後一律照下表，不要走回頭路**：

| 用途 | 格式 | 尺寸 | 指令 |
|---|---|---|---|
| 內文資訊圖 | WebP q82 | **維持原始寬度**（1376px） | `magick "$f" -alpha off -strip /tmp/t.png && cwebp -quiet -q 82 -m 6 /tmp/t.png -o "${f%.png}.webp"` |
| 封面 `cover` | JPEG q85 | 1200px 寬 | `magick "$f" -resize 1200x -strip -quality 85 "$d/cover.jpg"` |
| YouTube 縮圖 | JPG | 不動 | — |

三個不能違反的理由：

1. **內文圖絕不可再縮小。** PaperMod `--main-width: 720px`，1376px ≈ 1.9x 是正確的 retina 倍率。縮到 1000px 只剩 1.4x，retina 螢幕會糊。只換格式、不改尺寸。
2. **`-alpha off` 是必要的。** 這些 Gemini 產出的圖 alpha 通道 100% 不透明（`alpha_min == alpha_max`），留著只是死重。
3. **封面用 JPEG 而非 WebP。** PaperMod 把 `cover.image` 直接塞進 `<meta property="og:image">`，Facebook / LinkedIn 對 WebP 的 og:image 支援不完整。

⚠️ **en 側的引用路徑必須與 zh-tw 完全一致**：`content/en/posts/tech-trends-*/` 刻意沒有 `images/`，靠 Hugo 跨 bundle 解析到 zh-tw。改檔名時漏改英文版，英文頁就整片破圖。
