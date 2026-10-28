#!/usr/bin/env python3
"""Build the cover and the five data figures for the DeepSeek-V4.1-Flash post.

Charts are written as WebP straight into the page bundle. The PNG intermediate
stays in a temp dir, so Hugo never publishes it.

Run from anywhere:
    /Users/jiejiefu/Documents/Visual_Studio_Code/.venv/bin/python \
        scripts/deepseek-v4-1-flash/make_figures.py
"""

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from image_utils import save_figure_webp, svg_to_jpeg  # noqa: E402

SLUG = "deepseek-v4-1-flash"
BUNDLE = ROOT / "content" / "zh-tw" / "posts" / SLUG
IMAGES = BUNDLE / "images"
SCRIPT_DIR = Path(__file__).resolve().parent

INK = "#111827"
MUTED = "#6B7280"
FAINT = "#9CA3AF"
GRID = "#E5E7EB"
PAPER = "#FFFFFF"
ACCENT = "#4F46E5"
ACCENT_SOFT = "#A5B4FC"
TEAL = "#0E9F6E"
AMBER = "#D97706"
RED = "#B91C1C"
GREY = "#9CA3AF"

plt.rcParams.update(
    {
        "font.family": ["PingFang TC", "DejaVu Sans"],
        "font.size": 10.2,
        "axes.titlesize": 11.5,
        "axes.labelsize": 10.2,
        "xtick.labelsize": 10.2,
        "ytick.labelsize": 10.2,
        "legend.fontsize": 9.6,
        "axes.unicode_minus": False,
        "axes.edgecolor": GRID,
        "axes.labelcolor": MUTED,
        "xtick.color": MUTED,
        "ytick.color": INK,
        "text.color": INK,
        "figure.facecolor": PAPER,
        "axes.facecolor": PAPER,
        "savefig.facecolor": PAPER,
    }
)


def style(ax, grid_axis="x"):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)


def source(fig, text, y=0.015):
    fig.text(0.012, y, text, fontsize=8.8, color=FAINT, ha="left", va="bottom")


def title(fig, main, sub):
    fig.text(0.012, 0.965, main, fontsize=16.5, fontweight="bold", color=INK, ha="left", va="top")
    fig.text(0.012, 0.905, sub, fontsize=10.4, color=MUTED, ha="left", va="top")


def figure_1():
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(10, 4.8), gridspec_kw={"width_ratios": [1, 1], "wspace": 0.34}
    )

    rows = ["DeepSeek-V1", "V4-Flash", "V4.1-Flash"]
    per_token = [389 * 1024, 3.5 * 1024, 890]
    colors = [GREY, ACCENT, TEAL]

    ax1.barh(rows, per_token, color=colors, height=0.52, zorder=3)
    ax1.set_xscale("log")
    ax1.set_xlim(500, 2_000_000)
    ax1.set_xticks([1e3, 1e4, 1e5, 1e6])
    ax1.set_xticklabels(["1 KB", "10 KB", "100 KB", "1 MB"])
    ax1.set_title("每個 token 的 global KV", fontsize=11.5, color=INK, pad=10, loc="left")
    ax1.invert_yaxis()
    style(ax1)

    labels = ["389 KB", "3.5 KB", "890 bytes"]
    for y, value, label in zip(rows, per_token, labels):
        ax1.text(value * 1.35, y, label, va="center", ha="left", fontsize=10.8, fontweight="bold", color=INK)

    total = [v * 1_000_000 for v in per_token]
    ax2.barh(rows, total, color=colors, height=0.52, zorder=3)
    ax2.set_xscale("log")
    ax2.set_xlim(5e8, 2e12)
    ax2.set_xticks([1e9, 1e10, 1e11, 1e12])
    ax2.set_xticklabels(["1 GB", "10 GB", "100 GB", "1 TB"])
    ax2.set_title("換成 1M context 的總量", fontsize=11.5, color=INK, pad=10, loc="left")
    ax2.invert_yaxis()
    style(ax2)

    totals = ["389 GB", "3.5 GB", "890 MB"]
    for y, value, label in zip(rows, total, totals):
        ax2.text(value * 1.35, y, label, va="center", ha="left", fontsize=10.8, fontweight="bold", color=INK)

    title(
        fig,
        "global KV 的世代差距：同一個 1M context，從 389 GB 到 890 MB",
        "只計 global KV；SWA 的 128-token 窗口與其他啟動記憶體另計。倍數依論文 437× / 約 4× 回推。",
    )
    source(fig, "資料來源：DeepSeek-V4.1-Flash 論文（arXiv 2609.19969）Fig. 1b；數值為回推的近似值。")
    fig.subplots_adjust(left=0.15, right=0.985, top=0.79, bottom=0.15)

    out = IMAGES / "01_kv_generations.webp"
    save_figure_webp(fig, out, dpi=160)
    plt.close(fig)
    return out


