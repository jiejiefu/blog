# AGENTS.md — Jay Fu Blog

⚠️ **專案路徑**：`/Users/jiejiefu/Documents/Visual_Studio_Code/blog`
所有指令與相對路徑都以這裡為基準。不要用 `~/Downloads/blog` 或其它 checkout；`pwd` 不對就先切回。

## Quick facts

- Hugo v0.157+（extended），PaperMod v8.0（git submodule）
- 雙語：zh-tw（預設，weight 1）、en（weight 2）
- 設定：`config.yaml`（`_hugo.toml` 是舊 scaffold，忽略）
- 沒有 Node.js／npm／Go modules，純 Hugo
- push `main` → GitHub Actions 部署到 `https://jiejiefu.github.io/blog/`

## Commands

```sh
hugo server                       # dev server（zh-tw 預設）
hugo server --minify              # 模擬正式
hugo --minify                     # 產出 ./public/
python3 scripts/check_slug_style.py
python3 scripts/check_generated_images.py --check
python3 scripts/ai_slop_check.py content/zh-tw/posts/<slug>/index.md
```

⚠️ `hugo server` 會改寫 `public/`。要檢查 `public/` 前先 `rm -rf public && hugo --minify`。
⚠️ 使用者常自己開 1313 的 dev server，不要當成殘留 process 殺掉。

## Content structure

```
content/
  zh-tw/                    # 預設語言
    posts/<slug>/           # leaf page bundle：index.md + images/
    projects/<slug>/
    resume/  search.md
  en/                       # 鏡像結構；刻意沒有 images/
```

### 硬規則

- **slug 一律 hyphen**，不用底線。URL 由目錄名直接產生，沒有 front matter 覆寫。新文章用 `hugo new posts/my-new-post/index.md`；圖片檔名不受限。
- **草稿不進 `content/`**。bundle 裡任何 `.md` 都會被渲染；曾因草稿內含 `{{< mermaid >}}` 讓 build 失敗。草稿放 repo 根的 `drafts/`。
- **新文章 `draft: true`**，front matter 用 YAML `---`。常用欄位：`draft`、`date`、`title`、`tags`、`description`、`math`、`cover`。
- **`cover.relative: true` 只給 zh-tw**。en 用絕對網址（`https://jiejiefu.github.io/blog/...`），否則 og:image 404。驗證：`rg -o 'og:image" content="[^"]+' public/<lang>/posts/<slug>/index.html`。
- **en 刻意沒有 `images/`**，靠 Hugo 跨 bundle 解析到 zh-tw。不要在 en 複製圖片。
- TECH_TRENDS 系列（2021–2026）全部 `draft: true`。

## 投影片系列

`fab-predictive-maintenance-ppt169` 與 `edge-ai-platform-ppt169` 的圖來自自製 SVG 簡報。

- 投影片與文章是兩份獨立檔案，改一邊要同步另一邊。
- 對外 slug 不得含公司名稱或業態字樣。
- 圖片只放 `content/zh-tw/...`，en 自動解析。
- 本地路徑、專案代號與禁用字串見 `AGENTS.local.md`（不進版控）。

細節：`docs/slides-and-content.md`。

## Layouts & assets

| 檔案 | 職責 |
|---|---|
| `layouts/index.html` | 首頁 |
| `layouts/partials/home_posts_list.html` | 首頁文章列表 |
| `layouts/partials/lab_console.html` / `lab_icon.html` / `glyph_art.html` | 首頁區塊 |
| `layouts/partials/extend_head.html` | 逐頁載入 KaTeX／Mermaid／Plotly／音檔字幕 |
| `layouts/partials/extend_footer.html` | AOS、share-link |
| `layouts/partials/share_link.html` / `viewer_comment.html` | 文章底部區塊 |
| `layouts/shortcodes/` | `tldr`、`animate`、`video`、`audio`、`plotly`、`mermaid`、`code-fold` |
| `layouts/_default/single.html` | **覆寫 PaperMod**，多了分享框與觀眾留言 |
| `assets/js/` | console、文字畫、分享、留言、mermaid（唯一 ESM）、plotly、字幕 |
| `assets/css/extended/` | `custom.css`、`lab-console.css`、`lab-glyph.css`、`chroma-*.css`、`zz-chroma.css` |
| `data/home.yaml` | 首頁雙語文案 |
| `scripts/` | 共用工具；每篇文章一個資料夾（完整對照：`docs/features/layouts-map.md`） |

