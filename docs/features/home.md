> 本文件是 `AGENTS.md` 的延伸，只在改到這個功能時讀。回到 [AGENTS.md](../../AGENTS.md)。

## 首頁（Personal Engineering Lab）

首頁已從 PaperMod 原生的「自我介紹 + 文章列表」改成自訂版面。**原 `homeInfoParams` 機制在首頁已完全失效**，見下方踩坑紀錄。

### 檔案與職責

| 檔案 | 職責 |
|---|---|
| `layouts/index.html` | 首頁全部版面 |
| `layouts/partials/home_posts_list.html` | 底部文章列表 + 分頁 |
| `layouts/partials/lab_icon.html` | 4 個 inline SVG icon（`cpu` / `chart` / `layers` / `agent`） |
| `layouts/partials/lab_console.html` | Engineering Console 區塊本體 |
| `assets/js/lab-console.js` | Console 的假日誌 / 指標 / 時鐘 |
| `assets/css/extended/lab-console.css` | Console 的 `.lab-term*` 樣式 |
| `data/home.yaml` | 雙語文案，**頂層以語言代碼分組** |
| `assets/css/extended/custom.css` 末段 | `.lab-*` 樣式 + `--accent` 點綴色 |

**版面順序**：Hero → **Console** → 技術領域 → 精選文章 → 最新文章。
Console 原本在精選文章之後，移到 Hero 正下方 —— 它是整頁 Edge AI 氛圍最強的一塊，
放第一屏就能建立印象，也不用捲到底才看到。

### Engineering Console（genact 風格動態終端機）

紅黃綠圓點 + `edge-node-01` 主機名 + LIVE 時鐘、四格真實統計、
三個假即時指標（吞吐量 / 延遲 / 異常分數，各 24 格長條）、genact 日誌串流與進度條任務。

**真實 vs 假資料要分清楚：**

| 區塊 | 性質 | 來源 |
|---|---|---|
| 文章 / 標籤 / 累積字數 / 最後建置 | **真實** | Hugo 建置時算出 |
| 吞吐量 / 延遲 / 異常分數 / 日誌 / 進度條 | **假的**（genact 風格噪音） | `data/home.yaml` 的 `shared.console` |

不要拿指標數字去宣稱任何效能宣稱 —— 那是寫死的序列，不是量測值。

⚠️ **三個指標是「腳本化序列」，不是隨機數。** `shared.console.metrics[].series` 是
48 個寫死的值，每 900ms 前進一格（43.2 秒一輪），首尾刻意接得起來所以循環無斷崖。

- **為什麼不用 `base + jitter`**：白雜訊的相鄰兩點互不相關，24 根長條同時亂跳
  只會像雜訊，看不出時序。有連貫性的序列才會讓波形「往左流動」。
- **流動是怎麼發生的**：`hist.push(v)` + `hist.shift()`（右進左出）本來就是對的，
  加上 CSS 的 `transition: height 0.5s ease` 對**全部 24 根**同時補間，
  第 i 格拿到的是第 i+1 格上一輪的值 → 整條波形左移一格。**不需要** `translateX`。
- **`domain` 是固定尺標**，不是自動 min/max。自動縮放會讓平穩時段被拉滿格，
  看起來永遠很忙；固定尺標才看得出「安靜」與「尖峰」的差別。
- **三條序列同索引聯動**：k=9（輕微）、k=25–26（嚴重）、k=38–40（輕微復發）。
  異常分數尖峰時延遲同步升高、吞吐量同步下探 —— 這是真實感最大的來源。
- **沒有 `series` 時** JS 會退回舊的 `base + jitter` 行為，改壞 data 不會整塊不動。
- **初始值**由 partial 取 `index .series 0` 並用 `printf "%.*f" .digits` 補零，
  JS 也從 `series[0]` 起跑 → 有無 JS 的畫面一致。

⚠️ **anomaly 的長條三色分級。** 只有帶 `levels` 的 metric 會被染色，
其他（throughput / latency）維持單色綠 —— 這是刻意的，兩條平穩序列分色只會顯得多餘。