def figure_2():
    fig, ax = plt.subplots(figsize=(10, 4.7))

    labels = [
        "HBM\nV4-Flash",
        "HBM\nV4.1-Flash",
        "Persistent SSD\nV4-Flash",
        "Persistent SSD\nV4.1-Flash",
    ]
    y = [3, 2, 1, 0]

    ax.barh(y[0], 100, color=ACCENT, height=0.5, zorder=3)
    ax.barh(y[1], 25, color=ACCENT, height=0.5, zorder=3)
    ax.barh(y[2], 50, color=ACCENT, height=0.5, zorder=3)
    ax.barh(y[2], 50, left=50, color=GREY, height=0.5, zorder=3, hatch="//", edgecolor=PAPER, linewidth=0)
    ax.barh(y[3], 12.5, color=ACCENT, height=0.5, zorder=3)

    ax.text(101.8, y[0], "100", va="center", fontsize=10.2, color=INK, fontweight="bold")
    ax.text(26.8, y[1], "25  →  1/4", va="center", fontsize=10.5, color=TEAL, fontweight="bold")
    ax.text(14.3, y[3], "12.5  →  1/8", va="center", fontsize=10.5, color=TEAL, fontweight="bold")
    ax.text(25, y[2], "50 · global", va="center", ha="center", fontsize=9.5, color=PAPER, fontweight="bold")
    ax.text(75, y[2], "50 · SWA", va="center", ha="center", fontsize=9.5, color=INK, fontweight="bold")
    ax.text(34, y[3], "global only · SWA 不落盤", va="center", ha="left", fontsize=9.3, color=AMBER)

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=10.2)
    ax.set_xlim(0, 118)
    ax.set_xlabel("相對 V4-Flash 的 KV 足跡（V4-Flash = 100）", fontsize=10.2)
    style(ax, "x")

    title(
        fig,
        "兩個儲存層各自被砍：HBM 剩 1/4，SSD 剩 1/8",
        "V4.1 用 CSA2 與 FP4 壓 global KV；再用 SWA Bounded Replay 把短期窗口整個移出 persistent storage。",
    )
    source(fig, "資料來源：DeepSeek-V4.1-Flash 論文 §3.2.1、§3.2.2、Fig. 1b。SWA 條紋區為不落盤的短期 KV。")
    fig.subplots_adjust(left=0.21, right=0.97, top=0.78, bottom=0.16)

    out = IMAGES / "02_kv_budget.webp"
    save_figure_webp(fig, out, dpi=160)
    plt.close(fig)
    return out


