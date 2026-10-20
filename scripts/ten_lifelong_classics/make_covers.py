#!/usr/bin/env python3
"""Generate the 11 original covers for the ten-classics essay.

Every cover is drawn from scratch with basic SVG shapes. No film stills,
posters, logos, or characters are used.

Usage:
    python3 scripts/ten_lifelong_classics/make_covers.py
    python3 scripts/ten_lifelong_classics/make_covers.py --preview
    python3 scripts/ten_lifelong_classics/make_covers.py --render
"""

import argparse
import html
import math
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = Path(__file__).resolve().parent
BUNDLE_IMAGES = ROOT / "content/zh-tw/posts/ten_lifelong_classics/images"
PREVIEW_DIR = Path(tempfile.gettempdir()) / "ten_classics_preview"

sys.path.insert(0, str(ROOT / "scripts"))
from image_utils import svg_to_jpeg, svg_to_webp  # noqa: E402

W, H = 1200, 630
SANS = "'PingFang TC','Noto Sans TC','Heiti TC',sans-serif"
SERIF = "'Songti TC','Noto Serif TC','Songti SC',serif"
MONO = "'SF Mono','Menlo','DejaVu Sans Mono',monospace"
DISPLAY = "'Avenir Next','Helvetica Neue','Arial',sans-serif"


def esc(value):
    return html.escape(str(value), quote=True)


def dotgrid(color, opacity, step=26):
    return (
        f'<pattern id="dots" width="{step}" height="{step}" '
        f'patternUnits="userSpaceOnUse">'
        f'<circle cx="1" cy="1" r="1" fill="{color}" opacity="{opacity}"/>'
        f"</pattern>"
        f'<rect width="{W}" height="{H}" fill="url(#dots)"/>'
    )


def scanlines(color, opacity, step=4):
    return (
        f'<pattern id="scan" width="4" height="{step}" '
        f'patternUnits="userSpaceOnUse">'
        f'<rect width="4" height="1" fill="{color}" opacity="{opacity}"/>'
        f"</pattern>"
        f'<rect width="{W}" height="{H}" fill="url(#scan)"/>'
    )


def stars(seed, count, x0, x1, y0, y1, color, maxr=1.7):
    rng = random.Random(seed)
    out = []
    for _ in range(count):
        x = rng.uniform(x0, x1)
        y = rng.uniform(y0, y1)
        r = rng.uniform(0.4, maxr)
        o = rng.uniform(0.15, 0.9)
        out.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" '
            f'fill="{color}" opacity="{o:.2f}"/>'
        )
    return "".join(out)


# --------------------------------------------------------------------------
# Motifs
# --------------------------------------------------------------------------


def motif_black_mirror(c):
    accent = c["accent"]
    defs = f"""
    <linearGradient id="bmglass" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#1A1A1F"/>
      <stop offset=".52" stop-color="#08080A"/>
      <stop offset="1" stop-color="#121216"/>
    </linearGradient>
    <linearGradient id="bmsheen" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{accent}" stop-opacity=".18"/>
      <stop offset=".48" stop-color="{accent}" stop-opacity="0"/>
    </linearGradient>
    """
    body = [
        f'<rect x="690" y="112" width="402" height="422" rx="10" '
        f'fill="url(#bmglass)" stroke="#2E2E34" stroke-width="1.4"/>',
        f'<rect x="690" y="112" width="402" height="422" rx="10" '
        f'fill="url(#bmsheen)"/>',
        f'<path d="M700 116 L1080 116 L790 522 L700 522 Z" fill="#FFFFFF" opacity=".025"/>',
        # scan line glow
        f'<rect x="690" y="300" width="402" height="26" fill="{accent}" opacity=".05"/>',
        f'<rect x="690" y="306" width="402" height="10" fill="{accent}" opacity=".13"/>',
        f'<rect x="690" y="309" width="402" height="2.5" fill="{accent}" opacity=".95"/>',
    ]
    rng = random.Random(11)
    for _ in range(9):
        x = rng.uniform(710, 1040)
        y = rng.choice([284, 316, 328])
        s = rng.choice([10, 14, 18])
        body.append(
            f'<rect x="{x:.0f}" y="{y}" width="{s}" height="{s}" '
            f'fill="{accent}" opacity="{rng.uniform(0.18, 0.7):.2f}"/>'
        )
    body += [
        f'<path d="M812 534 L832 470 L828 430" fill="none" stroke="#6B6B75" stroke-width="1.2" opacity=".55"/>',
        f'<path d="M832 470 L868 452" fill="none" stroke="#6B6B75" stroke-width="1" opacity=".45"/>',
        f'<path d="M1016 534 L996 486 L1004 452" fill="none" stroke="#6B6B75" stroke-width="1.2" opacity=".5"/>',
        f'<text x="1064" y="512" text-anchor="end" font-family="{MONO}" '
        f'font-size="10" letter-spacing="2.4" fill="#6B6B75">SIGNAL // LOST</text>',
    ]
    return defs, "".join(body)


def motif_2001(c):
    ink = c["ink"]
    accent = c["accent"]
    body = [
        f'<circle cx="912" cy="292" r="152" fill="{accent}"/>',
        f'<ellipse cx="912" cy="292" rx="268" ry="66" fill="none" '
        f'stroke="{ink}" stroke-width="1.2" opacity=".22" transform="rotate(-17 912 292)"/>',
        f'<circle cx="676" cy="330" r="3.4" fill="{ink}" opacity=".55"/>',
        f'<polygon points="884,146 1006,146 1006,494 884,494" fill="#0A0A0A"/>',
        f'<polygon points="884,146 844,126 966,126 1006,146" fill="#1F1F1F"/>',
        f'<polygon points="1006,146 1046,126 1046,474 1006,494" fill="#000000"/>',
        f'<line x1="884" y1="150" x2="884" y2="490" stroke="#FFFFFF" stroke-width="1" opacity=".12"/>',
        f'<rect x="884" y="474" width="122" height="20" fill="#000000" opacity=".22"/>',
    ]
    rng = random.Random(21)
    for _ in range(26):
        x = rng.uniform(610, 1150)
        y = rng.uniform(110, 540)
        if 820 < x < 1060 and 110 < y < 510:
            continue
        body.append(
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rng.choice([0.8, 1, 1.4])}" '
            f'fill="{ink}" opacity="{rng.uniform(0.08, 0.3):.2f}"/>'
        )
    body += [
        f'<line x1="640" y1="536" x2="1140" y2="536" stroke="{ink}" stroke-width="1" opacity=".18"/>',
        f'<text x="640" y="558" font-family="{MONO}" font-size="10" '
        f'letter-spacing="3" fill="{ink}" opacity=".55">MONOLITH / 1 : 4 : 9</text>',
    ]
    return "", "".join(body)


