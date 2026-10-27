#!/usr/bin/env python3
"""Generate the terminal-style cover for the edge AI platform article.

A light "paper terminal" in the Claude palette: cream Pampas surface, Crail
terracotta accent, ink text. The right pane prints the five-layer platform
stack, a bounded deque buffer gauge and the agent governance line. The SVG
source is kept next to this script; the JPEG is written into the page bundle,
so no PNG ever reaches Hugo.

Usage:
    python3 scripts/edge-ai-platform-ppt169/make_cover.py
    python3 scripts/edge-ai-platform-ppt169/make_cover.py --preview
"""

import argparse
import html
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BUNDLE_IMAGES = ROOT / "content/zh-tw/projects/edge-ai-platform-ppt169/images"

sys.path.insert(0, str(ROOT / "scripts"))
from image_utils import svg_to_jpeg  # noqa: E402

W, H = 1200, 630

MONO = "'SF Mono','Menlo','DejaVu Sans Mono',monospace"
SANS = "'PingFang TC','Noto Sans TC','Heiti TC',sans-serif"

BG = "#F4F3EE"
PANEL = "#FFFFFF"
BAR = "#EDEAE2"
LINE = "#DCD7CC"
INK = "#181715"
MID = "#4A4945"
MUTED = "#6B6A65"
DIM = "#8C8983"
ACCENT = "#C15F3C"
ACCENT_TEXT = "#B0522F"
ACCENT_SOFT = "#D4896E"
GREEN = "#7E9A70"
GOLD = "#D8A15F"


def esc(value):
    return html.escape(str(value), quote=True)


