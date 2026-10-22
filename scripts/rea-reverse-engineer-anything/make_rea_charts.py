"""Generate the five charts used in the REA post.

Usage:
    python3 scripts/rea-reverse-engineer-anything/make_rea_charts.py

Writes 1600px-wide WebP files directly into the post's page bundle. The PNG
intermediates stay in a temporary directory and are never published.

Figure numbering follows document order; 圖二 is a Mermaid diagram in the
post, so there is no 02_* image file.
"""

import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from matplotlib.ticker import FuncFormatter
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from image_utils import save_figure_webp

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "content/zh-tw/posts/rea-reverse-engineer-anything/images"

plt.rcParams["font.sans-serif"] = ["PingFang TC", "Arial Unicode MS", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False

INK = "#111827"
MUTED = "#6B7280"
GRID = "#E5E7EB"
ACCENT = "#4F46E5"
ACCENT_LIGHT = "#EEF2FF"
PAPER = "#FFFFFF"

dates = ["2026-10-09","2026-10-10","2026-10-11","2026-10-12","2026-10-13",
         "2026-10-14","2026-10-15","2026-10-16","2026-10-17","2026-10-18","2026-10-19"]
stars = [42878,63995,99759,151317,203436,238743,267586,289438,306152,320903,326825]
d = [datetime.strptime(x, "%Y-%m-%d") for x in dates]

fig, ax = plt.subplots(figsize=(8, 4.5), dpi=200)
fig.patch.set_facecolor(PAPER)
ax.set_facecolor(PAPER)
ax.fill_between(d, stars, color=ACCENT_LIGHT, zorder=1)
ax.plot(d, stars, color=ACCENT, linewidth=2.6, marker="o", markersize=5.5,
        markerfacecolor=PAPER, markeredgecolor=ACCENT, markeredgewidth=2, zorder=3)

ax.annotate("42,878", xy=(d[0], stars[0]), xytext=(6, -22), textcoords="offset points",
            fontsize=9.5, color=INK, fontweight="600")
ax.annotate("151,317", xy=(d[3], stars[3]), xytext=(14, -24), textcoords="offset points",
            ha="left", fontsize=9.5, color=INK, fontweight="600")
ax.annotate("326,825", xy=(d[-1], stars[-1]), xytext=(-12, 18), textcoords="offset points",
            ha="right", fontsize=9.5, color=INK, fontweight="600")

ax.text(d[0] + (d[-1]-d[0])*0.03, 305000,
        "10 天增加約 284,000 stars\n單週 +229,268（GitHub Trending #1）",
        fontsize=10, color=INK, va="top", linespacing=1.5,
        bbox=dict(boxstyle="round,pad=0.55", facecolor="#F9FAFB", edgecolor=GRID, linewidth=1))

ax.set_ylim(0, 360000)
ax.set_xlim(d[0], d[-1] + timedelta(hours=14))
ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{int(x/1000)}k" if x else "0"))
ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
ax.grid(axis="y", color=GRID, linewidth=1)
ax.set_axisbelow(True)
for spine in ["top", "right", "left"]:
    ax.spines[spine].set_visible(False)
ax.spines["bottom"].set_color("#D1D5DB")
ax.tick_params(axis="both", colors=MUTED, labelsize=9, length=0)
ax.set_ylabel("GitHub stars", color=MUTED, fontsize=9.5, labelpad=8)
ax.set_title("REA 的 GitHub Stars 成長曲線", loc="left", fontsize=15,
             color=INK, fontweight="700", pad=16)
fig.text(0.012, 0.018,
         "資料來源：githubtrending.today 每日 07:00 UTC 讀數；10/19 13:48 UTC GitHub API 回報 331,637。",
         fontsize=7.2, color=MUTED)
fig.subplots_adjust(left=0.085, right=0.975, top=0.83, bottom=0.17)
out = OUT_DIR / "01_star_growth.webp"
save_figure_webp(fig, out, facecolor=PAPER)
plt.close(fig)
print(out)

fig, axes = plt.subplots(1, 2, figsize=(8, 4.2), dpi=200)
fig.patch.set_facecolor(PAPER)
labels = ["compact profile", "完整 schema"]
kb = [290, 496]
tok = [68, 120]
colors = ["#C7D2FE", ACCENT]
y = [0, 1]

for ax, vals, unit, title, maxv in [
    (axes[0], kb, " KB", "Schema 大小（KB）", 580),
    (axes[1], tok, "k", "估算 tokens（k）", 150),
]:
    ax.set_facecolor(PAPER)
    bars = ax.barh(y, vals, height=0.52, color=colors, edgecolor="none", zorder=3)
    for b, v in zip(bars, vals):
        ax.text(v + maxv*0.022, b.get_y() + b.get_height()/2, f"{v:,}{unit}",
                va="center", ha="left", fontsize=10.5, color=INK, fontweight="600")
    ax.set_xlim(0, maxv)
    ax.set_ylim(-0.55, 1.55)
    ax.set_title(title, loc="left", fontsize=10.5, color=INK, fontweight="600", pad=10)
    ax.grid(axis="x", color=GRID, linewidth=1)
    ax.set_axisbelow(True)
    for spine in ["top", "right", "left", "bottom"]:
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="both", colors=MUTED, labelsize=8.5, length=0)

