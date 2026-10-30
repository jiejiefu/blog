> 本文件是 `AGENTS.md` 的延伸，只在改到這個功能時讀。回到 [AGENTS.md](../../AGENTS.md)。

## 觀眾留言區塊

每篇文章尾端都有一個「假觀眾留言」卡片，內容是 **Rick Sanchez 的英文台詞**，每次載入隨機換一則（故意不對應文章主題）。目的是氣氛，不是功能。

### 檔案與職責

| 檔案 | 職責 |
|---|---|
| `data/rick_quotes.yaml` | 台詞清單（`text` / `who` / `episode` / `handle`） |
| `layouts/partials/viewer_comment.html` | 卡片本體 + 內嵌 JSON + 載入 JS |
| `assets/js/viewer-comment.js` | ES5、無相依；載入時抽一則、按鈕再抽 |
| `assets/images/rick-avatar.png` | Rick 頭像原始檔（透明背景，1024×1186） |
| `assets/css/extended/custom.css` | `.viewer-comment*` 樣式 |
| `layouts/_default/single.html` | 在 share box 之後插入 partial |

### 隨機邏輯（漸進增強）

1. **伺服器端**：`index (shuffle hugo.Data.rick_quotes) 0` 先渲染一則 → 無 JS 也看得到完整內容。
2. **前端**：`viewer-comment.js` 解析同一份 JSON，載入時再抽一則；若抽到與目前相同就重抽（清單 > 1 時保證換）。
3. **`another one, Morty`**：再抽一次。
4. 初始自動抽換**不掛** `aria-live`；JS 換完後才用 `setTimeout(…, 0)` 掛上，避免頁面載入就被螢幕閱讀器朗讀。按鈕造成的變更才會播報。
5. JS 失敗／停用時，畫面停在伺服器端那一則，功能全不影響。

⚠️ **不要搬到 `extend_footer.html`**：那裡走 `partialCached`，快取鍵是 `.Layout`/`.Kind` 不是頁面，`data` 會變成「第一個被算到的頁面決定全站」。與 Mermaid / Plotly 踩的是同一個坑。

### 台詞規則

- **只收可考證的原作台詞**。不確定集數就把 `episode` 留空，不要硬猜。
- **不收 F-word、不收粉絲仿寫**。引用一律保留 `— Rick Sanchez · 集數` attribution。
- 卡片內有免責聲明：`Unofficial quote from Rick and Morty (© Adult Swim). This “viewer” is fictional.` 不要拿掉 —— 這是「不是真讀者留言」與版權標註的唯一說明。
- `Nobody exists on purpose…` 是 **Morty** 的台詞（S1E8），不要放進 Rick 的清單。
- `handle` 只是裝飾，不需要對應真實帳號。

### 頭像

- 原始檔放 `assets/images/rick-avatar.png`，**不要放 `static/`**：原檔 279 KB，放 static 會原樣發佈。
- partial 內用 Hugo 影像管線：`.Fit "96x96 webp q82"` → 產出約 3.4 KB 的 `public/images/rick-avatar_hu_<hash>.webp`。
- `Fit` 保留完整頭型（不裁頭髮／下巴），CSS 用 `object-fit: contain`；`alt=""` 因為頭像純裝飾。
- 圖片有真實 alpha 通道（`opaque=False`），深色模式不會出現白方塊。若日後換成白底圖，要先退地。

### 開關與樣式

- 單篇關閉：front matter 加 `disableViewerComment: true`（與 `disableShareBox` 同慣例）。
- 顏色全部沿用 `--border` / `--code-bg` / `--content` / `--secondary`，**沒有新增色票**；`--accent` 只用在按鈕的 `:focus-visible` 外框。

### 驗證

```sh
rm -rf public && hugo --minify          # 零 warning

# 每篇已發佈文章都要有，而且只能有一個區塊
# （不能只寫 class=viewer-comment，會一併命中 __kicker）
rg -c '<aside class=viewer-comment[ >]' public/posts/<slug>/index.html

# 頭像縮圖必須真的存在，且是 webp（不是原檔）
rg -o 'src=[^ >]*rick-avatar[^ >]*' public/posts/<slug>/index.html
magick identify public/images/rick-avatar_*.webp    # 應為 83x96

# 內嵌 JSON 必須可 parse
python3 -c "import re,json;h=open('public/posts/<slug>/index.html',encoding='utf-8').read();print(len(json.loads(re.search(r'data-viewer-comment-data[^>]*>(.*?)</script>',h,re.S).group(1))))"
```

⚠️ **`hugo --minify` 會拿掉屬性引號**，所以 `rg` 要寫 `class=viewer-comment`，不要寫 `class="viewer-comment"`。

瀏覽器端（驗證真的會換）：

```sh
hugo server -D -p 1413 &
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$CH" --headless=new --disable-gpu --user-data-dir="$(mktemp -d)" \
  --virtual-time-budget=10000 --dump-dom \
  "http://localhost:1413/blog/posts/<slug>/" > /tmp/vc.html
# 與 curl 取得的伺服器端 HTML 比對 data-vc-quote，兩者必須不同
```

按鈕需用 CDP（`--remote-debugging-port`）執行 `document.querySelector('[data-vc-reroll]').click()` 後再讀 `data-vc-quote`；`--dump-dom` 不會幫你點。