def motif_akira(c):
    accent = c["accent"]
    cx, cy = 908, 322
    body = [f'<circle cx="{cx}" cy="{cy}" r="238" fill="{accent}" opacity=".05"/>']
    rng = random.Random(31)
    for i in range(44):
        angle = (i / 44) * math.tau
        r1 = rng.uniform(238, 262)
        r2 = 300
        x1 = cx + math.cos(angle) * r1
        y1 = cy + math.sin(angle) * r1
        x2 = cx + math.cos(angle) * r2
        y2 = cy + math.sin(angle) * r2
        body.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{accent}" stroke-width="{rng.choice([1, 2, 3])}" '
            f'opacity="{rng.uniform(0.12, 0.5):.2f}"/>'
        )
    body += [
        f'<circle cx="{cx}" cy="{cy}" r="194" fill="none" stroke="{accent}" stroke-width="27"/>',
        f'<circle cx="{cx}" cy="{cy}" r="194" fill="none" stroke="#FF6B72" stroke-width="2" opacity=".55"/>',
        f'<circle cx="{cx}" cy="{cy}" r="150" fill="none" stroke="{accent}" stroke-width="1.6" opacity=".5"/>',
    ]
    for i in range(12):
        angle = (i / 12) * math.tau + 0.13
        x1 = cx + math.cos(angle) * 72
        y1 = cy + math.sin(angle) * 72
        x2 = cx + math.cos(angle) * 150
        y2 = cy + math.sin(angle) * 150
        body.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{accent}" stroke-width="4" opacity=".62"/>'
        )
    body += [
        f'<circle cx="{cx}" cy="{cy}" r="56" fill="{accent}"/>',
        f'<circle cx="{cx}" cy="{cy}" r="30" fill="#0A0A0A"/>',
        f'<circle cx="{cx}" cy="{cy}" r="9" fill="#FF6B72"/>',
        f'<path d="M640 500 C 720 470, 780 520, 840 500" fill="none" '
        f'stroke="{accent}" stroke-width="1.4" opacity=".3"/>',
        f'<text x="640" y="556" font-family="{MONO}" font-size="10" '
        f'letter-spacing="4" fill="#8A8A8A">NEO-TOKYO / 1988</text>',
    ]
    return "", "".join(body)


def motif_blade_runner(c):
    amber, cyan, pink = c["accent"], c["accent2"], c["accent3"]
    rng = random.Random(41)
    body = []
    # rain
    for _ in range(110):
        x = rng.uniform(610, 1160)
        y = rng.uniform(90, 560)
        length = rng.uniform(14, 62)
        color = rng.choice([cyan, "#DCE9F7", amber])
        body.append(
            f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x - 3:.1f}" y2="{y + length:.1f}" '
            f'stroke="{color}" stroke-width="{rng.choice([1, 1, 1.5])}" '
            f'opacity="{rng.uniform(0.08, 0.32):.2f}"/>'
        )
    # skyline
    x = 610
    while x < 1180:
        width = rng.choice([16, 22, 28, 34])
        top = rng.uniform(340, 470)
        body.append(
            f'<rect x="{x}" y="{top:.0f}" width="{width}" height="{560 - top:.0f}" '
            f'fill="#0B0D12" stroke="#1B202B" stroke-width="1"/>'
        )
        for wy in range(int(top) + 12, 548, 16):
            if rng.random() < 0.55:
                body.append(
                    f'<rect x="{x + 5}" y="{wy}" width="{rng.choice([2, 3])}" '
                    f'height="3" fill="{rng.choice([amber, cyan, pink])}" '
                    f'opacity="{rng.uniform(0.25, 0.75):.2f}"/>'
                )
        x += width + rng.choice([3, 6, 10])
    # neon signs
    for nx, ny, nh, color in [
        (760, 250, 132, amber),
        (948, 214, 170, pink),
        (1044, 296, 96, cyan),
    ]:
        body += [
            f'<rect x="{nx - 4}" y="{ny - 4}" width="26" height="{nh + 8}" '
            f'fill="{color}" opacity=".08"/>',
            f'<rect x="{nx}" y="{ny}" width="18" height="{nh}" fill="none" '
            f'stroke="{color}" stroke-width="1.6" opacity=".8"/>',
        ]
        for i in range(5):
            body.append(
                f'<line x1="{nx + 4}" y1="{ny + 16 + i * 20}" x2="{nx + 14}" '
                f'y2="{ny + 16 + i * 20}" stroke="{color}" stroke-width="2" opacity=".55"/>'
            )
    # wet street + reflections
    body += [
        f'<rect x="600" y="560" width="580" height="70" fill="#05060A"/>',
        f'<line x1="600" y1="560" x2="1180" y2="560" stroke="{amber}" stroke-width="1" opacity=".35"/>',
    ]
    for _ in range(28):
        rx = rng.uniform(620, 1160)
        rh = rng.uniform(8, 44)
        color = rng.choice([amber, cyan, pink])
        body.append(
            f'<line x1="{rx:.0f}" y1="566" x2="{rx:.0f}" y2="{566 + rh:.0f}" '
            f'stroke="{color}" stroke-width="{rng.choice([2, 3])}" '
            f'opacity="{rng.uniform(0.06, 0.22):.2f}"/>'
        )
    body += [
        f'<path d="M848 566 L878 536 L908 566 Z" fill="#EDEAE3" opacity=".82"/>',
        f'<path d="M878 536 L878 566" stroke="#08090C" stroke-width="1.2" opacity=".5"/>',
    ]
    return "", "".join(body)


def motif_interstellar(c):
    accent = c["accent"]
    cx, cy = 902, 318
    body = [stars(51, 150, 600, 1170, 70, 560, "#DCE9F7", 1.5)]
    body.append(
        f'<g transform="rotate(-15 {cx} {cy})">'
        f'<ellipse cx="{cx}" cy="{cy}" rx="264" ry="62" fill="none" stroke="{accent}" stroke-width="1.2" opacity=".28"/>'
        f'<ellipse cx="{cx}" cy="{cy}" rx="236" ry="52" fill="none" stroke="{accent}" stroke-width="4" opacity=".38"/>'
        f'<ellipse cx="{cx}" cy="{cy}" rx="205" ry="42" fill="none" stroke="{accent}" stroke-width="11" opacity=".78"/>'
        f'<ellipse cx="{cx}" cy="{cy}" rx="172" ry="33" fill="none" stroke="#FFE2C0" stroke-width="2.5" opacity=".65"/>'
        f"</g>"
    )
    body += [
        f'<circle cx="{cx}" cy="{cy}" r="104" fill="#02040A"/>',
        f'<circle cx="{cx}" cy="{cy}" r="104" fill="none" stroke="{accent}" stroke-width="1.8" opacity=".85"/>',
        f'<path d="M 826 246 A 104 104 0 0 1 978 246" fill="none" stroke="#FFF1DE" stroke-width="2" opacity=".55"/>',
        f'<circle cx="700" cy="402" r="3" fill="#DCE9F7"/>',
        f'<path d="M676 408 L700 402" stroke="#DCE9F7" stroke-width="1.2" opacity=".7"/>',
        f'<path d="M700 402 L714 412 L702 416" fill="none" stroke="#DCE9F7" stroke-width="1" opacity=".45"/>',
        f'<text x="640" y="556" font-family="{MONO}" font-size="10" letter-spacing="3" '
        f'fill="#7E93AD">GARGANTUA / r = 1.000</text>',

    ]
    return "", "".join(body)


