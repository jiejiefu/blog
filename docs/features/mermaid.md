> 本文件是 `AGENTS.md` 的延伸，只在改到這個功能時讀。回到 [AGENTS.md](../../AGENTS.md)。

## Mermaid 流程圖

兩種寫法都支援，底層是同一套轉義邏輯：

````markdown
```mermaid
flowchart LR
    A[感測器資料] --> B[特徵工程]
```

{{< mermaid >}}
flowchart LR
    A[感測器資料] --> B[特徵工程]
{{< /mermaid >}}
````

` ``` mermaid `（語言名前有空格）同樣會命中 render hook —— Goldmark 會 trim 空白，`drafts/` 裡 ChatGPT 產的稿件用的就是這種寫法。

### 檔案與職責

| 檔案 | 職責 |
|---|---|
| `layouts/_default/_markup/render-codeblock-mermaid.html` | fenced block → `<pre class="mermaid">` |
| `layouts/shortcodes/mermaid.html` | shortcode → `<div class="mermaid">` |
| `layouts/partials/extend_head.html` | importmap + 條件判斷 + `<script type="module">` |
| `assets/js/mermaid-init.js` | 初始化 + `mermaid.run()` |
| `assets/css/extended/custom.css` | `.mermaid` 排版 + 深色模式反相 |

### ⚠️ 踩過的坑 1：逐頁判斷絕對不能放 `extend_footer.html`

`baseof.html:28` 是：

```
{{ partialCached "footer.html" . .Layout .Kind (.Param "hideFooter") (.Param "ShowCodeCopyButtons") }}
```

**快取鍵是 `.Layout` 與 `.Kind`，不是頁面。** 所有 `Layout`/`Kind` 相同的頁面共用同一份 footer 輸出。所以任何「這個頁面要不要做 X」的判斷放進 `extend_footer.html`，實際會變成「第一個被算到的頁面決定全站」，而且**不會報錯、沒有 warning**。

Mermaid 最初就是踩在這裡 —— 判斷條件寫對了，卻因為 footer 是全站共用的快取，102 個頁面裡只有 1 個拿到了 `<script type="importmap">`。

`extend_head.html` 沒有這個問題：`baseof.html:16` 呼叫 `head.html` 用的是 `{{ partial }}`（逐頁求值）。KaTeX 的 `math: true` 判斷之所以一直正確，正是因為它在 head 裡。

**規則：逐頁條件一律放 `extend_head.html`。**

### ⚠️ 踩過的坑 2：`deterministicIds` 不開，同頁第 2 張圖之後全壞

`mermaid.run()` 內部：

```js
let n = new InitIDGenerator(config.deterministicIds, config.deterministicIDSeed);
for (let el of elements) { ... let id = `mermaid-${n.next()}`; ... }
```

`InitIDGenerator` 在 `deterministicIds: false`（預設）時 `next()` 回傳 **`Date.now()`**。而 `run()` 是用 `await` 在一個緊密迴圈裡跑完所有圖的 —— 同一毫秒內很容易撞到相同 id。

撞到的後果（不是報錯，是靜靜地畫錯）：
- 後來的圖拿到**重複的 SVG id**，mermaid 對到別張圖的節點
- 產出**沒有 `viewBox`、沒有 `style="max-width:…"`** 的空 SVG
- 視覺上：第 2 張之後的圖**疊在一起**，某張圖的錯誤方塊還會**蓋住別張圖**

診斷方式（看 SVG 根元素就知道，正常的一定要有 `viewBox`）：

```sh
rg -o '<svg[^>]*>' public/posts/<slug>/index.html
```

修法：`mermaid.initialize({ deterministicIds: true })`，`next()` 變成 `count++`（0,1,2…），同一個 `run()` 內保證不重複。**這個選項不能拿掉。**

回歸測試在 `content/zh-tw/posts/mermaid-smoke-test/index.md`（draft），那一頁刻意放了 5 張圖。

### ⚠️ 踩過的坑 3：mermaid 讀的是 `innerHTML` 不是 `textContent`

`run()` 的實際行為是 `el.innerHTML` → `entityDecode()` → `.trim()`。所以 render hook 裡的 `htmlEscape` 剛好是對的：Hugo 轉義成實體 → mermaid 的 `entityDecode` 用臨時 div 的 `textContent` 解回來。

兩層轉義都要過，缺一不可：
- **Hugo 層** `htmlEscape`：`>` `<` `&` `"` `'` → 實體，否則節點標籤裡的 `<` 會被瀏覽器當成真實標籤
- **mermaid 層**標籤跳脫：想放雙引號要用 `#quot;`，**`\"` 不是 mermaid 語法**，會直接 parse error

