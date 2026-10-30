> 本文件是 `AGENTS.md` 的延伸，只在改到這個功能時讀。回到 [AGENTS.md](../../AGENTS.md)。

## Plotly 互動圖表

`{{< plotly >}}` 把一段 JSON 交給 Plotly 渲染成可縮放、可 hover、可下載 PNG 的互動圖表。
body 直接對應 `Plotly.newPlot(div, data, layout, config)`。

### 檔案與職責

| 檔案 | 職責 |
|---|---|
| `layouts/shortcodes/plotly.html` | 驗證 JSON、輸出 `<figure>` + 空的圖表容器 + `<script type="application/json">` |
| `assets/js/plotly-init.js` | 解析 JSON、動態載入 Plotly、`newPlot`、主題切換重繪（ES5，無相依） |
| `layouts/partials/extend_head.html` | 只在用到 plotly 的頁面載入 `plotly-init.js`（**不載 Plotly 本體**） |
| `assets/css/extended/custom.css` | `.plotly-figure` / `.plotly-chart` / figcaption / `.plotly-chart__error` |

### 用法

```markdown
{{< plotly height="420" caption="季度增長" >}}
{
  "data": [{ "x": [1,2,3], "y": [10,20,15], "type": "scatter", "mode": "lines+markers" }],
  "layout": { "title": "季度增長" }
}
{{< /plotly >}}
```

- `height`（預設 `420`，可寫 `420` 或 `420px`）、`caption`（可省略；有給就進 `<figcaption>` 並當 `aria-label`）。
- 需要 Basic bundle 沒有的圖表型別（3D、heatmap、geo、contour、sankey…）時加 `bundle="full"`：

```markdown
{{< plotly bundle="full" height="520" >}} { "data": [{ "type": "scatter3d", ... }] } {{< /plotly >}}
```

- `bundle` 只接受 `basic` / `full`，其他值在 build 就 `errorf`。

### 為什麼由 JS 動態載入 Plotly，而不是在 head 直接 `<script>`

Full bundle 是 **4.83 MB min / 1.48 MB gzip**，Basic 是 **1.20 MB min / 398 KB gzip**。
在 head 直接載就得先決定載哪一個，但 shortcode 的 `bundle` 參數在模板端不好可靠解析。
改成由 `plotly-init.js`（約 2 KB）依容器上的 `data-plotly-bundle` 決定：

- 模板不用解析 `.RawContent` 猜 bundle
- 同一頁只要有一張 `full`，全頁載一次 `full`（full 是 basic 的超集）
- 非圖表頁面連 `plotly-init.js` 都不會載入 → 0 bytes

| 頁面 | 首次 | 回訪 |
|---|---|---|
| 一般文章 | 0 | 0 |
| Basic 圖表頁 | ~398 KB gzip | 0（jsDelivr immutable，快取一年） |
| Full 圖表頁 | ~1.48 MB gzip | 0 |

⚠️ **Basic bundle 只含 scatter / bar / pie。** 用 histogram、box、heatmap 等要 `bundle="full"`，
否則 `newPlot` 會 throw，`plotly-init.js` 會把它翻成「此圖表需要 bundle="full"」顯示在圖表位置。
若日後 2D 圖表幾乎都用到 histogram/heatmap，可把預設改載 `plotly.js-cartesian-dist-min`
（約 1.51 MB min / ~450 KB gzip，含多數 2D 型別），改 `plotly-init.js` 的 `BUNDLES` 即可。

### ⚠️ 踩過的坑

