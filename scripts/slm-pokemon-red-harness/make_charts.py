#!/usr/bin/env python3
"""Generate the static charts for the SLM x Pokemon Red harness post.

Usage:
    python3 scripts/slm-pokemon-red-harness/make_charts.py

The script reads the derived snapshot in ``data/`` (produced by
``extract_data.py``) and writes 1376px-wide WebP files into the post's page
bundle. No ROM or game screenshots are used.
"""

import csv
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
from matplotlib.ticker import NullFormatter, NullLocator

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from image_utils import save_figure_webp

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUT_DIR = ROOT / "content/zh-tw/posts/slm-pokemon-red-harness/images"

PINGFANG = font_manager.findfont("PingFang TC")
FONT = font_manager.FontProperties(fname=PINGFANG)

INK = "#1a1a1f"
MUTED = "#6b6b76"
GRID = "#e6e6ee"
INDIGO = "#5b4bff"
INDIGO_LIGHT = "#c7c2ff"
GREEN = "#22C55E"
RED = "#EF4444"
AMBER = "#F59E0B"
AMBER_LIGHT = "#fde68a"
TEAL = "#14B8A6"
GRAY = "#8a8fa3"

MAP_STYLE = {
    38: {"name": "Red's House 2F", "color": INDIGO, "short": "2F"},
    37: {"name": "Red's House 1F", "color": TEAL, "short": "1F"},
    0: {"name": "Pallet Town", "color": GREEN, "short": "Pallet"},
}

ACTION_COLORS = {
    "A": GRAY,
    "UP": INDIGO,
    "DOWN": GREEN,
    "LEFT": AMBER,
    "RIGHT": RED,
}