同理，**標籤裡不要放 `-->` 或 `->`**。原本 `edge-ai-platform-ppt169` 的 PCA 與 One-Class SVM 圖，尾節點標籤寫成 `New Feature Vector -> Normal / Anomaly`，轉成 mermaid 時改成用全形冒號描述（`新特徵向量：正常或異常`），不去賭 lexer 會不會誤判。

### diagram type 由內容決定，不是 fence

`stateDiagram-v2` 要寫在 ` ```mermaid ` 區塊**裡面**，不要另開 ` ```stateDiagram `。fence 的語言名必須是 `mermaid` 才會命中 render hook；mermaid 看到內容開頭是 `stateDiagram-v2` 就會切到狀態圖語法。§6.4 的模型建置狀態機就是這樣做的。

### 深色模式

只有一行 CSS，沒有任何 JS：

```css
:root[data-theme="dark"] .mermaid svg { filter: invert(1) hue-rotate(180deg); }
```

`custom.css` 的深色模式是純黑（`--theme: rgb(0,0,0)`），mermaid 預設淺色主題正好 invert 成黑底白線。**刻意不做「監聽 `data-theme` 切換重跑 `mermaid.run()`」** —— 那要先清 `data-processed` 再還原原始文字，切換瞬間必然有空白幀閃爍，而 filter 是 GPU 圖層操作，瞬間完成。

代價：彩色語意（綠=Pass、紅=Fail）會偏色。目前站上沒有這種圖。

### ⚠️ 踩過的坑 4：置中不能用 `justify-content: center`

原本寫的是：

```css
.mermaid { display: flex; justify-content: center; overflow-x: auto; }
```

這是 flexbox 的經典陷阱：**內容比容器寬時，溢出被平均推到左右兩側，而左側溢出捲不到**，讀者會發現圖的左邊怎麼滑都看不到。當時只有 TB 與短 LR，沒有任何一張圖會溢出，所以看不出來；全改成 LR 之後 §9.3 那張（9 節點、7 欄）就會踩到。

修法是置中改用**子元素的 `margin: auto`**，捲動就會從最左端開始：

```css
.mermaid { display: block; margin: 1.5rem 0; overflow-x: auto; }
.mermaid > svg { display: block; margin: 0 auto; }
```

順帶一提，mermaid 的 SVG 帶 `width="100%"` + `style="max-width: Npx"`，所以**寬圖是「縮」而不是「溢」**。實測最寬那張在 720px 的 `--main-width` 下縮到約 0.55×，中文仍可辨識，因此不需要再加 `min-width` 強制橫向捲動（那會讓手機版每張圖都要滑）。

### 其他注意事項