def motif_dune(c):
    ink, accent = c["ink"], c["accent"]
    body = [
        f'<circle cx="1010" cy="208" r="90" fill="#F8E7C0" opacity=".92"/>',
        f'<circle cx="1048" cy="186" r="22" fill="#D9A05B" opacity=".55"/>',
        f'<path d="M600 630 L600 486 C 700 438 782 470 854 500 C 934 534 1030 512 1200 420 L1200 630 Z" fill="#D09352"/>',
        f'<path d="M600 630 L600 536 C 706 492 796 522 872 548 C 952 576 1060 548 1200 478 L1200 630 Z" fill="#B5763C"/>',
        f'<path d="M600 630 L600 584 C 714 548 812 574 900 596 C 1006 622 1090 604 1200 548 L1200 630 Z" fill="#8E5629"/>',
        f'<path d="M600 486 C 700 438 782 470 854 500 C 934 534 1030 512 1200 420" fill="none" stroke="#F2CE96" stroke-width="2" opacity=".65"/>',
        f'<path d="M600 536 C 706 492 796 522 872 548 C 952 576 1060 548 1200 478" fill="none" stroke="#E0AE6D" stroke-width="1.4" opacity=".5"/>',
    ]
    # tiny figure on the first ridge
    body += [
        f'<g stroke="{ink}" stroke-width="2.4" stroke-linecap="round">',
        f'<circle cx="868" cy="486" r="4.2" fill="{ink}" stroke="none"/>',
        f'<line x1="868" y1="492" x2="868" y2="508"/>',
        f'<line x1="868" y1="498" x2="857" y2="506"/>',
        f'<line x1="868" y1="498" x2="879" y2="504"/>',
        f'<line x1="868" y1="508" x2="860" y2="520"/>',
        f'<line x1="868" y1="508" x2="876" y2="520"/>',
        f"</g>",
        f'<path d="M640 168 q 22 -16 44 0 q -22 -7 -44 0 Z" fill="{ink}" opacity=".5"/>',
        f'<path d="M712 198 q 18 -13 36 0 q -18 -6 -36 0 Z" fill="{ink}" opacity=".38"/>',
        f'<text x="640" y="556" font-family="{MONO}" font-size="10" letter-spacing="3" '
        f'fill="{ink}" opacity=".62">ARRAKIS / SPICE / 10191</text>',
    ]
    return "", "".join(body)


def motif_matrix(c):
    accent, bright = c["accent"], c["accent2"]
    rng = random.Random(71)
    glyphs = "01010101{}[]<>/\\|=+*"
    body = [
        f'<rect x="600" y="0" width="600" height="630" fill="url(#mxfall)" opacity=".55"/>'
    ]
    for col in range(22):
        x = 626 + col * 25
        y = rng.uniform(124, 268)
        count = rng.randint(9, 19)
        for i in range(count):
            ch = rng.choice(glyphs)
            opacity = max(0.06, 0.86 - i * 0.055)
            color = bright if i == 0 else accent
            body.append(
                f'<text x="{x}" y="{y + i * 24:.0f}" font-family="{MONO}" '
                f'font-size="15" fill="{color}" opacity="{opacity:.2f}">{esc(ch)}</text>'
            )
    body += [
        f'<rect x="588" y="0" width="1.5" height="630" fill="{accent}" opacity=".35"/>',
        f'<rect x="748" y="0" width="2" height="630" fill="{accent}" opacity=".5"/>',
        f'<rect x="744" y="238" width="10" height="150" fill="{accent}" opacity=".07"/>',
        f'<text x="1160" y="582" text-anchor="end" font-family="{MONO}" font-size="9.5" '
        f'letter-spacing="2.6" fill="{accent}" opacity=".55">FOLLOW THE WHITE RABBIT</text>',
    ]
    return (
        '<linearGradient id="mxfall" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#00FF66" stop-opacity=".05"/>'
        '<stop offset=".6" stop-color="#00FF66" stop-opacity=".12"/>'
        '<stop offset="1" stop-color="#00FF66" stop-opacity=".22"/>'
        "</linearGradient>",
        "".join(body),
    )


def motif_paprika(c):
    pink, teal, yellow = c["accent"], c["accent2"], c["accent3"]
    defs = (
        '<clipPath id="ppclip"><circle cx="922" cy="302" r="196"/></clipPath>'
        '<linearGradient id="ppribbon" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{pink}"/><stop offset=".5" stop-color="{yellow}"/>'
        f'<stop offset="1" stop-color="{teal}"/></linearGradient>'
    )
    body = [
        # striped disc
        f'<circle cx="922" cy="302" r="196" fill="{yellow}"/>',
        '<g clip-path="url(#ppclip)">',
    ]
    for i in range(-14, 15):
        body.append(
            f'<rect x="{922 + i * 30 - 16}" y="96" width="16" height="420" '
            f'fill="{pink if i % 2 == 0 else teal}" transform="rotate(26 922 302)"/>'
        )
    body += [
        "</g>",
        f'<circle cx="922" cy="302" r="196" fill="none" stroke="#12100F" stroke-width="2" opacity=".55"/>',
        f'<circle cx="812" cy="250" r="112" fill="{yellow}" opacity=".72"/>',
        f'<circle cx="812" cy="250" r="112" fill="none" stroke="#12100F" stroke-width="1.5" opacity=".4"/>',
        f'<circle cx="1032" cy="382" r="86" fill="{teal}" opacity=".7"/>',
        f'<circle cx="1032" cy="382" r="86" fill="none" stroke="#12100F" stroke-width="1.5" opacity=".4"/>',
        f'<path d="M604 470 C 690 400 760 528 846 448 C 906 392 972 470 1036 420" '
        f'fill="none" stroke="url(#ppribbon)" stroke-width="26" opacity=".85"/>',
        f'<path d="M604 470 C 690 400 760 528 846 448 C 906 392 972 470 1036 420" '
        f'fill="none" stroke="#12100F" stroke-width="2" opacity=".35"/>',
    ]
    rng = random.Random(81)
    for _ in range(11):
        x = rng.uniform(640, 1120)
        y = rng.uniform(120, 500)
        size = rng.uniform(7, 15)
        body.append(
            f'<path d="M{x:.0f} {y - size:.0f} L{x + size:.0f} {y + size:.0f} '
            f'L{x - size:.0f} {y + size:.0f} Z" fill="{rng.choice([pink, teal, yellow])}" '
            f'stroke="#12100F" stroke-width="1" opacity="{rng.uniform(0.55, 0.95):.2f}"/>'
        )
    return defs, "".join(body)