def load_csv(name):
    with (DATA / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_memory():
    return json.loads((DATA / "memory_snapshot.json").read_text(encoding="utf-8"))


def style_axes(ax):
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.yaxis.grid(False)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color("#d0d0d8")
    ax.tick_params(axis="x", colors=MUTED, labelsize=12, length=0)
    ax.tick_params(axis="y", colors=INK, labelsize=14, length=0)


def save(fig, name):
    path = OUT_DIR / name
    save_figure_webp(fig, path)
    plt.close(fig)
    print(f"wrote {path.relative_to(ROOT)}")


# ---------------------------------------------------------------------------
# 1. Spatial memory: three maps, visited cells, blocked edges, warps
# ---------------------------------------------------------------------------


def make_spatial_memory():
    memory = load_memory()
    new_rows = load_csv("episodes_new.csv")
    final = new_rows[-1]

    visited = {map_id: set() for map_id in MAP_STYLE}
    for coord in memory["seen_coords"]:
        visited.setdefault(coord["map_id"], set()).add((coord["x"], coord["y"]))

    blocked = {map_id: [] for map_id in MAP_STYLE}
    for edge in memory["blocked_moves"]:
        blocked.setdefault(edge["map_id"], []).append(edge)

    warps = {map_id: [] for map_id in MAP_STYLE}
    for map_id, entries in memory["discovered_warps"].items():
        warps.setdefault(int(map_id), []).extend(entries)

    fig, axes = plt.subplots(
        1, 3, figsize=(13.76, 5.6), dpi=100, constrained_layout=False
    )
    fig.patch.set_facecolor("white")
    fig.subplots_adjust(left=0.03, right=0.985, top=0.82, bottom=0.16, wspace=0.10)

    order = [38, 37, 0]

    for ax, map_id in zip(axes, order):
        style = MAP_STYLE[map_id]
        cells = visited.get(map_id, set())
        edges = blocked.get(map_id, [])
        doors = warps.get(map_id, [])

        max_x = max((x for x, _ in cells), default=7)
        max_y = max((y for _, y in cells), default=7)
        width = max(8, max_x + 1)
        height = max(8, max_y + 1)

        ax.set_xlim(-0.7, width - 0.3)
        ax.set_ylim(height - 0.3, -0.7)
        ax.set_aspect("equal")
        ax.axis("off")

        for x in range(width + 1):
            ax.plot(
                [x - 0.5, x - 0.5],
                [-0.5, height - 0.5],
                color=GRID,
                linewidth=0.8,
                zorder=0,
            )
        for y in range(height + 1):
            ax.plot(
                [-0.5, width - 0.5],
                [y - 0.5, y - 0.5],
                color=GRID,
                linewidth=0.8,
                zorder=0,
            )

        for x, y in cells:
            ax.add_patch(
                Rectangle(
                    (x - 0.5, y - 0.5),
                    1,
                    1,
                    facecolor=style["color"],
                    alpha=0.22,
                    edgecolor="none",
                    zorder=1,
                )
            )

        for edge in edges:
            x, y = edge["x"], edge["y"]
            direction = edge["dir"]
            if direction == "UP":
                segment = ([x - 0.5, x + 0.5], [y - 0.5, y - 0.5])
            elif direction == "DOWN":
                segment = ([x - 0.5, x + 0.5], [y + 0.5, y + 0.5])
            elif direction == "LEFT":
                segment = ([x - 0.5, x - 0.5], [y - 0.5, y + 0.5])
            else:
                segment = ([x + 0.5, x + 0.5], [y - 0.5, y + 0.5])
            ax.plot(
                segment[0],
                segment[1],
                color=INK,
                linewidth=2.4,
                solid_capstyle="round",
                zorder=4,
                clip_on=False,
            )

        for door in doors:
            ax.scatter(
                [door["x"]],
                [door["y"]],
                marker="s",
                s=95,
                facecolor=AMBER,
                edgecolor="white",
                linewidth=1.4,
                zorder=6,
            )

        pair_labels = {}
        for door in doors:
            dest = door.get("desc", "").replace("Warp to ", "")
            dest = {
                "Red's House 1F": "→1F",
                "Red's House 2F": "→2F",
                "Pallet Town": "→Pallet",
            }.get(dest, "→?")
            pair_labels.setdefault(dest, []).append((door["x"], door["y"]))

        for label, coords in pair_labels.items():
            mid_x = sum(x for x, _ in coords) / len(coords)
            mid_y = min(y for _, y in coords) - 0.35
            text = f"{label} ×{len(coords)}" if len(coords) > 1 else label
            ax.text(
                mid_x,
                mid_y,
                text,
                ha="center",
                va="bottom",
                fontsize=9,
                color="#b45309",
                fontproperties=FONT,
                zorder=7,
                bbox=dict(
                    boxstyle="round,pad=0.18",
                    facecolor="white",
                    edgecolor="none",
                    alpha=0.85,
                ),
            )

        if str(final["map_id"]) == str(map_id):
            ax.scatter(
                [int(final["x"])],
                [int(final["y"])],
                marker="*",
                s=260,
                facecolor=RED,
                edgecolor="white",
                linewidth=1.2,
                zorder=8,
            )
            ax.annotate(
                "最後位置",
                (int(final["x"]), int(final["y"])),
                xytext=(12, -19),
                textcoords="offset points",
                fontsize=9,
                color=RED,
                fontproperties=FONT,
                zorder=9,
                bbox=dict(
                    boxstyle="round,pad=0.2",
                    facecolor="white",
                    edgecolor="none",
                    alpha=0.85,
                ),
            )

        ax.set_title(
            f"{style['name']}（map {map_id}）\n"
            f"{len(cells)} 格 · {len(edges)} 阻擋 · {len(doors)} warp",
            fontproperties=FONT,
            fontsize=13,
            color=INK,
            pad=14,
        )

    handles = [
        Patch(facecolor=GRAY, alpha=0.25, label="走過的格子"),
        Line2D([0], [0], color=INK, linewidth=2.4, label="阻擋邊界"),
        Line2D(
            [0],
            [0],
            marker="s",
            color="none",
            markerfacecolor=AMBER,
            markeredgecolor="white",
            markersize=10,
            label="warp / 門口",
        ),
        Line2D(
            [0],
            [0],
            marker="*",
            color="none",
            markerfacecolor=RED,
            markeredgecolor="white",
            markersize=13,
            label="最後位置",
        ),
    ]
    fig.legend(
        handles=handles,
        loc="lower center",
        ncol=4,
        frameon=False,
        prop=FONT,
        fontsize=10,
        bbox_to_anchor=(0.5, 0.065),
    )
    fig.text(
        0.5,
        0.02,
        "格子座標為 (x, y)；只畫出實際走過的範圍。",
        ha="center",
        va="bottom",
        fontproperties=FONT,
        fontsize=9.5,
        color=MUTED,
    )
    save(fig, "01_spatial_memory.webp")


# ---------------------------------------------------------------------------
# 2. Latency CDF + button frame budget
# ---------------------------------------------------------------------------


def make_latency_budget():
    rows = load_csv("episodes_new.csv")
    latency = np.array(
        [float(row["latency"]) for row in rows if float(row["latency"]) > 0]
    )
    latency.sort()
    cdf = np.arange(1, len(latency) + 1) / len(latency) * 100
    p50, p90, p95 = np.percentile(latency, [50, 90, 95])

    fig, (ax, ax2) = plt.subplots(
        1,
        2,
        figsize=(13.76, 5.6),
        dpi=100,
        gridspec_kw={"width_ratios": [1.35, 1], "wspace": 0.18},
    )
    fig.patch.set_facecolor("white")
    fig.subplots_adjust(left=0.07, right=0.98, top=0.82, bottom=0.16)

    ax.step(latency, cdf, where="post", color=INDIGO, linewidth=2.8, zorder=4)
    ax.axvspan(1.0, 2.0, color=RED, alpha=0.09, linewidth=0, zorder=0)
    ax.text(
        1.38,
        8,
        "VLM 1–2 s",
        ha="center",
        va="bottom",
        fontproperties=FONT,
        fontsize=10,
        color=RED,
    )

    for value, label, y, marker_y in (
        (p50, f"p50 {p50:.2f} s", 56, 50),
        (p95, f"p95 {p95:.2f} s", 79, 95),
    ):
        ax.axvline(value, color=GRAY, linewidth=1.2, linestyle=(0, (4, 3)), zorder=2)
        ax.scatter([value], [marker_y], s=38, color=INDIGO, zorder=6)
        ax.text(
            value * 1.06,
            y,
            label,
            fontproperties=FONT,
            fontsize=10,
            color=INK,
        )

    ax.set_xscale("log")
    ax.xaxis.set_minor_locator(NullLocator())
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_xlim(0.35, 8.0)
    ax.set_ylim(0, 100)
    ax.set_xticks([0.4, 0.5, 1, 2, 5])
    ax.set_xticklabels(["0.4", "0.5", "1", "2", "5"])
    ax.set_yticks([0, 25, 50, 75, 95, 100])
    ax.set_xlabel(
        "秒（對數刻度）", fontproperties=FONT, fontsize=12, color=MUTED, labelpad=8
    )
    ax.set_ylabel(
        "累積比例（%）", fontproperties=FONT, fontsize=12, color=MUTED, labelpad=8
    )
    ax.set_title(
        f"Ollama 往返延遲分布（{len(latency)} 筆）",
        fontproperties=FONT,
        fontsize=14,
        color=INK,
        pad=12,
    )
    style_axes(ax)
    ax.text(
        0.98,
        0.06,
        "48 步未呼叫模型\n（L1 BFS／節奏步）",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontproperties=FONT,
        fontsize=9,
        color=MUTED,
        bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor=GRID),
    )

    # Frame timing: 24 frames at 60 Hz.
    ax2.set_xlim(0, 30)
    ax2.set_ylim(0.2, 2.65)
    ax2.set_yticks([])
    ax2.set_xticks([0, 4, 8, 12, 16, 20, 24, 28])
    ax2.set_xlabel(
        "Game Boy 幀（60 Hz）",
        fontproperties=FONT,
        fontsize=12,
        color=MUTED,
        labelpad=8,
    )
    style_axes(ax2)
    ax2.yaxis.grid(False)

    ax2.add_patch(
        Rectangle((0, 1.72), 12, 0.34, facecolor=INDIGO, edgecolor="none", zorder=3)
    )
    ax2.add_patch(
        Rectangle(
            (12, 1.72), 12, 0.34, facecolor=INDIGO_LIGHT, edgecolor="none", zorder=3
        )
    )
    ax2.text(
        6,
        1.89,
        "按住 12 幀",
        ha="center",
        va="center",
        fontproperties=FONT,
        fontsize=10,
        color="white",
    )
    ax2.text(
        18,
        1.89,
        "放開 12 幀",
        ha="center",
        va="center",
        fontproperties=FONT,
        fontsize=10,
        color=INK,
    )
    ax2.text(
        -0.8,
        1.89,
        "方向鍵",
        ha="right",
        va="center",
        fontproperties=FONT,
        fontsize=10,
        color=INK,
    )

    ax2.add_patch(
        Rectangle((0, 0.92), 8, 0.34, facecolor=AMBER, edgecolor="none", zorder=3)
    )
    ax2.add_patch(
        Rectangle(
            (8, 0.92), 10, 0.34, facecolor=AMBER_LIGHT, edgecolor="none", zorder=3
        )
    )
    ax2.text(
        4,
        1.09,
        "按住 8 幀",
        ha="center",
        va="center",
        fontproperties=FONT,
        fontsize=9.5,
        color="white",
    )
    ax2.text(
        13,
        1.09,
        "放開 10 幀",
        ha="center",
        va="center",
        fontproperties=FONT,
        fontsize=9.5,
        color=INK,
    )
    ax2.text(
        -0.8,
        1.09,
        "A / B",
        ha="right",
        va="center",
        fontproperties=FONT,
        fontsize=10,
        color=INK,
    )

    ax2.annotate(
        "太快：只轉向",
        xy=(6, 1.62),
        xytext=(1.4, 2.32),
        fontproperties=FONT,
        fontsize=9.5,
        color=MUTED,
        arrowprops=dict(
            arrowstyle="-", color=GRAY, linewidth=1, linestyle=(0, (3, 3))
        ),
    )
    ax2.annotate(
        "太慢：一步變兩步",
        xy=(24, 1.62),
        xytext=(18.4, 2.32),
        fontproperties=FONT,
        fontsize=9.5,
        color=MUTED,
        arrowprops=dict(
            arrowstyle="-", color=GRAY, linewidth=1, linestyle=(0, (3, 3))
        ),
    )
    ax2.axvline(24, color=INK, linewidth=1.1, linestyle=(0, (4, 3)), zorder=2)
    ax2.text(
        24.6,
        0.42,
        "24 幀 = 400 ms",
        fontproperties=FONT,
        fontsize=10,
        color=INK,
    )
    ax2.set_title(
        "按鍵時序：方向鍵 24 幀 = 400 ms",
        fontproperties=FONT,
        fontsize=14,
        color=INK,
        pad=12,
    )

    fig.text(
        0.5,
        0.025,
        "延遲為 Ollama HTTP 往返；README 的 10–50 ms 是不同量測邊界，兩者不直接比較。",
        ha="center",
        va="bottom",
        fontproperties=FONT,
        fontsize=9.5,
        color=MUTED,
    )
    save(fig, "02_latency_budget.webp")


