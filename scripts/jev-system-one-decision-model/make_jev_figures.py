"""Generate the figures and cover used in the Jev post.

Usage (run from the repo root):
    ../.venv/bin/python scripts/jev-system-one-decision-model/make_jev_figures.py

Writes six 1600px-wide WebP figures and one 1200px JPEG cover directly into
the post's page bundle. PNG intermediates stay in a temporary directory.
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Patch, Rectangle

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

FS_TITLE = 18
FS_SUB = 12
FS_PANEL = 13.5
FS_AXIS = 12
FS_DATA = 12.5
FS_LEGEND = 11.5
FS_NOTE = 9.5
FS_SOURCE = 9


def source(fig, text):
    fig.text(0.012, 0.018, text, fontsize=FS_SOURCE, color=MUTED)


def title_block(fig, title, subtitle):
    fig.suptitle(title, x=0.012, ha="left", fontsize=FS_TITLE,
                 color=INK, fontweight="700", y=0.98)
    fig.text(0.012, 0.87, subtitle, fontsize=FS_SUB, color=MUTED)


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
        "ratio": "同端點相比 43–658×",
        "note": None,
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
        "ratio": "同端點相比 5–238×",
        "note": "$42 / 十億 tokens；output 免費",
    },
]

for panel in panels:
    ax = panel["ax"]
    ax.set_facecolor(PAPER)
    ax.set_xscale("log")
    ax.set_xlim(*panel["xlim"])
    ax.set_ylim(-0.55, 1.75)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax.grid(axis="x", color=GRID, linewidth=1)
    ax.set_axisbelow(True)
    for spine in ["top", "right", "left", "bottom"]:
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="both", colors=MUTED, labelsize=FS_AXIS, length=0)

    ax.text(0.98, 0.97, panel["ratio"], transform=ax.transAxes,
            ha="right", va="top", fontsize=FS_NOTE + 1.5, color=ACCENT,
            fontweight="700")

    for i, (label, lo, hi, color) in enumerate(panel["rows"]):
        y = 1 - i
        if lo == hi:
            ax.plot([lo], [y], marker="v", markersize=11, color=color, zorder=4)
            ax.text(lo, y + 0.24, f"{lo:g}", va="bottom", ha="center",
                    fontsize=FS_DATA, color=INK, fontweight="600")
        else:
            ax.hlines(y, lo, hi, color=color, linewidth=17, zorder=3,
                      alpha=0.95 if color == ACCENT else 0.65)
            ax.text(lo, y + 0.23, f"{lo:g}", va="bottom", ha="center",
                    fontsize=FS_DATA, color=INK, fontweight="600")
            ax.text(hi, y + 0.23, f"{hi:g}", va="bottom", ha="center",
                    fontsize=FS_DATA, color=INK, fontweight="600")

        if i == 0 and panel["note"]:
            ax.text(0.055, y - 0.34, panel["note"], ha="left", va="top",
                    fontsize=FS_NOTE, color=MUTED)

    ax.set_yticks([1, 0])
    ax.set_yticklabels([row[0] for row in panel["rows"]],
                       fontsize=FS_AXIS, color=INK)
    ax.set_title(panel["title"], loc="left", fontsize=FS_PANEL, color=INK,
                 fontweight="700", pad=10)
    ax.set_xlabel(panel["unit"], color=MUTED, fontsize=FS_NOTE + 1, labelpad=8)

title_block(
    fig,
    "兩個數量級的差距",
    "同一個決策，不需要等模型把字一個一個寫完。",
)
source(fig, "資料來源：TypeSafe AI 官方 blog（2026-09-15）、首頁；LLM 延遲為其引用之 benchmark，"
            "價格為前沿模型常見區間。")
fig.subplots_adjust(left=0.11, right=0.965, top=0.76, bottom=0.18, wspace=0.32)

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
option_colors = [ACCENT, "#A7B0AA", "#CBD5D1"]
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
                    va="center", fontsize=FS_DATA,
                    color=PAPER if color in (ACCENT, "#A7B0AA") else INK,
                    fontweight="600")
        left += prob

ax.set_xlim(0, 1)
ax.set_ylim(-0.62, 2.62)
ax.set_yticks(y_positions)
ax.set_yticklabels([row[0] for row in rows], fontsize=FS_DATA, color=INK)
ax.set_xlabel("三個選項的機率分布", color=MUTED, fontsize=FS_AXIS, labelpad=8)
ax.grid(axis="x", color=GRID, linewidth=1)
ax.set_axisbelow(True)
for spine in ["top", "right", "left", "bottom"]:
    ax.spines[spine].set_visible(False)
ax.tick_params(axis="both", colors=MUTED, labelsize=FS_AXIS, length=0)
ax.set_title("答案的形狀", loc="left", fontsize=FS_PANEL, color=INK,
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
    inside = conf >= 0.7
    ax.text(conf - 0.035 if inside else conf + 0.03, y,
            f"{conf:.2f}", va="center",
            ha="right" if inside else "left",
            fontsize=FS_DATA,
            color=PAPER if inside else INK, fontweight="700")
ax.text(0.25, 2.45, "低", ha="center", va="center",
        fontsize=FS_LEGEND, color=MUTED, fontweight="700")
ax.text(0.70, 2.45, "中", ha="center", va="center",
        fontsize=FS_LEGEND, color=MUTED, fontweight="700")
ax.text(0.95, 2.45, "高", ha="center", va="center",
        fontsize=FS_LEGEND, color=MUTED, fontweight="700")
ax.axvline(0.5, color="#B45309", linewidth=1, linestyle=(0, (4, 3)), zorder=4)
ax.axvline(0.9, color="#15803D", linewidth=1, linestyle=(0, (4, 3)), zorder=4)
ax.set_yticks(y_positions)
ax.set_yticklabels([])
ax.set_xlabel("confidence（0–1）", color=MUTED,
              fontsize=FS_AXIS, labelpad=8)
ax.set_xticks([0, 0.5, 0.9])
ax.set_xticklabels(["0", "0.5", "0.9"], fontsize=FS_AXIS)
for spine in ["top", "right", "left", "bottom"]:
    ax.spines[spine].set_visible(False)
ax.tick_params(axis="both", colors=MUTED, labelsize=FS_AXIS, length=0)
ax.set_title("程式怎麼讀", loc="left", fontsize=FS_PANEL, color=INK,
             fontweight="700", pad=10)

legend_handles = [
    Patch(facecolor=color, edgecolor="none", label=name)
    for color, name in zip(option_colors, option_names)
]
axes[0].legend(handles=legend_handles, loc="lower right",
               bbox_to_anchor=(1.0, 1.0), ncol=3, frameon=False,
               fontsize=FS_LEGEND, handlelength=1.0, handletextpad=0.5,
               columnspacing=1.2)

title_block(
    fig,
    "Choice 的 confidence 是分布的形狀，不是裝飾",
    "以 Choice 為例：機率越集中，程式越敢自動往下走。",
)
fig.text(0.115, 0.125,
         "confidence <0.5 人工覆核　0.5–0.9 確認　≥0.9 自動",
         fontsize=FS_NOTE + 0.5, color=MUTED)
fig.text(0.115, 0.082,
         "confidence = (p_max − 1/n) / (1 − 1/n)　n = 3，p_max = 0.61 → 0.42",
         fontsize=FS_NOTE, color=MUTED)
source(fig, "資料來源：TypeSafe docs/confidence.md；第一、三列為示意，第二列為官方 Choice 範例。")
fig.subplots_adjust(left=0.12, right=0.965, top=0.75, bottom=0.30, wspace=0.10)

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

for bars, values, call_label, label_size, label_y, label_va in (
    (bars1, separate, "13 次", FS_LEGEND, 0.35, "bottom"),
    (bars2, batched, "1 次", FS_NOTE, 0.50, "center"),
):
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.25,
                f"{value:.1f}x", ha="center", va="bottom",
                fontsize=FS_DATA + 1, color=INK, fontweight="700")
        ax.text(bar.get_x() + bar.get_width() / 2, label_y, call_label,
                ha="center", va=label_va, fontsize=label_size,
                color=PAPER, fontweight="600")

ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=FS_AXIS + 1, color=INK)
ax.set_ylim(0, 14.8)
ax.set_yticks(range(0, 15, 2))
ax.set_ylabel("相對倍數（逐題送出 = 1.0×）", color=MUTED,
              fontsize=FS_AXIS, labelpad=10)
ax.grid(axis="y", color=GRID, linewidth=1)
ax.set_axisbelow(True)
for spine in ["top", "right", "left", "bottom"]:
    ax.spines[spine].set_visible(False)
ax.tick_params(axis="both", colors=MUTED, labelsize=FS_AXIS, length=0)
ax.legend(frameon=False, fontsize=FS_LEGEND, loc="upper right", ncol=2,
          bbox_to_anchor=(1.0, 1.02))

title_block(
    fig,
    "把 13 個問題塞進同一次請求",
    "文件只付一次、只傳一次；5 次重複實驗答案不變。",
)
fig.text(0.10, 0.10,
         "文件重送 13 次：53,777 字元 × 13 = 699,101 字元　→　一次送出：53,777 字元",
         fontsize=FS_NOTE, color=MUTED)
source(fig, "資料來源：TypeSafe docs/cookbooks/parallel_questions.md；"
            "GDPR 文章 53,777 字元，13 題，5 次重複，回答無變化。")
fig.subplots_adjust(left=0.11, right=0.965, top=0.75, bottom=0.20)

out = OUT_DIR / "03_parallel_batching.webp"
save_figure_webp(fig, out, facecolor=PAPER)
plt.close(fig)
print(out)


# --- 04_score_normalization -------------------------------------------------
fig = plt.figure(figsize=(8, 4.5), dpi=200)
fig.patch.set_facecolor(PAPER)

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

ax = fig.add_axes([0.09, 0.27, 0.50, 0.49])
ax.set_facecolor(PAPER)
x_left, x_right = 0.0, 1.0
ax.set_xlim(-0.45, 1.45)
ax.set_ylim(2.60, 0.40)
ax.set_xticks([x_left, x_right])
ax.set_xticklabels(["原始總分", "歸一化平均（0–1）"],
                   fontsize=FS_AXIS, color=INK)
ax.set_yticks([1, 2])
ax.set_yticklabels(["較好", "較差"], fontsize=FS_LEGEND, color=MUTED)
ax.grid(axis="y", color=GRID, linewidth=1)
ax.set_axisbelow(True)
for spine in ["top", "right", "left", "bottom"]:
    ax.spines[spine].set_visible(False)
ax.tick_params(axis="both", colors=MUTED, labelsize=FS_AXIS, length=0)

for x in (x_left, x_right):
    ax.axvline(x, color=GRID, linewidth=1, zorder=1)

for c in candidates:
    y0 = raw_rank[c["name"]]
    y1 = norm_rank[c["name"]]
    ax.plot([x_left, x_right], [y0, y1], color=c["color"], linewidth=3.2,
            marker="o", markersize=11, markeredgecolor=PAPER,
            markeredgewidth=2, zorder=4)
    ax.text(x_left - 0.07, y0, f'{c["name"]}  {c["raw"]:.2f}',
            ha="right", va="center", fontsize=FS_AXIS, color=INK,
            fontweight="700", zorder=5)
    ax.text(x_right + 0.07, y1, f'{c["name"]}  {c["norm"]:.3f}',
            ha="left", va="center", fontsize=FS_AXIS, color=INK,
            fontweight="700", zorder=5)

ax.scatter([0.5], [1.5], s=180, facecolors="none", edgecolors=ACCENT,
           linewidths=1.6, zorder=5)
ax.annotate("排名翻轉", xy=(0.5, 1.5), xytext=(0.5, 0.66),
            ha="center", va="center", fontsize=FS_DATA, color=ACCENT,
            fontweight="700",
            arrowprops=dict(arrowstyle="-|>", color=ACCENT, lw=1.4,
                            shrinkA=0, shrinkB=9))

ax_t = fig.add_axes([0.64, 0.27, 0.33, 0.49])
ax_t.set_xlim(0, 1)
ax_t.set_ylim(0, 1)
ax_t.axis("off")
ax_t.text(0.02, 0.98, "0.5×(風險/2) + 0.5×(工作量/3)",
          ha="left", va="top", fontsize=FS_NOTE, color=MUTED)

col_x = [0.02, 0.30, 0.57, 0.76, 0.98]
headers = ["候選", "風險", "工作量", "原始", "歸一化"]
aligns = ["left", "right", "right", "right", "right"]
for xpos, head, align in zip(col_x, headers, aligns):
    ax_t.text(xpos, 0.86, head, ha=align, va="center",
              fontsize=FS_LEGEND, color=MUTED, fontweight="700")
ax_t.plot([0.02, 0.98], [0.79, 0.79], color=GRID, linewidth=1)

table_rows = [
    ("A", "1.000", "0.000", "2.00", "0.500", ACCENT),
    ("B", "0.000", "0.967", "2.90", "0.483", "#6B7280"),
]
for i, (name, risk, work, raw, norm, color) in enumerate(table_rows):
    y = 0.66 - i * 0.16
    for xpos, val, align in zip(
        col_x[:4], (name, risk, work, raw), aligns[:4]
    ):
        ax_t.text(xpos, y, val, ha=align, va="center",
                  fontsize=FS_LEGEND, color=INK,
                  fontweight="700" if align == "left" else "400")
    ax_t.text(0.98, y, norm, ha="right", va="center",
              fontsize=FS_LEGEND, color=color, fontweight="700")

ax_t.plot([0.02, 0.98], [0.39, 0.39], color=GRID, linewidth=1)
ax_t.text(0.02, 0.29, "原始總分：B 較高", ha="left", va="center",
          fontsize=FS_LEGEND, color="#6B7280", fontweight="700")
ax_t.text(0.02, 0.18, "歸一化後：A 較高", ha="left", va="center",
          fontsize=FS_LEGEND, color=ACCENT, fontweight="700")

title_block(
    fig,
    "先歸一化，排名就反了",
    "同一組分數，只改變計分方式，領先者就換人。",
)
fig.text(0.09, 0.105,
         "示意：A、B 為假想候選；風險 3 級（0–2）、工作量 4 級（0–3），權重各 0.5。",
         fontsize=FS_NOTE, color=MUTED)
source(fig, "概念示意；數值為假想案例，非官方數據。")

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
    (0.5, 0.5, "又錯又不合法", "最差",
     "回傳一段解釋，還判斷錯", "#991B1B"),
    (1.5, 0.5, "合法但錯", "Jev 的失敗模式",
     '「billing」，其實是技術問題', "#92400E"),
    (0.5, 1.5, "對但不合法", "LLM 的失敗模式",
     '判斷對了，卻回傳 "Billing Team"', "#1E3A8A"),
    (1.5, 1.5, "合法且正確", "理想",
     '「billing」，確實是帳務問題', "#166534"),
]
for x, y, title, sub, example, color in quads:
    ax.text(x, y + 0.17, title, ha="center", va="center",
            fontsize=FS_PANEL, color=INK, fontweight="700", zorder=3)
    ax.text(x, y - 0.08, sub, ha="center", va="center",
            fontsize=FS_LEGEND - 0.5, color=color, fontweight="600", zorder=3)
    ax.text(x, y - 0.28, example, ha="center", va="center",
            fontsize=FS_NOTE + 1.5, color=MUTED, zorder=3)

ax.text(0.5, -0.15, "不合法", ha="center", va="top",
        fontsize=FS_AXIS, color=MUTED)
ax.text(1.5, -0.15, "合法", ha="center", va="top",
        fontsize=FS_AXIS, color=MUTED)
ax.text(1.0, -0.31, "輸出格式／型別", ha="center", va="top",
        fontsize=FS_AXIS, color=INK, fontweight="600")
ax.text(-0.10, 0.5, "錯誤", ha="right", va="center",
        fontsize=FS_AXIS, color=MUTED)
ax.text(-0.10, 1.5, "正確", ha="right", va="center",
        fontsize=FS_AXIS, color=MUTED)
ax.text(-0.24, 1.0, "答案語意", ha="center", va="center", rotation=90,
        fontsize=FS_AXIS, color=INK, fontweight="600")

title_block(
    fig,
    "type-safe 只保證右半邊",
    "Jev 把失敗模式移到右下：格式可控，語意仍可能錯。",
)
fig.text(0.012, 0.105,
         "四格是常見失敗模式，不是互斥分類；type-safe 只保證格式，不保證答案正確。",
         fontsize=FS_NOTE, color=MUTED)
source(fig, "概念示意；非 TypeSafe 官方分類。")
fig.subplots_adjust(left=0.16, right=0.95, top=0.78, bottom=0.27)

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

ax.add_patch(Rectangle((0, 0), 1, 1, facecolor="#D1FAE5", edgecolor="none", zorder=0))
ax.add_patch(Rectangle((0, 1), 1, 1, facecolor="#ECFDF5", edgecolor="none", zorder=0))
ax.add_patch(Rectangle((1, 0), 1, 1, facecolor="#F3F4F6", edgecolor="none", zorder=0))
ax.add_patch(Rectangle((1, 1), 1, 1, facecolor="#E5E7EB", edgecolor="none", zorder=0))

ax.annotate("", xy=(1.92, 1.92), xytext=(0.08, 0.08),
            arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.6,
                            alpha=0.16, linestyle=(0, (6, 4)),
                            shrinkA=0, shrinkB=0),
            zorder=0.5)

ax.axvline(1, color=PAPER, linewidth=4, zorder=2)
ax.axhline(1, color=PAPER, linewidth=4, zorder=2)

ax.text(0.5, 1.92, "Jev 的主場", ha="center", va="center",
        fontsize=FS_LEGEND, color=ACCENT, fontweight="700", zorder=3)
ax.text(1.5, 1.92, "LLM 的主場", ha="center", va="center",
        fontsize=FS_LEGEND, color=MUTED, fontweight="700", zorder=3)

quads = [
    (0.5, 0.5, "Jev（單步）", "封閉答案、語意判斷",
     "「這張工單屬於哪一隊？」", "#065F46"),
    (0.5, 1.5, "Workflow + Jev", "多步，但每步封閉",
     "「13 題平行，每題封閉」", "#065F46"),
    (1.5, 0.5, "單次 LLM", "單步、開放生成",
     "「寫一段客服回覆」", "#4B5563"),
    (1.5, 1.5, "Agent / reasoning LLM", "多步、開放生成",
     "「規劃並執行多步退款」", "#374151"),
]
for x, y, title, sub, example, color in quads:
    ax.text(x, y + 0.17, title, ha="center", va="center",
            fontsize=FS_PANEL - 0.5, color=INK, fontweight="700", zorder=3)
    ax.text(x, y - 0.08, sub, ha="center", va="center",
            fontsize=FS_LEGEND - 0.5, color=color, fontweight="600", zorder=3)
    ax.text(x, y - 0.28, example, ha="center", va="center",
            fontsize=FS_NOTE + 1.5, color=MUTED, zorder=3)

ax.text(0.5, -0.15, "可列舉", ha="center", va="top",
        fontsize=FS_AXIS, color=MUTED)
ax.text(1.5, -0.15, "開放生成", ha="center", va="top",
        fontsize=FS_AXIS, color=MUTED)
ax.text(1.0, -0.31, "答案空間", ha="center", va="top",
        fontsize=FS_AXIS, color=INK, fontweight="600")
ax.text(-0.10, 0.5, "單步", ha="right", va="center",
        fontsize=FS_AXIS, color=MUTED)
ax.text(-0.10, 1.5, "多步", ha="right", va="center",
        fontsize=FS_AXIS, color=MUTED)
ax.text(-0.24, 1.0, "任務形狀", ha="center", va="center", rotation=90,
        fontsize=FS_AXIS, color=INK, fontweight="600")

title_block(
    fig,
    "Jev 在封閉答案那一側",
    "它不是 agent；它是 workflow 裡每個決策點的一顆 if。",
)
fig.text(0.012, 0.115,
         "判斷順序：① 答案能不能列舉？ ② 需不需要多步推理？",
         fontsize=FS_NOTE, color=MUTED)
fig.text(0.012, 0.075,
         "箭頭方向：答案越開放、步驟越多，越適合 LLM。",
         fontsize=FS_NOTE, color=MUTED)
source(fig, "概念示意；非 TypeSafe 官方 positioning。")
fig.subplots_adjust(left=0.16, right=0.95, top=0.78, bottom=0.27)

out = OUT_DIR / "06_decision_boundary.webp"
save_figure_webp(fig, out, facecolor=PAPER)
plt.close(fig)
print(out)


# --- cover.jpg --------------------------------------------------------------
out = OUT_DIR / "cover.jpg"
svg_to_jpeg(COVER_SVG, out, width=1200, quality=85)
print(out)