def motif_ghost(c):
    accent = c["accent"]
    cx, cy = 910, 316
    body = []
    for i in range(1, 7):
        ry = 196 * math.cos(i * math.pi / 14)
        body.append(
            f'<ellipse cx="{cx}" cy="{cy}" rx="196" ry="{ry:.1f}" fill="none" '
            f'stroke="{accent}" stroke-width="1" opacity=".22"/>'
        )
    for i in range(1, 7):
        rx = 196 * math.cos(i * math.pi / 14)
        body.append(
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx:.1f}" ry="196" fill="none" '
            f'stroke="{accent}" stroke-width="1" opacity=".22"/>'
        )
    body += [
        f'<circle cx="{cx}" cy="{cy}" r="196" fill="none" stroke="{accent}" stroke-width="1.4" opacity=".55"/>',
        f'<ellipse cx="{cx}" cy="{cy}" rx="196" ry="62" fill="none" stroke="{accent}" stroke-width="2.4" opacity=".85"/>',
        f'<ellipse cx="{cx}" cy="{cy}" rx="62" ry="196" fill="none" stroke="{accent}" stroke-width="2.4" opacity=".85"/>',
        f'<line x1="910" y1="{cy - 190}" x2="910" y2="{cy + 190}" stroke="{accent}" stroke-width="1" opacity=".5"/>',
        f'<circle cx="910" cy="{cy - 190}" r="3" fill="{accent}"/>',
        f'<circle cx="910" cy="{cy + 190}" r="3" fill="{accent}"/>',
        f'<circle cx="910" cy="306" r="7" fill="{accent}"/>',
        f'<circle cx="910" cy="306" r="18" fill="none" stroke="{accent}" stroke-width="1" opacity=".55"/>',
    ]
    rng = random.Random(91)
    for _ in range(30):
        angle = rng.uniform(0, math.tau)
        radius = rng.uniform(206, 260)
        x = cx + math.cos(angle) * radius
        y = cy + math.sin(angle) * radius * 0.82
        length = rng.uniform(4, 16)
        body.append(
            f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x + length:.0f}" y2="{y:.0f}" '
            f'stroke="{accent}" stroke-width="1" opacity="{rng.uniform(0.15, 0.5):.2f}"/>'
        )
    body += [
        f'<text x="640" y="556" font-family="{MONO}" font-size="10" letter-spacing="3" '
        f'fill="{accent}" opacity=".55">GHOST / SHELL / 1995</text>',

    ]
    return "", "".join(body)


def motif_titan(c):
    ink, accent = c["ink"], c["accent"]
    body = [
        f'<circle cx="1002" cy="266" r="140" fill="{accent}" opacity=".92"/>',
        f'<circle cx="1002" cy="266" r="140" fill="none" stroke="#6E0A10" stroke-width="2" opacity=".5"/>',
        f'<rect x="610" y="286" width="560" height="300" fill="#12100F"/>',
        f'<rect x="610" y="286" width="560" height="10" fill="#2C2724"/>',
    ]
    for x in range(610, 1180, 58):
        body.append(
            f'<line x1="{x}" y1="296" x2="{x}" y2="586" stroke="#2A2521" stroke-width="1.6"/>'
        )
    for y in range(350, 586, 58):
        body.append(
            f'<line x1="610" y1="{y}" x2="1170" y2="{y}" stroke="#211D1A" stroke-width="1.2"/>'
        )
    # tiny figure on the wall
    body += [
        f'<circle cx="762" cy="272" r="4" fill="{ink}"/>',
        f'<g stroke="{ink}" stroke-width="2.2" stroke-linecap="round">',
        f'<line x1="762" y1="277" x2="762" y2="290"/>',
        f'<line x1="762" y1="281" x2="753" y2="287"/>',
        f'<line x1="762" y1="281" x2="771" y2="286"/>',
        f'<line x1="762" y1="290" x2="755" y2="299"/>',
        f'<line x1="762" y1="290" x2="769" y2="299"/>',
        f"</g>",
    ]
    for bx, by, s in [(690, 170, 1.0), (724, 148, 0.72), (660, 142, 0.55)]:
        body.append(
            f'<path d="M{bx - 7 * s:.0f} {by:.0f} q {7 * s:.0f} {-6 * s:.0f} {14 * s:.0f} 0" '
            f'fill="none" stroke="{ink}" stroke-width="1.4" opacity=".6"/>'
        )
    body += [
        f'<path d="M610 586 L1170 586" stroke="{ink}" stroke-width="2" opacity=".8"/>',
        f'<text x="640" y="580" font-family="{MONO}" font-size="9.5" '
        f'letter-spacing="2.6" fill="#8E857A">WALL MARIA / 845</text>',
    ]
    return "", "".join(body)


# --------------------------------------------------------------------------
# Layout
# --------------------------------------------------------------------------


