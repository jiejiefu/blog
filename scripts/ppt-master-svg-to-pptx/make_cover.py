#!/usr/bin/env python3
"""Generate the terminal-style cover for the PPT Master deep dive.

The SVG source is kept next to this script so the cover stays editable. The
JPEG is written into the post's page bundle; no PNG intermediate is published.

Usage:
    python3 scripts/ppt-master-svg-to-pptx/make_cover.py
    python3 scripts/ppt-master-svg-to-pptx/make_cover.py --preview
"""

import argparse
import html
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BUNDLE_IMAGES = ROOT / "content/zh-tw/posts/ppt-master-svg-to-pptx/images"

sys.path.insert(0, str(ROOT / "scripts"))
from image_utils import svg_to_jpeg, svg_to_webp  # noqa: E402

MONO = "'SF Mono','Menlo','DejaVu Sans Mono',monospace"
SANS = "'PingFang TC','Noto Sans TC','Heiti TC',sans-serif"

BG = "#0A0A0A"
PANEL = "#141414"
BAR = "#1B1B1B"
LINE = "#2B2B2B"
INK = "#F5F5F5"
MID = "#D1D5DB"
MUTED = "#9A9A9A"
DIM = "#5C5C5C"
ACCENT = "#938BFF"


def esc(value):
    return html.escape(str(value), quote=True)


def text(x, y, value, *, size=14, fill=MUTED, family=MONO, weight=None,
         spacing=None, anchor=None):
    attrs = [f'x="{x}"', f'y="{y}"', f'font-family="{family}"',
             f'font-size="{size}"', f'fill="{fill}"']
    if weight:
        attrs.append(f'font-weight="{weight}"')
    if spacing:
        attrs.append(f'letter-spacing="{spacing}"')
    if anchor:
        attrs.append(f'text-anchor="{anchor}"')
    return f'<text {" ".join(attrs)}>{esc(value)}</text>'


def chip(x, y, label, *, width, accent=False):
    stroke = ACCENT if accent else LINE
    fill = "#1B1B1B"
    color = ACCENT if accent else MUTED
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="32" rx="2" '
        f'fill="{fill}" stroke="{stroke}"/>'
        + text(x + 12, y + 21, label, size=11, fill=color, spacing="1")
    )


