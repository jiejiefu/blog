> 本文件是 `AGENTS.md` 的延伸，只在改到這個功能時讀。回到 [AGENTS.md](../../AGENTS.md)。

## 網站圖示（favicon / PWA）

原始素材只有一份：`assets/images/brand/djfj-logo.png`（416×204 透明「DJFJ」字標）。
`scripts/site-icon/make_icons.sh` 會把它置中放進 `#0B1220` 圓角方塊，產出下列**已 commit 的成品**：

| 檔案 | 尺寸 | 用途 |
|---|---|---|
| `static/favicon.ico` | 16/32/48/64/128/256 多層 | 舊瀏覽器 fallback、Windows |
| `static/favicon-16x16.png` / `favicon-32x32.png` | 16、32 | 分頁圖示（圓角方塊） |
| `static/apple-touch-icon.png` | 180 | iOS 主畫面（滿版、不透明） |
| `static/android-chrome-{192,512}.png` | 192、512 | Web App Manifest |
| `static/site.webmanifest` | — | `theme_color` / `background_color` = `#0B1220` |
| `static/safari-pinned-tab.svg` | — | Safari 釘選分頁（best-effort） |

**為什麼放 `static/` 而不是 `assets/`：**

- PaperMod `head.html:93-97` 已寫死根目錄檔名，且瀏覽器會隱式請求 `/favicon.ico`
- `assets/` 的 `fingerprint` 會產生 hash 檔名，上述兩件事都會失效
- 原始 `djfj-logo.png` 留在 `assets/images/brand/`，因為它**不該**被發佈

**設計取捨：**

- favicon 用圓角方塊（半徑 22%），apple-touch / Android 用**滿版**方塊 —— iOS 與 launcher 自己會裁圓角，再做一次會出現透明黑角
- 方形圖示是**不透明**的，所以 apple-touch / android 用 PNG8（256 色）。實測金屬漸層 RMSE ≈ 0.9%，檔案從 197 KB 降到 68 KB
- ICO 的 64/128/256 層也用 PNG8，整包從 361 KB 降到 112 KB；16/32/48 維持 PNG32 讓圓角抗鋸齒乾淨
- 寬版字標在 16px 仍偏小是必然結果；圓角深色底至少提供可辨識的輪廓

**重產：**

```sh
./scripts/site-icon/make_icons.sh
```

⚠️ 腳本需要 ImageMagick 7（`magick`）。Safari mask-icon 沒有用 `potrace`（未安裝），而是把黑色 silhouette PNG 以 base64 嵌進 SVG；Safari 釘選分頁是舊功能，可接受。

**驗證：**

```sh
rm -rf public && hugo --minify
magick identify public/favicon.ico          # 應有 16~256 六層
python3 -c "import json;print(json.load(open('public/site.webmanifest'))['theme_color'])"
rg -o '<link rel=[^>]*(icon|manifest)[^>]*>' public/index.html
```

⚠️ 本機驗證圖示 URL 時，`public/` 必須掛在 `/blog/` 底下（baseURL 含前綴），不能直接 serve `public/`。

⚠️ **改完圖示後按 Cmd+Shift+R 不會重抓 favicon。** Chrome 的 favicon 是獨立快取，硬重新載入只刷新頁面。要看到新圖示：直接開 `http://localhost:1313/blog/favicon-32x32.png` 確認檔案存在 → 關閉分頁重開／重啟瀏覽器，或 DevTools → Application → Storage → Clear site data。正式站則要先 commit + push，等 GitHub Actions 部署完成；部署前 `/blog/favicon.ico` 仍是 404。