```yaml
- id: anomaly
  levels: { warn: 88, err: 94 }   # 百分位門檻
```

- **門檻是百分位，不是固定值**：JS 在 init 時把 `series` 複製排序、用線性插值
  各算一次 p88 / p94（與 numpy 預設 method 一致），序列固定所以只算一次、不進 tick。
  **改 `series` 顏色會自動跟著調**，這是選百分位而非寫死門檻的理由。
- **為什麼不是 75 / 90**：事件只佔 6/48 = 12.5%，p75 會被拉進正常雜訊（0.043），
  正常運轉時就有 13 根變黃、等於雜訊。p88/p94 = 0.064/0.120 正好落在
  正常段（≤0.046）與事件段（≥0.095）之間的空隙裡 → 平常全綠，只有事件亮起來。
- **染色依「該格的值」而定，與位置無關**：`paint()` 逐根比對 `hist[i]` 後掛 `class`，
  所以紅色長條往左移動時仍保持紅色，滑出視野才消失。讀數（`<b data-val>`）
  與最右邊那根同源，同步轉色。
- **`tier()` 回傳空字串給正常值**（`className = ''`），所以沒帶 `levels` 的 metric
  永不進這個分支；沒有 JS 時 bar 完全沒有 class → 全綠，與伺服器端渲染一致。
- 顏色沿用終端機既有的 `--t-amber` / `--t-red`，不另開新色。
  對比：綠 7.45:1、黃 7.50:1、紅 5.65:1（皆遠超圖形 3:1 門檻）。

⚠️ **日誌等級是加權抽樣，不是均勻抽。** `shared.console.weights` 決定各等級的機率
（`info .40 / ok .28 / warn .16 / dbg .11 / err .05`），JS 先依權重抽等級、
再從該等級的桶子裡抽一則。

- **為什麼不能均勻抽**：`stream` 現在有 43 則、其中 7 則是 `err`。直接 `pick(stream)`
  會變成 ~16% 錯誤率，console 看起來像壞掉。加權後 ERR 佔 stream 的 5.2%，
  再乘上 `tick()` 有 22% 走進度條分支 → **約每 9 秒一行紅色 ERROR**。
- **要調紅色 ERROR 的密度就改 `weights.err`**（例如 `0.025`），不要動 JS。
- 空桶自動跳過、總和自動重新歸一；`weights` 缺失時退回均勻抽樣。

**改文案的位置**：`data/home.yaml` 的 `shared.console`（假日誌 / 指標 / 進度條任務，
兩種語言共用，因為是技術術語氛圍不翻譯）與各語言的 `console`（四格統計的標籤、
開機訊息、status / focus / wisdom）。可用 placeholder：
`{ms} {pct} {f2} {f3} {hex} {n} {h} {node} {temp} {khz} {ver}`，lv 只能是
`info / ok / warn / err / dbg`。**要新增 placeholder 就改 `lab-console.js` 的 `subs`**，
不要改 data。

⚠️ **值域不是裝飾，用錯會寫出自相矛盾的句子：**

| placeholder | 值域 | 為什麼需要它 |
|---|---|---|
| `{f3}` | 0.000–0.120 | 一般小數。**不能**拿來寫「score 超過 0.85」 |
| `{score}` | 0.860–0.990 | 異常分數，專門給「exceeds threshold 0.85」用 |
| `{pct}` | 1–99 | 百分比。拿來寫 `psi=0.{pct}` 會出現 0.99 這種不現實的漂移值 |
| `{psi}` | 0.12–0.41 | PSI 漂移指標 |
| `{n}` | 100–9999 | 一般整數。拿來寫 `buffer={n}/5000` 會出現 8734/5000 |
| `{buf}` | 1200–4980 | deque 緩衝量，配合 `/5000` 上限 |
| `{code}` | 1/2/125/126/127/134/137/139/143 | 行程結束碼（`{n}` 是四位數，不像 exit code） |
| `{ver}` | `v2.3.14` | **已自帶 `v`**，寫 `phm-v{ver}` 會變成 `phm-vv2.3.14` |

