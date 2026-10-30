> 本文件是 `AGENTS.md` 的延伸，只在改到這個功能時讀。回到 [AGENTS.md](../../AGENTS.md)。

## 數學公式（KaTeX）

啟用方式：`config.yaml` 的 `markup.goldmark.extensions.passthrough` + front matter 加 `math: true`。

⚠️ **四個踩過的坑：**

1. **Hugo 沒有 `math` 這個設定鍵。** 寫 `markup.goldmark.extensions.math: true` 會被**靜默忽略**（`hugo config` 查不到），render 出來是字面上的 `$$`。Hugo 的機制是 **passthrough extension**。
2. **delimiter 必須是「一對」，不是扁平陣列。** 官方文件寫的 `block: ['\[', '\]']` 是錯的寫法 —— Go 端對每個元素取 `d[0]`/`d[1]`，扁平陣列會讓 open/close 變成單一字元，正確寫法是巢狀：
   ```yaml
   block:
     - ['$$', '$$']
   inline:
     - ['\(', '\)']
   ```
3. **單字元 delimiter 會讓 Hugo 直接 panic**（`index out of range [1] with length 1`），整個 build 失敗。
4. **inline 千萬不要用 `$`。** 站上英文 TECH_TRENDS 有 `$100 billion`、`$900,000`、`$3,500`、`$100,000`。一旦 `$` 成為 delimiter，同一段落裡出現兩個金額就會被整段當成 LaTeX 吞掉。所以 inline 一律用 `\(...\)`。

**SRI 一定要用程式算，不要憑印象寫。** `integrity` 填錯瀏覽器會**直接封鎖該 script**（不是警告，是不執行），`renderMathInElement` 就不存在 → 整頁數學不渲染，而且 CSS 正常載入所以看起來像有設定好，最難debug。
驗證方式（每次升級 KaTeX 版號後都要重跑）：
```sh
python3 - <<'PY'
import re,hashlib,base64,urllib.request
s=open('layouts/partials/extend_head.html',encoding='utf-8').read()
for m in re.finditer(r'(?:src|href)=(?:"([^"]+)"|(\S+))\s+integrity="?([^"\s>]+)"?',s):
    u=m.group(1) or m.group(2)
    if 'jsdelivr' not in u: continue
    real=base64.b64encode(hashlib.sha384(urllib.request.urlopen(u,timeout=30).read()).digest()).decode()
    print(('MATCH   ' if real==m.group(3).split('-',1)[1] else 'MISMATCH'), u)
PY
```
