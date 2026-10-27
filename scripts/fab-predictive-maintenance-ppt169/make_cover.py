#!/usr/bin/env python3
"""Generate the terminal-style cover for the fab predictive maintenance article.

A dark TSMC-red terminal window streams a PHM pipeline (ingest, detect, RUL,
canary rollout, agent) with an anomaly burst in the signal strip. The SVG
source is kept next to this script so the cover stays editable; the JPEG is
written into the project's page bundle, so no PNG ever reaches Hugo.

Usage:
    python3 scripts/fab-predictive-maintenance-ppt169/make_cover.py
    python3 scripts/fab-predictive-maintenance-ppt169/make_cover.py --preview
"""

import argparse
import html
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BUNDLE_IMAGES = (
    ROOT / "content/zh-tw/projects/fab-predictive-maintenance-ppt169/images"
)

sys.path.insert(0, str(ROOT / "scripts"))
from image_utils import svg_to_jpeg  # noqa: E402

W, H = 1200, 630

MONO = "'SF Mono','Menlo','DejaVu Sans Mono',monospace"
SANS = "'PingFang TC','Noto Sans TC','Heiti TC',sans-serif"

BG = "#0B0909"
PANEL = "#141011"
BAR = "#1B1516"
LINE = "#302325"
INK = "#FAF9F5"
MID = "#D8D2CC"
MUTED = "#A09D95"
DIM = "#8A837E"
ACCENT = "#DA291C"
ACCENT_TEXT = "#FF5C4A"
AMBER = "#E8A33D"
ERR = "#FF4B3E"
GREEN = "#4E9A6B"


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
        rect(x, y, width, 32, fill=BAR, stroke=border, rx=2)
        + text(x + 12, y + 21, label, size=10.5, fill=color, spacing="1")
    )


ROWS = [
    ("00:00.4", "ingest", "20 dev · 3 ch · 2 kHz", INK),
    ("00:00.9", "stream", "deque 500 / 5 s", INK),
    ("00:01.2", "detect", "isolation forest → autoencoder", INK),
    ("00:01.6", "score", "0.93  ▲ anomaly", AMBER),
    ("00:02.1", "rul", "weibull · lstm    7 d / 30 d", INK),
    ("00:02.9", "deploy", "canary 5% → 20% → 100%", INK),
    ("00:03.4", "agent", "allowlist · audit · rollback", INK),
]

BARS = [30, 34, 26, 38, 31, 44, 27, 33, 40, 29, 36, 31, 47, 42, 34, 58,
        76, 92, 84, 66, 50, 38, 33, 30]
SPIKES = {16: AMBER, 17: ERR, 18: AMBER}