def text(x, y, value, *, size=12, fill=MUTED, family=MONO, weight=None,
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


def line(x1, y1, x2, y2, *, stroke=LINE, width=1, dash=None, opacity=None):
    attrs = [f'x1="{x1}"', f'y1="{y1}"', f'x2="{x2}"', f'y2="{y2}"',
             f'stroke="{stroke}"', f'stroke-width="{width}"']
    if dash:
        attrs.append(f'stroke-dasharray="{dash}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    return f'<line {" ".join(attrs)}/>'


def rect(x, y, w, h, *, fill="none", stroke=None, width=1, rx=None,
         opacity=None):
    attrs = [f'x="{x}"', f'y="{y}"', f'width="{w}"', f'height="{h}"',
             f'fill="{fill}"']
    if stroke:
        attrs.append(f'stroke="{stroke}"')
        attrs.append(f'stroke-width="{width}"')
    if rx is not None:
        attrs.append(f'rx="{rx}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    return f'<rect {" ".join(attrs)}/>'


def chip(x, y, label, *, width, accent=False):
    border = ACCENT if accent else LINE
    color = ACCENT_TEXT if accent else MUTED
    return (
        rect(x, y, width, 32, fill=PANEL, stroke=border, rx=2)
        + text(x + 12, y + 21, label, size=10.5, fill=color, spacing="1")
    )


LAYERS = [
    ("L1", "ui", "react 18 · mui · react flow"),
    ("L2", "api", "flask · blueprints"),
    ("L3", "analytics", "rms/fft · one-class svm · dtw · pca"),
    ("L4", "edge", "on-device inference"),
    ("L5", "data", "sqlite · model files"),
]


def build_svg():
    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}">'
    )
    parts.append(
        "<title>edge-ai-platform-01 — Semiconductor equipment Edge AI "
        "platform</title>"
    )
    parts.append(
        "<desc>Light terminal-style cover in the Claude palette: a five-layer "
        "platform stack, a bounded deque buffer and governed agent tools, "
        "printed on a cream surface.</desc>"
    )

    parts.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    parts.append(
        '<pattern id="dotgrid" width="24" height="24" '
        'patternUnits="userSpaceOnUse">'
        f'<circle cx="1" cy="1" r="1" fill="{INK}" opacity="0.07"/>'
        "</pattern>"
    )
    parts.append(f'<rect width="{W}" height="{H}" fill="url(#dotgrid)"/>')
    parts.append(
        '<radialGradient id="wash" cx="0.85" cy="0.05" r="0.7">'
        f'<stop offset="0" stop-color="{ACCENT_SOFT}" stop-opacity="0.22"/>'
        f'<stop offset="1" stop-color="{ACCENT_SOFT}" stop-opacity="0"/>'
        "</radialGradient>"
    )
    parts.append(f'<rect width="{W}" height="{H}" fill="url(#wash)"/>')

    # Window
    parts.append(rect(64, 52, 1088, 542, fill=INK, rx=14, opacity=0.08))
    parts.append(
        rect(56, 44, 1088, 542, fill=PANEL, stroke=LINE, width=1, rx=12)
    )
    parts.append(
        f'<path d="M56 56a12 12 0 0 1 12-12h1064a12 12 0 0 1 12 12v28H56z" '
        f'fill="{BAR}"/>'
    )
    parts.append(line(56, 84, 1144, 84))

    parts.append(f'<circle cx="88" cy="64" r="5" fill="{ACCENT}"/>')
    parts.append(f'<circle cx="112" cy="64" r="5" fill="{GOLD}"/>')
    parts.append(f'<circle cx="136" cy="64" r="5" fill="{GREEN}"/>')
    parts.append(text(160, 69, "edge-ai-platform-01 — phm/stack", size=13.5,
                      fill=MUTED))
    parts.append(f'<circle cx="1018" cy="64" r="4" fill="{ACCENT}"/>')
    parts.append(text(1032, 69, "RUNNING", size=10.5, fill=ACCENT_TEXT,
                      spacing="2"))

    # Prompt
    parts.append(text(100, 138, "$", size=15, fill=ACCENT_TEXT))
    parts.append(text(122, 138, "docker compose up -d edge-ai-platform", size=12.5,
                      fill=INK))

    # Wordmark
    parts.append(text(96, 310, "EDGE", size=118, fill=INK, weight="700",
                      spacing="-2"))
    parts.append(text(96, 404, "PLATFORM", size=82, fill=INK, weight="700"))
    parts.append(
        '<linearGradient id="accentBar" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{ACCENT}"/>'
        f'<stop offset="1" stop-color="{ACCENT}" stop-opacity="0.1"/>'
        "</linearGradient>"
    )
    parts.append(rect(100, 428, 340, 5, fill="url(#accentBar)"))

    parts.append(text(98, 476, "從感測器到智慧決策的端到端平台", size=23,
                      fill=MID, family=SANS))
    parts.append(text(98, 504, "React · Flask · SQLite · one edge node",
                      size=12, fill=MUTED))

    parts.append(chip(98, 520, "5 LAYERS", width=88, accent=True))
    parts.append(chip(198, 520, "FLASK", width=66))
    parts.append(chip(276, 520, "SQLITE", width=74))
    parts.append(chip(362, 520, "DOCKER COMPOSE", width=134))

    # Divider
    parts.append(line(608, 108, 608, 560))

    # Right pane: platform stack
    parts.append(text(644, 136, "PLATFORM STACK", size=10.5, fill=DIM,
                      spacing="2.5"))
    parts.append(text(1112, 136, "5 LAYERS", size=10, fill=DIM,
                      spacing="1.5", anchor="end"))

    parts.append(line(652, 188, 652, 358, stroke=LINE, width=2))

    y = 190
    for tag, name, detail in LAYERS:
        parts.append(rect(646, y - 8, 12, 12, fill=ACCENT, rx=2))
        parts.append(text(672, y, tag, size=10.5, fill=ACCENT_TEXT,
                          spacing="1"))
        parts.append(text(712, y, name, size=13, fill=INK))
        parts.append(text(812, y, detail, size=11, fill=MUTED))
        y += 42

    parts.append(line(644, 392, 1112, 392))

    # Buffer gauge
    parts.append(text(644, 420, "DEQUE 5000", size=10.5, fill=DIM,
                      spacing="2.5"))
    parts.append(text(1112, 420, "FLUSH 500 / 5 S", size=10, fill=DIM,
                      spacing="1.5", anchor="end"))

    x = 644
    for i in range(24):
        if i < 11:
            parts.append(rect(x, 436, 15, 26, fill=ACCENT, rx=2))
        elif i == 11:
            parts.append(rect(x, 436, 15, 26, fill=ACCENT_SOFT, rx=2,
                              opacity=0.55))
        else:
            parts.append(rect(x, 436, 15, 26, fill="none", stroke=LINE,
                              rx=2))
        x += 19

    parts.append(text(644, 482, "high-frequency I/O stays off the query path",
                      size=11, fill=MUTED))
    parts.append(text(644, 520, "agent", size=11.5, fill=ACCENT_TEXT))
    parts.append(text(696, 520, "tools allowlisted · authz · audit", size=11.5,
                      fill=MUTED))
    parts.append(text(644, 550, "✓ one node · docker compose · no cluster",
                      size=11, fill=MUTED))

    parts.append("</svg>")
    return "".join(parts)


def main():
    parser = argparse.ArgumentParser(
        description="Build the edge AI platform cover."
    )
    parser.add_argument("--preview", action="store_true",
                        help="render to a temp directory instead of the bundle")
    args = parser.parse_args()

    svg_path = HERE / "cover.svg"
    svg_path.write_text(build_svg(), encoding="utf-8")

    if args.preview:
        out_dir = Path(tempfile.mkdtemp(prefix="edge-cover-"))
        dest = out_dir / "cover.jpg"
    else:
        dest = BUNDLE_IMAGES / "cover.jpg"

    svg_to_jpeg(svg_path, dest, width=W, quality=85)
    print(f"wrote {svg_path.relative_to(ROOT)}")
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()