- **CDN 版本釘在 `extend_head.html` 的 importmap**，換版號只改那裡。`assets/js/mermaid-init.js` 用 `import mermaid from "mermaid"`（裸代碼）走 importmap。
- **選 ESM（`mermaid.esm.min.mjs`）而非 UMD**：實測 ESM 靜態 import 圖 ~183 KB gzip（約 26 個請求），UMD `mermaid.min.js` 是 1.57 MB gzip，貴 8.6 倍。代價：dynamic import 拿不到 SRI。
- **條件載入**靠 `.RawContent` 掃 `"mermaid"`（同時命中 fenced 與 shortcode），沒圖的頁面不會付這 183 KB。include/partial 帶進來的圖掃不到，在 front matter 手動加 `mermaid: true`。
- **`hugo --minify` 不會破壞 importmap**：實測 minifier 只會把 `type="importmap"` 的引號去掉，JSON 內容原樣保留。
- **不要用 `suppressErrorRendering: true`**：那會讓語法錯的圖直接 throw，而 throw 會中斷 `run()` 的迴圈，導致**後面的圖全部不再渲染**。預設的 `false` 會把錯誤畫成一個（置中的、不會蓋到別人）錯誤方塊，可以接受。
- 語法錯的圖**只會影響自己那張**，頁面其他部分照常運作，`mermaid-init.js` 只 `console.error` 不往上拋。
- JS 載入前會短暫顯示 mermaid 原始碼。**刻意不做 `.mermaid:not([data-processed]) { visibility: hidden }`** —— 那會讓 CDN 失敗時圖表變成隱形空白，比顯示原始碼更糟；原始碼本身可讀就是好的降級。

### 驗證

⚠️ **`public/` 是 client 渲染前的產物**，裡面永遠不會有 mermaid 產生的 SVG（只有 PaperMod 的靜態圖示 svg）。所以「每張圖都要有 viewBox」這件事**只能在瀏覽器渲染後驗**，不能對 `public/` 跑。

Hugo 端（純模板檢查）：

```sh
hugo -D --minify                                    # 零新 warning
rg -c '<pre class=mermaid>' public/posts/<slug>/index.html   # fenced 數量對不對
rg -o '<script type=importmap>[^<]*' public/posts/<slug>/index.html \
  | python3 -c 'import json,sys;print(json.loads(sys.stdin.read().split(">",1)[1]))'
rg -l 'importmap' public/index.html                  # 負向測試：無圖的頁面應無輸出
```

⚠️ **`hugo server` 會改寫 `public/`。** v0.168 的 dev server 會把非 minify、含 draft 的版本寫進 `public/`，所以剛跑完 server 就去讀 `public/` 會讀到 dev 產物而不是正式產物。要對 `public/` 做檢查就先 `rm -rf public && hugo --minify` 重跑。

⚠️ **minify 會改變屬性引號。** `hugo --minify` 產出 `<pre class=mermaid>`（無引號），dev server 產出 `<pre class="mermaid">`（有引號）。用 Python `re` 抓 HTML 時兩種都要接受：

```python
re.findall(r'<pre class="?mermaid"?>.*?</pre>', html, re.S)
```

只寫其中一種就會出現「明明有 12 張圖卻抓到 0 張」的情況。

瀏覽器端（坑 2 的真正回歸測試）：

```sh
hugo server -D &
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$CH" --headless=new --disable-gpu --user-data-dir="$(mktemp -d)" \
  --virtual-time-budget=60000 --dump-dom \
  "http://localhost:1313/posts/mermaid-smoke-test/" > /tmp/d.html
python3 - /tmp/d.html <<'PY'
import re,sys
h=open(sys.argv[1],encoding='utf-8').read()
svg=re.findall(r'<svg[^>]*aria-roledescription="[^"]*"[^>]*>',h)
bad=[s for s in svg if 'viewBox' not in s]
print(f"{len(svg)} 張圖，缺 viewBox 的有 {len(bad)} 張")
PY
```

`缺 viewBox 的有 0 張` 才算過。只要大於 0，就是坑 2 復發（`deterministicIds` 被拿掉了）。

想肉眼看深色模式：`HUGO_PARAMS_DEFAULTTHEME=dark hugo server -D`，
因為 PaperMod 的主題是 front matter 參數驅動的，這樣才不用手動點切換。

`assets/js/mermaid-init.js` 是 `assets/js/` 裡**唯一**的 ESM 檔（其餘如 `share-link.js` 刻意是 ES5），差異是刻意的，不要「修正」成 ES5。