def figure_3():
    fig, ax = plt.subplots(figsize=(10, 5.0))
    ax.set_xlim(-3.5, 20.5)
    ax.set_ylim(-0.02, 3.32)
    ax.axis("off")

    swa = "#D1D5DB"
    full = ACCENT
    reindex = AMBER
    reuse = "#C7D2FE"

    encoder = [swa, swa] + [full] + [reuse] * 5 + [full] + [reuse] * 5 + [full] + [reuse] * 5
    decoder = [full] + [reuse] * 3 + ([reindex] + [reuse] * 3) * 4
    assert len(encoder) == 20 and len(decoder) == 20

    def draw(y, seq):
        for i, color in enumerate(seq):
            ax.add_patch(
                Rectangle(
                    (i + 0.04, y),
                    0.92,
                    0.62,
                    facecolor=color,
                    edgecolor=PAPER,
                    linewidth=1.2,
                )
            )

    def bracket(start, end, y, label, above=True):
        ax.plot([start + 0.08, end - 0.08], [y, y], color=FAINT, linewidth=0.9, zorder=2)
        ax.plot([start + 0.08, start + 0.08], [y, y - 0.05], color=FAINT, linewidth=0.9, zorder=2)
        ax.plot([end - 0.08, end - 0.08], [y, y - 0.05], color=FAINT, linewidth=0.9, zorder=2)
        ax.text(
            (start + end) / 2,
            y + 0.10 if above else y - 0.14,
            label,
            fontsize=9.4,
            color=MUTED,
            ha="center",
            va="bottom" if above else "top",
        )

    draw(2.30, encoder)
    draw(1.05, decoder)

    ax.text(-3.38, 2.61, "causal encoder\n20 layers · m = 2", fontsize=10.0, color=INK, fontweight="bold", va="center")
    ax.text(-3.38, 1.36, "decoder\n20 layers · m = 1", fontsize=10.0, color=INK, fontweight="bold", va="center")

    bracket(0, 2, 2.12, "2×SWA", above=False)
    for start in (2, 8, 14):
        bracket(start, start + 6, 2.12, "Full + 5×Reuse", above=False)

    bracket(0, 4, 0.86, "Full + 3×Reuse", above=False)
    for start in (4, 8, 12, 16):
        bracket(start, start + 4, 0.86, "Reindex + 3×Reuse", above=False)

    handles = [
        Rectangle((0, 0), 1, 1, facecolor=swa, edgecolor="none"),
        Rectangle((0, 0), 1, 1, facecolor=full, edgecolor="none"),
        Rectangle((0, 0), 1, 1, facecolor=reindex, edgecolor="none"),
        Rectangle((0, 0), 1, 1, facecolor=reuse, edgecolor="none"),
    ]
    ax.legend(
        handles,
        ["SWA（FP8）", "Full（重算 main KV）", "Reindex（重跑 indexer）", "Reuse（直接共用）"],
        loc="lower center",
        bbox_to_anchor=(0.5, 0.03),
        ncol=4,
        frameon=False,
        fontsize=9.4,
        handlelength=1.0,
        handleheight=0.9,
        columnspacing=1.4,
    )

    title(
        fig,
        "40 層不是 40 份 global KV：18 層 encoder 只算 3 次",
        "同一個 group 內，main KV、indexer K 與 Top-K 由 1 層 Full 算完，後面 m−1 層直接 Reuse；encoder 只跑 prefill。",
    )
    source(fig, "資料來源：DeepSeek-V4.1-Flash 論文 §2.1–2.3、§4.2.1；層配置依 Fig. 4 重繪。", y=0.012)
    fig.subplots_adjust(left=0.02, right=0.985, top=0.82, bottom=0.17)

    out = IMAGES / "03_layer_layout.webp"
    save_figure_webp(fig, out, dpi=160)
    plt.close(fig)
    return out