def build_svg():
    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}">'
    )
    parts.append(
        "<title>Sentinel-07 — Smart Fab Edge AI predictive maintenance "
        "pipeline</title>"
    )
    parts.append(
        "<desc>Terminal-style cover: a PHM pipeline log streams ingest, "
        "two-stage detection, RUL, canary rollout and a governed agent, with "
        "a red anomaly burst in the signal strip.</desc>"
    )

    parts.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    parts.append(
        '<pattern id="dotgrid" width="24" height="24" '
        'patternUnits="userSpaceOnUse">'
        '<circle cx="1" cy="1" r="1" fill="#FFFFFF" opacity="0.05"/>'
        "</pattern>"
    )
    parts.append(f'<rect width="{W}" height="{H}" fill="url(#dotgrid)"/>')
    parts.append(
        '<radialGradient id="glow" cx="0.55" cy="0.9" r="0.65">'
        f'<stop offset="0" stop-color="{ACCENT}" stop-opacity="0.16"/>'
        f'<stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/>'
        "</radialGradient>"
    )
    parts.append(f'<rect width="{W}" height="{H}" fill="url(#glow)"/>')

    # Window
    parts.append(rect(64, 52, 1088, 542, fill="#000000", rx=14, opacity=0.5))
    parts.append(
        rect(56, 44, 1088, 542, fill=PANEL, stroke=LINE, width=1, rx=12)
    )
    parts.append(
        f'<path d="M56 56a12 12 0 0 1 12-12h1064a12 12 0 0 1 12 12v28H56z" '
        f'fill="{BAR}"/>'
    )
    parts.append(line(56, 84, 1144, 84))

    parts.append(f'<circle cx="88" cy="64" r="5" fill="{ACCENT_TEXT}"/>')
    parts.append(f'<circle cx="112" cy="64" r="5" fill="{AMBER}"/>')
    parts.append(f'<circle cx="136" cy="64" r="5" fill="{GREEN}"/>')
    parts.append(text(160, 69, "sentinel-07 — phm/pipeline", size=13.5,
                      fill=MUTED))
    parts.append(f'<circle cx="1000" cy="64" r="4" fill="{ACCENT_TEXT}"/>')
    parts.append(text(1014, 69, "STREAMING", size=10.5, fill=ACCENT_TEXT,
                      spacing="2"))

    # Prompt
    parts.append(text(100, 138, "$", size=15, fill=ACCENT_TEXT))
    parts.append(text(122, 138, "sentinel watch --devices 20 --ch 3 --rate 2k",
                      size=12.5, fill=INK))

    # Wordmark
    parts.append(text(96, 310, "PHM", size=118, fill=INK, weight="700",
                      spacing="-2"))
    parts.append(text(96, 408, "EDGE", size=82, fill=INK, weight="700"))
    parts.append(text(316, 408, "AI", size=82, fill=INK, weight="700"))
    parts.append(
        '<linearGradient id="accentBar" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{ACCENT}"/>'
        f'<stop offset="1" stop-color="{ACCENT}" stop-opacity="0.1"/>'
        "</linearGradient>"
    )
    parts.append(rect(100, 430, 300, 5, fill="url(#accentBar)"))

    parts.append(text(98, 476, "從預測性維護到自主決策 Agent", size=23,
                      fill=MID, family=SANS))
    parts.append(text(98, 504, "Two-stage detection · RUL · canary rollout",
                      size=12, fill=MUTED))

    parts.append(chip(98, 520, "20 DEVICES", width=104, accent=True))
    parts.append(chip(214, 520, "3 CH · 2 KHZ", width=122))
    parts.append(chip(348, 520, "41.5 GB/DAY", width=114))
    parts.append(chip(474, 520, "IF→AE", width=84))

    # Divider
    parts.append(line(608, 108, 608, 560))

    # Right pane: pipeline log
    parts.append(text(644, 136, "PHM PIPELINE", size=10.5, fill=DIM,
                      spacing="2.5"))
    parts.append(text(1112, 136, "3 EVENT BURSTS", size=10, fill=AMBER,
                      spacing="1.5", anchor="end"))

    y = 186
    for clock, tag, value, color in ROWS:
        parts.append(text(644, y, clock, size=11, fill=DIM))
        parts.append(text(706, y, tag, size=11, fill=MUTED))
        parts.append(text(812, y, value, size=12, fill=color))
        y += 36

    parts.append(line(644, 426, 1112, 426))

    # Signal strip
    parts.append(text(644, 452, "SIGNAL · 2 KHZ", size=10.5, fill=DIM,
                      spacing="2.5"))
    parts.append(text(1112, 452, "t → 43 s", size=10, fill=DIM,
                      spacing="1.5", anchor="end"))

    anomaly_x = 644 + 17 * 19 + 6
    parts.append(line(anomaly_x, 462, anomaly_x, 538, stroke=ERR, width=1,
                      dash="3 4", opacity=0.35))

    base = 538
    peak = max(BARS)
    x = 644
    for i, h in enumerate(BARS):
        color = SPIKES.get(i, ACCENT)
        opacity = 1.0 if i in SPIKES else 0.30 + 0.45 * (h / peak)
        parts.append(rect(x, base - h, 12, h, fill=color, rx=1,
                          opacity=opacity))
        x += 19
    parts.append(line(644, base, 1096, base))

    parts.append(text(644, 562, "0 s", size=9.5, fill=DIM))
    parts.append(text(1096, 562, "43 s", size=9.5, fill=DIM, anchor="end"))

    parts.append("</svg>")
    return "".join(parts)


def main():
    parser = argparse.ArgumentParser(
        description="Build the fab predictive maintenance cover."
    )
    parser.add_argument("--preview", action="store_true",
                        help="render to a temp directory instead of the bundle")
    args = parser.parse_args()

    svg_path = HERE / "cover.svg"
    svg_path.write_text(build_svg(), encoding="utf-8")

    if args.preview:
        out_dir = Path(tempfile.mkdtemp(prefix="fab-cover-"))
        dest = out_dir / "cover.jpg"
    else:
        dest = BUNDLE_IMAGES / "cover.jpg"

    svg_to_jpeg(svg_path, dest, width=W, quality=85)
    print(f"wrote {svg_path.relative_to(ROOT)}")
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()
