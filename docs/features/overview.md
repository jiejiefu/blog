> 本文件是 `AGENTS.md` 的延伸，只在改到內容總覽頁時讀。回到 [AGENTS.md](../../AGENTS.md)。

## 內容總覽（`/posts/overview/`）

把站上的 Posts、Notebooks、Projects 攤在同一頁：四個統計數字、每年產出、標籤分佈，以及可搜尋／篩選／排序的總表。

這一頁**不是即時 dashboard**：沒有 `setInterval`、沒有隨機波動、沒有假的連線狀態。所有數字都在 Hugo build 時算完，瀏覽器只負責 client-side 篩選與排序。

- 中文：`/posts/overview/`
- 英文：`/en/posts/overview/`
- 入口：`content/{zh-tw,en}/posts/_index.md` 的 `{{< posts-overview-link >}}`
- 刻意不加頂部選單；它是一個索引頁，不是主要導覽目的地。

### 檔案與職責

| 檔案 | 職責 |
|---|---|
| `content/zh-tw/posts/overview/index.md` | 中文頁面；只有 front matter，內容由 layout 產生 |
| `content/en/posts/overview/index.md` | 英文頁面 |
| `layouts/_default/overview.html` | 統計、圖表、篩選器、總表、JS 載入 |
| `data/overview.yaml` | 雙語文案（hero／link／stats／filters／types／table／charts／count／draft／empty／no_tags／noscript） |
| `assets/js/overview.js` | 篩選、排序、URL query string 同步；無相依 |
| `assets/css/extended/overview.css` | `.ov-*`、Posts 頁入口、手機版卡片式表格 |
| `layouts/shortcodes/posts-overview-link.html` | Posts 列表頁的入口卡片 |
| `content/zh-tw/posts/_index.md` / `content/en/posts/_index.md` | 插入入口 shortcode |

### Front matter 與輸出

```yaml
---
title: "內容總覽"
description: "..."
date: 2026-11-01
draft: false
layout: "overview"
searchHidden: true
build:
  render: always
  list: never
---
```

⚠️ Hugo v0.168 已移除 `_build`，必須寫 `build:`。用 `_build:` 會直接 build 失敗。

`build.list: never` 讓這一頁不進 Posts 列表、首頁統計、RSS、sitemap、search index 等列表輸出，但 `render: always` 仍會產生頁面。它是「有頁面、不當列表項目」的組合。`searchHidden: true` 是第二道保險。

預設語言（zh-tw）的輸出在 repo 根：

```text
public/posts/overview/index.html
public/en/posts/overview/index.html
```

不是 `public/zh-tw/posts/overview/`。

### 資料來源

模板只抓三個 section：

```go-html-template
{{ $sections := slice "posts" "notebooks" "projects" }}
{{ $all := where site.RegularPages "Section" "in" $sections }}
{{ $all = where $all "RelPermalink" "ne" .RelPermalink }}
{{ $published := where $all "Draft" false }}
{{ $rows := sort $all "Date" "desc" }}
```

- `$published`：統計與圖表只算 `draft: false`。正式 build 與 `hugo server -D` 的統計數字一致。
- `$rows`：總表資料。正式 build 只有已發布內容；`hugo server -D`（或 `hugo --buildDrafts`）會多出草稿，並在標題旁顯示「草稿」badge。
- `where ... RelPermalink ne .RelPermalink`：再排除自己一次，避免 Hugo 版本差異或 front matter 設定改動時遞迴。
- 目前沒有把 `resume` 收進來；要加新類型時，同步改 `$sections`、`data/overview.yaml` 的 `types`，以及需要的 CSS。

統計數字：

| 指標 | 算法 |
|---|---|
| 文章 / Notebooks / 專案 | `$published` 依 `Section` 過濾後計數 |
| 標籤 | 收集 `$published` 的 `.Params.tags`，`uniq` 去重 |

標籤數刻意不讀 `len site.Taxonomies.tags`：taxonomy 會把草稿算進去，跨語言合併行為也不適合直接依賴。

### 每年產出

年份只取 `$published` 的 `.Date.Format "2006"`。圖表會從最新年份往回補到**至少 5 年**：

```text
2022  2023  2024  2025  2026
  0     0     0     0     9
```

- 資料本身跨度超過 5 年時，保留全部年份，不裁掉舊資料。
- 沒有內容的年份仍保留，讓時間軸連續；`0` 顯示在年份上方，長條本身不畫。
- `$yearMax` 是目前最大值，長條高度以它為 100%。

### 標籤分佈

- 用 `.GetTerms "tags"` 取得每篇已發布內容的 tag 與 taxonomy URL。
- 依出現次數取前 12 名；計數相同時用名稱排序，輸出才穩定。
- 標籤名稱是 `.LinkTitle`，所以 front matter 寫 `System Design`，圖上就是 `System Design`，連結仍是 Hugo `urlize` 後的 `/tags/system-design/`。

Tag 命名規則見 [`docs/article-brief.md`](../article-brief.md) 的「Tags 規則」：英文 Title Case、縮寫全大寫、不寫中文或 hyphen 版本。

### 總表與篩選

表格由 Hugo 直接輸出完整 `<tbody>`，沒有 JS 也能看到所有內容。每列帶這些 data attribute：

