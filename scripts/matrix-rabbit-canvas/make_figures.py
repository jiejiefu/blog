#!/usr/bin/env python3
"""Build the silhouette -> brightness grid -> text art figure.

Reads the same data the homepage uses (glyph-art-data.js and hare.txt) so the
middle and right panels are not illustrations: they are the real 132x110 grid.

Usage:
    python3 scripts/matrix-rabbit-canvas/make_figures.py
"""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA_JS = ROOT / "assets/js/glyph-art-data.js"
HARE_TXT = ROOT / "assets/glyph-art/hare.txt"
SILHOUETTE = HERE / "silhouette.svg"
OUT = ROOT / "content/zh-tw/posts/matrix-rabbit-canvas/images/01_grid_to_text.webp"

S = 2
W, H = 1376 * S, 640 * S
BG = "#0a110c"
PANEL = "#0d1710"
BORDER = "#1e3327"
INK = "#e6f3e9"
MUTED = "#8fa895"
ACCENT = "#6ee79a"

MONO = "/Users/jiejiefu/Library/Fonts/JetBrainsMono-Regular.ttf"
MONO_BOLD = "/Users/jiejiefu/Library/Fonts/JetBrainsMono-Bold.ttf"
CJK = "/System/Library/AssetsV2/com_apple_MobileAsset_Font7/3419f2a427639ad8c8e139149a287865a90fa17e.asset/AssetData/PingFang.ttc"

RAMP = [
    "#0a110c",
    "#1d3b28",
    "#2b5c3a",
    "#3b804d",
    "#4fa762",
    "#68cf7c",
    "#8be89a",
    "#b6ffc4",
    "#e2fff0",
]


def load_grid() -> list[list[int]]:
    raw = DATA_JS.read_text(encoding="utf-8").strip()
    raw = re.sub(r"^window\.ART=", "", raw)
    raw = raw.rstrip(";")
    hare = json.loads(raw)["hare"]
    return [[int(c) for c in row] for row in hare["lv"]]


def cjk_font(size: int) -> ImageFont.FreeTypeFont:
    for index in range(12):
        try:
            return ImageFont.truetype(CJK, size, index=index)
        except OSError:
            continue
    raise SystemExit("PingFang.ttc: no usable face")


def rounded(draw: ImageDraw.ImageDraw, box, radius, fill, outline=None, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def main() -> None:
    grid = load_grid()
    rows, cols = len(grid), len(grid[0])

    with tempfile.TemporaryDirectory(prefix="rabbit-fig-") as tmp:
        sil_png = Path(tmp) / "sil.png"
        subprocess.run(
            ["rsvg-convert", "-h", str(900), str(SILHOUETTE), "-o", str(sil_png)],
            check=True,
        )
        silhouette = Image.open(sil_png).convert("RGBA")

    canvas = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(canvas)

    margin, gap = 80, 40
    panel_w = (W - margin * 2 - gap * 2) // 3
    top, panel_h = 150, 1060
    xs = [margin + i * (panel_w + gap) for i in range(3)]

    label_font = cjk_font(30)
    small_font = ImageFont.truetype(MONO, 22)

    labels = ["原始剪影", "132 × 110 亮度網格", "文字輸出 hare.txt"]
    subs = [
        f"{silhouette.width} × {silhouette.height}",
        f"{cols} × {rows} · 8 levels",
        "132 cols × 110 rows",
    ]

    for i, x in enumerate(xs):
        rounded(draw, (x, top, x + panel_w, top + panel_h), 18, PANEL, BORDER, 3)
        draw.text((x + 4, 74), labels[i], font=label_font, fill=INK)
        draw.text((x + 4, 112), subs[i], font=small_font, fill=MUTED)

    # 1. silhouette
    pad = 60
    max_w, max_h = panel_w - pad * 2, panel_h - pad * 2
    scale = min(max_w / silhouette.width, max_h / silhouette.height)
    sw, sh = int(silhouette.width * scale), int(silhouette.height * scale)
    sil = silhouette.resize((sw, sh), Image.LANCZOS)
    green = Image.new("RGBA", (sw, sh), (110, 231, 154, 255))
    green.putalpha(sil.getchannel("A"))
    px = xs[0] + (panel_w - sw) // 2
    py = top + (panel_h - sh) // 2
    canvas.paste(green, (px, py), green)

    # 2. brightness grid
    cell = 5
    gw, gh = cols * cell, rows * cell
    heat = Image.new("RGB", (gw, gh), RAMP[0])
    hd = ImageDraw.Draw(heat)
    for y, row in enumerate(grid):
        for x, v in enumerate(row):
            if v:
                hd.rectangle(
                    (x * cell, y * cell, x * cell + cell - 1, y * cell + cell - 1),
                    fill=RAMP[min(8, v + 1)],
                )
    scale = min((panel_w - pad * 2) / gw, (panel_h - pad * 2) / gh)
    hw, hh = int(gw * scale), int(gh * scale)
    heat = heat.resize((hw, hh), Image.NEAREST)
    hx = xs[1] + (panel_w - hw) // 2
    hy = top + (panel_h - hh) // 2
    canvas.paste(heat, (hx, hy))
    draw.rectangle((hx, hy, hx + hw, hy + hh), outline=BORDER, width=2)

    # 3. text art (same rows, same characters)
    lines = HARE_TXT.read_text(encoding="utf-8").splitlines()
    lines = [line for line in lines if line.strip()][:rows]
    fs = min(
        (panel_w - pad * 1.4) / (cols * 0.65),
        (panel_h - pad * 1.4) / (len(lines) * 1.2025),
    )
    font = ImageFont.truetype(MONO, int(fs))
    lh = fs * 1.2025
    cw = fs * 0.65
    total_w = cols * cw
    tx0 = xs[2] + (panel_w - total_w) / 2
    ty0 = top + (panel_h - len(lines) * lh) / 2
    for r, line in enumerate(lines):
        for c, ch in enumerate(line[:cols]):
            v = int(grid[r][c]) if r < rows and c < cols else 0
            if not v:
                continue
            draw.text(
                (tx0 + c * cw, ty0 + r * lh),
                ch,
                font=font,
                fill=RAMP[min(8, v + 1)],
                anchor="la",
            )

    canvas = canvas.resize((W // S, H // S), Image.LANCZOS)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="rabbit-fig-") as tmp:
        png = Path(tmp) / "fig.png"
        canvas.save(png)
        subprocess.run(
            ["cwebp", "-quiet", "-q", "85", "-m", "6", "-metadata", "none", "-noalpha", str(png), "-o", str(OUT)],
            check=True,
        )
    print(OUT)


if __name__ == "__main__":
    main()