1. **不要在 `{{< plotly >}}` 的正文裡直接寫 `{{< plotly >}}` 當說明。** Hugo 在 Markdown 之前就解析 shortcode，會被當成一個未關閉的 shortcode 而出錯（`shortcode "plotly" must be closed or self-closed`）。要示範語法時改成純文字描述，示範頁 `plotly-smoke-test` 因此改寫了該句。
2. **`.Inner` 一定要先 `transform.Unmarshal` 驗證。** 直接把未驗證的字串塞進 `<script>`，JSON 打錯只會在瀏覽器留下空白圖表；驗證後 build 就會失敗並指出頁面路徑。
3. **輸出用 `jsonify | safeJS`，不要直接 `.Inner | safeJS`。** Go 的 `encoding/json` 預設把 `<` 轉成 `\u003c`，字串裡即使有 `</script>` 也無法提前關閉標籤；但 `<script>` 在 `html/template` 裡是 JS context，少了 `safeJS`，`jsonify` 的輸出會被再包成一層字串，`JSON.parse` 拿到 string，圖表空白。
4. **id 用 `.Ordinal`，不要抄網路上的 `div (mul rand 100000) 1`。** Hugo 沒有 `rand` 這個函式，會直接 build error；`.Ordinal` 同頁唯一且可重現。
5. **CDN 是 `cdn.jsdelivr.net`，不是 `plot.ly`。** `https://plot.ly` 是官網 HTML，`Plotly` 會是 undefined。
6. **逐頁判斷只能放 `extend_head.html`。** 與 Mermaid 同一個坑：`extend_footer.html` 走 `partialCached`，快取鍵是 `.Layout`/`.Kind` 不是頁面。
7. **偵測用 `.HasShortcode "plotly"`**（不是 `strings.Contains .RawContent "plotly"`），正文或程式碼提到 `plotly` 不會誤載。由 partial / include 帶進來的圖表掃不到，那時在 front matter 加 `plotly: true`。
8. **深色模式是 `MutationObserver` 監看 `<html data-theme>` 後 `Plotly.relayout`**，不是 CSS filter。PaperMod 切主題只改 attribute、不發事件。使用者的 `layout` 優先：`mergeLayout` 只補沒被指定的鍵，並在 `relayout` 時只動字色與軸線色，保留縮放/平移。
9. **升版要同時改版本與 SRI**（`plotly-init.js` 的 `BUNDLES`）。重算方式：

```sh
curl -s https://cdn.jsdelivr.net/npm/plotly.js-basic-dist-min@<ver>/plotly-basic.min.js | openssl dgst -sha384 -binary | openssl base64 -A
curl -s https://cdn.jsdelivr.net/npm/plotly.js-dist-min@<ver>/plotly.min.js | openssl dgst -sha384 -binary | openssl base64 -A
```

### 驗證

```sh
rm -rf public && hugo --minify          # 零 warning（draft 的示範頁不會進正式建置）
hugo -D --minify                        # 含 draft，才能檢查 plotly-smoke-test

P=public/posts/plotly-smoke-test/index.html
rg -o '<script[^>]*plotly[^>]*>' "$P"                     # 應只有 plotly-init，不該直接載 Plotly 本體
rg -o 'id=plotly-[0-9]+' "$P"                             # 數量與 unique 都要對

# 負向：已發佈的無圖文章不該出現 plotly-init / plotly-chart
rg -c 'plotly-init|plotly-chart' public/posts/rea-reverse-engineer-anything/index.html   # 應為 0

# JSON 全部可 parse
python3 -c "import re,json;h=open('$P',encoding='utf-8').read();[json.loads(s) for s in re.findall(r'<script[^>]*plotly-chart__spec[^>]*>(.*?)</script>',h,re.S)];print('spec ok')"
```

⚠️ **`public/` 是 client 渲染前的產物**，只載入 init、不會有 Plotly 產生的 SVG，也看不到實際載入哪個 bundle。
「有沒有真的畫出來、載的是 basic 還是 full」只能在瀏覽器驗：

```sh
hugo server -D -p 1413 &
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$CH" --headless=new --disable-gpu --user-data-dir="$(mktemp -d)" \
  --virtual-time-budget=40000 --dump-dom \
  "http://localhost:1413/blog/posts/plotly-smoke-test/" > /tmp/plotly.html
python3 -c "import re;h=open('/tmp/plotly.html',encoding='utf-8').read();print('charts:',len(re.findall(r'js-plotly-plot',h)));print('lib:',re.findall(r'src=\"(https://cdn[^\"]*plotly[^\"]*)\"',h))"
```

- 含 `bundle="full"` 的頁面應載入 `plotly.js-dist-min@…/plotly.min.js`；只有 basic 的頁面載 `plotly.js-basic-dist-min@…/plotly-basic.min.js`。
- CDN 掛掉時圖表位置應顯示「圖表載入失敗（無法連線至 CDN）。」，頁面其餘部分正常。可用 `--host-resolver-rules="MAP cdn.jsdelivr.net 127.0.0.1"` 模擬。

⚠️ **`hugo server` 會改寫 `public/`**，要對 `public/` 做檢查前先 `rm -rf public && hugo --minify`。