def cover(spec, motif_defs, motif_body, texture):
    rank = spec["rank"]
    ink = spec["ink"]
    muted = spec["muted"]
    accent = spec["accent"]
    frame = ink

    title_size = spec["title_size"]
    lines = spec["title_lines"]
    line_height = title_size * 1.02
    title_y = spec.get("title_y", 236)
    if len(lines) == 2:
        title_y = spec.get("title_y", 206)
    zh_y = title_y + (len(lines) - 1) * line_height + spec.get("zh_gap", 58)
    rule_y = zh_y + spec.get("rule_gap", 34)
    thesis_y = rule_y + spec.get("thesis_gap", 44)

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}">',
        f"<title>{esc(spec['title'])}</title>",
        f"<desc>{esc(spec['desc'])}</desc>",
        "<defs>",
        motif_defs,
        "</defs>",
        f'<rect width="{W}" height="{H}" fill="{spec["bg"]}"/>',
        texture,
        motif_body,
        f'<rect x="40" y="40" width="{W - 80}" height="{H - 80}" fill="none" '
        f'stroke="{frame}" stroke-width="1" opacity=".28"/>',
        f'<text x="88" y="86" font-family="{MONO}" font-size="12" letter-spacing="3.4" '
        f'fill="{accent}">NO. {rank:02d}</text>',
        f'<text x="1112" y="86" text-anchor="end" font-family="{MONO}" font-size="10" '
        f'letter-spacing="3.2" fill="{muted}">TEN LIFELONG CLASSICS</text>',
        f'<line x1="40" y1="108" x2="1160" y2="108" stroke="{frame}" stroke-width="1" opacity=".22"/>',
        f'<text x="88" y="{spec.get("kicker_y", 150)}" font-family="{MONO}" font-size="11.5" '
        f'letter-spacing="3.6" fill="{muted}">{esc(spec["kicker"])}</text>',
    ]

    for i, line in enumerate(lines):
        y = title_y + i * line_height
        out.append(
            f'<text x="86" y="{y:.1f}" font-family="{DISPLAY}" font-size="{title_size}" '
            f'font-weight="700" letter-spacing="{spec.get("tracking", 0.5)}" '
            f'fill="{ink}">{esc(line)}</text>'
        )

    out += [
        f'<text x="88" y="{zh_y:.1f}" font-family="{SERIF}" font-size="{spec["zh_size"]}" '
        f'font-weight="700" letter-spacing="{spec.get("zh_tracking", 2)}" '
        f'fill="{ink}">{esc(spec["zh"])}</text>',
        f'<line x1="88" y1="{rule_y:.1f}" x2="188" y2="{rule_y:.1f}" '
        f'stroke="{accent}" stroke-width="3"/>',
    ]

    for i, line in enumerate(spec["thesis"]):
        out.append(
            f'<text x="88" y="{thesis_y + i * 31:.1f}" font-family="{SANS}" '
            f'font-size="20.5" letter-spacing="0.6" fill="{muted}">{esc(line)}</text>'
        )

    out += [
        f'<text x="88" y="538" font-family="{MONO}" font-size="10.5" '
        f'letter-spacing="2.4" fill="{muted}" opacity=".85">{esc(spec["meta"])}</text>',
        f'<text x="88" y="566" font-family="{MONO}" font-size="9.5" '
        f'letter-spacing="2.2" fill="{muted}" opacity=".55">ORIGINAL ARTWORK · 2026</text>',
        f'<text x="1112" y="566" text-anchor="end" font-family="{MONO}" font-size="10.5" '
        f'letter-spacing="2.4" fill="{spec.get("pair_fill", accent)}" opacity=".9">PAIR {spec["pair"]:02d} · {rank:02d}/10</text>',
        "</svg>",
    ]
    return "\n".join(out)


SPECS = [
    {
        "file": "01_black_mirror",
        "rank": 10,
        "pair": 5,
        "title_lines": ["BLACK MIRROR"],
        "title_size": 58,
        "zh": "黑鏡",
        "zh_size": 50,
        "kicker": "TELEVISION · 2011–",
        "thesis": ["我們自願走進的動物園，", "卻忘了欄杆是自己焊的。"],
        "meta": "ANTHOLOGY · CHARLIE BROOKER",
        "bg": "#050506",
        "ink": "#F2F2F4",
        "muted": "#9A9AA4",
        "accent": "#7DD3FC",
        "texture": "dots",
        "title": "黑鏡 Black Mirror — 自製封面",
        "desc": "An original abstract cover: a black glass slab with a cyan scan line and pixel fragments.",
        "motif": motif_black_mirror,
    },
    {
        "file": "02_2001",
        "rank": 9,
        "pair": 5,
        "title_lines": ["2001: A SPACE", "ODYSSEY"],
        "title_size": 52,
        "zh": "2001：太空漫遊",
        "zh_size": 42,
        "zh_gap": 54,
        "zh_tracking": 0,
        "kicker": "FILM · 1968",
        "thesis": ["工具、墓碑，", "與尚未到來的黎明。"],
        "meta": "DIR. STANLEY KUBRICK",
        "bg": "#EDEAE3",
        "ink": "#0A0A0A",
        "muted": "#5B554C",
        "accent": "#D7263D",
        "pair_fill": "#0A0A0A",
        "texture": "dots_dark",
        "title": "2001：太空漫遊 — 自製封面",
        "desc": "An original abstract cover: a black monolith in front of a red sun and a thin orbit.",
        "motif": motif_2001,
    },
    {
        "file": "03_akira",
        "rank": 8,
        "pair": 4,
        "title_lines": ["AKIRA"],
        "title_size": 78,
        "zh": "阿基拉",
        "zh_size": 50,
        "kicker": "ANIMATION · 1988",
        "thesis": ["力量沒有長大，", "只有失控。"],
        "meta": "DIR. KATSUHIRO OTOMO",
        "bg": "#0A0A0A",
        "ink": "#F5F5F5",
        "muted": "#A3A3A3",
        "accent": "#E11D2E",
        "texture": "scan",
        "title": "阿基拉 AKIRA — 自製封面",
        "desc": "An original abstract cover: a red motorcycle wheel made of concentric rings and speed lines.",
        "motif": motif_akira,
    },
    {
        "file": "04_blade_runner",
        "rank": 7,
        "pair": 4,
        "title_lines": ["BLADE", "RUNNER"],
        "title_size": 66,
        "zh": "銀翼殺手",
        "zh_size": 46,
        "zh_gap": 56,
        "kicker": "FILM · 1982",
        "thesis": ["比人更懂懷念的", "複製品。"],
        "meta": "DIR. RIDLEY SCOTT",
        "bg": "#08090C",
        "ink": "#EDEAE3",
        "muted": "#8B93A3",
        "accent": "#F0A21B",
        "accent2": "#22D3EE",
        "accent3": "#E23A7A",
        "texture": "none",
        "title": "銀翼殺手 Blade Runner — 自製封面",
        "desc": "An original abstract cover: rain, neon signs and a wet street skyline.",
        "motif": motif_blade_runner,
    },
    {
        "file": "05_interstellar",
        "rank": 6,
        "pair": 3,
        "title_lines": ["INTERSTELLAR"],
        "title_size": 54,
        "zh": "星際效應",
        "zh_size": 48,
        "kicker": "FILM · 2014",
        "thesis": ["愛是唯一能穿過", "維度的資料。"],
        "meta": "DIR. CHRISTOPHER NOLAN",
        "bg": "#071426",
        "ink": "#DCE9F7",
        "muted": "#8FA6BE",
        "accent": "#F2A65A",
        "texture": "none",
        "title": "星際效應 Interstellar — 自製封面",
        "desc": "An original abstract cover: a black hole accretion ring and a tiny spacecraft.",
        "motif": motif_interstellar,
    },
    {
        "file": "06_dune",
        "rank": 5,
        "pair": 3,
        "title_lines": ["DUNE"],
        "title_size": 82,
        "zh": "沙丘",
        "zh_size": 50,
        "kicker": "FILM · 2021",
        "thesis": ["預知讓自由變成", "最重的負擔。"],
        "meta": "DIR. DENIS VILLENEUVE",
        "bg": "#D9A05B",
        "ink": "#1A120B",
        "muted": "#4A2E17",
        "accent": "#C2410C",
        "pair_fill": "#F2EFE7",
        "texture": "none",
        "title": "沙丘 Dune — 自製封面",
        "desc": "An original abstract cover: layered dunes, a pale sun and a tiny figure on the ridge.",
        "motif": motif_dune,
    },
    {
        "file": "07_matrix",
        "rank": 4,
        "pair": 2,
        "title_lines": ["THE MATRIX"],
        "title_size": 60,
        "zh": "駭客任務",
        "zh_size": 48,
        "kicker": "FILM · 1999",
        "thesis": ["選擇本身，", "也是被設計好的。"],
        "meta": "DIR. THE WACHOWSKIS",
        "bg": "#030804",
        "ink": "#D9FFE6",
        "muted": "#4F9E68",
        "accent": "#00FF66",
        "accent2": "#C8FFDA",
        "texture": "none",
        "title": "駭客任務 The Matrix — 自製封面",
        "desc": "An original abstract cover: green code rain falling over a dark frame.",
        "motif": motif_matrix,
    },
    {
        "file": "08_paprika",
        "rank": 3,
        "pair": 2,
        "title_lines": ["PAPRIKA"],
        "title_size": 66,
        "zh": "紅辣椒",
        "zh_size": 48,
        "kicker": "ANIMATION · 2006",
        "thesis": ["夢是還沒被命名", "的心靈。"],
        "meta": "DIR. SATOSHI KON",
        "bg": "#F7F1E3",
        "ink": "#12100F",
        "muted": "#5B5550",
        "accent": "#FF2E88",
        "accent2": "#00A6B8",
        "accent3": "#FFD400",
        "pair_fill": "#12100F",
        "texture": "dots_dark",
        "title": "紅辣椒 Paprika — 自製封面",
        "desc": "An original abstract cover: a striped dream disc, overlapping circles and confetti.",
        "motif": motif_paprika,
    },
    {
        "file": "09_ghost_in_the_shell",
        "rank": 2,
        "pair": 1,
        "title_lines": ["GHOST IN", "THE SHELL"],
        "title_size": 54,
        "zh": "攻殼機動隊",
        "zh_size": 44,
        "zh_gap": 54,
        "kicker": "ANIMATION · 1995",
        "thesis": ["當記憶可以備份，", "靈魂住在哪裡？"],
        "meta": "DIR. MAMORU OSHII",
        "bg": "#06171A",
        "ink": "#CDEDEA",
        "muted": "#5E8F8B",
        "accent": "#59E1D6",
        "texture": "dots",
        "title": "攻殼機動隊 Ghost in the Shell — 自製封面",
        "desc": "An original abstract cover: a wireframe sphere crossed by a vertical data spine.",
        "motif": motif_ghost,
    },
    {
        "file": "10_attack_on_titan",
        "rank": 1,
        "pair": 1,
        "title_lines": ["ATTACK ON TITAN"],
        "title_size": 48,
        "zh": "進擊的巨人",
        "zh_size": 46,
        "kicker": "ANIMATION · 2013–2023",
        "thesis": ["自由，是踩過", "別人的自由。"],
        "meta": "STUDIO WIT · MAPPA",
        "bg": "#E8E4DA",
        "ink": "#12100F",
        "muted": "#5A534B",
        "accent": "#B3121A",
        "pair_fill": "#F2EFE7",
        "texture": "dots_dark",
        "title": "進擊的巨人 Attack on Titan — 自製封面",
        "desc": "An original abstract cover: a massive wall, a tiny human silhouette and a red sun.",
        "motif": motif_titan,
    },
]