| Attribute | 用途 |
|---|---|
| `data-type` | `posts` / `notebooks` / `projects` |
| `data-year` | 四位年份 |
| `data-date` | `YYYY-MM-DD`，排序用 |
| `data-title` | 標題排序用 |
| `data-tags` | 以 `|` 分隔的完整 tag 名稱，tag 篩選用 |
| `data-search` | 標題 + 摘要 + tags，轉小寫後做子字串搜尋 |

`assets/js/overview.js` 的行為：

- 支援 `?q=`、`?type=`、`?year=`、`?tag=`、`?sort=title|type|date`、`?order=asc|desc`。
- 無效的 `type` / `year` / `tag` / `sort` 會退回 `all` 或 `date`，不會留下空畫面。
- 預設依日期新到舊；第一次點標題或類型是升冪，再點同欄切換升降。
- 搜尋是 `data-search` 的子字串比對，tag 篩選是 `data-tags` 的精確成員比對。
- 狀態用 `history.replaceState` 寫回 URL，不會在瀏覽歷史塞入每個按鍵。
- 「重設」清空所有條件並回到日期新到舊。

⚠️ 篩選器的年份與 tag 選項是從 `$rows` 產生，不是只從 `$published`。所以在 `hugo server -D`（或 `hugo --buildDrafts`）下，可能出現「只有草稿使用」的年份或 tag；正式 build 不會。

⚠️ 手機版 `<thead>` 隱藏、每列改成卡片，靠 CSS `td::before { content: attr(data-label) }` 顯示欄位名。`.ov-page [hidden] { display: none !important; }` 是必要的，否則 `tr[hidden]` 會被卡片樣式的 `display: block` 蓋掉。

### 樣式與版面

- `.main:has(.ov-page)` 把版心放寬到 1120px；`:has()` 不支援時只會維持 PaperMod 預設寬度，不影響閱讀。
- `body:has(.ov-page)` 套列表頁灰底；深色模式另外覆寫。
- 圖表與表格都用 CSS 變數（`--entry`、`--border`、`--secondary`），不新增主題色。
- 沒有任何 AOS 或進場動畫；`prefers-reduced-motion` 只關掉長條的 `transition`。
- 年度圖的 `0` 年份用 `.ov-yearbar--zero` 把數字排到年份上方，避免 `0` 飄在圖表頂端。

### JS 載入位置

```go-html-template
{{ $js := resources.Get "js/overview.js" | minify | fingerprint }}
<script src="{{ $js.RelPermalink }}" integrity="{{ $js.Data.Integrity }}" defer></script>
```

⚠️ 必須留在 `layouts/_default/overview.html`，不要搬到 `extend_footer.html`。footer 是 `partialCached`，快取鍵是 `.Layout` / `.Kind`，會變成第一頁決定全站，其他頁面可能拿到錯的 script 或完全沒有。

⚠️ script 走 assets pipeline（`resources.Get` + `minify` + `fingerprint`），不要放 `static/js/`。沒有指紋就沒有 cache busting。

### 驗證

```sh
rm -rf public && hugo --minify
python3 scripts/check_slug_style.py
python3 scripts/ai_slop_check.py content/zh-tw/posts/overview/index.md

# 這一頁有渲染，且年度圖至少 5 根
rg -c 'ov-page' public/posts/overview/index.html
rg -o 'ov-yearbar__year[^>]*>[0-9]{4}<' public/posts/overview/index.html

# 不該進 RSS、sitemap、search index
rg -c 'posts/overview' public/index.xml public/sitemap.xml public/index.json

# Posts 頁只該有入口 shortcode 的連結，不該多出文章卡
rg -o 'posts/overview' public/posts/index.html | wc -l   # 應為 1
```

最後兩條的預期分別是「找不到」與「1」。若 RSS／sitemap／search 出現，先檢查 `build.list` 是否還是 `never`；若 Posts 頁多於 1，檢查是不是 front matter 的 `list` 被改掉。

互動只能在瀏覽器驗。`public/` 是 client 渲染前的產物；本機靜態伺服器要架在父層，讓 `/blog/` 指到 `public/`：

```sh
cd /tmp && mkdir -p ovtest && ln -sfn /path/to/blog/public /tmp/ovtest/blog
cd /tmp/ovtest && python3 -m http.server 8765
```

```text
http://localhost:8765/blog/posts/overview/?type=projects
http://localhost:8765/blog/posts/overview/?tag=AI
http://localhost:8765/blog/posts/overview/?q=deepseek
http://localhost:8765/blog/posts/overview/?sort=title&order=asc
```

### 踩過的坑

1. **`_build` 不是 `build`。** Hugo v0.168 對 `_build:` 直接報錯；本頁的 front matter 與文件都要用 `build:`。
2. **JS 不能放 footer。** `extend_footer.html` 是 `partialCached`，頁面層級的 script 會被別頁的快取蓋掉。
3. **`build.list: never` 會讓頁面從搜尋與 sitemap 消失。** 這是刻意的；若哪天要讓總覽頁被搜尋，請先確認它不會同時變成 Posts 列表的一張卡。
4. **`data/overview.yaml` 的語言鍵要用 `index`。** `zh-tw` 含連字號，不能寫 `hugo.Data.overview.zh-tw`；模板用 `index hugo.Data "overview" site.Language.Lang`。
5. **年度圖只畫有資料的年份會變成一根巨大長條。** 現在至少補到 5 年，且 0 的年份不畫長條，只留時間軸。