axes[0].set_yticks(y)
axes[0].set_yticklabels(labels, fontsize=9.5, color=INK)
axes[1].set_yticks([])

fig.suptitle("172 個工具的 schema 成本", x=0.012, ha="left", fontsize=15,
             color=INK, fontweight="700", y=0.975)
fig.text(0.012, 0.895,
         "Claude Code 關閉 tool search 時，每次請求都要帶上完整工具定義。",
         fontsize=9, color=MUTED)
fig.text(0.012, 0.018,
         "資料來源：REA docs/client-configuration.md（main @ 04089d5be，172 tools）。",
         fontsize=7.2, color=MUTED)
fig.subplots_adjust(left=0.16, right=0.965, top=0.78, bottom=0.17, wspace=0.28)
out = OUT_DIR / "05_schema_payload.webp"
save_figure_webp(fig, out, facecolor=PAPER)
plt.close(fig)
print(out)

# --- 04_timeout_budget -------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 4.5), dpi=200)
fig.patch.set_facecolor(PAPER)
ax.set_facecolor(PAPER)

budget_labels = [
    "客戶端 SDK 預設",
    "Hopper 冷啟動上限",
    "Ghidra 冷啟動上限",
    "可調高的 Ghidra 上限",
]
budget_values = [60, 120, 330, 360]
budget_colors = [MUTED, "#C7D2FE", ACCENT, "#A5B4FC"]
budget_y = [3, 2, 1, 0]

bars = ax.barh(budget_y, budget_values, height=0.5, color=budget_colors,
               edgecolor="none", zorder=3)
for b, v in zip(bars, budget_values):
    ax.text(v + 6, b.get_y() + b.get_height() / 2, f"{v}s",
            va="center", ha="left", fontsize=10.5, color=INK, fontweight="600")

ax.axvline(60, color=INK, linestyle=(0, (4, 3)), linewidth=1.2, zorder=4)
ax.text(60, 3.62, "  客戶端在這裡放棄", fontsize=9, color=INK, va="bottom", ha="left")

ax.set_yticks(budget_y)
ax.set_yticklabels(budget_labels, fontsize=9.5, color=INK)
ax.set_xlim(0, 400)
ax.set_ylim(-0.6, 3.75)
ax.set_xlabel("秒", color=MUTED, fontsize=9.5, labelpad=6)
ax.grid(axis="x", color=GRID, linewidth=1)
ax.set_axisbelow(True)
for spine in ["top", "right", "left", "bottom"]:
    ax.spines[spine].set_visible(False)
ax.tick_params(axis="both", colors=MUTED, labelsize=9, length=0)

ax.set_title("同一個請求，兩個計時器", loc="left", fontsize=15,
             color=INK, fontweight="700", pad=26)
fig.text(0.012, 0.845,
         "引擎還在匯入與自動分析，客戶端就已經把請求砍了。",
         fontsize=9.2, color=MUTED)
fig.text(0.012, 0.018,
         "資料來源：REA docs/client-configuration.md 與 docs/installation.md；360s 為文件示例的 REA_GHIDRA_STARTUP_TIMEOUT_MS。",
         fontsize=7.2, color=MUTED)
fig.subplots_adjust(left=0.20, right=0.975, top=0.80, bottom=0.16)
out = OUT_DIR / "04_timeout_budget.webp"
save_figure_webp(fig, out, facecolor=PAPER)
plt.close(fig)
print(out)

# --- 03_authority_matrix ----------------------------------------------------
rows = [
    "shipped-artifact\n出貨產物",
    "controlled-replay\n受控重播",
    "live-observation\n實際觀察",
    "external\n外部服務",
]
cols = [
    "shipped-\nartifact",
    "controlled-\nreplay",
    "external-\nservice",
    "inference\n（推論）",
]
# ● 可核銷（同級或更高的可比權威）、○ 不可核銷
grid = [
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
]

fig, ax = plt.subplots(figsize=(8, 4.5), dpi=200)
fig.patch.set_facecolor(PAPER)
ax.set_facecolor(PAPER)

for i, row in enumerate(grid):
    for j, ok in enumerate(row):
        face = ACCENT_LIGHT if ok else "#F9FAFB"
        ax.add_patch(plt.Rectangle((j, i), 1, 1, facecolor=face,
                                   edgecolor=PAPER, linewidth=3))
        ax.text(j + 0.5, i + 0.5, "●" if ok else "○",
                ha="center", va="center", fontsize=19,
                color=ACCENT if ok else "#9CA3AF")

