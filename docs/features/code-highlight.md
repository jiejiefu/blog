> 本文件是 `AGENTS.md` 的延伸，只在改到這個功能時讀。回到 [AGENTS.md](../../AGENTS.md)。

## 程式碼高亮（Chroma / Atom One Light + Tokyo Night）

改版前的設定是 Hugo 預設的 `noClasses: true` → 每個 token 都帶**行內 style**、主題是 **Monokai**（`#272822`）。問題出在外框：`.post-content .highlight:not(table)` 用 `--code-block-bg`（淺色 `#f5f5f5`、深色 `#000`）塗底色 + `border-radius: 8px`，而內層 `<pre>` 是**直角**的 `#272822` → 視覺上就是「程式碼區塊四個角黑黑的、外圍一圈灰底」。同一組不一致也讓部分 token（例如 Monokai 的註解 `#75715e`）在灰底上讀不清楚。

### 檔案與職責

| 檔案 | 職責 |
|---|---|
| `config.yaml` → `markup.highlight.noClasses: false` | 關掉行內樣式，改用 class（`.chroma .k` 等）。**沒有這行，下面三層全部無效** |
| `assets/css/extended/chroma-00-reset.css` | reset 層（見下方「為什麼需要 reset」） |
| `assets/css/extended/chroma-atom-one-light.css` | 淺色 Atom One Light token 色，`:root:not([data-theme="dark"])` |
| `assets/css/extended/chroma-tokyonight-night.css` | 深色 token 色，`:root[data-theme="dark"]` |
| `assets/css/extended/zz-chroma.css` | `--code-block-bg`（分模式）、圓角裁切、`pre code` 文字色、行內 code |

產生／更新 token 色的方式（換主題時照做，再手動加 scope 前綴）：

```sh
# 深色：Chroma 內建 tokyonight-night
hugo gen chromastyles --style=tokyonight-night  # → 加 `:root[data-theme="dark"] ` 前綴

# 淺色：Chroma 沒有 atom-one-light，依官方色盤手動維護
# assets/css/extended/chroma-atom-one-light.css（scope: `:root:not([data-theme="dark"])`）
```

### ⚠️ 為什麼需要 reset 層：PaperMod 內建的是 Catppuccin

`themes/PaperMod/assets/css/includes/chroma-styles.css` 是 **Catppuccin Macchiato**，而且**不會被移除**——它跟我們的 Atom One Light／Tokyo Night 疊在同一份 `stylesheet.css`（core.css 先、extended.css 後）。

**（0,0,2,0）** 的層級只能靠順序贏，但**只要我們主題沒定義那個 token class，就會直接漏出 Catppuccin 的顏色**。實際踩到的：

- `.nv`（NameVariable）→ Catppuccin `#f4dbd6`（淡粉），在淺色 `#FAFAFA` 底上等於隱形
- 苦主是 bash 的環境變數賦值：`export REA_ANALYSIS_PROVIDER=ghidra`（Chroma 把 `REA_ANALYSIS_PROVIDER` 標成 `.nv`）

`chroma-00-reset.css` 用一個**低特異度** `(0,0,2,0)` 的規則把 token 樣式歸零：

```css
:root .chroma *, :root .bg { color: inherit; background-color: transparent; font-style: inherit; font-weight: inherit; text-decoration: inherit; }
```

- 對 Catppuccin（同為 2,0）→ 靠原始碼順序勝出
- 對 `chroma-atom-one-light.css` / `chroma-tokyonight-night.css`（帶 scope 後是 4,0）→ 讓它們把要的顏色蓋回來
- 結果：我們主題沒定義的 token 一律 `inherit` 到 `.chroma` 的前景色，**換主題也不會再漏色**

⚠️ 用 `hugo gen chromastyles` 產出的檔案**天生缺一堆 class**（Chroma 對「不特別上色」的 token 不輸出規則），所以**不能只靠順序、一定要有 reset 層**。

### ⚠️ 檔名排序就是行為的一部分

`themes/PaperMod/layouts/partials/head.html` 是這樣組的：

```
{{- $extended := (resources.Match "css/extended/*.css") | resources.Concat "assets/css/extended.css" | resources.Minify }}
```

`resources.Match` **依檔名排序**，而 `extended.css` 被接在 `core.css`（含主題的 chroma-styles.css）後面。所以：

- `chroma-00-reset.css` 的 `00-` 必須**早於** `chroma-*`，否則 reset 會蓋掉主題色
- `zz-chroma.css` 的 `zz-` 必須**晚於** `custom.css`，因為 `custom.css` 把 `--code-block-bg` 設成舊值（`rgb(245,245,245)` / `rgb(0,0,0)`），要靠後載入才能覆蓋
- **改名會靜默改變結果**，不會報錯。要動這些檔名之前先想清楚排序

### ⚠️ 刻意不動 `--code-bg`

`--code-bg` 不只餵程式碼，還餵 `.toc` / `.post-tags a` / `.share-buttons` / `.paginav` / `.share-box` / 行內 `code`。改它會連帶換掉那些 UI 表面，所以**只覆蓋 `--code-block-bg`**（它只被 `.highlight:not(table)` 與 `pre code` 用到），行內 code 另外用 scoped 選擇器處理：

```css
.post-content :not(pre) > code { background: #E5E5E6 }
:root[data-theme="dark"] .post-content :not(pre) > code { background: #1a1b26 }
```

### 圓角與文字色

- `.post-content .highlight:not(table)` 有 `border-radius` 但**沒有** `overflow: hidden`，內層 `pre` 是直角 → 加 `overflow: hidden` 保險（底色一致時其實看不出來，但別依賴這件事）
- PaperMod 把 `.post-content pre code` 的文字色**寫死成 `rgb(213,213,214)`**，在淺色的 Atom One Light 底上幾乎看不見 → 覆蓋成 `color: inherit`，讓它跟著 `.chroma` 的 `#383A42` / `#c0caf5`

### 驗證

```sh
rm -rf public && hugo --minify
CSS=$(ls public/assets/css/stylesheet.*.css | head -1)

# 1) 外框底色：最後兩個必須是我們的（#FAFAFA / #1a1b26），不能停在 custom.css 的舊值
rg -o '\-\-code-block-bg:[^;]*' "$CSS"

# 2) 程式碼必須是 class-based，不能再有行內 style
rg -c 'class=chroma' public/posts/<slug>/index.html
rg -c 'style=color' public/posts/<slug>/index.html        # 應為 0

# 3) 漏色（Catppuccin 殘留色）只能在瀏覽器驗，見下方 audit
```

瀏覽器端 audit（把 `CAT` 換成 Catppuccin 的值，抓頁面上 0 個殘留才算過）：

```python
CAT=['#f4dbd6','#cad3f5','#6e738d','#24273a','#8aadf4','#a6da95','#f5a97f','#ed8796','#c6a0f6','#eed49f','#91d7e3','#8bd5ca','#363a4f','#8087a2']
# 對 .chroma span 逐個 getComputedStyle(el).color 轉 hex，與 CAT 取交集 → 必須是空集合
```

⚠️ 驗證要用**瀏覽器算完 computed style**，不能只看 CSS 原始碼——漏色的成因是「另一個檔案的舊規則還在生效」，光掃自己的 CSS 看不到。