# ---------------------------------------------------------------------------
# 3. Action mix before/after
# ---------------------------------------------------------------------------


def make_action_mix():
    old_rows = load_csv("episodes_old.csv")
    new_rows = load_csv("episodes_new.csv")

    old_counts = {}
    for row in old_rows:
        old_counts[row["action"]] = old_counts.get(row["action"], 0) + 1
    new_counts = {}
    for row in new_rows:
        new_counts[row["action"]] = new_counts.get(row["action"], 0) + 1

    fig, ax = plt.subplots(figsize=(13.76, 4.2), dpi=100)
    fig.patch.set_facecolor("white")
    fig.subplots_adjust(left=0.16, right=0.86, top=0.80, bottom=0.20)

    rows = [
        ("舊管線\n132 episodes", old_counts, 132, "1 種動作"),
        ("新管線\n595 steps", new_counts, 595, "4 種動作"),
    ]
    ypos = [1, 0]

    for y, (_, counts, total, _) in zip(ypos, rows):
        left = 0.0
        for action in ["A", "UP", "DOWN", "LEFT", "RIGHT"]:
            count = counts.get(action, 0)
            if not count:
                continue
            width = count / total * 100
            ax.barh(
                y,
                width,
                left=left,
                height=0.46,
                color=ACTION_COLORS[action],
                edgecolor="white",
                linewidth=2,
                zorder=3,
            )
            if width >= 7:
                ax.text(
                    left + width / 2,
                    y,
                    f"{action}\n{count}",
                    ha="center",
                    va="center",
                    fontproperties=FONT,
                    fontsize=11 if width > 15 else 9.5,
                    color="white" if action in ("UP", "DOWN", "RIGHT") else INK,
                    linespacing=1.25,
                    zorder=4,
                )
            left += width

    ax.set_yticks(ypos)
    ax.set_yticklabels(
        [row[0] for row in rows], fontproperties=FONT, fontsize=13, linespacing=1.45
    )
    ax.set_xlim(0, 112)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
    ax.set_xlabel("動作比例", fontproperties=FONT, fontsize=12, color=MUTED, labelpad=8)
    ax.set_ylim(-0.55, 1.55)
    ax.set_title(
        "動作分布：從單一 A 到四種方向鍵",
        fontproperties=FONT,
        fontsize=15,
        color=INK,
        pad=14,
    )

    for y, (_, _, _, label) in zip(ypos, rows):
        ax.text(
            101.5,
            y,
            label,
            ha="left",
            va="center",
            fontproperties=FONT,
            fontsize=11,
            color=MUTED,
        )

    ax.set_axisbelow(True)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color("#d0d0d8")
    ax.tick_params(axis="x", colors=MUTED, labelsize=12, length=0)
    ax.tick_params(axis="y", colors=INK, labelsize=13, length=0)

    fig.text(
        0.16,
        0.055,
        "長度為比例；區塊內為次數。舊管線的 A 佔 100%，新管線出現四種方向鍵。",
        ha="left",
        va="bottom",
        fontproperties=FONT,
        fontsize=9.5,
        color=MUTED,
    )
    save(fig, "03_action_mix.webp")