⚠️ **四格統計必須先 `where "Draft" false`。** 站上目前只有 2 篇 `draft: false`
（其餘 TECH_TRENDS 系列 / `mermaid-smoke-test` / `hello-world` 全是草稿），
Hugo 的 `site.RegularPages` 與 `site.Taxonomies` 都把草稿算進去，直接用會顯示
「文章 10」。`hugo --buildDrafts` **不會**把 `.Draft` 改成 true（它只是把草稿納入建置），
所以這裡過濾後 `-D` 與正式 build 的數字一致。

⚠️ 標籤數**刻意不用** `len site.Taxonomies.tags`，改成從已發布文章的 `.Params.tags`
收集後 `uniq` 去重 —— taxonomy 詞彙表含草稿，跨語言時的合併行為不想賭。

⚠️ 「最後建置」用 `now`，**不是** `site.Lastmod`。後者是站上最新頁面的修改時間，
會永遠停在最後一次寫文章的日期，跟「建置」是兩件事。代價是輸出不可重現。

⚠️ `$allPosts` 本身**不能**動：它同時餵給精選卡與 `home_posts_list.html`，
那兩處刻意保留草稿（本地 `hugo server` 要看得到）。只有統計這裡另開一份 `$published`。

**漸進增強**：伺服器端已渲染開機訊息 + 靜態指標 + 四格統計，
沒有 JS 時版面完整不空白，只是沒有串流。JS 在三種情況會停掉計時器：
`prefers-reduced-motion`、分頁隱藏（`visibilitychange`）、捲出視窗（`IntersectionObserver`）。

⚠️ **不要把這個 partial 搬到 `extend_footer.html`**：footer 是 `partialCached`，
快取鍵是 `.Layout`/`.Kind` 不是頁面（見下方踩坑紀錄），`data-cfg` 會變成
「第一個被算到的頁面決定全站」。

⚠️ **script 必須走 assets pipeline**（`resources.Get` + `minify` + `fingerprint`），
不能放 `static/js/` 配 `absURL` —— 沒有指紋就是沒有快取破壞，讀者會拿到舊的 JS。
寫法與 `extend_footer.html` 的 `share-link.js` 相同，坑也相同（見「踩過的坑 3」）。

⚠️ **`.lab-term` 配色固定深色，不跟隨 light/dark 主題** —— 這是 genact 的視覺語言。
終端機有自己的 `--t-green` / `--t-cyan` / `--t-amber` / `--t-red` log 等級語意色，
**刻意沒有套 `--accent`**，套了 warn 跟 ok 會分不出來。

⚠️ **`.lab-term__log` 是 `aria-hidden`** —— 每 0.15 秒跳動一次的裝飾區塊，
螢幕閱讀器唸出來只是噪音。下面的 status / focus / wisdom 才是真內容。

### Hero 的文字畫（兔子）

首頁 hero 右半邊是「用 dotfiles 文字畫出的兔子」，移植自 Hallmark "Terminal" 主題 demo（burrow），
網格、色票、字重、右下對齊全部照抄。

| 檔案 | 職責 |
|---|---|
| `layouts/partials/glyph_art.html` | 只有首頁呼叫：`@font-face`（走 assets pipeline）+ `<canvas>` + 無 JS 的 `<pre>` |
| `assets/js/glyph-art-data.js` | `window.ART`：hare 132×110（ratio 1.85）、mark 250×31，**原樣搬，不要改** |
| `assets/js/glyph-art.js` | 渲染器（原版 `page.js` 的 `art()` 移植） |
| `assets/glyph-art/hare.txt` | 無 JS 版本的同一份網格 |
| `assets/fonts/martian-mono-latin-var.woff2` + `OFL.txt` | 38 KB 變體字型；OFL 要求授權檔一起發佈，**不要刪** |
| `assets/css/extended/lab-glyph.css` | 8 階色票、版心加寬、grid、`<pre>` 縮放 |

