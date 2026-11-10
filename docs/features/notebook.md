> 本文件是 `AGENTS.md` 的延伸，只在改到 Notebook 區塊時讀。回到 [AGENTS.md](../../AGENTS.md)。

## Notebook 區塊

Notebook 是獨立的 top-level section，不是 `posts/` 的子分類。文章頁只放一個 shortcode：

```go-html-template
{{< notebook >}}
```

## 資料流

```text
scripts/<slug>/notebook.ipynb
  → scripts/<slug>/build.py
  → content/zh-tw/notebooks/<slug>/notebook.json
  → content/zh-tw/notebooks/<slug>/images/*.webp
  → content/zh-tw/notebooks/<slug>/videos/*.mp4
  → {{< notebook >}} → layouts/partials/notebook/*
```

- `scripts/notebook_build.py` 是共用 builder：清空 outputs、用 `nbclient` 執行、把 PNG/JPEG 轉 WebP、清洗 HTML 表格、寫 JSON。
- `scripts/<slug>/build.py` 只負責填來源與 bundle 路徑。
- 瀏覽器不執行 Python，也不載入互動套件。

## 建置

```sh
python3 scripts/intro-to-jupyter-notebook/build.py
```

需在裝有 `nbformat`、`nbclient` 的環境執行；本機 venv 與解譯器路徑記在 `AGENTS.local.md`。builder 會覆寫 `notebook.json`、`images/cell-*-out-*.webp`、`executed.ipynb` 與 `notebook.md`。後兩者是本地審閱用，已列在 `.gitignore`。

## JSON 結構

```json
{
  "schema": 1,
  "meta": {
    "title": "...",
    "filename": "notebook.ipynb",
    "kernel": "Python 3 (ipykernel)",
    "executed_at": "...",
    "duration_ms": 1234
  },
  "cells": [
    {"type": "markdown", "source": "...", "tags": []},
    {"type": "code", "source": "...", "execution_count": 1, "tags": [], "outputs": []}
  ]
}
```

Output 型別：`stream`、`result`、`image`、`html`、`video`、`error`。`result`、`image`、`html` 帶 `execution_count`；`image` 一定有 `src`、`alt`、`width`、`height`，可選 `caption`。`video` 帶 `src`、`poster`、`alt`、`width`、`height`，可選 `caption`、`controls`、`autoplay`、`muted`、`loop`、`playsinline`；影片不帶 `execution_count`，所以不會出現輸出選單。

## Cell metadata

在 `.ipynb` 的 cell metadata 設定：

- `tags: ["hide-input"]`：只顯示輸出。
- `tags: ["hide-output"]`：只顯示程式碼。
- `tags: ["remove-cell"]`：整顆 cell 不進 JSON。
- `alt`：圖片替代文字。
- `caption`：圖片說明。
- `video`：把同一顆 cell 產生的 mp4 放進 notebook 流程。

```json
{
  "tags": ["hide-input"],
  "alt": "三張子圖顯示 x-y、x-z、y-z 的散佈圖",
  "caption": "以 NumPy 產生的 100 個三維隨機點。"
}
```

影片使用 cell metadata。`src` 與 `poster` 是相對 `notebook.ipynb` 的檔名；builder 會把 mp4 複製到 bundle 的 `videos/`，poster 轉成 WebP 放進 `images/`。

```json
{
  "video": {
    "src": "square_wave_increasing_terms.mp4",
    "poster": "square_wave_increasing_terms.png",
    "alt": "方波逼近動畫",
    "caption": "n=1、3、5、7 的方波逼近。",
    "width": 1200,
    "height": 960
  }
}
```

影片預設 `controls`、`muted`、`loop`、`playsinline` 開啟，`autoplay` 關閉以節省流量。要自動播放，在 cell metadata 設 `"autoplay": true`。

## 硬規則