def texture_for(spec):
    if spec["texture"] == "dots":
        return dotgrid("#FFFFFF", 0.055)
    if spec["texture"] == "dots_dark":
        return dotgrid("#000000", 0.06)
    if spec["texture"] == "scan":
        return scanlines("#FFFFFF", 0.035)
    return ""


def build_svgs():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for spec in SPECS:
        defs, body = spec["motif"](spec)
        svg = cover(spec, defs, body, texture_for(spec))
        path = OUT_DIR / f"{spec['file']}.svg"
        path.write_text(svg, encoding="utf-8")
        written.append(path)
    collection = collection_svg()
    path = OUT_DIR / "00_collection.svg"
    path.write_text(collection, encoding="utf-8")
    written.append(path)
    return written


# --------------------------------------------------------------------------
# Collection mini marks: one original symbol per film, drawn at 58x58
# --------------------------------------------------------------------------


def _mini(cx, cy, key, body):
    return (
        f'<g data-mini="{key}" transform="translate({cx:.1f} {cy:.1f})">'
        f"{body}</g>"
    )


def mini_black_mirror(cx, cy):
    body = (
        '<rect x="-17" y="-23" width="34" height="46" rx="3" '
        'fill="#0E1014" stroke="#3B4450" stroke-width="1.5"/>'
        '<rect x="-17" y="-2" width="34" height="8" fill="#7DD3FC" opacity=".12"/>'
        '<line x1="-17" y1="2" x2="17" y2="2" stroke="#7DD3FC" stroke-width="2.6"/>'
        '<rect x="-9" y="-10" width="4" height="4" fill="#7DD3FC" opacity=".8"/>'
        '<rect x="2" y="-10" width="4" height="4" fill="#7DD3FC" opacity=".55"/>'
        '<rect x="-4" y="10" width="4" height="4" fill="#7DD3FC" opacity=".7"/>'
    )
    return _mini(cx, cy, "bm", body)


def mini_2001(cx, cy):
    body = (
        '<circle cx="6" cy="-2" r="16" fill="#D7263D"/>'
        '<rect x="-9" y="-20" width="17" height="40" fill="#08080A"/>'
        '<line x1="-9" y1="-20" x2="-9" y2="20" stroke="#FFFFFF" stroke-opacity=".22"/>'
        '<line x1="8" y1="-20" x2="8" y2="20" stroke="#FFFFFF" stroke-opacity=".08"/>'
    )
    return _mini(cx, cy, "2001", body)


def mini_akira(cx, cy):
    parts = [
        '<circle cx="0" cy="0" r="19" fill="none" stroke="#E11D2E" stroke-width="5"/>'
    ]
    for i in range(8):
        angle = (i / 8) * math.tau
        x1, y1 = math.cos(angle) * 8, math.sin(angle) * 8
        x2, y2 = math.cos(angle) * 16, math.sin(angle) * 16
        parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            'stroke="#E11D2E" stroke-width="2.2"/>'
        )
    parts += [
        '<circle cx="0" cy="0" r="4.5" fill="#E11D2E"/>',
        '<circle cx="0" cy="0" r="1.8" fill="#141416"/>',
    ]
    return _mini(cx, cy, "ak", "".join(parts))


