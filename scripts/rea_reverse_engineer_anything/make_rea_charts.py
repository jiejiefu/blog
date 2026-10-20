"""Generate the two charts used in the REA post.

Usage:
    python3 scripts/rea_reverse_engineer_anything/make_rea_charts.py

Writes 1600x900 and 1600x840 WebP files directly into the post's page
bundle. The PNG intermediates stay in a temporary directory and are never
published.
"""

import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from image_utils import save_figure_webp

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "content/zh-tw/posts/rea_reverse_engineer_anything/images"

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
out = OUT_DIR / "02_schema_payload.webp"
save_figure_webp(fig, out, facecolor=PAPER)
plt.close(fig)
print(out)