⚠️ 不能改的數字（改了就不像）：
- `cw = min(W/132, H/(110×1.85))`、`ch = cw×1.85`、`fs = cw×1.62`、`ox = W - cw×132`、`oy = H - ch×110`
- 色階索引是 **`ramp[v-1]`**，不是 `ramp[v]`；`ramp[7]` 只給雜訊／熱點用
- 字重 `v>6 ? 700 : 500`、字級係數 `0.62 + 0.38×min(1, v/6)`
- **canvas 不要設 `font-stretch`**：原版也沒設，字元重疊 ~20% 正是它的樣子（`<pre>` 那邊才設 87.5%）

⚠️ `--glyph-*` scope 在 `.lab-glyph` 上（原版放 `:root`），JS 用 `getComputedStyle(box)` 讀；
搬到 `:root` 只是讓全站多 9 個變數。

⚠️ 版面：`.main:has(.lab-hero)` 放寬到 1168（1120 內容 + 2×24），**其餘區塊仍 720 置中**；
桌機同時把 `--nav-width` 設成 1120，logo 才跟 hero 左緣對齊。

⚠️ 降級：`<pre>` 用 `min(100cqw/85.8, 100cqh/132.3)` + `line-height: 1.2025` 對齊 canvas
（`container-type: size` 是必需的，只寫 `100cqw/80.85` 會高 6% 裁掉耳朵）；
`prefers-reduced-motion` 只畫一幀；滑鼠熱點只在 `(hover:hover) and (pointer:fine)`；
分頁隱藏時停 raf。

⚠️ `<pre>` 內文必須 `| safeHTML`：`.Content` 是字串，Hugo 會把 `+` 轉成 `&#43;`，
整張圖變成實體碼（症狀：非空白字元數從 6,306 暴增到 12k）。

⚠️ `.lab-glyph` 底色固定深綠黑 `oklch(12.5% 0.012 150)`，**淺色模式也是一塊深色**，
刻意的（跟 `.lab-term` 同一個理由）。

```sh
rm -rf public && hugo --minify
rg -c 'lab-glyph' public/index.html
rg -c 'glyph-art' public/posts/<slug>/index.html        # 應為 0（只有首頁）
python3 - <<'PY'
import re,html
h=open('public/index.html',encoding='utf-8').read()
t=html.unescape(re.search(r'<pre class=lab-glyph__still[^>]*>(.*?)</pre>',h,re.S).group(1))
print(len([c for c in t if not c.isspace()]), max(len(l) for l in t.split('\n')))  # 6306 125
PY
```

### 精選文章會自動增加

文章 front matter 加一行 `featured: true` 就會自動進首頁精選區，**不需要改模板也不需要改 data**：

```yaml
featured: true
```

中英文各自為政（兩份 front matter 分開設）。卡片標題、摘要、封面、tags 全部從文章自己的 front matter 讀，**沒有數量上限**（刻意如此：要的就是卡片隨文章一起長），依日期新到舊排序。

### ⚠️ 踩過的坑 1：只要有 `layouts/index.html`，PaperMod 的 list.html 在首頁永遠不會被呼叫

Hugo 的 home page lookup 順序是 `layouts/index.html` > `layouts/_default/list.html`。所以：

- `config.yaml` 的 `homeInfoParams` 設定**在首頁完全無效**（`home_info.html` 只會被 `_default/list.html` 呼叫）
- 刪掉 `homeInfoParams` 不會有任何視覺變化
- 要新增首頁內容，只能寫進 `layouts/index.html`，改 `config.yaml` 沒用

這也是為什麼文章列表要自己搬一份到 `home_posts_list.html`。

### ⚠️ 踩過的坑 2：data 檔的語言後綴無效，要用 `site.Language.Lang` 取

實測 `data/home.zh-tw.yaml` 在 Hugo v0.168 會被註冊成 key `"home.zh-tw"`，`site.Data.home` **取不到**（回傳空字串，不是 fallback）。

正確做法（本專案採用的）：

```yaml
# data/home.yaml
zh-tw:
  hero: { title: "..." }
en:
  hero: { title: "..." }
```

```go-html-template
{{ $home := index hugo.Data "home" site.Language.Lang }}
```