def build_svg():
    parts = []
    parts.append(
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" '
        'viewBox="0 0 1200 630">'
    )
    parts.append("<title>PPT Master — 從 SVG 編譯原生 PPTX</title>")
    parts.append(
        "<desc>Terminal-style cover: a project SVG slide on the left is "
        "compiled into native PowerPoint shapes, text and charts on the right."
        "</desc>"
    )

    parts.append(f'<rect width="1200" height="630" fill="{BG}"/>')
    parts.append(
        '<pattern id="dotgrid" width="24" height="24" patternUnits="userSpaceOnUse">'
        f'<circle cx="1" cy="1" r="1" fill="#FFFFFF" opacity="0.065"/>'
        "</pattern>"
    )
    parts.append('<rect width="1200" height="630" fill="url(#dotgrid)"/>')

    parts.append(
        f'<rect x="64" y="56" width="1072" height="518" rx="12" fill="{PANEL}" '
        f'stroke="{LINE}" stroke-width="1"/>'
    )
    parts.append(
        f'<path d="M64 68a12 12 0 0 1 12-12h1048a12 12 0 0 1 12 12v36H64z" '
        f'fill="{BAR}"/>'
    )
    parts.append(f'<line x1="64" y1="104" x2="1136" y2="104" stroke="{LINE}"/>')

    parts.append(f'<circle cx="92" cy="80" r="5" fill="{ACCENT}"/>')
    parts.append(f'<circle cx="116" cy="80" r="5" fill="{DIM}"/>')
    parts.append(f'<circle cx="140" cy="80" r="5" fill="{DIM}"/>')
    parts.append(text(164, 85, "ppt-master — svg → pptx", size=14))

    parts.append(f'<circle cx="1014" cy="80" r="4" fill="{ACCENT}"/>')
    parts.append(text(1026, 85, "COMPILING", size=11, spacing="2"))

    # Command line
    parts.append(text(104, 154, "$", size=17, fill=ACCENT))
    parts.append(text(124, 154, "npx skills add hugohe3/ppt-master", size=17,
                      fill=INK))

    # Wordmark
    parts.append(text(100, 306, "PPT", size=120, fill=INK, weight="700",
                      spacing="2"))
    parts.append(text(100, 420, "MASTER", size=120, fill=INK, weight="700",
                      spacing="2"))
    parts.append(f'<rect x="106" y="440" width="330" height="4" fill="{ACCENT}"/>')

    parts.append(text(104, 486, "工程師不再親手做投影片", size=25, fill=MID,
                      family=SANS))
    parts.append(text(104, 516, "From project-canonical SVG to native DrawingML",
                      size=12.5, fill=MUTED))

    parts.append(chip(104, 530, "v6.7.2", width=76, accent=True))
    parts.append(chip(192, 530, "MIT", width=58))
    parts.append(chip(262, 530, "70 EXAMPLES", width=116))
    parts.append(chip(390, 530, "PYTHON 3.10+", width=122))

    # Divider
    parts.append(f'<line x1="620" y1="140" x2="620" y2="548" stroke="{LINE}"/>')

    # Right: source SVG slide
    parts.append(text(664, 159, "PROJECT SVG", size=10.5, fill=DIM, spacing="2"))
    parts.append(
        f'<rect x="664" y="174" width="222" height="266" rx="2" fill="#101010" '
        f'stroke="{LINE}"/>'
    )
    parts.append(f'<rect x="664" y="174" width="222" height="24" fill="{BAR}"/>')
    parts.append(text(676, 191, "slide_07.svg", size=10, fill=MUTED))
    parts.append(f'<circle cx="870" cy="186" r="2.5" fill="{ACCENT}"/>')

    parts.append(f'<rect x="680" y="214" width="96" height="8" fill="{INK}"/>')
    parts.append(f'<rect x="680" y="230" width="132" height="4" fill="{DIM}"/>')
    for i, w in enumerate((150, 128, 158)):
        y = 258 + i * 17
        parts.append(f'<rect x="680" y="{y}" width="5" height="5" fill="{ACCENT}"/>')
        parts.append(f'<rect x="692" y="{y}" width="{w}" height="4" fill="{DIM}"/>')

    for i, h in enumerate((30, 52, 40, 64, 46)):
        x = 682 + i * 18
        parts.append(
            f'<rect x="{x}" y="{336 - h}" width="9" height="{h}" fill="{ACCENT}" '
            f'opacity="{0.35 + i * 0.11:.2f}"/>'
        )
    parts.append(f'<line x1="680" y1="338" x2="766" y2="338" stroke="{LINE}"/>')

    parts.append(
        f'<rect x="792" y="214" width="78" height="124" rx="2" fill="#161616" '
        f'stroke="{LINE}"/>'
    )
    for i in range(4):
        parts.append(f'<line x1="802" y1="{230 + i * 24}" x2="860" y2="{230 + i * 24}" '
                     f'stroke="{LINE}"/>')
    parts.append(f'<rect x="802" y="222" width="34" height="3" fill="{MUTED}"/>')

    parts.append(f'<rect x="680" y="356" width="190" height="1" fill="{LINE}"/>')
    parts.append(text(680, 380, "<text> <rect> <path>", size=10, fill=DIM))
    parts.append(text(680, 400, "font-size=\"24\"", size=10, fill=DIM))
    parts.append(text(680, 420, "fill=\"#938BFF\"", size=10, fill=DIM))

    # Arrow
    parts.append(f'<line x1="902" y1="306" x2="934" y2="306" stroke="{ACCENT}"/>')
    parts.append(f'<path d="M934 306l-8 -4v8z" fill="{ACCENT}"/>')
    parts.append(text(904, 294, "compile", size=9, fill=ACCENT, spacing="1"))

    # Right: native objects
    parts.append(text(952, 159, "NATIVE PPTX", size=10.5, fill=DIM, spacing="2"))
    cards = [
        ("shape", "rounded rect"),
        ("text", "editable run"),
        ("chart", "native bars"),
    ]
    for i, (title, sub) in enumerate(cards):
        y = 174 + i * 90
        parts.append(
            f'<rect x="952" y="{y}" width="150" height="76" rx="2" fill="#101010" '
            f'stroke="{LINE}"/>'
        )
        parts.append(text(964, y + 18, title.upper(), size=9, fill=DIM, spacing="1.5"))
        if i == 0:
            parts.append(
                f'<rect x="964" y="{y + 30}" width="54" height="28" rx="6" '
                f'fill="none" stroke="{ACCENT}" stroke-width="1.5"/>'
            )
            parts.append(f'<rect x="1030" y="{y + 36}" width="54" height="3" fill="{DIM}"/>')
            parts.append(f'<rect x="1030" y="{y + 46}" width="38" height="3" fill="{DIM}"/>')
        elif i == 1:
            parts.append(text(964, y + 56, "Aa", size=28, fill=INK, weight="700"))
            parts.append(f'<rect x="1014" y="{y + 36}" width="70" height="4" fill="{MUTED}"/>')
            parts.append(f'<rect x="1014" y="{y + 48}" width="54" height="4" fill="{DIM}"/>')
        else:
            for j, h in enumerate((20, 34, 26, 40)):
                parts.append(
                    f'<rect x="{966 + j * 13}" y="{y + 60 - h}" width="7" height="{h}" '
                    f'fill="{ACCENT}" opacity="{0.45 + j * 0.14:.2f}"/>'
                )
            parts.append(f'<line x1="964" y1="{y + 60}" x2="1024" y2="{y + 60}" '
                         f'stroke="{LINE}"/>')
            parts.append(text(1034, y + 56, sub, size=9, fill=MUTED))

    # Compile rail
    rail_y = 480
    parts.append(f'<line x1="664" y1="{rail_y + 16}" x2="1112" y2="{rail_y + 16}" '
                 f'stroke="{LINE}"/>')
    nodes = [("SVG", 664, 68), ("DrawingML", 760, 136), (".pptx", 924, 76)]
    for i, (label, x, w) in enumerate(nodes):
        accent = i == 1
        parts.append(
            f'<rect x="{x}" y="{rail_y}" width="{w}" height="32" rx="2" '
            f'fill="{BG}" stroke="{ACCENT if accent else LINE}"/>'
        )
        parts.append(text(x + 12, rail_y + 21, label, size=11,
                          fill=ACCENT if accent else MUTED, spacing="1"))
    for x in (740, 904):
        parts.append(f'<line x1="{x}" y1="{rail_y + 16}" x2="{x + 12}" y2="{rail_y + 16}" '
                     f'stroke="{DIM}"/>')
        parts.append(f'<path d="M{x + 12} {rail_y + 16}l-6 -3v6z" fill="{DIM}"/>')

    parts.append(text(664, 540, "same slide, not a screenshot", size=11, fill=DIM))
    parts.append(text(1112, 540, "01 / 01", size=11, fill=DIM, anchor="end"))

    parts.append("</svg>")
    return "".join(parts)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true",
                        help="also write a WebP preview into the temp directory")
    args = parser.parse_args()

    svg = build_svg()
    svg_path = HERE / "cover.svg"
    svg_path.write_text(svg, encoding="utf-8")

    BUNDLE_IMAGES.mkdir(parents=True, exist_ok=True)
    jpg_path = BUNDLE_IMAGES / "cover.jpg"
    svg_to_jpeg(svg_path, jpg_path, width=1200, quality=85)

    if args.preview:
        preview = Path(tempfile.gettempdir()) / "ppt-master-cover-preview.webp"
        svg_to_webp(svg_path, preview, width=1200, quality=88)
        print(f"preview: {preview}")

    print(f"svg: {svg_path}")
    print(f"jpg: {jpg_path}")


if __name__ == "__main__":
    main()
