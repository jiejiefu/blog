> 本文件是 `AGENTS.md` 的延伸，只在改到這個功能時讀。回到 [AGENTS.md](../../AGENTS.md)。

## 分享連結區塊

讀者一鍵複製「標題 + 永久連結 + 出處」，另有 Facebook / X / LINE 三顆按鈕（PaperMod 自帶的 share icons 仍在 `.post-footer` 裡，兩組並存）。

文章底部順序：`tags → 分享框 → 觀眾留言 → 上一篇/下一篇 → PaperMod 小圖示`。

- **分享文字在伺服器端組好**（`share_link.html` 用 `{{ T }}` 走 i18n），塞進 `data-share-text`；JS 只負責複製 → 中英文自動分流，不用在 JS 裡判斷語言
- **用 `.Permalink` 而非 `window.location.href`**：讀者從 staging 網址進來時不會複製到錯的網址
- **按鈕文字沿用 PaperMod 現成的 i18n key** `code_copy` / `code_copied`（zh-tw = 複製／已複製！，en = copy／copied!），沒有另建
- 新增的 i18n key（`i18n/zh-tw.yaml` + `i18n/en.yaml`）：`share_quote`、`share_title_format`、`share_url_label`、`share_source_label`
- JS 用**事件委派**（`document` 上攔 `[data-share-copy]`）而非硬編碼 `id` → 同頁放幾個都不會衝突
- 有 `navigator.clipboard` + `execCommand` 兩條路徑，非 secure context 不會炸
- `.share-box__status` 帶 `role="status" aria-live="polite"`，螢幕閱讀器會唸出複製結果

⚠️ **踩過的坑 1：`--theme` 和 `--entry` 不能當反色配對。**

PaperMod 的 `theme-vars.css` 在淺色模式把**兩個都設成白色**，`custom.css` 在深色模式又把**兩個都設成黑色**。拿 `background: var(--theme)` + `color: var(--entry)` 會做出白底白字（淺色）／黑底黑字（深色）——**兩種模式都看不見**。

真正互斥的是 **`--primary`（文字色）↔ `--theme`（表面色）**，因為 `custom.css` 刻意做成純黑白色系：

| | `--primary` | `--theme` |
|---|---|---|
| light | `rgb(0,0,0)` | `rgb(255,255,255)` |
| dark | `rgb(255,255,255)` | `rgb(0,0,0)` |

`background: var(--primary); color: var(--theme)` → 兩種模式都是 21:1（AAA）。

驗證對比度（別只靠目視）：

```sh
CSS=$(ls public/assets/css/stylesheet.*.css | head -1)
# ⚠️ 別用 'data-theme="dark"' 比對：minifier 會把引號去掉，變成 [data-theme=dark]
python3 - "$CSS" <<'PY'
import re,sys
css=open(sys.argv[1],encoding='utf-8').read()
blocks=[(('data-theme' in m.group(2)), m.group(3)) for m in re.finditer(r'(@media[^{]*\{)?(:root(?:\[[^\]]*\])?)\{([^}]*)\}', css)]
def lum(rgb):
    c=[int(x)/255 for x in re.findall(r'[\d.]+', rgb)[:3]]
    c=[x/12.92 if x<=0.03928 else ((x+0.055)/1.055)**2.4 for x in c]
    return 0.2126*c[0]+0.7152*c[1]+0.0722*c[2]
for theme in ('light','dark'):
    v={}
    for isdark, body in blocks:
        if isdark == (theme=='dark'):
            v.update(re.findall(r'(--[\w-]+):\s*([^;]+);', body))
    a,b=lum(v['--primary']),lum(v['--theme'])
    print(theme, f"{(max(a,b)+0.05)/(min(a,b)+0.05):.2f}:1")
PY
```

⚠️ **踩過的坑 2：`.post-footer > *` 會蓋掉子元素的 margin。**

PaperMod 有 `.post-footer>* { margin-bottom: 10px }`，與 `.share-box` 同為 (0,1,0) specificity，靠**原始碼順序**決勝 —— `extended.css` 排在 `core.css` 之後，所以 `custom.css` 贏。分享框的 `margin` 必須自己給**上下兩側**的值（目前 `16px 0 24px`），只寫 `margin: 25px 0` 會讓下方完全貼到 `.paginav`。

⚠️ **踩過的坑 3：`{{ . | minify | fingerprint }}` 不能直接印在 `src="{{ }}"` 裡。**

直接插值會呼叫 Resource 的 `String()`，回傳的是**來源路徑** `/js/share-link.js`（沒有 `.min`、沒有 hash，而且該檔案根本不會被 publish）→ 404。必須取加工後的資源指標：

```go-html-template
{{- with resources.Get "js/share-link.js" }}
{{- $js := . | minify | fingerprint }}
<script src="{{ $js.RelPermalink }}" defer></script>
{{- end }}
```

驗證方式：`grep -o '<script src=[^>]*share-link[^>]*>' public/posts/<slug>/index.html` 看到的路徑必須在 `public/` 底下真的存在。


## 覆寫 PaperMod 的 `single.html`

`layouts/_default/single.html` 是整份複製 PaperMod 的檔案，只多插三行：`disableShareBox` 判斷、`partial "share_link.html"`、`end`，位置在 `<footer class="post-footer">` 內、tags 的 `</ul>` 之後。

**主題升級時要 `diff` 一次這個檔案**，不要直接覆蓋。單篇要關掉分享區塊：front matter 加 `disableShareBox: true`。
