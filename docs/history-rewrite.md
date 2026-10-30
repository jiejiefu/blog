# 歷史清理（已完成）

曾用 `git filter-repo` 做過一次歷史重寫並 force-push，若日後要重做，先讀這段。

## 做過什麼

| 目標 | 手法 |
|---|---|
| 移除浮水印來源圖 | `--path ... --invert-paths`（新舊路徑都要列） |
| 移除改名前的舊投影片專案路徑 | `--path <舊路徑> --invert-paths` |
| 清除歷史履歷的舊業態字樣 | `--replace-text`（字串見 `AGENTS.local.md`） |
| 歷史大圖瘦身 | `--blob-callback` 查表替換 blob 內容 |

實際路徑與字串見 `AGENTS.local.md`。

## 三個踩過的坑

- ⚠️ **filter-repo 會自建備份 ref** `refs/original/refs/heads/main`，且不會刪除 `refs/filter-repo/`。跑完必須手動 `git update-ref -d` + `git reflog expire --expire=now --all` + `git gc --prune=now`，否則舊 blob 還在。
- ⚠️ **zsh 裡不要把變數命名為 `path`** —— 它與 `$PATH` 是同一個特殊變數，會直接清空環境。
- ⚠️ **`--blob-callback` 吃的是函式「主體」，不是完整函式。** 寫 `def callback(blob):` 會被巢狀成內層函式、永遠不會被呼叫（而且不報錯）。正確寫法見下：

```
import os
k = blob.original_id            # 是 bytes，不是 str
if isinstance(k, bytes): k = k.decode('ascii', 'replace')
p = os.path.join("/tmp/blobs", k)
if os.path.exists(p) and blob.data[:8] == b"\x89PNG\r\n\x1a\n":
    blob.data = open(p, "rb").read()
return blob
```

另外 `--blob-callback` 支援直接傳檔案路徑（`--blob-callback /path/to/body.py`），比塞在引號裡安全。

## 效果

完整 clone 從 145 MB 降到 16 MB，`content/` 從 210 MB 降到 13 MB。

⚠️ force-push 只清本地。**GitHub 對 public repo 的無參照 blob 仍會保留一段時間**，舊 SHA 可能暫時還能訪問；要連歷史 SHA 都封死需另外開 Support ticket。
