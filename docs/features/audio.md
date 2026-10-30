> 本文件是 `AGENTS.md` 的延伸，只在改到這個功能時讀。回到 [AGENTS.md](../../AGENTS.md)。

## 口述音檔與同步字幕

英文文章可放 narrated audio；目前只有 `content/en/projects/fab-predictive-maintenance-ppt169/audio/morty-introduction.m4a` + 同名 `.vtt`。音檔與字幕**只放 en bundle**，zh-tw 不共用。

### 檔案與職責

| 檔案 | 職責 |
|---|---|
| `layouts/shortcodes/audio.html` | 原生 `<audio>` 播放器；自動偵測同名 `.vtt`，也可用 `captions="..."` 指定 |
| `assets/js/audio-captions.js` | fetch VTT、解析 cue、依播放時間換句（ES5，無相依） |
| `assets/css/extended/custom.css` | `.post-audio__player` / `.post-audio__cue` / `.post-audio__caption` |
| `content/en/projects/fab-predictive-maintenance-ppt169/audio/morty-introduction.m4a` | 口述音檔 |
| `content/en/projects/fab-predictive-maintenance-ppt169/audio/morty-introduction.vtt` | 同步字幕 |
| `scripts/build_audio_vtt.py` | 泛用 VTT 產生器：帶音檔／影片路徑即可；有 `--cues` 時用逐字稿對齊，否則用 ASR 文字切句 |
| `scripts/fab-predictive-maintenance-ppt169/morty-introduction.cues.txt` | 這篇文章的一行一個 cue 原文 |

### 規則

- **caption 不加秒數。** 目前是 `Introduction — narrated by Morty`；秒數會隨重錄變動，不寫進 caption。
- 音檔與 VTT 檔名全小寫 + hyphen（`morty-introduction.m4a`），不要空格或大寫。
- **VTT 文字逐字等於文章原文。** ASR 只用來取時間，不能把 ASR 轉錄文字直接當字幕；TTS 的數字、縮寫、標點都可能與原文不同。
- 同名 `.vtt` 會自動掛上；`captions="audio/other.vtt"` 可覆寫。顯式指定的字幕找不到時 build error，自動偵測找不到則安靜跳過（音檔仍可播）。
- `<audio>` 原生不渲染 `<track>` 字幕，所以由 JS fetch + 自行解析。字幕容器有 `aria-hidden="true"`，因為文章本身就是逐字稿，避免螢幕閱讀器重複朗讀。
- 字幕**不在頁面載入時顯示**；`play` / `seeking` / `seeked` / `timeupdate` 換句。句與句之間與 `ended` 之後**保留最後一句**，只有 `emptied` 才清空，避免文章上下跳動。無 JS 時音檔照常播放，只是沒有字幕。
- `.post-audio__cue[hidden]` 用 `display: block; visibility: hidden`，**保留 `min-height` 佔位**。若改回 `display: none`，字幕出現／消失時下方文章會跳動。
- JS 只在 `.HasShortcode "audio"` 的頁面載入，且**只能放 `extend_head.html`**；footer 是 `partialCached`，逐頁判斷會變成第一頁決定全站。

### 離線產生 VTT（不下載模型）

VoiceStudio 的 runtime venv 已有 `faster-whisper`，HF cache 也有 `Systran/faster-whisper-large-v3`。腳本會設 `HF_HUB_OFFLINE=1` 並用 `local_files_only=True`，**不會下載模型**：

```sh
V=~/Library/Application\ Support/VoiceStudio/runtime/project/.venv/bin/python
"$V" scripts/build_audio_vtt.py \
  content/en/projects/fab-predictive-maintenance-ppt169/audio/morty-introduction.m4a \
  --cues scripts/fab-predictive-maintenance-ppt169/morty-introduction.cues.txt \
  --language en --words-per-cue 5
```

- **預設輸出到媒體檔旁邊的同名 `.vtt`**（`morty-introduction.m4a` → `morty-introduction.vtt`）；`--out` 可指定檔案或既存目錄。
- **`--cues` 模式**：逐字稿是文字來源，ASR 只取 word timings；腳本用 `initial_prompt=全文`，把原文 token 對到 ASR word timings，對不上的 token（數字、`RUL`、標點）用前後 word 內插。token similarity < 0.80 時預設拒絕寫檔，並印出差異；確認是 ASR 正常誤差才加 `--force`。
- **`--words-per-cue N`**：把每個 cue 再切成每段約 N 個字（這篇用 5，產出 29 cues）；同一 cue 內會平均分配，不會留下 1 個字的碎片。不要拆分就省略（預設 0）。所有 cues 會**前後相接**，`end` 等於下一段的 `start`，播放中不會出現空白。
- **不帶 `--cues` 模式**：直接用 ASR 文字當字幕，依標點、`--max-chars`（預設 84）與 `--max-duration`（預設 7 秒）切句。適合未來臨時影片；要精確文字仍應提供 cue 檔。
- 支援影片路徑（mp4/mov/mkv 等），faster-whisper 會自動取音軌。
- `--model` 可指向本機 snapshot 目錄；若模型不在 cache，腳本會直接失敗，不會偷偷下載。
- `--dump-transcript` 只印 segments/words，不寫 VTT。
- 無 `--cues` 的逐字稿模式適合臨時影片；ASR 可能把專有名詞轉小寫、把 `real-time` 斷成 `real -time`，腳本會修掉多餘空白並折疊相鄰重複詞（例如尾端 `systems. systems.`），但正式文章仍建議提供 cue 檔。
- cue 檔一行一個 cue；不要在 cue 內換行，也不要有 `-->`。

### 驗證

```sh
rm -rf public && hugo --minify

# 英文頁有字幕屬性，zh-tw 沒有
rg -o 'data-audio-captions=[^ >]+' public/en/projects/fab-predictive-maintenance-ppt169/index.html
rg -c 'audio-captions' public/en/projects/fab-predictive-maintenance-ppt169/index.html   # 2（data 屬性 + script）
rg -c 'audio-captions' public/projects/fab-predictive-maintenance-ppt169/index.html      # 0

# VTT 與 m4a 都要真的 publish
ls -lh public/en/projects/fab-predictive-maintenance-ppt169/audio/
```

⚠️ **`public/` 是 client 渲染前的產物**；字幕文字要等 JS fetch VTT 後才會出現，不能只對 `public/` 斷言換句。瀏覽器驗證要設 `audio.currentTime` 到多個時間點，確認 `[data-audio-cue]` 的 `textContent` 會變且 `hidden` 會切換。

⚠️ **不要用 `python3 -m http.server` 驗 seek 字幕。** 它不支援 HTTP Range，`audio.seekable` 只有 `[0,0]`，`currentTime` 永遠停在 0，字幕看起來像壞掉。用 `hugo server -p 1414`（Go 的 `http.ServeContent` 支援 Range）或任何支援 Range 的靜態伺服器。實測 `hugo server` 下 seek 到 0.5 / 8 / 30 / 45.5 秒都會換句；`ended` 後保留最後一句，`emptied` 才清空。

⚠️ **改 `--words-per-cue` 後要同時確認高度不跳。** 在瀏覽器量 `.post-audio__cue` 的 `offsetHeight`（多個時間點應相同），並確認 `figure.post-audio` 的 `offsetHeight` 不變。`min-height: 3.1em` 只夠 2 行；若把 N 調大或視窗很窄導致換行超過 2 行，要同步調高 `min-height`。
