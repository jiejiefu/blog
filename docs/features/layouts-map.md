> 這是 `AGENTS.md` 的延伸，只在找檔案時讀。回到 [AGENTS.md](../../AGENTS.md)。

## 檔案與職責

| File | What it does |
|---|---|
| `layouts/partials/extend_head.html` | Loads AOS CSS from CDN + KaTeX（僅 `math: true` 的頁面）+ Mermaid importmap/module（僅頁面用到 mermaid 時）+ `plotly-init.js`（僅頁面用到 plotly shortcode 時）+ PWA manifest |
| `layouts/partials/extend_footer.html` | Loads/initializes AOS JS + `assets/js/share-link.js` |
| `layouts/_default/_markup/render-codeblock-mermaid.html` | 把 ```` ```mermaid ```` fenced block 轉成 `<pre class="mermaid">` |
| `layouts/shortcodes/mermaid.html` | `{{< mermaid >}}...{{< /mermaid >}}` — 同一套轉義邏輯，輸出 `<div class="mermaid">` |
| `assets/js/mermaid-init.js` | Mermaid 初始化（ESM，經 importmap 從 CDN 取 mermaid） |
| `layouts/partials/share_link.html` | 分享連結區塊本體（每篇 single page 自動插入） |
| `layouts/shortcodes/animate.html` | `{{< animate type="fade-up" delay="200" >}}...{{< /animate >}}` — wraps content in AOS div |
| `layouts/shortcodes/video.html` | `{{< video src="demo.mp4" width="80%" >}}` — HTML5 video player |
| `layouts/shortcodes/audio.html` | `{{< audio src="audio/introduction.m4a" caption="..." >}}` — page bundle 音檔播放器（原生 `<audio>`，MIME 依副檔名，`.m4a` → `audio/mp4`；有同名 `.vtt` 或 `captions="..."` 時另掛同步字幕） |
| `assets/js/audio-captions.js` | 音檔同步字幕：fetch VTT、依 `timeupdate` / `seeking` 換句（ES5，無相依） |
| `layouts/shortcodes/youtube.html` | `{{< youtube id="..." >}}` — 覆寫 Hugo 內建版；先顯示縮圖，點擊才載入 iframe，斷網時保留縮圖（見 [youtube.md](youtube.md)） |
| `assets/js/youtube-lite.js` | YouTube 縮圖 facade：點擊／鍵盤載入 iframe、離線判斷、遠端縮圖 fallback |
| `assets/css/extended/youtube-lite.css` | `.yt-lite` 16:9 容器、播放鍵、離線提示 |
| `layouts/shortcodes/tldr.html` | `{{< tldr >}}...{{< /tldr >}}` — 文章開頭的 TL;DR callout（標籤用 `<p>`，不會進 TOC） |
| `layouts/shortcodes/code-fold.html` | `{{< code-fold label="..." open="true" >}}...{{< /code-fold >}}` — 可收合程式碼；預設收合，`open="true"` 預設展開 |
| `layouts/shortcodes/share-link.html` | `{{< share-link >}}` — 轉呼叫 `share_link.html` partial（正常情況不會用到，全站已自動插入） |
| `layouts/shortcodes/plotly.html` | `{{< plotly >}}…{{< /plotly >}}` — body 是 JSON（data/layout/config），見「Plotly 互動圖表」節 |
| `assets/js/plotly-init.js` | Plotly 初始化 + 依 `data-plotly-bundle` 動態載入 Basic/Full（ES5，無相依） |
| `layouts/index.html` | **首頁專屬模板** — Hero / Console / 技術領域卡 / 精選文章 / 最新文章 |
| `layouts/partials/home_posts_list.html` | 首頁底部的文章列表（從 PaperMod `_default/list.html` 抽出） |
| `layouts/partials/lab_icon.html` | 首頁技術卡的 inline SVG icon（4 個，24×24） |
| `layouts/partials/lab_console.html` | 首頁 Engineering Console 區塊本體（genact 風格終端機） |
| `assets/js/lab-console.js` | Console 的假日誌串流 / 指標 / 時鐘（ES5，無相依） |
| `assets/css/extended/lab-console.css` | Console 的終端機樣式（`.lab-term*`） |
| `data/home.yaml` | 首頁雙語文案（hero / 卡片 / console / 區塊標題）+ `shared.console`（兩種語言共用的假日誌） |
| `assets/css/extended/custom.css` | Fade-up keyframe animation + `.share-box` + `.mermaid` + `.tldr` + `.plotly-*` + `.post-audio*` + 首頁 `.lab-*` 樣式與 `--accent` |
| `assets/css/extended/chroma-00-reset.css` | Chroma **reset 層**（把 PaperMod 內建 Catppuccin 的 token 色歸零），見「程式碼高亮」節 |
| `assets/css/extended/chroma-atom-one-light.css` / `chroma-tokyonight-night.css` | 淺色 Atom One Light、深色 Tokyo Night token 配色，分別 scope 在 `:root:not([data-theme=dark])` / `:root[data-theme=dark]` |
| `assets/css/extended/zz-chroma.css` | 程式碼區塊底色（`--code-block-bg`）、圓角裁切、行內 code；`zz-` 前綴是排序需求 |
| `assets/js/code-copy.js` | 程式碼區塊右上角的複製按鈕（GitHub 風格圖示，ES5，無相依） |
| `assets/css/extended/code-copy.css` | 複製按鈕樣式（hover/focus 浮現、觸控常駐） |
| `config.yaml` → `markup.highlight.noClasses: false` | 改用 class-based 高亮（否則 Hugo 輸出 Monokai 行內樣式，自訂 CSS 完全無效） |