⚠️ 別寫 `hugo.Data.home.zh-tw.title` —— 語言代碼含連字號，用 `index` 取值才保險。
⚠️ `.Site.Data` 在 v0.156 起已 deprecated，要用 `hugo.Data`（用錯會出 WARN）。

### ⚠️ 踩過的坑 3：技術卡對不到 tag 頁會整張消失（這是刻意的）

模板用 `site.GetPage (printf "/tags/%s" (urlize .tag))` 查詢，**查不到就整張卡不渲染**。

這是刻意的：與其輸出一個 404 的入口，不如先不給這張卡。但副作用是 —— **在 `data/home.yaml` 加新 tag 之前，一定要先確認那個分類真的有文章**，否則卡片會無聲消失。

站上實際存在的 tag：`edge-ai` / `machine-learning` / `system-design` / `ai-agent` / `predictive-maintenance` / `backend-engineering` / `phm` / `fab-domain` / `預測性維護` / `系統設計`。

### ⚠️ 踩過的坑 4：首頁**刻意不用** AOS 的 `data-aos`

AOS 的 CSS 有這條：

```css
[data-aos^=fade][data-aos^=fade] { opacity: 0 }
```

只要元素帶 `data-aos`，**CDN 的 aos.js 掛掉時內容就永遠是隱形的**，而且不會報錯、沒有 fallback、沒有 console warning。AOS 是從 jsdelivr 載入的（`extend_footer.html`），CDN 被擋就會發生。

這與 mermaid 那條「不要用 `visibility: hidden`」是同一個道理：寧可不要動畫，也不要讓 CDN 失敗等於內容消失。

首頁因此改用純 CSS `lab-rise` keyframe，起始狀態寫在選擇器上、動畫結束停在 `opacity: 1`，所以即使 animation 被整個忽略，**元素仍然可見**（只少了位移效果）。已用 `--disable-javascript` 截圖驗證過。

`{{< animate >}}` shortcode 仍然可以用在文章內文（那是有逐篇決策的地方）。

### ⚠️ 踩過的坑 5：hugo --minify 會拿掉最後一個宣告的分號

驗證 CSS 對比度的腳本用 `(--[\w-]+):\s*([^;]+);` 抓宣告，會**靜默漏掉每個 block 的最後一個變數**。踩到時 `--accent` 整個消失在字典裡，卻沒有報錯。

正確寫法是不要要求結尾分號：

```python
re.findall(r'(--[\w-]+):\s*([^;}]+)', body)
```

### 點綴色與對比度

`--accent` 是唯一的彩色變數，其餘維持純黑白色系：

| 模式 | `--accent` | 白/黑底對比 | 用在哪 |
|---|---|---|---|
| light | `rgb(79, 70, 229)` | 6.29:1 ✓ AA | eyebrow / icon / 卡片計數 / primary 按鈕底 |
| dark | `rgb(147, 139, 255)` | 7.38:1 ✓ AAA | 同上 |

⚠️ 點綴色**沒有用在內文**，只用在 icon 線條與小標。淺色模式 6.29:1 剛好過 AA 的一般文字門檻（4.5:1），不要再把它拿來當長段內文色。

驗證腳本（記得用 `[^;}]+` 不是 `[^;]+;`）：

```sh
CSS=$(ls public/assets/css/stylesheet.*.css | head -1)
python3 - "$CSS" <<'PY'
import re,sys
css=open(sys.argv[1],encoding='utf-8').read()
blocks=[(('data-theme' in m.group(2)), m.group(3)) for m in re.finditer(r'(@media[^{]*\{)?(:root(?:\[[^\]]*\])?)\{([^}]*)\}', css)]
def lum(rgb):
    c=[int(float(x))/255 for x in re.findall(r'[\d.]+', rgb)[:3]]
    c=[x/12.92 if x<=0.03928 else ((x+0.055)/1.055)**2.4 for x in c]
    return 0.2126*c[0]+0.7152*c[1]+0.0722*c[2]
def ratio(a,b):
    hi,lo=max(a,b),min(a,b); return (hi+0.05)/(lo+0.05)
for theme in ('light','dark'):
    v={}
    for isdark, body in blocks:
        if isdark == (theme=='dark'):
            v.update(re.findall(r'(--[\w-]+):\s*([^;}]+)', body))
    a,b=lum(v['--accent']),lum(v['--theme'])
    print(theme, f"accent {ratio(a,b):.2f}:1")
PY
```