def figure_4():
    fig, ax = plt.subplots(figsize=(10, 4.7))

    series = [
        ("Terminal-Bench 2.1", 82.4, 90.6, ACCENT),
        ("DeepSWE v1.1", 66.0, 74.2, TEAL),
        ("Reasoning 平均", 67.1, 76.3, AMBER),
    ]
    x = [0, 1]

    ax.axvspan(0.47, 0.73, color="#EEF2FF", zorder=0)
    ax.text(0.60, 61.0, "論文：60–80 已回收大部分增益", fontsize=9.2, color=ACCENT, ha="center")

    for name, start, end, color in series:
        ax.plot(x, [start, end], color=color, linewidth=2.2, marker="o", markersize=5, zorder=3)
        ax.text(-0.045, start, f"{start:.1f}", ha="right", va="center", fontsize=10.2, color=color, fontweight="bold")
        ax.text(1.045, end, f"{end:.1f}", ha="left", va="center", fontsize=10.2, color=color, fontweight="bold")
        ax.text(1.15, end, name, ha="left", va="center", fontsize=9.3, color=MUTED)

    ax.set_xlim(-0.14, 1.42)
    ax.set_ylim(60, 95)
    ax.set_xticks(x)
    ax.set_xticklabels(["effort 25", "effort 100"], fontsize=10.0)
    ax.set_ylabel("Pass@1", fontsize=10.2)
    style(ax, "y")

    ax.text(0.5, 92.6, "token 用量約 ×2.5", fontsize=9.6, color=RED, ha="center", fontweight="bold")

    title(
        fig,
        "effort 從 25 拉到 100：分數 +9，token ×2.5",
        "API 只開放 low / high / max（50 / 75 / 100）；圖中 25 是論文的最小值，不是 API 選項。",
    )
    source(fig, "資料來源：DeepSeek-V4.1-Flash 論文 §5.1.4、§5.3.3、Fig. 9。只畫兩個端點，中間不插值。")
    fig.subplots_adjust(left=0.09, right=0.82, top=0.79, bottom=0.15)

    out = IMAGES / "04_effort_frontier.webp"
    save_figure_webp(fig, out, dpi=160)
    plt.close(fig)
    return out


def figure_5():
    rows = [
        ("Automation-Bench", 60.5, 50.3),
        ("Agents' Last Exam", 35.4, 28.6),
        ("MathArena Apex", 72.1, 65.8),
        ("DeepSWE v1.1", 77.0, 74.0),
        ("NL2Repo-Bench", 68.2, 75.3),
        ("ProgramBench", 29.1, 37.0),
        ("Terminal-Bench 4.0", 42.3, 51.8),
        ("Humanity's Last Exam", 42.6, 56.3),
    ]
    fig, ax = plt.subplots(figsize=(10, 5.3))

    y = list(range(len(rows)))[::-1]
    for yi, (name, ours, opus) in zip(y, rows):
        color = TEAL if ours >= opus else RED
        ax.plot([ours, opus], [yi, yi], color=color, linewidth=1.6, alpha=0.55, zorder=2)
        ax.scatter([opus], [yi], s=58, color=GREY, zorder=3)
        ax.scatter([ours], [yi], s=64, color=color, zorder=4)
        ax.text(min(ours, opus) - 1.6, yi, f"{min(ours, opus):.1f}", ha="right", va="center", fontsize=9.3, color=MUTED)
        ax.text(max(ours, opus) + 1.6, yi, f"{max(ours, opus):.1f}", ha="left", va="center", fontsize=9.3, color=MUTED)

    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows], fontsize=10.2)
    ax.set_xlim(15, 90)
    ax.set_xlabel("Pass@1", fontsize=10.2)
    style(ax, "x")

    ax.scatter([], [], s=58, color=GREY, label="Opus-5")
    ax.scatter([], [], s=58, color=TEAL, label="V4.1-Flash-1017（贏）")
    ax.scatter([], [], s=58, color=RED, label="V4.1-Flash-1017（輸）")
    ax.legend(loc="lower right", frameon=False, fontsize=9.4, handletextpad=0.4, borderaxespad=0.2)

    title(
        fig,
        "贏在 agentic 迴圈，輸在知識與長流程",
        "同一組分數裡，V4.1-Flash-1017 拿下 4 項，也明確輸掉 4 項；這比「全面超車」更接近真實。",
    )
    source(fig, "資料來源：Hugging Face DeepSeek-V4.1-Flash-1017 模型卡 benchmark 表。Opus-5 為其對照欄。")
    fig.subplots_adjust(left=0.24, right=0.97, top=0.79, bottom=0.15)

    out = IMAGES / "05_benchmark_gap.webp"
    save_figure_webp(fig, out, dpi=160)
    plt.close(fig)
    return out