- **Notebook markdown cell 不支援 Hugo shortcode。** 需要 callout、音檔時，改寫進頁面 markdown 或另做 partial。影片用 cell metadata 的 `video`，不要用 shortcode。
- **HTML output 只接受清洗後的 `<table>`。** builder 會移除 `<script>`、`<style>`、事件屬性、`style` 與 `javascript:`；不是表格就 fallback 成 `text/plain`。
- **圖片與影片只放 zh-tw bundle。** en 沒有 `images/`，靠 Hugo 跨 bundle 解析。
- **Notebook 頁面不進首頁。** 首頁查詢只取 `mainSections`；不要為了 notebook 改動首頁查詢。
- **`notebook.json` 是 page resource。** 不要搬到 `static/`，否則 shortcode 的 `Resources.GetMatch` 找不到。
- **CSS 檔名要排序在 chroma 之後。** 使用 `assets/css/extended/zz-notebook.css`，才能覆寫 `--code-block-bg`。
- **v1 不支援互動。** Plotly、widgets、即時輸入都不在範圍內。

## 版面

- 桌機與手機都以 `90vw` 顯示，透過 `margin-left: calc(50% - 45vw)` 置中；列印回到 `100%`。
- 每個 code cell 的 input 與所有 outputs 共用一個外框；outputs 不再有獨立框線或底色，背景沿用 `.jp-notebook` 的 `--jp-bg`。
- code block 保留 `--jp-code-bg` 淡色底；code 與 output 共用 `--jp-mono-size: 14px`。
- PaperMod 的 `.post-content code` 是 `0.78em`，會讓 code 比 output 小；`.jp-code .highlight pre code` 必須覆寫成 `font-size: inherit`，並清掉 `margin`／`padding`／`background`。
- code block padding 為 `4px`（桌機與 `max-width: 720px` 都是）；output body 仍是左右 `12px`（手機 `8px`），`Out[n]:` 與 output 之間保留 `8px`（手機 `6px`）間距。
- markdown 內文字級 `1.02rem`；prompt `12px`；Jupyter chrome 與狀態列約 `12px`。
- Jupyter chrome 使用英文標籤；唯讀提示依語言切換。
- 狀態列顯示 cell 數、執行時間、duration 與 Idle。
- code cell 沿用 `assets/js/code-copy.js` 的程式碼複製按鈕；outputs 由 `assets/js/notebook-output.js` 處理。
- 深色模式由 `:root[data-theme="dark"] .jp-notebook` 覆寫 `--jp-*`。

## Output 操作

- 每個有輸出的 code cell 都有一個三點選單，複製整個 cell 的輸出。
- 選單放在第一個 `Out[n]:` 下方，`Out[n]:` 與按鈕在左側 prompt 欄垂直排列。
- 若 cell 沒有 `Out[n]:`（例如只有 `print()` 的 stream，或 error），選單放在 output 左上角 prompt 欄頂端。
- 按鈕維持 hover／focus 才出現，但 prompt 欄會保留約 `26px` 高度，避免多 output 時與下一個 output 的 prompt 重疊。
- 選單只有一個選項：`複製儲存格輸出`（en 為 `Copy Cell Output`）。
- 複製規則：
  - `stream`／`result`／`error`：複製純文字。
  - `html`：把 rendered table 轉成 TSV；不從 `notebook.json` 取 `text/plain`。
  - 沒有文字、只有圖片：複製第一張圖片；失敗時退回下載。
  - 文字與圖片混合：複製文字，圖片用圖片上的按鈕處理。
- 圖片 hover／focus 時右上角顯示「複製圖片」與「儲存圖片」；觸控裝置常駐顯示。
- 圖片複製會把 WebP 轉成 PNG 再寫入剪貼簿；瀏覽器不支援或逾時時退回下載原始 WebP。
- 選單支援點擊外部關閉、`Escape` 關閉、鍵盤 focus；靠近視窗底部時往上開。

## 驗證

```sh
rm -rf public && hugo --minify --buildDrafts
rg -o 'jp-output-prompt|jp-output-actions|data-jp-copy-output|複製儲存格輸出' public/notebooks/intro-to-jupyter-notebook/index.html
rg -o 'jp-output-video|jp-video' public/notebooks/<slug>/index.html
rm -rf public && hugo --minify
python3 scripts/check_slug_style.py
python3 scripts/ai_slop_check.py scripts/intro-to-jupyter-notebook/notebook.md
```

`check_generated_images.py` 目前只掃 posts，notebook 的 WebP 不在它的守備範圍。