def mini_blade_runner(cx, cy):
    parts = []
    for bx, bh in [(-27, 26), (-17, 38), (-8, 30), (2, 44), (13, 34)]:
        width = 9 if bx == 2 else 8
        parts.append(
            f'<rect x="{bx}" y="{20 - bh}" width="{width}" height="{bh}" '
            'fill="#0B0D12" stroke="#2C3442" stroke-width="1"/>'
        )
    for bx, by, color in [
        (-24, -6, "#F0A21B"),
        (-14, -12, "#E23A7A"),
        (15, -4, "#22D3EE"),
    ]:
        parts.append(
            f'<rect x="{bx}" y="{by}" width="3" height="12" fill="{color}" opacity=".9"/>'
        )
    for x1, y1, x2, y2 in [
        (-26, -28, -29, -10),
        (-8, -28, -11, -10),
        (9, -26, 6, -8),
        (24, -28, 21, -10),
    ]:
        parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#22D3EE" '
            'stroke-width="1.2" opacity=".35"/>'
        )
    parts.append(
        '<line x1="-29" y1="20" x2="29" y2="20" stroke="#F0A21B" '
        'stroke-width="1.2" opacity=".5"/>'
    )
    return _mini(cx, cy, "br", "".join(parts))


def mini_interstellar(cx, cy):
    body = (
        '<g transform="rotate(-15)">'
        '<ellipse cx="0" cy="0" rx="28" ry="11" fill="none" stroke="#F2A65A" '
        'stroke-width="1" opacity=".35"/>'
        '<ellipse cx="0" cy="0" rx="24" ry="8.5" fill="none" stroke="#F2A65A" '
        'stroke-width="4"/>'
        "</g>"
        '<circle cx="0" cy="0" r="9" fill="#071426"/>'
        '<circle cx="0" cy="0" r="9" fill="none" stroke="#F2A65A" '
        'stroke-width="1.2" opacity=".8"/>'
        '<circle cx="-24" cy="18" r="1.6" fill="#DCE9F7"/>'
    )
    return _mini(cx, cy, "is", body)


def mini_dune(cx, cy):
    body = (
        '<circle cx="16" cy="-16" r="8" fill="#F8E7C0"/>'
        '<path d="M-29 12 C-15 2 -6 4 0 8 C10 14 20 10 29 2 L29 29 L-29 29 Z" '
        'fill="#D09352"/>'
        '<path d="M-29 18 C-18 10 -8 14 0 17 C12 22 22 18 29 12 L29 29 L-29 29 Z" '
        'fill="#B5763C"/>'
        '<path d="M-29 24 C-18 18 -6 22 0 24 C12 28 22 25 29 21 L29 29 L-29 29 Z" '
        'fill="#8E5629"/>'
        '<circle cx="6" cy="7" r="1.4" fill="#1A120B"/>'
        '<path d="M6 8.5 L6 13 M6 10 L3.5 12 M6 10 L8.5 11.6 M6 13 L4 16 M6 13 L8 16" '
        'fill="none" stroke="#1A120B" stroke-width="1.3" stroke-linecap="round"/>'
    )
    return _mini(cx, cy, "du", body)


def mini_matrix(cx, cy):
    parts = []
    for ci, glyphs in enumerate(["01|{", "1}0|", "|01}", "{1|0"]):
        x = -18 + ci * 12
        for ri, glyph in enumerate(glyphs):
            y = -20 + ri * 9
            color = "#C8FFDA" if ri == 0 else "#00FF66"
            opacity = 0.95 - ri * 0.16
            parts.append(
                f'<text x="{x}" y="{y}" text-anchor="middle" font-family="{MONO}" '
                f'font-size="8" fill="{color}" opacity="{opacity:.2f}">'
                f"{esc(glyph)}</text>"
            )
    return _mini(cx, cy, "mx", "".join(parts))


def mini_paprika(cx, cy):
    stripes = []
    for k in range(-4, 5):
        color = "#FF2E88" if k % 2 == 0 else "#00A6B8"
        stripes.append(
            f'<rect x="{k * 7 - 3.5}" y="-28" width="7" height="56" fill="{color}"/>'
        )
    body = (
        '<defs><clipPath id="mini-pp-clip">'
        '<circle cx="0" cy="0" r="20"/></clipPath></defs>'
        '<circle cx="0" cy="0" r="20" fill="#FFD400"/>'
        '<g clip-path="url(#mini-pp-clip)" transform="rotate(26)">'
        + "".join(stripes)
        + "</g>"
        '<circle cx="0" cy="0" r="20" fill="none" stroke="#12100F" '
        'stroke-width="1.5" opacity=".55"/>'
        '<path d="M-26 -14 L-21 -6 L-29 -6 Z" fill="#FF2E88" '
        'stroke="#12100F" stroke-width="1"/>'
        '<path d="M24 12 L29 20 L20 19 Z" fill="#00A6B8" '
        'stroke="#12100F" stroke-width="1"/>'
    )
    return _mini(cx, cy, "pp", body)


def mini_ghost(cx, cy):
    body = (
        '<circle cx="0" cy="0" r="20" fill="none" stroke="#59E1D6" stroke-width="1.8"/>'
        '<ellipse cx="0" cy="0" rx="20" ry="7" fill="none" stroke="#59E1D6" '
        'stroke-width="1.5"/>'
        '<ellipse cx="0" cy="0" rx="7" ry="20" fill="none" stroke="#59E1D6" '
        'stroke-width="1.5"/>'
        '<line x1="0" y1="-22" x2="0" y2="22" stroke="#59E1D6" '
        'stroke-width="1" opacity=".6"/>'
        '<circle cx="0" cy="0" r="6" fill="none" stroke="#59E1D6" '
        'stroke-width="1" opacity=".55"/>'
        '<circle cx="0" cy="0" r="2.6" fill="#59E1D6"/>'
    )
    return _mini(cx, cy, "gs", body)


def mini_titan(cx, cy):
    parts = [
        '<circle cx="10" cy="-12" r="13" fill="#B3121A"/>',
        '<rect x="-24" y="6" width="48" height="20" fill="#211C18" '
        'stroke="#7A6E62" stroke-width="1.2"/>',
    ]
    for bx in (-24, -12, 0, 12):
        parts.append(
            f'<rect x="{bx}" y="0" width="8" height="6" fill="#1A1714" '
            'stroke="#5A534B" stroke-width="1.1"/>'
        )
    for bx in (-18, -6, 6, 18):
        parts.append(
            f'<line x1="{bx}" y1="7" x2="{bx}" y2="25" stroke="#3A332D" stroke-width="1"/>'
        )
    parts += [
        '<line x1="-24" y1="16" x2="24" y2="16" stroke="#3A332D" stroke-width="1"/>',
        '<circle cx="0" cy="-7" r="1.5" fill="#F2EFE7"/>',
        '<path d="M0 -5.5 L0 -1 M0 -4 L-2.5 -2 M0 -4 L2.5 -2.8 '
        'M0 -1 L-1.5 1.5 M0 -1 L1.5 1.5" fill="none" stroke="#F2EFE7" '
        'stroke-width="1.1" stroke-linecap="round"/>',
    ]
    return _mini(cx, cy, "at", "".join(parts))