def figure_6():
    fig, ax = plt.subplots(figsize=(10, 5.25))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    def arrow(x1, y1, x2, y2):
        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops=dict(arrowstyle="-|>", color=FAINT, lw=1.5, shrinkA=0, shrinkB=0),
        )

    ax.add_patch(Rectangle((3, 37), 15, 38, facecolor="#F3F4F6", edgecolor=GRID, linewidth=1.0))
    ax.text(3, 78, "1M context", fontsize=10.2, color=INK, fontweight="bold", va="bottom")
    ax.text(3, 34.5, "N 個 visible KV entry", fontsize=8.9, color=MUTED, va="top")
    for i in range(24):
        y = 39 + i * 1.45
        color = "#D1D5DB"
        if i in (3, 8, 14, 19):
            color = ACCENT_SOFT
        if i in (8, 19):
            color = AMBER
        ax.add_patch(Rectangle((4.5, y), 12, 1.02, facecolor=color, edgecolor=PAPER, linewidth=0.8))

    ax.add_patch(Rectangle((24, 42), 14, 26, facecolor=ACCENT, edgecolor=PAPER, linewidth=1.0))
    ax.text(31, 58, "Full", ha="center", va="center", fontsize=11.0, color=PAPER, fontweight="bold")
    ax.text(31, 50, "掃全部 KV", ha="center", va="center", fontsize=9.0, color=PAPER)

    ax.add_patch(Rectangle((43, 38), 17, 34, facecolor="#EEF2FF", edgecolor=ACCENT, linewidth=1.2))
    ax.text(51.5, 69.3, "候選池", ha="center", va="center", fontsize=10.2, color=INK, fontweight="bold")
    ax.text(51.5, 40.2, "16,384 positions", ha="center", va="center", fontsize=9.2, color=INK)
    for row in range(5):
        for col in range(8):
            selected = (row, col) in {
                (0, 1), (0, 4), (0, 6),
                (1, 2), (1, 5),
                (2, 0), (2, 3), (2, 7),
                (3, 1), (3, 6),
                (4, 4),
            }
            ax.add_patch(
                Rectangle(
                    (44.2 + col * 1.85, 45.0 + row * 4.3),
                    1.45,
                    3.45,
                    facecolor=ACCENT if selected else "#E5E7EB",
                    edgecolor=PAPER,
                    linewidth=0.8,
                )
            )

    ax.add_patch(Rectangle((66, 42), 14, 26, facecolor=AMBER, edgecolor=PAPER, linewidth=1.0))
    ax.text(73, 58, "Reindex", ha="center", va="center", fontsize=11.0, color=PAPER, fontweight="bold")
    ax.text(73, 50, "只掃 pool", ha="center", va="center", fontsize=9.0, color=PAPER)

    ax.add_patch(Rectangle((85, 42), 12, 26, facecolor=TEAL, edgecolor=PAPER, linewidth=1.0))
    ax.text(91, 58, "Top-512", ha="center", va="center", fontsize=11.0, color=PAPER, fontweight="bold")
    ax.text(91, 50, "attention", ha="center", va="center", fontsize=9.0, color=PAPER)

    arrow(18.2, 55, 23.8, 55)
    arrow(38.2, 55, 42.8, 55)
    arrow(60.2, 55, 65.8, 55)
    arrow(80.2, 55, 84.8, 55)

    ax.text(51.5, 76.8, "blockwise max → 選 block", ha="center", va="bottom", fontsize=8.8, color=MUTED)

    ax.add_patch(Rectangle((24, 18), 73, 11, facecolor="#F9FAFB", edgecolor=GRID, linewidth=1.0))
    ax.text(
        60.5,
        25.8,
        "Reuse 層：跳過 index，直接沿用上一層 Top-K",
        ha="center",
        va="center",
        fontsize=9.8,
        color=INK,
        fontweight="bold",
    )
    ax.text(
        60.5,
        21.2,
        "成本：Full O(N) 一次 · Reindex O(16,384) 常數 · Reuse O(1)",
        ha="center",
        va="center",
        fontsize=9.2,
        color=MUTED,
    )

    title(
        fig,
        "Indexer 的兩段式搜尋：全掃一次，之後只掃 16,384 個位置",
        "Full 層掃全部 main KV；blockwise 選出候選池；Reindex 只在此重打分，Reuse 直接沿用 Top-K。",
    )
    source(fig, "資料來源：文章 §6。圖為示意，區塊與位置非等比例。", y=0.012)
    fig.subplots_adjust(left=0.02, right=0.985, top=0.80, bottom=0.16)

    out = IMAGES / "06_sparse_indexer_pool.webp"
    save_figure_webp(fig, out, dpi=160)
    plt.close(fig)
    return out


