> 本文件是 `AGENTS.md` 的延伸，只在改到全站底色、PaperMod 變數或 GitHub 色票時讀。回到 [AGENTS.md](../../AGENTS.md)。

## 全站底色與 PaperMod 變數

淺色對齊 GitHub Primer（`#FFFFFF` 畫布 + `#F6F8FA` muted surface）；深色維持站上的純黑系。

| 變數 | 淺色 | 深色 | 主要用途 |
|---|---|---|---|
| `--theme` | `#FFFFFF`（`custom.css`） | `#000`（`custom.css`） | 畫布、反白按鈕的文字色 |
| `--entry` | `#F6F8FA`（`custom.css`） | `#000`（`custom.css`） | `.post-entry`、`.lab-card` |
| `--code-bg` | `#F6F8FA`（`custom.css`） | `#000`（`custom.css`） | TOC／tags／paginav／share-box／tldr／viewer-comment |
| `--code-block-bg` | `#F6F8FA`（`zz-chroma.css`） | `#1a1b26`（`zz-chroma.css`） | 程式碼區塊外框與 `pre code` |
| `--border` | `#E6E6E6`（`custom.css`） | `#282828`（`custom.css`） | 卡片、分隔線、邊框 |

`--theme` 與 `--entry` 都在 `custom.css` 的淺色 `:root` 明寫，不再依賴 PaperMod 預設。

## ⚠️ 列表頁灰底的根因（已修正）

改版前首頁、`/posts/`、`/tags/`、`/archives/`、`/search/` 的畫布是淡灰 `#f5f5f5`，但單篇文章是白的。原因是三件事疊在一起：

1. `themes/PaperMod/layouts/_default/baseof.html` —

   ```go-html-template
   {{- if (or (ne .Kind `page`) (eq .Layout `archives`) (eq .Layout `search`)) }}
   <body class="list" id="top">
   {{- else }}
   <body id="top">
   {{- end }}
   ```

   只有列表型頁面的 `<body>` 帶 `class="list"`；單篇文章沒有。

2. `themes/PaperMod/assets/css/core/theme-vars.css` —

   ```css
   .list { background: var(--code-bg); }          /* 淺色 */
   [data-theme="dark"] .list { background: var(--theme); }
   ```

3. `assets/css/extended/custom.css` 把淺色 `--code-bg` 設成 `#f5f5f5`。

   → `<body class="list">` 的底色就是 `--code-bg`，所以列表頁變灰。單篇文章沒有 `.list`，走 `body { background: var(--theme) }`，所以是白的。

### 修正方式

`assets/css/extended/custom.css` 在變數區塊後覆寫：

```css
.list {
    background: var(--theme);
}
```

- `extended.css` 在 `core.css` 之後載入（`themes/PaperMod/layouts/partials/head.html` 的 `slice $core $extended`），同特異度下這條會蓋掉 `theme-vars.css`。
- 深色下等於原本的 `var(--theme)` = `#000`，行為不變。
- **不要**靠改 `--code-bg` 來修畫布：它同時餵 TOC／tags／paginav／share-box／tldr 等表面，改下去會連帶換掉那些 UI。

## 卡片用 muted 表面

`.post-entry`／`.lab-card` 走 `--entry`，淺色設為 `#F6F8FA` + `--border` 框，疊在純白畫布上形成層次（GitHub 的 `--bgColor-default` / `--bgColor-muted` 分層）。深色維持 `#000`。

若日後想回到「卡片也全白」，把淺色 `--entry` 改回 `rgb(255,255,255)` 即可；`.list` 畫布覆寫不受影響。

## 驗證

```sh
rm -rf public && hugo --minify
CSS=$(ls public/assets/css/stylesheet.*.css | head -1)

# .list 必須是 var(--theme)，且出現在 core 的 .list 之後
rg -o '\.list\{[^}]*\}' "$CSS"

# 淺色 muted 表面
rg -o '\-\-code-bg:[^;]*' "$CSS"
rg -o '\-\-code-block-bg:[^;]*' "$CSS"

python3 scripts/check_slug_style.py
```

瀏覽器端看：首頁、`/posts/`、`/tags/`、`/archives/`、`/search/` 的畫布應為純白；單篇文章不變；深色模式不變。

## 相關檔案

| 檔案 | 職責 |
|---|---|
| `assets/css/extended/custom.css` | `--theme` / `--entry` / `--code-bg` / `--border` 分模式值、`.list` 畫布覆寫 |
| `assets/css/extended/zz-chroma.css` | `--code-block-bg`、行內 code 底色與圓角 |
| `assets/css/extended/chroma-atom-one-light.css` | 淺色 token 色與 `.chroma` 背景 `#F6F8FA` |
| `themes/PaperMod/assets/css/core/theme-vars.css` | PaperMod 預設變數與 `.list` 原始規則（**不要直接改 theme**） |