ax.set_xlim(0, len(cols))
ax.set_ylim(0, len(rows))
ax.invert_yaxis()
ax.set_xticks([j + 0.5 for j in range(len(cols))])
ax.set_xticklabels(cols, fontsize=9, color=INK)
ax.set_yticks([i + 0.5 for i in range(len(rows))])
ax.set_yticklabels(rows, fontsize=9, color=INK)
ax.xaxis.tick_top()
ax.tick_params(axis="both", length=0)
for spine in ax.spines.values():
    spine.set_visible(False)

fig.suptitle("權威可比性：哪種證據能核銷哪種主張", x=0.012, ha="left",
             fontsize=15, color=INK, fontweight="700", y=0.975)
fig.text(0.012, 0.885,
         "● 可比，可關閉該筆項目；○ 權威不足，維持未關閉。推論永遠不能升格為觀察。",
         fontsize=9.2, color=MUTED)
fig.text(0.012, 0.018,
         "資料來源：docs/reconstruction-coverage.md、docs/reconstruction-obligation-ledgers.md。此為依文件描述整理的概念示意，非官方等級表。",
         fontsize=7.2, color=MUTED)
fig.subplots_adjust(left=0.20, right=0.975, top=0.755, bottom=0.14)
out = OUT_DIR / "03_authority_matrix.webp"
save_figure_webp(fig, out, facecolor=PAPER)
plt.close(fig)
print(out)

# --- 06_dxball_verification -------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(8, 4.5), dpi=200,
                         gridspec_kw={"width_ratios": [2.15, 1.0]})
fig.patch.set_facecolor(PAPER)

scales = ["1.0x", "1.5x", "2.0x", "2.5x", "3.0x"]
y = list(range(len(scales)))

ax = axes[0]
ax.set_facecolor(PAPER)
ax.barh(y, [641] * len(scales), height=0.5, color=GRID, edgecolor="none", zorder=2)
ax.barh(y, [641] * len(scales), height=0.5, color=ACCENT, edgecolor="none", zorder=3)
ax.set_yticks(y)
ax.set_yticklabels(scales, fontsize=9, color=INK)
ax.set_xlim(0, 760)
ax.set_ylim(-0.6, len(scales) - 0.4)
ax.set_xlabel("位置 0–640，每個尺度 641 個案例（灰色為上限，實心為通過）",
              color=MUTED, fontsize=8.2, labelpad=6)
ax.grid(axis="x", color=GRID, linewidth=1)
ax.set_axisbelow(True)
for spine in ["top", "right", "left", "bottom"]:
    ax.spines[spine].set_visible(False)
ax.tick_params(axis="both", colors=MUTED, labelsize=8.5, length=0)
ax.set_title("行為等價：3,205 / 3,205 通過，0 失敗", loc="left", fontsize=10.5,
             color=INK, fontweight="600", pad=10)

ax = axes[1]
ax.set_facecolor(PAPER)
ax.barh([1], [63], height=0.5, color="#C7D2FE", edgecolor="none", zorder=3)
ax.barh([0], [63], height=0.5, color=ACCENT, edgecolor="none", zorder=3)
for yy in (1, 0):
    ax.text(65, yy, "63 B", va="center", ha="left", fontsize=9.5,
            color=INK, fontweight="600")
ax.set_yticks([1, 0])
ax.set_yticklabels(["原始", "重建"], fontsize=9, color=INK)
ax.set_xlim(0, 86)
ax.set_ylim(-0.65, 1.65)
ax.set_xlabel("函式長度（bytes）", color=MUTED, fontsize=8.5, labelpad=6)
ax.grid(axis="x", color=GRID, linewidth=1)
ax.set_axisbelow(True)
for spine in ["top", "right", "left", "bottom"]:
    ax.spines[spine].set_visible(False)
ax.tick_params(axis="both", colors=MUTED, labelsize=8.5, length=0)
ax.set_title("位元組等價：63 / 63", loc="left", fontsize=10.5,
             color=INK, fontweight="600", pad=10)

fig.suptitle("驗證強度：從「看起來像」到「逐位元組全等」", x=0.012, ha="left",
             fontsize=15, color=INK, fontweight="700", y=0.975)
fig.text(0.012, 0.885,
         "DX-Ball 的左右聲道平移函式：0x406400–0x40643e，23 條指令。",
         fontsize=9.2, color=MUTED)
fig.text(0.012, 0.018,
         "資料來源：https://rea.tools/showcase/dx-ball/（數字綁定該案例記錄的版本）。",
         fontsize=7.2, color=MUTED)
fig.subplots_adjust(left=0.065, right=0.965, top=0.77, bottom=0.19, wspace=0.30)
out = OUT_DIR / "06_dxball_verification.webp"
save_figure_webp(fig, out, facecolor=PAPER)
plt.close(fig)
print(out)