def figure_7():
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(10, 4.9), gridspec_kw={"width_ratios": [1.08, 1], "wspace": 0.30}
    )
    ax1.set_xlim(0, 100)
    ax1.set_ylim(0, 100)
    ax1.axis("off")
    ax1.set_title("每個 16-channel group 的位元帳", loc="left", fontsize=11.0, color=INK, pad=8)

    for i in range(16):
        ax1.add_patch(
            Rectangle((4 + i * 5.1, 60), 4.2, 14, facecolor=ACCENT, edgecolor=PAPER, linewidth=1.0)
        )
    ax1.add_patch(Rectangle((88, 60), 8, 14, facecolor=AMBER, edgecolor=PAPER, linewidth=1.0))
    ax1.text(4, 77, "16 × 4-bit E2M1 = 64 bits", fontsize=10.0, color=INK, fontweight="bold")
    ax1.text(92, 77, "1 × E4M3 scale = 8 bits", ha="center", va="bottom", fontsize=8.6, color=AMBER)
    ax1.text(92, 55.5, "每 16 channels 共用", ha="center", va="top", fontsize=8.2, color=MUTED)

    ax1.text(4, 48, "64 + 8 = 72 bits / group", fontsize=11.2, color=INK, fontweight="bold")
    ax1.text(4, 40, "72 ÷ 16 = 4.5 bits / channel", fontsize=11.2, color=INK, fontweight="bold")
    ax1.text(4, 32, "512 channels ≈ 288 bytes / entry", fontsize=10.6, color=INK)
    ax1.text(4, 23, "未計對齊、indexer K 與跨層共享", fontsize=8.8, color=MUTED)
    ax1.text(4, 14, "有效位元 = 4.0（資料）+ 0.5（scale 攤提）", fontsize=9.6, color=ACCENT, fontweight="bold")

    ax2.set_xscale("log")
    ax2.set_xlim(1, 5000)
    ax2.set_ylim(0, 1)
    ax2.set_yticks([])
    ax2.set_title("為什麼可以省略 global scale", loc="left", fontsize=11.0, color=INK, pad=8)
    ax2.axvspan(10, 2688, color="#ECFDF5", alpha=0.85, zorder=0)
    ax2.axhline(0.45, color=GRID, linewidth=1.2, zorder=1)
    ax2.scatter([10, 22.6, 2688], [0.45, 0.45, 0.45], s=[46, 46, 58], color=[INK, MUTED, TEAL], zorder=3)
    ax2.text(10, 0.61, "觀測最大 10", ha="center", va="bottom", fontsize=9.2, color=INK, fontweight="bold")
    ax2.text(22.6, 0.29, "RMSNorm L2 上限 22.6", ha="center", va="top", fontsize=9.0, color=MUTED)
    ax2.text(
        2688,
        0.61,
        "可表示上限 2,688\n(E2M1 6 × E4M3 448)",
        ha="right",
        va="bottom",
        fontsize=8.8,
        color=TEAL,
        fontweight="bold",
    )
    ax2.text(100, 0.82, "~2 個數量級的 headroom", ha="center", va="center", fontsize=9.4, color=TEAL)
    ax2.set_xticks([1, 10, 100, 1000, 5000])
    ax2.set_xticklabels(["1", "10", "100", "1,000", "5,000"])
    ax2.set_xlabel("KV magnitude（log scale）", fontsize=9.8)
    style(ax2, "x")

    title(
        fig,
        "FP4 的兩個數字：4.5 bits/channel，以及 100 倍以上的範圍餘裕",
        "左：每個 16-channel group 的位元帳；右：實際最大值與可表示上限。",
    )
    source(
        fig,
        "資料來源：文章 §7。4.5 bits/channel 未計對齊、indexer K 與跨層共享；890 bytes 是全 cache 的結果。",
        y=0.012,
    )
    fig.subplots_adjust(left=0.035, right=0.975, top=0.79, bottom=0.16)

    out = IMAGES / "07_fp4_budget_range.webp"
    save_figure_webp(fig, out, dpi=160)
    plt.close(fig)
    return out


