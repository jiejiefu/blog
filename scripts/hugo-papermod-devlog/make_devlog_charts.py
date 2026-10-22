#!/usr/bin/env python3
"""Generate charts for the Hugo/PaperMod build-log post.

Usage:
    python3 scripts/hugo-papermod-devlog/make_devlog_charts.py

Writes a 1376x720 WebP directly into the post's page bundle. The PNG
intermediate stays in a temporary directory and is never published.
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from image_utils import save_figure_webp

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "content/zh-tw/posts/hugo-papermod-devlog/images"

PINGFANG = font_manager.findfont("PingFang TC")
FONT = font_manager.FontProperties(fname=PINGFANG)

INK = "#1a1a1f"
MUTED = "#6b6b76"
GRID = "#e6e6ee"
PURPLE = "#5b4bff"
PURPLE_LIGHT = "#c7c2ff"
GRAY = "#8a8fa3"


def style_axes(ax):
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.yaxis.grid(False)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color("#d0d0d8")
    ax.tick_params(axis="x", colors=MUTED, labelsize=13, length=0)
    ax.tick_params(axis="y", colors=INK, labelsize=16, length=0)


def content_size_chart():
    fig, ax = plt.subplots(figsize=(13.76, 7.2), dpi=100)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    labels = [
        "content/ 改版前\n（PNG）",
        "content/ 改版後\n（WebP / JPEG）",
        "public/\n（部署產物）",
    ]
    values = [204, 15, 8.9]
    colors = [PURPLE, PURPLE_LIGHT, GRAY]
    ypos = [2, 1, 0]

    bars = ax.barh(ypos, values, height=0.42, color=colors, zorder=3)

    ax.set_yticks(ypos)
    ax.set_yticklabels(labels, fontproperties=FONT, linespacing=1.35)
    ax.set_xlim(0, 250)
    ax.set_ylim(-0.55, 2.7)
    ax.set_xticks([0, 50, 100, 150, 200])
    ax.set_xlabel("MB", fontproperties=FONT, fontsize=14, color=MUTED, labelpad=10)

    for bar, value in zip(bars, values):
        if value >= 100:
            text = f"{value:.0f} MB"
        elif value >= 10:
            text = f"{value:.0f} MB"
        else:
            text = f"{value:.1f} MB"
        ax.text(
            value + 4,
            bar.get_y() + bar.get_height() / 2,
            text,
            va="center",
            ha="left",
            fontproperties=FONT,
            fontsize=18,
            fontweight="bold",
            color=INK,
        )

    style_axes(ax)

    fig.text(
        0.06,
        0.925,
        "換個格式，content/ 從 204 MB 降到 15 MB",
        fontproperties=FONT,
        fontsize=27,
        fontweight="bold",
        color=INK,
    )
    fig.text(
        0.06,
        0.875,
        "同一批資訊圖，只換編碼與尺寸，不改內容。",
        fontproperties=FONT,
        fontsize=15,
        color=MUTED,
    )
    fig.text(
        0.06,
        0.045,
        "資料來源：本站 repo（2026-10）。改版前單檔最大 9.3 MB，六篇合計約 204 MB。",
        fontproperties=FONT,
        fontsize=12.5,
        color=MUTED,
    )

    fig.subplots_adjust(left=0.235, right=0.955, top=0.80, bottom=0.16)
    out = OUT_DIR / "01_content_size.webp"
    save_figure_webp(fig, out, dpi=100, facecolor="white")
    plt.close(fig)
    print(out)


if __name__ == "__main__":
    content_size_chart()