# ---------------------------------------------------------------------------
# 4. Resolution / tile loss
# ---------------------------------------------------------------------------


GLYPH = np.array(
    [
        [0, 0, 1, 1, 1, 1, 0, 0],
        [0, 1, 1, 0, 0, 1, 1, 0],
        [1, 1, 0, 0, 0, 0, 1, 1],
        [1, 1, 0, 0, 0, 0, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 0, 0, 0, 0, 1, 1],
        [1, 1, 0, 0, 0, 0, 1, 1],
        [1, 1, 0, 0, 0, 0, 1, 1],
    ]
)


def draw_frame(ax, width, height, title, subtitle):
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_aspect("equal")
    ax.axis("off")

    ax.add_patch(
        Rectangle(
            (0, 0),
            width,
            height,
            facecolor="white",
            edgecolor=INK,
            linewidth=1.4,
            zorder=2,
        )
    )
    for x in np.arange(0, width + 0.1, 8):
        ax.plot([x, x], [0, height], color="#d9d9e3", linewidth=0.8, zorder=1)
    for y in np.arange(0, height + 0.1, 8):
        ax.plot([0, width], [y, y], color="#d9d9e3", linewidth=0.8, zorder=1)

    tile_x = (width // 16) * 8
    tile_y = (height // 16) * 8
    ax.add_patch(
        Rectangle(
            (tile_x, tile_y),
            8,
            8,
            facecolor=AMBER,
            alpha=0.28,
            edgecolor=RED,
            linewidth=2.0,
            zorder=3,
        )
    )
    ax.annotate(
        "1 tile",
        xy=(tile_x + 4, tile_y + 4),
        xytext=(tile_x + 20, tile_y + 24),
        fontproperties=FONT,
        fontsize=8.5,
        color=RED,
        arrowprops=dict(arrowstyle="-", color=RED, linewidth=0.8),
    )
    ax.set_title(title, fontproperties=FONT, fontsize=12.5, color=INK, pad=7)
    ax.text(
        0.5,
        -0.10,
        subtitle,
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontproperties=FONT,
        fontsize=9.5,
        color=MUTED,
    )


def draw_tile(ax, tile_w, tile_h, label, note):
    pad_x = (8 - tile_w) / 2
    pad_y = (8 - tile_h) / 2
    ax.set_xlim(-pad_x, tile_w + pad_x)
    ax.set_ylim(tile_h + pad_y, -pad_y)
    ax.set_aspect("equal")
    ax.axis("off")

    ax.imshow(
        GLYPH,
        cmap=ListedColormap(["white", INDIGO]),
        interpolation="nearest",
        extent=(0, tile_w, tile_h, 0),
        vmin=0,
        vmax=1,
        zorder=2,
    )
    for x in np.linspace(0, tile_w, 9):
        ax.plot(
            [x, x], [0, tile_h], color="white", alpha=0.45, linewidth=0.6, zorder=3
        )
    for y in np.linspace(0, tile_h, 9):
        ax.plot(
            [0, tile_w], [y, y], color="white", alpha=0.45, linewidth=0.6, zorder=3
        )
    ax.add_patch(
        Rectangle(
            (0, 0),
            tile_w,
            tile_h,
            facecolor="none",
            edgecolor=INK,
            linewidth=1.2,
            zorder=4,
        )
    )
    ax.text(
        0.5,
        -0.15,
        label,
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontproperties=FONT,
        fontsize=10.5,
        color=INK,
    )
    ax.text(
        0.5,
        -0.25,
        note,
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontproperties=FONT,
        fontsize=9,
        color=MUTED,
    )


def make_resolution_loss():
    fig = plt.figure(figsize=(13.76, 6.4), dpi=100)
    fig.patch.set_facecolor("white")
    grid = fig.add_gridspec(
        2,
        3,
        height_ratios=[0.75, 1.25],
        left=0.06,
        right=0.94,
        top=0.86,
        bottom=0.14,
        hspace=0.34,
        wspace=0.16,
    )

    frames = [
        (160, 144, "160×144（10:9）", "20 × 18 tiles", 8, 8),
        (120, 96, "120×96（5:4）", "15 × 12 tiles", 6, 5.33),
        (120, 108, "120×108（10:9）", "15 × 13.5 tiles", 6, 6),
    ]

    for col, (w, h, title, subtitle, tile_w, tile_h) in enumerate(frames):
        ax_frame = fig.add_subplot(grid[0, col])
        draw_frame(ax_frame, w, h, title, subtitle)

        ax_tile = fig.add_subplot(grid[1, col])
        if col == 0:
            draw_tile(ax_tile, tile_w, tile_h, "8×8 px/tile", "等向，細節保留")
        elif col == 1:
            draw_tile(ax_tile, tile_w, tile_h, "6×5.33 px/tile", "非等向壓縮，字變扁")
        else:
            draw_tile(ax_tile, tile_w, tile_h, "6×6 px/tile", "等向，但只剩 6 px")

    fig.suptitle(
        "同一個 8×8 字元，在三種縮放下的樣子",
        fontproperties=FONT,
        fontsize=15,
        color=INK,
        y=0.97,
    )
    save(fig, "04_resolution_loss.webp")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    make_spatial_memory()
    make_latency_budget()
    make_action_mix()
    make_resolution_loss()


if __name__ == "__main__":
    main()