### 已知死鏈（本次未修）

首頁原本的 4 個入口在正式 build 全部 404，本次已從首頁移除，但**頂部選單仍然是死鏈**：

- `/projects/` — `content/zh-tw/projects/index.md` 是 `draft: true`，而且內容只有一行 `## Signal Proecessing`（拼錯了）
- `/resume/` — `content/{zh-tw,en}/resume/index.md` 也是 `draft: true`

待 `projects` 頁真的寫完、resume 拿掉 draft，再把選單打開。

### 驗證

```sh
rm -rf public && hugo --minify          # 零 warning
rg -c 'lab-hero' public/index.html      # 首頁有渲染
rg -c 'lab-term' public/{index,en/index}.html   # Console 有渲染
rg -o 'href=["\x27]?[^"\x27 >]*tags/[^"\x27 >]*' public/index.html   # 4 條 tag 都要存在
rg -c 'lab-console' public/index.html   # 只該命中 script 的檔名，不該有舊的 .lab-console 類

# Console 的 script 指紋檔必須真的被 publish（駁掉「印出來源路徑」那個坑）
rg -o '<script src=[^>]*lab-console[^>]*>' public/index.html
# data-cfg 必須是合法 JSON，否則 JS 直接 return 整塊不動、而且沒有錯誤訊息
python3 -c "import re,json;h=open('public/index.html',encoding='utf-8').read();json.loads(re.search(r'data-cfg>(.*?)</script>',h,re.S).group(1));print('cfg ok')"
```

⚠️ **`hugo --minify` 會把屬性的引號拿掉**，所以 `href="x"` 在正式 build 是
`href=x`。正則要寫成 `href=["\x27]?` 才兩種都收，否則會出現「明明有 4 條卻抓到 0 條」。

⚠️ **負向測試（首頁不該有 projects / resume 死鏈）不能用 `rg 'href=.*(projects|resume)'`** ——
那會抓到 PaperMod 頂部選單的兩個連結，而那正是 AGENTS.md 已記載的「已知死鏈」。
要測的是首頁**內文**，必須先切出 `<main>`：

```sh
python3 -c "
import re;h=open('public/index.html',encoding='utf-8').read()
main=re.search(r'<main[^>]*>(.*?)</main>',h,re.S).group(1)
print('main 內死鏈數:',len(re.findall(r'(projects|resume)/',main)))"   # 應為 0
```

**JS 有沒有真的跑起來**只能在瀏覽器驗（`public/` 是 client 渲染前的產物）。
伺服器端只有 5 行開機訊息，跑起來後應該逼近 `shared.console.max`（預設 14）行：

```sh
hugo server -D &
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$CH" --headless=new --disable-gpu --user-data-dir="$(mktemp -d)" \
  --virtual-time-budget=20000 --dump-dom "http://localhost:1313/" > /tmp/lab.html
rg -c 'class="lab-log ' /tmp/lab.html    # > 5 代表 JS 有在串流
```

⚠️ **`public/` 是 client 渲染前的產物**，且 `hugo server` 會改寫它。要檢查就先 `rm -rf public && hugo --minify`。
⚠️ baseURL 有 `/blog/` 前綴，本機靜態伺服器要架在父層（`/blog/` 指到 `public/`），否則 CSS 404、頁面全無樣式。
⚠️ headless Chrome 的 `--window-size=390` **不會**真的給你 390px 版面（layout 被夾在 500px），截圖會看起來像右側被切掉。用 iframe 夾出真實寬度來量：

```python
# 塞進同一個 http server 的子頁，用 iframe 量真正的 390px viewport
de.scrollWidth == de.clientWidth   # 兩者相等 = 沒有水平溢出
```