## i18n & Search

- `i18n/zh-tw.yaml` 覆寫「閱讀全文」「履歷」；`i18n/en.yaml` 刻意留空，用 PaperMod 預設。
- 兩個 `search.md` 都用 `layout: "search"`；`config.yaml` 的 `outputs.home: [HTML, RSS, JSON]` 是必要條件。

## `scripts/`

- 文章專屬封面 SVG、產圖腳本放 `scripts/<slug>/`；封面 JPG 正本在 `content/zh-tw/posts/<slug>/images/cover.jpg`，不要複製到 `scripts/`。
- 共用工具留在 `scripts/` 根目錄，腳本路徑以 repo 根為基準（`Path(__file__).resolve().parents[2]`）。
- 產圖一律用 `scripts/image_utils.py` 的 `save_figure_webp()`；PNG 只留暫存，不寫進 `content/`。
- `check_generated_images.py --check` 發現 PNG 會擋 CI；`--fix` 只處理未被 markdown 引用的 PNG。

## 五個高風險陷阱

- **逐頁條件只能放 `extend_head.html`**。footer 是 `partialCached`，快取鍵是 `.Layout`/`.Kind`，會變成第一頁決定全站。
- **mermaid 必須 `deterministicIds: true`**，否則同頁第 2 張之後的圖會疊在一起。
- **`data/home.yaml` 的語言鍵用 `index hugo.Data "home" site.Language.Lang`**，不能寫 `home.zh-tw`。
- **首頁技術卡查不到 tag 頁就整張不渲染**，加新 tag 前先確認有文章。
- **`assets/css/extended/` 的檔名排序會改變行為**（`chroma-00-` 要在前、`zz-` 要在後）。

## CI & commit

- CI：slug 檢查 → 生成圖檢查 → `hugo --minify` → 部署 gh-pages。
- commit message 不得出現公司名稱或業態字樣。
- 已 push 的歷史改寫需 force-push，**未經同意不得執行**。

## Docs

| 要改什麼 | 先讀 |
|---|---|
| 開新文章、規劃圖表 | [`docs/article-brief.md`](docs/article-brief.md) |
| 改寫、去 AI 感 | [`docs/ai-slop-style-guide.md`](docs/ai-slop-style-guide.md) |
| 首頁、Console、文字畫 | [`docs/features/home.md`](docs/features/home.md) |
| 分享框 | [`docs/features/share.md`](docs/features/share.md) |
| 觀眾留言 | [`docs/features/viewer-comment.md`](docs/features/viewer-comment.md) |
| 口述音檔、字幕 | [`docs/features/audio.md`](docs/features/audio.md) |
| KaTeX | [`docs/features/katex.md`](docs/features/katex.md) |
| Mermaid | [`docs/features/mermaid.md`](docs/features/mermaid.md) |
| Plotly | [`docs/features/plotly.md`](docs/features/plotly.md) |
| 程式碼高亮 | [`docs/features/code-highlight.md`](docs/features/code-highlight.md) |
| 版面與 shortcode 對照 | [`docs/features/layouts-map.md`](docs/features/layouts-map.md) |
| SVG 轉檔指令 | [`docs/image-conversion.md`](docs/image-conversion.md) |
| favicon、PWA | [`docs/features/icons.md`](docs/features/icons.md) |
| 投影片、去識別化、用詞 | [`docs/slides-and-content.md`](docs/slides-and-content.md) |
| git 歷史重寫 | [`docs/history-rewrite.md`](docs/history-rewrite.md) |

## 每次改完

```sh
rm -rf public && hugo --minify
python3 scripts/check_slug_style.py
```

有改文章再加 `ai_slop_check`；有改產圖腳本再加 `check_generated_images.py --check`。
