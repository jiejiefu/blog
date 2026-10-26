"""Generate the figures and cover used in the Jev post.

Usage:
    /Users/jiejiefu/Documents/Visual_Studio_Code/.venv/bin/python \
        scripts/jev-system-one-decision-model/make_jev_figures.py

Writes six 1600px-wide WebP figures and one 1200px JPEG cover directly into
the post's page bundle. PNG intermediates stay in a temporary directory.
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from image_utils import save_figure_webp, svg_to_jpeg

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "content/zh-tw/posts/jev-system-one-decision-model/images"
COVER_SVG = Path(__file__).resolve().with_name("jev_system_one_models.svg")

plt.rcParams["font.sans-serif"] = ["PingFang TC", "Arial Unicode MS", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False

INK = "#111827"
MUTED = "#6B7280"
GRID = "#E5E7EB"
ACCENT = "#0E9F6E"
ACCENT_LIGHT = "#E6F7F0"
PAPER = "#FFFFFF"


def source(fig, text):
    fig.text(0.012, 0.018, text, fontsize=7.2, color=MUTED)


# --- 01_latency_cost --------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(8, 4.5), dpi=200)
fig.patch.set_facecolor(PAPER)

panels = [
    {
        "ax": axes[0],
        "title": "端到端延遲",
        "xlim": (0.05, 500),
        "rows": [
            ("Jev", 0.07, 0.5, ACCENT),
            ("前沿 LLM", 3, 329, "#9CA3AF"),
        ],
        "unit": "秒（log scale）",
    },
    {
        "ax": axes[1],
        "title": "輸入價格",
        "xlim": (0.03, 15),
        "rows": [
            ("Jev", 0.042, 0.042, ACCENT),
            ("前沿 LLM", 0.20, 10, "#9CA3AF"),
        ],
        "unit": "美元 / 百萬 input tokens（log scale）",
    },
]

for panel in panels:
    ax = panel["ax"]
    ax.set_facecolor(PAPER)
    ax.set_xscale("log")
    ax.set_xlim(*panel["xlim"])
    ax.set_ylim(-0.65, 1.65)
    ax.grid(axis="x", color=GRID, linewidth=1)
    ax.set_axisbelow(True)
    for spine in ["top", "right", "left", "bottom"]:
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="both", colors=MUTED, labelsize=8.5, length=0)

    for i, (label, lo, hi, color) in enumerate(panel["rows"]):
        y = 1 - i
        if lo == hi:
            ax.plot([lo], [y], marker="v", markersize=9, color=color, zorder=4)
            ax.text(lo, y + 0.24, f"{lo:g}", va="bottom", ha="center",
                    fontsize=10.5, color=INK, fontweight="600")
        else:
            ax.hlines(y, lo, hi, color=color, linewidth=17, zorder=3,
                      alpha=0.95 if color == ACCENT else 0.65)
            ax.text(lo, y + 0.23, f"{lo:g}", va="bottom", ha="center",
                    fontsize=9.5, color=INK, fontweight="600")
            ax.text(hi, y + 0.23, f"{hi:g}", va="bottom", ha="center",
                    fontsize=9.5, color=INK, fontweight="600")

    ax.set_yticks([1, 0])
    ax.set_yticklabels([row[0] for row in panel["rows"]], fontsize=9.5, color=INK)
    ax.set_title(panel["title"], loc="left", fontsize=11, color=INK,
                 fontweight="700", pad=10)
    ax.set_xlabel(panel["unit"], color=MUTED, fontsize=8.2, labelpad=6)

fig.suptitle("兩個數量級的差距", x=0.012, ha="left", fontsize=16,
             color=INK, fontweight="700", y=0.975)
fig.text(0.012, 0.895,
         "同一個決策，不需要等模型把字一個一個寫完。",
         fontsize=9.4, color=MUTED)
source(fig, "資料來源：TypeSafe AI 官方 blog（2026-09-15）、首頁；LLM 延遲為其引用之 benchmark，"
            "價格為前沿模型常見區間。")
fig.subplots_adjust(left=0.11, right=0.965, top=0.76, bottom=0.18, wspace=0.30)

out = OUT_DIR / "01_latency_cost.webp"
save_figure_webp(fig, out, facecolor=PAPER)
plt.close(fig)
print(out)


# --- 02_confidence_distribution --------------------------------------------
fig, axes = plt.subplots(
    1, 2, figsize=(8, 4.5), dpi=200,
    gridspec_kw={"width_ratios": [1.75, 1.0]},
)
fig.patch.set_facecolor(PAPER)

rows = [
    ("清楚答案", [0.88, 0.08, 0.04], 0.82),
    ("官方範例", [0.61, 0.35, 0.04], 0.42),
    ("幾乎平手", [0.34, 0.33, 0.33], 0.01),
]
option_colors = [ACCENT, "#A7B0AA", GRID]
option_names = ["returns", "billing", "shipping"]

ax = axes[0]
ax.set_facecolor(PAPER)
y_positions = [2, 1, 0]
for y, (label, probs, _) in zip(y_positions, rows):
    left = 0.0
    for prob, color, name in zip(probs, option_colors, option_names):
        ax.barh(y, prob, left=left, height=0.46, color=color,
                edgecolor=PAPER, linewidth=2, zorder=3)
        if prob >= 0.12:
            ax.text(left + prob / 2, y, f"{prob:.2f}", ha="center",
                    va="center", fontsize=9,
                    color=PAPER if color in (ACCENT, "#A7B0AA") else INK,
                    fontweight="600")
        left += prob

ax.set_xlim(0, 1)
ax.set_ylim(-0.62, 2.62)
ax.set_yticks(y_positions)
ax.set_yticklabels([row[0] for row in rows], fontsize=9.5, color=INK)
ax.set_xlabel("三個選項的機率分布", color=MUTED, fontsize=8.5, labelpad=6)
ax.grid(axis="x", color=GRID, linewidth=1)
ax.set_axisbelow(True)
for spine in ["top", "right", "left", "bottom"]:
    ax.spines[spine].set_visible(False)
ax.tick_params(axis="both", colors=MUTED, labelsize=8.5, length=0)
ax.set_title("答案的形狀", loc="left", fontsize=10.5, color=INK,
             fontweight="700", pad=10)

ax = axes[1]
ax.set_facecolor(PAPER)
ax.set_xlim(0, 1)
ax.set_ylim(-0.62, 2.62)
ax.add_patch(Rectangle((0, -0.62), 0.5, 3.24, color="#FEE2E2", zorder=1))
ax.add_patch(Rectangle((0.5, -0.62), 0.4, 3.24, color="#FEF3C7", zorder=1))
ax.add_patch(Rectangle((0.9, -0.62), 0.1, 3.24, color="#DCFCE7", zorder=1))
for y, (_, _, conf) in zip(y_positions, rows):
    ax.barh(y, conf, height=0.30, color=INK, zorder=3)
    ax.text(conf + 0.03 if conf < 0.88 else conf - 0.03, y,
            f"{conf:.2f}", va="center",
            ha="left" if conf < 0.88 else "right",
            fontsize=9.5, color=INK, fontweight="700")
ax.axvline(0.5, color="#B45309", linewidth=1, linestyle=(0, (4, 3)), zorder=4)
ax.axvline(0.9, color="#15803D", linewidth=1, linestyle=(0, (4, 3)), zorder=4)
ax.set_yticks(y_positions)
ax.set_yticklabels([])
ax.set_xlabel("confidence（0–1）", color=MUTED, fontsize=8.5, labelpad=6)
ax.set_xticks([0, 0.5, 0.9, 1])
ax.set_xticklabels(["0", "0.5", "0.9", "1"], fontsize=8)
for spine in ["top", "right", "left", "bottom"]:
    ax.spines[spine].set_visible(False)
ax.tick_params(axis="both", colors=MUTED, labelsize=8.5, length=0)
ax.set_title("程式怎麼讀", loc="left", fontsize=10.5, color=INK,
             fontweight="700", pad=10)

fig.suptitle("Choice 的 confidence 是分布的形狀，不是裝飾", x=0.012, ha="left",
             fontsize=16, color=INK, fontweight="700", y=0.975)
fig.text(0.012, 0.895,
         "以 Choice 為例：機率越集中，程式越敢自動往下走。",
         fontsize=9.4, color=MUTED)
source(fig, "資料來源：TypeSafe docs/confidence.md；第一、三列為示意，第二列為官方 Choice 範例。")
fig.subplots_adjust(left=0.12, right=0.965, top=0.75, bottom=0.18, wspace=0.08)

out = OUT_DIR / "02_confidence_distribution.webp"
save_figure_webp(fig, out, facecolor=PAPER)
plt.close(fig)
print(out)


# --- 03_parallel_batching ---------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 4.5), dpi=200)
fig.patch.set_facecolor(PAPER)
ax.set_facecolor(PAPER)

categories = ["成本", "延遲"]
separate = [12.2, 10.0]
batched = [1.0, 1.0]
x = [0, 1]
width = 0.30

bars1 = ax.bar([v - width / 2 for v in x], separate, width,
               color="#A7B0AA", edgecolor="none", zorder=3, label="逐題送出")
bars2 = ax.bar([v + width / 2 for v in x], batched, width,
               color=ACCENT, edgecolor="none", zorder=3, label="一次送出 13 題")

for bars, values in ((bars1, separate), (bars2, batched)):
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.25,
                f"{value:.1f}x", ha="center", va="bottom",
                fontsize=10.5, color=INK, fontweight="700")

ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=10.5, color=INK)
ax.set_ylim(0, 14.5)
ax.set_ylabel("相對倍數", color=MUTED, fontsize=9, labelpad=8)
ax.grid(axis="y", color=GRID, linewidth=1)
ax.set_axisbelow(True)
for spine in ["top", "right", "left", "bottom"]:
    ax.spines[spine].set_visible(False)
ax.tick_params(axis="both", colors=MUTED, labelsize=9, length=0)
ax.legend(frameon=False, fontsize=9, loc="upper right", ncol=2,
          bbox_to_anchor=(1.0, 1.02))
fig.suptitle("把 13 個問題塞進同一次請求", x=0.012, ha="left",
             fontsize=16, color=INK, fontweight="700", y=0.975)
fig.text(0.012, 0.895,
         "文件只付一次、只傳一次；答案與逐題送出相同。",
         fontsize=9.4, color=MUTED)
source(fig, "資料來源：TypeSafe docs/cookbooks/parallel_questions.md；"
            "GDPR 文章 53,777 字元，13 題，5 次重複，回答無變化。")
fig.subplots_adjust(left=0.10, right=0.965, top=0.75, bottom=0.17)

out = OUT_DIR / "03_parallel_batching.webp"
save_figure_webp(fig, out, facecolor=PAPER)
plt.close(fig)
print(out)


# --- 04_score_normalization -------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 4.5), dpi=200)
fig.patch.set_facecolor(PAPER)
ax.set_facecolor(PAPER)

candidates = [
    {"name": "A", "raw": 2.0, "norm": 0.500, "color": ACCENT},
    {"name": "B", "raw": 2.9, "norm": 0.483, "color": "#A7B0AA"},
]
raw_rank = {
    c["name"]: i + 1
    for i, c in enumerate(sorted(candidates, key=lambda c: c["raw"], reverse=True))
}
norm_rank = {
    c["name"]: i + 1
    for i, c in enumerate(sorted(candidates, key=lambda c: c["norm"], reverse=True))
}

x_left, x_right = 0.0, 1.0
ax.set_xlim(-0.38, 1.38)
ax.set_ylim(2.60, 0.40)
ax.set_xticks([x_left, x_right])
ax.set_xticklabels(["原始總分", "歸一化平均（0–1）"], fontsize=10.5, color=INK)
ax.set_yticks([1, 2])
ax.set_yticklabels(["較差", "較好"], fontsize=8.5, color=MUTED)
ax.grid(axis="y", color=GRID, linewidth=1)
ax.set_axisbelow(True)
for spine in ["top", "right", "left", "bottom"]:
    ax.spines[spine].set_visible(False)
ax.tick_params(axis="both", colors=MUTED, labelsize=9, length=0)

for x in (x_left, x_right):
    ax.axvline(x, color=GRID, linewidth=1, zorder=1)

for c in candidates:
    y0 = raw_rank[c["name"]]
    y1 = norm_rank[c["name"]]
    ax.plot([x_left, x_right], [y0, y1], color=c["color"], linewidth=3.2,
            marker="o", markersize=11, markeredgecolor=PAPER,
            markeredgewidth=2, zorder=4)
    ax.text(x_left - 0.06, y0, f'{c["name"]}  {c["raw"]:.2f}',
            ha="right", va="center", fontsize=10.5, color=INK,
            fontweight="700", zorder=5)
    ax.text(x_right + 0.06, y1, f'{c["name"]}  {c["norm"]:.3f}',
            ha="left", va="center", fontsize=10.5, color=INK,
            fontweight="700", zorder=5)

ax.scatter([0.5], [1.5], s=180, facecolors="none", edgecolors=ACCENT,
           linewidths=1.6, zorder=5)
ax.annotate("排名翻轉", xy=(0.5, 1.5), xytext=(0.5, 0.66),
            ha="center", va="center", fontsize=10, color=ACCENT,
            fontweight="700",
            arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=1.4,
                            shrinkA=0, shrinkB=9))

fig.suptitle("先歸一化，排名就反了", x=0.012, ha="left", fontsize=16,
             color=INK, fontweight="700", y=0.975)
fig.text(0.012, 0.895,
         "同一組分數，只改變計分方式，領先者就換人。",
         fontsize=9.4, color=MUTED)
fig.text(0.012, 0.125,
         "A：風險 2/2 · 工作量 0/3    B：風險 0/2 · 工作量 2.9/3（權重各 0.5）",
         fontsize=7.6, color=MUTED)
source(fig, "示意：A、B 為假想候選；風險為 3 級（0–2）、工作量為 4 級（0–3）。")
fig.subplots_adjust(left=0.13, right=0.88, top=0.76, bottom=0.24)

out = OUT_DIR / "04_score_normalization.webp"
save_figure_webp(fig, out, facecolor=PAPER)
plt.close(fig)
print(out)


# --- 05_type_safe_vs_truth_safe ---------------------------------------------
fig, ax = plt.subplots(figsize=(8, 4.5), dpi=200)
fig.patch.set_facecolor(PAPER)
ax.set_facecolor(PAPER)
ax.set_xlim(0, 2)
ax.set_ylim(0, 2)
ax.axis("off")

ax.add_patch(Rectangle((0, 0), 1, 1, facecolor="#FEE2E2", edgecolor="none", zorder=0))
ax.add_patch(Rectangle((1, 0), 1, 1, facecolor="#FEF3C7", edgecolor="none", zorder=0))
ax.add_patch(Rectangle((0, 1), 1, 1, facecolor="#E0E7FF", edgecolor="none", zorder=0))
ax.add_patch(Rectangle((1, 1), 1, 1, facecolor="#DCFCE7", edgecolor="none", zorder=0))

ax.axvline(1, color=PAPER, linewidth=4, zorder=2)
ax.axhline(1, color=PAPER, linewidth=4, zorder=2)

quads = [
    (0.5, 0.5, "又錯又不合法", "最差", "#991B1B"),
    (1.5, 0.5, "合法但錯", "Jev 的失敗模式", "#92400E"),
    (0.5, 1.5, "對但不合法", "LLM 的失敗模式", "#1E3A8A"),
    (1.5, 1.5, "合法且正確", "理想", "#166534"),
]
for x, y, title, sub, color in quads:
    ax.text(x, y + 0.14, title, ha="center", va="center",
            fontsize=12, color=INK, fontweight="700", zorder=3)
    ax.text(x, y - 0.14, sub, ha="center", va="center",
            fontsize=9.2, color=color, fontweight="600", zorder=3)

ax.text(0.5, -0.15, "不合法", ha="center", va="top", fontsize=9, color=MUTED)
ax.text(1.5, -0.15, "合法", ha="center", va="top", fontsize=9, color=MUTED)
ax.text(1.0, -0.31, "輸出格式／型別", ha="center", va="top",
        fontsize=10, color=INK, fontweight="600")
ax.text(-0.10, 0.5, "錯誤", ha="right", va="center", fontsize=9, color=MUTED)
ax.text(-0.10, 1.5, "正確", ha="right", va="center", fontsize=9, color=MUTED)
ax.text(-0.24, 1.0, "答案語意", ha="center", va="center", rotation=90,
        fontsize=10, color=INK, fontweight="600")

fig.suptitle("type-safe 只保證右半邊", x=0.012, ha="left", fontsize=16,
             color=INK, fontweight="700", y=0.975)
fig.text(0.012, 0.895,
         "Jev 把失敗模式移到右下：格式可控，語意仍可能錯。",
         fontsize=9.4, color=MUTED)
fig.text(0.012, 0.105,
         "四格是常見失敗模式，不是互斥分類。",
         fontsize=7.6, color=MUTED)
source(fig, "概念示意；非 TypeSafe 官方分類。")
fig.subplots_adjust(left=0.16, right=0.95, top=0.78, bottom=0.25)

out = OUT_DIR / "05_type_safe_vs_truth_safe.webp"
save_figure_webp(fig, out, facecolor=PAPER)
plt.close(fig)
print(out)


# --- 06_decision_boundary ---------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 4.5), dpi=200)
fig.patch.set_facecolor(PAPER)
ax.set_facecolor(PAPER)
ax.set_xlim(0, 2)
ax.set_ylim(0, 2)
ax.axis("off")

ax.add_patch(Rectangle((0, 0), 1, 1, facecolor=ACCENT_LIGHT, edgecolor="none", zorder=0))
ax.add_patch(Rectangle((0, 1), 1, 1, facecolor="#F0FDF4", edgecolor="none", zorder=0))
ax.add_patch(Rectangle((1, 0), 1, 1, facecolor="#F3F4F6", edgecolor="none", zorder=0))
ax.add_patch(Rectangle((1, 1), 1, 1, facecolor="#E5E7EB", edgecolor="none", zorder=0))

ax.axvline(1, color=PAPER, linewidth=4, zorder=2)
ax.axhline(1, color=PAPER, linewidth=4, zorder=2)

ax.text(0.5, 1.92, "Jev 的主場", ha="center", va="center",
        fontsize=9, color=ACCENT, fontweight="700", zorder=3)
ax.text(1.5, 1.92, "LLM 的主場", ha="center", va="center",
        fontsize=9, color=MUTED, fontweight="700", zorder=3)

quads = [
    (0.5, 0.5, "Jev（單步）", "封閉答案、語意判斷", "#065F46"),
    (0.5, 1.5, "Workflow + Jev", "多步，但每步封閉", "#065F46"),
    (1.5, 0.5, "單次 LLM", "單步、開放生成", "#4B5563"),
    (1.5, 1.5, "Agent / reasoning LLM", "多步、開放生成", "#374151"),
]
for x, y, title, sub, color in quads:
    ax.text(x, y + 0.13, title, ha="center", va="center",
            fontsize=11.5, color=INK, fontweight="700", zorder=3)
    ax.text(x, y - 0.14, sub, ha="center", va="center",
            fontsize=9.2, color=color, fontweight="600", zorder=3)

ax.text(0.5, -0.15, "可列舉", ha="center", va="top", fontsize=9, color=MUTED)
ax.text(1.5, -0.15, "開放生成", ha="center", va="top", fontsize=9, color=MUTED)
ax.text(1.0, -0.31, "答案空間", ha="center", va="top",
        fontsize=10, color=INK, fontweight="600")
ax.text(-0.10, 0.5, "單步", ha="right", va="center", fontsize=9, color=MUTED)
ax.text(-0.10, 1.5, "多步", ha="right", va="center", fontsize=9, color=MUTED)
ax.text(-0.24, 1.0, "任務形狀", ha="center", va="center", rotation=90,
        fontsize=10, color=INK, fontweight="600")

fig.suptitle("Jev 在封閉答案那一側", x=0.012, ha="left", fontsize=16,
             color=INK, fontweight="700", y=0.975)
fig.text(0.012, 0.895,
         "它不是 agent；它是 workflow 裡每個決策點的一顆 if。",
         fontsize=9.4, color=MUTED)
fig.text(0.012, 0.105,
         "判斷順序：先看答案能不能列舉，再看需不需要多步推理。",
         fontsize=7.6, color=MUTED)
source(fig, "概念示意；非 TypeSafe 官方 positioning。")
fig.subplots_adjust(left=0.16, right=0.95, top=0.78, bottom=0.25)

out = OUT_DIR / "06_decision_boundary.webp"
save_figure_webp(fig, out, facecolor=PAPER)
plt.close(fig)
print(out)


# --- cover.jpg --------------------------------------------------------------
out = OUT_DIR / "cover.jpg"
svg_to_jpeg(COVER_SVG, out, width=1200, quality=85)
print(out)
