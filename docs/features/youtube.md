# YouTube 嵌入（離線縮圖）

`layouts/shortcodes/youtube.html` 覆寫 Hugo 內建的 `youtube` shortcode。畫面先顯示縮圖，點擊後才載入 `youtube-nocookie` iframe；斷網時只顯示縮圖與提示，不會留下一塊破圖或空白 iframe。

## 用法

```go-html-template
{{< youtube id="EKOU3JWDNLI" >}}
{{< youtube id="EKOU3JWDNLI" title="影片標題" >}}
{{< youtube id="EKOU3JWDNLI" thumb="images/custom.jpg" hl="en" >}}
```

| 參數 | 預設 | 說明 |
|---|---|---|
| `id` | 必填 | YouTube video ID（也可用第一個位置參數） |
| `title` | i18n `youtube_title` | `aria-label` 與縮圖 `alt`、iframe `title` |
| `thumb` | bundle 的 `images/maxresdefault.*` → 遠端 `i.ytimg.com` | 可指定自己的縮圖 |
| `hl` | 無 | 介面語言，附加到 embed 網址 |
| `class` | 無 | 追加到 `.yt-lite` 的 class |
| `loading` | `lazy` | 縮圖的 `loading` 屬性 |

## 行為

- 預設顯示 page bundle 內的 `images/maxresdefault.jpg`（或 `.png`／`.webp`）；找不到才用 `https://i.ytimg.com/vi/<id>/maxresdefault.jpg`
- 點擊或鍵盤 Enter／Space 才把 `.yt-lite` 換成 iframe，網址帶 `autoplay=1`、`rel=0`、`playsinline=1`
- 斷網（`navigator.onLine === false`）時不換 iframe，顯示「無法載入 YouTube，僅顯示影片縮圖。」
- 線上但 iframe 8 秒內沒有 `load`（YouTube 被擋／連不上）時，移除 iframe 並回到同一張縮圖與提示
- 遠端 maxres 縮圖 404 時，JS 自動退回 `hqdefault.jpg`
- 沒有 JS 時由 `<noscript>` 隱藏 facade 並直接載入 iframe（等同舊行為）
- `prefers-reduced-motion` 會關掉縮圖縮放動畫

## 檔案

| 檔案 | 職責 |
|---|---|
| `layouts/shortcodes/youtube.html` | facade markup、縮圖解析、iframe 網址 |
| `assets/js/youtube-lite.js` | 點擊／鍵盤載入 iframe、離線判斷、縮圖 fallback |
| `assets/css/extended/youtube-lite.css` | 16:9 容器、播放鍵、離線提示、focus 樣式 |
| `layouts/partials/extend_head.html` | 只在 `.HasShortcode "youtube"` 時載入 JS |
| `i18n/zh-tw.yaml` | `youtube_play` / `youtube_title` / `youtube_offline` |

## 英文版例外

英文版（`content/en/`）刻意不使用這個 shortcode，維持手寫 `<iframe>`，上方保留註解掉的 `{{< youtube ... >}}` 方便對照。英文版沒有 `images/`，改走遠端縮圖也失去離線意義，因此不動。

## 陷阱

- Hugo **仍會執行 HTML 註解裡的 shortcode**。`<!-- {{< youtube id="..." >}} -->` 會產生 markup，只是被包在註解裡；`hugo --minify` 通常會把整個註解拿掉，所以外觀沒事，但 `.HasShortcode "youtube"` 仍為 true。
- 要離線看到縮圖，`images/maxresdefault.jpg` 必須真的在該文章的 page bundle 裡；只靠遠端 `i.ytimg.com` 在斷網時一定載不到。
- 若之後要自動從 YouTube 抓縮圖，記得仍然存一份到 bundle，否則就回到遠端依賴。
- 新增語言鍵請加在 `i18n/zh-tw.yaml`；`i18n/en.yaml` 依慣例留空，英文用 `default` 值。

## 驗證

```sh
rm -rf public && hugo --minify

# 縮圖走本機 bundle，不是 i.ytimg.com
rg -o 'yt-lite__thumb" src="[^"]+' public/posts/tech-trends-2026/index.html

# facade 與 JS 有載入
rg -o 'data-yt-src="[^"]+' public/posts/tech-trends-2026/index.html
rg -o 'youtube-lite\.min\.[a-f0-9]+\.js' public/posts/tech-trends-2026/index.html

# 英文版仍是原始 iframe（註解已被 minify 移除）
rg -o '<iframe[^>]*youtube[^>]*>' public/en/posts/tech-trends-2026/index.html
```

Draft 文章要驗證時加 `--buildDrafts`（輸出到 `/tmp` 以免蓋掉 `public/`），或直接 `hugo server --buildDrafts`。