def figure_8():
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(10, 5.35), sharex=True, gridspec_kw={"height_ratios": [1, 1.15], "hspace": 0.34}
    )

    ax1.axvspan(0, 34, color="#F9FAFB", zorder=0)
    ax1.axvspan(34, 45, color="#EEF2FF", zorder=0)
    ax1.plot([0, 34, 34, 45], [64, 64, 1024, 1024], color=ACCENT, linewidth=2.4, solid_joinstyle="miter")
    ax1.axvline(34, color=FAINT, linestyle="--", linewidth=1.0)
    ax1.set_yscale("log")
    ax1.set_ylim(45, 1300)
    ax1.set_yticks([64, 128, 256, 512, 1024])
    ax1.set_yticklabels(["64K", "128K", "256K", "512K", "1M"])
    ax1.set_ylabel("Sequence length", fontsize=9.8)
    ax1.text(17, 78, "64K", ha="center", va="bottom", fontsize=10.0, color=MUTED, fontweight="bold")
    ax1.text(39.5, 860, "1M", ha="center", va="center", fontsize=10.0, color=ACCENT, fontweight="bold")
    ax1.text(34, 48, "34T", ha="center", va="bottom", fontsize=8.6, color=FAINT)
    style(ax1, "y")
    ax1.tick_params(axis="x", labelbottom=False)

    ax2.plot([0, 0.2, 28, 40, 45], [0, 2.6e-4, 2.6e-4, 2.6e-5, 2.6e-5], color=TEAL, linewidth=2.4)
    ax2.axvline(28, color=FAINT, linestyle="--", linewidth=1.0)
    ax2.axvline(40, color=FAINT, linestyle="--", linewidth=1.0)
    ax2.set_ylim(0, 2.95e-4)
    ax2.set_yticks([0, 1e-4, 2e-4, 2.6e-4])
    ax2.set_yticklabels(["0", "1e-4", "2e-4", "2.6e-4"])
    ax2.set_xlim(0, 45)
    ax2.set_xticks([0, 10, 20, 30, 40, 45])
    ax2.set_xticklabels(["0", "10T", "20T", "30T", "40T", "45T"])
    ax2.set_xlabel("Training tokens", fontsize=9.8)
    ax2.set_ylabel("Learning rate", fontsize=9.8)
    ax2.annotate(
        "warmup 2k steps",
        xy=(0.2, 2.6e-4),
        xytext=(7, 2.25e-4),
        fontsize=8.8,
        color=MUTED,
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.0),
    )
    ax2.text(14, 2.73e-4, "plateau", ha="center", va="center", fontsize=9.4, color=MUTED, fontweight="bold")
    ax2.text(34, 1.32e-4, "cosine", ha="center", va="center", fontsize=9.4, color=MUTED, fontweight="bold")
    ax2.text(42.5, 7.5e-5, "flat", ha="center", va="center", fontsize=9.4, color=MUTED, fontweight="bold")
    ax2.text(28.6, 0.42e-4, "28T：vision encoder 開始聯合訓練", ha="left", va="center", fontsize=8.4, color=FAINT)
    style(ax2, "y")

    title(
        fig,
        "45T tokens 的訓練節奏：64K 起訓，34T 才拉到 1M",
        "上方是 sequence length，下方是 learning rate；28T 開始 cosine，40T 後持平。",
    )
    source(
        fig,
        "資料來源：文章 §10；warmup 2,000 steps 以 batch 100.6M tokens 估算約 0.20T tokens。",
        y=0.012,
    )
    fig.subplots_adjust(left=0.12, right=0.975, top=0.80, bottom=0.12)

    out = IMAGES / "08_training_schedule.webp"
    save_figure_webp(fig, out, dpi=160)
    plt.close(fig)
    return out