def collection_svg():
    ink = "#F2EFE7"
    muted = "#8C887E"
    bg = "#0B0B0C"
    accent = "#E8B54A"
    codes = [
        ("BM", "#7DD3FC", mini_black_mirror),
        ("2001", "#D7263D", mini_2001),
        ("AK", "#E11D2E", mini_akira),
        ("BR", "#F0A21B", mini_blade_runner),
        ("IS", "#F2A65A", mini_interstellar),
        ("DU", "#C2410C", mini_dune),
        ("MX", "#00FF66", mini_matrix),
        ("PP", "#FF2E88", mini_paprika),
        ("GS", "#59E1D6", mini_ghost),
        ("AT", "#B3121A", mini_titan),
    ]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}">',
        "<title>從黑鏡到巨人：十部一生摯愛的科幻與人性史詩 — 自製封面</title>",
        "<desc>An original cover built from ten small abstract frames, one per film.</desc>",
        "<defs>",
        '<linearGradient id="cfade" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#E8B54A" stop-opacity=".9"/>'
        '<stop offset="1" stop-color="#E8B54A" stop-opacity=".15"/>'
        "</linearGradient>",
        "</defs>",
        f'<rect width="{W}" height="{H}" fill="{bg}"/>',
        dotgrid("#FFFFFF", 0.045),
        f'<rect x="40" y="40" width="{W - 80}" height="{H - 80}" fill="none" '
        f'stroke="{ink}" stroke-width="1" opacity=".2"/>',
        f'<text x="80" y="104" font-family="{MONO}" font-size="11" letter-spacing="4" '
        f'fill="{accent}">TEN LIFELONG CLASSICS</text>',
        f'<text x="1120" y="104" text-anchor="end" font-family="{MONO}" font-size="10" '
        f'letter-spacing="3" fill="{muted}">ESSAY · 2026</text>',
        f'<text x="80" y="196" font-family="{SERIF}" font-size="62" font-weight="700" '
        f'letter-spacing="3" fill="{ink}">從黑鏡到巨人</text>',
        f'<line x1="82" y1="222" x2="300" y2="222" stroke="url(#cfade)" stroke-width="3"/>',
        f'<text x="80" y="272" font-family="{SANS}" font-size="21" letter-spacing="2" '
        f'fill="{muted}">十部科幻與人性史詩 · 五組對讀</text>',
        f'<text x="80" y="308" font-family="{MONO}" font-size="10.5" letter-spacing="2.6" '
        f'fill="{muted}" opacity=".8">10 FILMS / 5 PAIRS / ONE QUESTION</text>',
    ]

    # filmstrip
    x0, y0, fw, fh, gap = 80, 356, 97, 132, 8
    for i, (code, color, mark) in enumerate(codes):
        x = x0 + i * (fw + gap)
        parts += [
            f'<rect x="{x}" y="{y0}" width="{fw}" height="{fh}" fill="#141416" '
            f'stroke="#2C2C31" stroke-width="1"/>',
            f'<rect x="{x}" y="{y0}" width="{fw}" height="3" fill="{color}"/>',
            f'<text x="{x + 10}" y="{y0 + 24}" font-family="{MONO}" font-size="9" '
            f'letter-spacing="1.4" fill="{muted}">{10 - i:02d}</text>',
        ]
        parts.append(mark(x + fw / 2, y0 + 78))
        parts.append(
            f'<text x="{x + fw / 2}" y="{y0 + 122}" text-anchor="middle" '
            f'font-family="{MONO}" font-size="9" letter-spacing="1.6" '
            f'fill="{ink}" opacity=".65">{code}</text>'
        )

    parts += [
        f'<text x="80" y="534" font-family="{SANS}" font-size="15" letter-spacing=".5" '
        f'fill="{muted}">黑鏡 · 2001 · 阿基拉 · 銀翼殺手 · 星際效應 · 沙丘 · 駭客任務 · 紅辣椒 · 攻殼機動隊 · 進擊的巨人</text>',
        f'<line x1="80" y1="552" x2="1120" y2="552" stroke="{ink}" stroke-width="1" opacity=".14"/>',
        f'<text x="80" y="576" font-family="{MONO}" font-size="9.5" letter-spacing="2.2" '
        f'fill="{muted}" opacity=".65">ORIGINAL ARTWORK · NO FILM STILLS USED</text>',
        f'<text x="1120" y="576" text-anchor="end" font-family="{MONO}" font-size="9.5" '
        f'letter-spacing="2.2" fill="{muted}" opacity=".65">JAY FU / 2026</text>',
        "</svg>",
    ]
    return "\n".join(parts)


def preview(svgs):
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    rsvg = shutil.which("rsvg-convert")
    if not rsvg:
        raise SystemExit("rsvg-convert not found: brew install librsvg")
    for svg in svgs:
        out = PREVIEW_DIR / f"{svg.stem}.png"
        subprocess.run([rsvg, "-w", "1200", "-o", str(out), str(svg)], check=True)
        print(out)


def render(svgs, collection_only=False):
    BUNDLE_IMAGES.mkdir(parents=True, exist_ok=True)
    collection = OUT_DIR / "00_collection.svg"
    svg_to_jpeg(collection, BUNDLE_IMAGES / "cover.jpg", width=1200, quality=85)
    print(BUNDLE_IMAGES / "cover.jpg")
    if collection_only:
        return
    for svg in svgs:
        if svg.name.startswith("00_"):
            continue
        dest = BUNDLE_IMAGES / f"{svg.stem}.webp"
        svg_to_webp(svg, dest, width=1376, quality=82)
        print(dest)
        thumb = BUNDLE_IMAGES / f"{svg.stem}_thumb.webp"
        svg_to_webp(svg, thumb, width=480, quality=80)
        print(thumb)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", action="store_true", help="render PNG previews to /tmp")
    parser.add_argument("--render", action="store_true", help="write final JPEG/WebP assets")
    parser.add_argument(
        "--collection-only",
        action="store_true",
        help="with --render, only write the collection cover",
    )
    args = parser.parse_args()

    svgs = build_svgs()
    print(f"wrote {len(svgs)} SVG file(s) to {OUT_DIR}")
    if args.preview:
        preview(svgs)
    if args.render:
        render(svgs, collection_only=args.collection_only)


if __name__ == "__main__":
    main()