def figure_9():
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(10, 4.8), gridspec_kw={"width_ratios": [1.05, 1], "wspace": 0.36}
    )

    labels1 = ["V4.1 hit", "V4.1 miss", "V4-Pro hit", "V4-Pro miss"]
    values1 = [0.003, 0.15, 0.022, 0.66]
    y1 = [3, 2, 1, 0]
    colors1 = ["#6EE7B7", TEAL, "#D1D5DB", GREY]
    ax1.barh(y1, values1, color=colors1, height=0.55, zorder=3)
    ax1.set_xscale("log")
    ax1.set_xlim(0.002, 1.0)
    ax1.set_ylim(-0.6, 3.65)
    ax1.set_xticks([0.003, 0.01, 0.03, 0.1, 0.3, 1.0])
    ax1.set_xticklabels(["$0.003", "$0.01", "$0.03", "$0.1", "$0.3", "$1"])
    ax1.set_yticks(y1)
    ax1.set_yticklabels(labels1)
    ax1.set_xlabel("USD / 1M input tokens", fontsize=9.2, color=MUTED)
    ax1.set_title("Input 價格（每 1M tokens, off-peak）", loc="left", fontsize=10.8, color=INK, pad=8)
    for yi, val in zip(y1, values1):
        ax1.text(val * 1.14, yi, f"${val:.3g}", va="center", ha="left", fontsize=9.4, color=INK)
    ax1.text(
        0.0022,
        3.42,
        "cache hit → miss：50×（V4.1）/ 30×（V4-Pro）",
        ha="left",
        va="center",
        fontsize=8.8,
        color=RED,
        fontweight="bold",
    )
    style(ax1, "x")

    labels2 = ["V4-Pro miss", "V4.1 miss", "V4.1 hit"]
    values2 = [0.858, 0.21, 0.063]
    y2 = [2, 1, 0]
    colors2 = [GREY, TEAL, "#6EE7B7"]
    ax2.barh(y2, values2, color=colors2, height=0.55, zorder=3)
    ax2.set_xlim(0, 0.99)
    ax2.set_ylim(-0.6, 2.65)
    ax2.set_yticks(y2)
    ax2.set_yticklabels(labels2)
    ax2.set_xlabel("USD / request", fontsize=9.2, color=MUTED)
    ax2.set_title("1M input + 100K output 總價（off-peak）", loc="left", fontsize=10.8, color=INK, pad=8)
    for yi, val in zip(y2, values2):
        ax2.text(val + 0.018, yi, f"${val:.3g}", va="center", ha="left", fontsize=9.4, color=INK)
    ax2.text(
        0.02,
        2.42,
        "V4-Pro miss → V4.1 miss：4.1×；miss → hit：3.3×",
        ha="left",
        va="center",
        fontsize=8.8,
        color=MUTED,
    )
    style(ax2, "x")

    title(
        fig,
        "Cache hit 很便宜，但 output 讓總帳單只差 3.3–4.1 倍",
        "左：input-only 差 50×；右：加上 100K output 後，總價差縮到 3.3–4.1×。",
    )
    source(fig, "資料來源：DeepSeek API 定價與文章 §13.3；Peak 為 Off-peak 的 2 倍。", y=0.012)
    fig.subplots_adjust(left=0.17, right=0.975, top=0.79, bottom=0.15)

    out = IMAGES / "09_cache_cost.webp"
    save_figure_webp(fig, out, dpi=160)
    plt.close(fig)
    return out


def build_cover():
    out = IMAGES / "cover.jpg"
    svg_to_jpeg(SCRIPT_DIR / "cover.svg", out, width=1200, quality=85)
    return out


def main():
    IMAGES.mkdir(parents=True, exist_ok=True)
    outputs = [
        figure_1(),
        figure_2(),
        figure_3(),
        figure_4(),
        figure_5(),
        figure_6(),
        figure_7(),
        figure_8(),
        figure_9(),
        build_cover(),
    ]
    for path in outputs:
        print(f"{path.relative_to(ROOT)}  {path.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
