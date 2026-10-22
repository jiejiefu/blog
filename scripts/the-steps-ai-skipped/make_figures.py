#!/usr/bin/env python3
"""Generate the cover and section figures for the-steps-ai-skipped.

Every figure is drawn from scratch as SVG with basic shapes and text. The
scripts keep the SVG sources next to this file so they can be edited later.

Usage:
    python3 scripts/the-steps-ai-skipped/make_figures.py
    python3 scripts/the-steps-ai-skipped/make_figures.py --preview
"""

import argparse
import html
import math
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = Path(__file__).resolve().parent
BUNDLE_IMAGES = ROOT / "content/zh-tw/posts/the-steps-ai-skipped/images"
PREVIEW_DIR = Path(tempfile.gettempdir()) / "the-steps-ai-skipped-preview"

sys.path.insert(0, str(ROOT / "scripts"))
from image_utils import svg_to_jpeg, svg_to_webp  # noqa: E402

BG = "#0B1220"
PANEL = "#101A2B"
PANEL_ALT = "#0D1524"
LINE = "#26354F"
INK = "#E8EEF9"
MUTED = "#93A4BE"
DIM = "#5D6E88"
ACCENT = "#8B93FF"
TEAL = "#5EEAD4"
AMBER = "#F5B84C"
RED = "#FF6B72"

SANS = "'PingFang TC','Noto Sans TC','Heiti TC',sans-serif"
SERIF = "'Noto Serif TC','Songti TC','Noto Serif CJK TC',serif"
MONO = "'SF Mono','Menlo','DejaVu Sans Mono',monospace"


def esc(value):
    return html.escape(str(value), quote=True)


DEFS = (
    "<defs>"
    '<linearGradient id="gPanel" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#121D30"/>'
    '<stop offset="1" stop-color="#0D1524"/>'
    "</linearGradient>"
    '<linearGradient id="gHeader" x1="0" y1="0" x2="1" y2="0">'
    '<stop offset="0" stop-color="#16213A"/>'
    '<stop offset="1" stop-color="#101A2B"/>'
    "</linearGradient>"
    '<linearGradient id="gAmber" x1="0" y1="0" x2="1" y2="0">'
    '<stop offset="0" stop-color="#D08A38"/>'
    '<stop offset="1" stop-color="#F5B84C"/>'
    "</linearGradient>"
    '<linearGradient id="gTeal" x1="0" y1="0" x2="1" y2="0">'
    '<stop offset="0" stop-color="#2DD4BF"/>'
    '<stop offset="1" stop-color="#5EEAD4"/>'
    "</linearGradient>"
    '<linearGradient id="gAccent" x1="0" y1="0" x2="1" y2="0">'
    '<stop offset="0" stop-color="#6F7BFF"/>'
    '<stop offset="1" stop-color="#A5ABFF"/>'
    "</linearGradient>"
    '<radialGradient id="gVignette" cx="0.5" cy="0.28" r="0.85">'
    '<stop offset="0" stop-color="#1A2742" stop-opacity="0.55"/>'
    '<stop offset="0.62" stop-color="#0B1220" stop-opacity="0"/>'
    '<stop offset="1" stop-color="#04070D" stop-opacity="0.65"/>'
    "</radialGradient>"
    '<filter id="glow" x="-70%" y="-70%" width="240%" height="240%">'
    '<feGaussianBlur stdDeviation="5" result="b"/>'
    '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
    "</filter>"
    "</defs>"
)


def t(
    x,
    y,
    text,
    size=22,
    fill=INK,
    family=SANS,
    weight=400,
    anchor="start",
    ls=0,
    opacity=None,
    style="",
):
    extra = f' letter-spacing="{ls}"' if ls else ""
    if opacity is not None:
        extra += f' opacity="{opacity}"'
    if style:
        extra += f' style="{style}"'
    return (
        f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{extra}>'
        f"{esc(text)}</text>"
    )


def rect(x, y, w, h, fill=PANEL, stroke=None, rx=12, sw=1.5, dash=None, opacity=None):
    extra = ""
    if stroke:
        extra += f' stroke="{stroke}" stroke-width="{sw}"'
    if dash:
        extra += f' stroke-dasharray="{dash}"'
    if opacity is not None:
        extra += f' opacity="{opacity}"'
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{extra}/>'


def line(x1, y1, x2, y2, color=LINE, sw=1.5, dash=None, opacity=None):
    extra = ""
    if dash:
        extra += f' stroke-dasharray="{dash}"'
    if opacity is not None:
        extra += f' opacity="{opacity}"'
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{color}" stroke-width="{sw}"{extra}/>'
    )


def circle(cx, cy, r, fill="none", stroke=None, sw=1.5, opacity=None):
    extra = ""
    if stroke:
        extra += f' stroke="{stroke}" stroke-width="{sw}"'
    if opacity is not None:
        extra += f' opacity="{opacity}"'
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"{extra}/>'


def arrow(x1, y1, x2, y2, color=ACCENT, sw=2.5, dash=None, head=11):
    dx = x2 - x1
    dy = y2 - y1
    length = math.hypot(dx, dy) or 1
    ux = dx / length
    uy = dy / length
    ex = x2 - ux * head
    ey = y2 - uy * head
    px = -uy
    py = ux
    p1 = (ex + px * head * 0.55, ey + py * head * 0.55)
    p2 = (ex - px * head * 0.55, ey - py * head * 0.55)
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{ex}" y2="{ey}" stroke="{color}" '
        f'stroke-width="{sw}"{extra} stroke-linecap="round"/>'
        f'<polygon points="{x2},{y2} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{color}"/>'
    )


def trim(x1, y1, x2, y2, w, h, pad=10):
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return x2, y2
    sx = (w / 2 + pad) / abs(dx) if dx else float("inf")
    sy = (h / 2 + pad) / abs(dy) if dy else float("inf")
    s = min(sx, sy, 1.0)
    return x2 - dx * s, y2 - dy * s


def arrow_to(x1, y1, x2, y2, w, h, color=ACCENT, sw=2.5, dash=None):
    tx, ty = trim(x1, y1, x2, y2, w, h)
    return arrow(x1, y1, tx, ty, color, sw, dash)


def chrome(w, h, idx, right="THE STEPS AI SKIPPED", left_note="JAY FU · ENGINEERING NOTES"):
    grid_id = f"dots{idx.replace(' ', '')}{w}{h}"
    dots = (
        f'<pattern id="{grid_id}" width="28" height="28" patternUnits="userSpaceOnUse">'
        f'<circle cx="1" cy="1" r="1" fill="#FFFFFF" opacity="0.05"/></pattern>'
        f'<rect width="{w}" height="{h}" fill="url(#{grid_id})"/>'
    )
    return (
        dots
        + rect(30, 30, w - 60, h - 60, fill="none", stroke=LINE, rx=0, sw=1, opacity=0.9)
        + t(64, 78, f"FIG. {idx}", 15, ACCENT, MONO, 500, ls=3)
        + t(w - 64, 78, right, 13, DIM, MONO, 400, anchor="end", ls=2.2)
        + line(52, 100, w - 52, 100, LINE, 1)
        + line(52, h - 64, w - 52, h - 64, LINE, 1)
        + t(64, h - 40, left_note, 10.5, DIM, MONO, 400, ls=2)
        + t(w - 64, h - 40, "2026", 10.5, DIM, MONO, 400, anchor="end", ls=2)
    )


def figure(idx, w, h, title, kicker, body):
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">'
        f"<title>{esc(title)}</title>"
        f"<desc>{esc(kicker)}</desc>"
        + DEFS
        + f'<rect width="{w}" height="{h}" fill="{BG}"/>'
        + f'<rect width="{w}" height="{h}" fill="url(#gVignette)"/>'
        + chrome(w, h, idx)
        + t(64, 146, kicker, 14, MUTED, MONO, 500, ls=2.6)
        + t(64, 198, title, 42, INK, SERIF, 700, ls=0.5)
        + body
        + "</svg>"
    )
    return svg


def chip(x, y, w, h, text, color, fill=None, size=18):
    fill = fill or PANEL
    return (
        rect(x, y, w, h, fill=fill, stroke=color, rx=10, sw=1.4)
        + t(x + w / 2, y + h / 2 + 6, text, size, color, MONO, 600, anchor="middle")
    )


def fig_01():
    idx = "01"
    w, h = 1376, 774
    x0, x1 = 190, 1250
    total = 250
    scale = (x1 - x0) / total
    segments = [
        ("重現", 20, "#6B5A2F"),
        ("關鍵字", 25, "#8A6E2E"),
        ("搜尋", 40, "#B07A2C"),
        ("版本", 35, "#D08A38"),
        ("文件", 50, "#E39A44"),
        ("試錯", 80, "#F5B84C"),
    ]
    body = []
    y_bar = 268
    bar_h = 58
    cx = x0
    for label, minutes, color in segments:
        seg_w = minutes * scale
        body.append(rect(cx, y_bar, seg_w - 2, bar_h, fill=color, rx=4, sw=0))
        body.append(
            t(cx + seg_w / 2 - 1, y_bar + 36, label, 17, "#1A1408", SANS, 700, anchor="middle")
        )
        cx += seg_w
    body.append(t(64, 262, "以前", 22, AMBER, SANS, 700))
    body.append(t(x1, 258, "4 小時 10 分", 26, AMBER, MONO, 600, anchor="end"))
    body.append(t(x0, 354, "0", 14, DIM, MONO, 400))
    body.append(t(x1, 354, "250 min", 14, DIM, MONO, 400, anchor="end"))

    body.append(t(64, 418, "現在", 22, TEAL, SANS, 700))
    body.append(rect(x0, 428, 10 * scale - 2, bar_h, fill=TEAL, rx=4, sw=0))
    body.append(t(x0 + 10 * scale + 16, 466, "10 min", 26, TEAL, MONO, 600))
    body.append(t(x0, 516, "0", 14, DIM, MONO, 400))
    body.append(t(x1, 516, "250 min", 14, DIM, MONO, 400, anchor="end"))
    body.append(line(232, 528, x1, 528, MUTED, 1.2, dash="5 7"))
    body.append(line(232, 522, 232, 534, MUTED, 1.2))
    body.append(line(x1, 522, x1, 534, MUTED, 1.2))
    body.append(t((232 + x1) / 2, 560, "兩百四十分鐘，被省下來了", 19, MUTED, SANS, 400, anchor="middle"))

    body.append(rect(64, 566, 1248, 142, fill="url(#gPanel)", stroke=LINE, rx=14))
    body.append(t(88, 598, "ZOOM · THE NEW 10 MINUTES", 12, DIM, MONO, 500, ls=2))
    body.append(
        t(1288, 598, "被省下的不是答案，是抵達答案之前的那段路。", 13, MUTED, SANS, 400, anchor="end")
    )
    tl_y = 644
    positions = [300, 486, 765, 1044, 1230]
    labels = [
        ("00:00", "貼上錯誤"),
        ("00:02", "讀答案"),
        ("00:05", "修改"),
        ("00:08", "執行"),
        ("00:10", "問題消失"),
    ]
    body.append(line(positions[0], tl_y, positions[-1], tl_y, LINE, 2))
    for x, (stamp, label) in zip(positions, labels):
        body.append(circle(x, tl_y, 8, fill=BG, stroke=TEAL, sw=2.5))
        body.append(t(x, tl_y - 18, stamp, 13, TEAL, MONO, 500, anchor="middle"))
        body.append(t(x, tl_y + 34, label, 16, MUTED, SANS, 400, anchor="middle"))
    return figure(
        idx,
        w,
        h,
        "十分鐘，與被省下的兩百四十分鐘",
        "TIME · BEFORE / AFTER",
        "".join(body),
    )


def fig_02():
    idx = "02"
    w, h = 1376, 860
    nodes = {
        "start": (150, 700, "錯誤訊息", "exception · line 42"),
        "n1": (400, 600, "拆成關鍵字", "拿掉路徑，留下符號"),
        "n2": (660, 470, "Stack Overflow", "accepted answer · 2019"),
        "n3": (900, 340, "官方文件", "版本差異寫在註腳"),
        "n4": (1080, 500, "重現問題", "最小可失敗案例"),
        "end": (1180, 240, "答案", "以及它為什麼成立"),
        "d1": (600, 690, "版本不符", "30 min wasted"),
        "d2": (850, 620, "錯誤的方向", "30 min wasted"),
    }
    nw, nh = 220, 82
    body = []

    body.append(line(1000, 142, 1046, 142, ACCENT, 3))
    body.append(t(1054, 148, "主路徑", 13, MUTED, MONO, 400, ls=1.5))
    body.append(line(1000, 172, 1046, 172, RED, 2, dash="5 6"))
    body.append(t(1054, 178, "死路", 13, MUTED, MONO, 400, ls=1.5))

    paths = [
        ("start", "n1", "20 min", 282, 632, "end"),
        ("n1", "n2", "40 min", 538, 514, "end"),
        ("n2", "n3", "35 min", 790, 424, "middle"),
        ("n3", "n4", "50 min", 1000, 436, "middle"),
        ("n4", "end", "15 min", 1164, 362, "start"),
    ]
    for a, b, label, lx, ly, anchor in paths:
        ax, ay = nodes[a][0], nodes[a][1]
        bx, by = nodes[b][0], nodes[b][1]
        body.append(arrow_to(ax, ay, bx, by, nw, nh, ACCENT, 2.4))
        body.append(t(lx, ly, label, 12.5, DIM, MONO, 500, anchor=anchor))

    for a, b in (("n1", "d1"), ("n2", "d2")):
        ax, ay = nodes[a][0], nodes[a][1]
        bx, by = nodes[b][0], nodes[b][1]
        body.append(arrow_to(ax, ay, bx, by, nw, nh, RED, 2, "6 7"))

    for key, (cx, cy, title, sub) in nodes.items():
        x, y = cx - nw / 2, cy - nh / 2
        if key in ("d1", "d2"):
            body.append(rect(x, y, nw, nh, fill="#1A1016", stroke=RED, rx=12, sw=1.4, dash="5 4"))
            body.append(t(cx, cy - 6, title, 21, RED, SANS, 700, anchor="middle"))
            body.append(t(cx, cy + 24, sub, 13, RED, MONO, 400, anchor="middle", opacity=0.8))
            body.append(t(x + nw - 16, y + 24, "✕", 18, RED, MONO, 700, anchor="end"))
        elif key == "end":
            body.append(
                f'<rect x="{x}" y="{y}" width="{nw}" height="{nh}" rx="12" fill="none" '
                f'stroke="{TEAL}" stroke-width="6" opacity="0.16" filter="url(#glow)"/>'
            )
            body.append(rect(x, y, nw, nh, fill="#0C2420", stroke=TEAL, rx=12, sw=1.8))
            body.append(t(cx, cy - 6, title, 22, TEAL, SANS, 700, anchor="middle"))
            body.append(t(cx, cy + 24, sub, 12.5, TEAL, MONO, 400, anchor="middle", opacity=0.85))
        elif key == "start":
            body.append(rect(x, y, nw, nh, fill="#171C33", stroke=ACCENT, rx=12, sw=1.6))
            body.append(t(cx, cy - 6, title, 22, INK, SANS, 700, anchor="middle"))
            body.append(t(cx, cy + 24, sub, 12.5, MUTED, MONO, 400, anchor="middle"))
        else:
            body.append(rect(x, y, nw, nh, fill="url(#gPanel)", stroke=LINE, rx=12, sw=1.4))
            body.append(t(cx, cy - 4, title, 21, INK, SANS, 600, anchor="middle"))
            body.append(t(cx, cy + 24, sub, 12.5, MUTED, MONO, 400, anchor="middle"))

    body.append(
        t(
            64,
            776,
            "彎路不會出現在答案裡。它只會出現在你下一次懷疑的速度裡。",
            18,
            MUTED,
            SANS,
            400,
        )
    )
    return figure(
        idx,
        w,
        h,
        "找答案的路，從來不是直線",
        "SEARCH · WHAT THE SHORTCUT SKIPPED",
        "".join(body),
    )


def fig_03():
    idx = "03"
    w, h = 1376, 860
    body = []
    rows = [
        ("01", "先猜想可能的原因", "假設：3 個", MUTED, PANEL),
        ("02", "把錯誤訊息貼給 AI", "假設：1 個", ACCENT, "#171C33"),
        ("03", "不讀完整錯誤，只貼最後一行", "假設：0 個", AMBER, "#201A10"),
        ("04", "把日誌、程式碼、環境全部丟進去", "假設：不用了", RED, "#201116"),
    ]
    ys = [244, 384, 524, 664]
    bh = 100
    bw = 540
    bx = 90
    for i, ((num, title, sub, color, fill), y) in enumerate(zip(rows, ys)):
        body.append(rect(bx, y, bw, bh, fill=fill, stroke=color, rx=14, sw=1.5))
        body.append(circle(bx + 54, y + bh / 2, 23, fill="none", stroke=color, sw=1.6))
        body.append(t(bx + 54, y + bh / 2 + 8, num, 18, color, MONO, 700, anchor="middle"))
        body.append(t(bx + 96, y + 44, title, 24, INK if i < 3 else "#FFD9DB", SANS, 600))
        body.append(t(bx + 96, y + 74, sub, 15, color, MONO, 500))
        if i < 3:
            body.append(arrow(bx + 360, y + bh + 4, bx + 360, ys[i + 1] - 8, LINE, 2.2))

    panel_x = 700
    body.append(rect(panel_x, 244, 596, 520, fill="url(#gPanel)", stroke=LINE, rx=14))
    body.append(t(panel_x + 30, 286, "SPEED", 13, TEAL, MONO, 600, ls=3))
    body.append(t(panel_x + 566, 286, "↑", 20, TEAL, MONO, 600, anchor="end"))
    speed_widths = [64, 128, 196, 264]
    for i, width in enumerate(speed_widths):
        y = 312 + i * 40
        body.append(rect(panel_x + 30, y, 264, 18, fill=LINE, rx=4, sw=0, opacity=0.35))
        body.append(
            rect(panel_x + 30, y, width, 18, fill="url(#gTeal)", rx=4, sw=0, opacity=0.4 + i * 0.18)
        )
        body.append(t(panel_x + 30 + width + 12, y + 14, f"{i + 1}", 12, MUTED, MONO, 500))

    body.append(t(panel_x + 30, 510, "ASSUMPTION", 13, RED, MONO, 600, ls=3))
    body.append(t(panel_x + 566, 510, "↓", 20, RED, MONO, 600, anchor="end"))
    assumption_widths = [264, 176, 88, 0]
    assumption_counts = [3, 1, 0, 0]
    for i, width in enumerate(assumption_widths):
        y = 536 + i * 40
        color = MUTED if i == 0 else AMBER if i < 3 else RED
        body.append(rect(panel_x + 30, y, 264, 18, fill=LINE, rx=4, sw=0, opacity=0.35))
        if width:
            body.append(rect(panel_x + 30, y, width, 18, fill=color, rx=4, sw=0, opacity=0.75))
            label_x = panel_x + 30 + width + 12
        else:
            body.append(circle(panel_x + 39, y + 9, 4, fill=RED))
            label_x = panel_x + 54
        body.append(
            t(label_x, y + 14, str(assumption_counts[i]), 12, RED if not width else MUTED, MONO, 500)
        )

    body.append(
        t(
            panel_x + 30,
            720,
            "速度是真的。問題是，假設也是真的消失了。",
            16,
            MUTED,
            SANS,
            400,
        )
    )
    return figure(
        idx,
        w,
        h,
        "每一次少想一點，都換來一點速度",
        "HABIT · THE ASSUMPTION STAIRCASE",
        "".join(body),
    )


def fig_04():
    idx = "04"
    w, h = 1376, 840
    body = []
    panels = [
        (74, "A · 原始資料", "timestamp 尚未排序", "原始"),
        (494, "B · sort_values", "順序對了，索引沒動", "排序後"),
        (914, "C · reset_index", "索引與列號重新對齊", "修正後"),
    ]
    pw, ph = 380, 380
    py = 250
    for px, title, sub, _ in panels:
        body.append(rect(px, py, pw, ph, fill="url(#gPanel)", stroke=LINE, rx=14))
        body.append(t(px + 22, py + 36, title, 20, INK, SANS, 700))
        body.append(t(px + 22, py + 62, sub, 13, MUTED, MONO, 400))

    def table(px, rows, index_color, index_fill):
        tx = px + 20
        ty = 342
        widths = [76, 116, 78, 78]
        headers = ["#", "timestamp", "value", "diff"]
        out = [rect(tx, ty, sum(widths), 40, fill="url(#gHeader)", rx=6, sw=0)]
        cx = tx
        for width, header in zip(widths, headers):
            out.append(t(cx + width / 2, ty + 26, header, 13, MUTED, MONO, 500, anchor="middle"))
            cx += width
        for r, row in enumerate(rows):
            ry = ty + 40 + r * 44
            out.append(rect(tx, ry, sum(widths), 44, fill=PANEL_ALT, rx=0, sw=0))
            cx = tx
            for c, (width, value) in enumerate(zip(widths, row)):
                fill = index_fill if c == 0 else "#0D1524"
                out.append(rect(cx, ry, width, 44, fill=fill, rx=0, sw=0))
                color = index_color if c == 0 else INK
                weight = 700 if c == 0 else 400
                out.append(
                    t(cx + width / 2, ry + 28, value, 18, color, MONO, weight, anchor="middle")
                )
                cx += width
        for r in range(5):
            yy = ty + r * 44
            out.append(line(tx, yy, tx + sum(widths), yy, LINE, 1))
        for width in widths:
            out.append(line(tx, ty, tx, ty + 40 + 3 * 44, LINE, 1))
            tx += width
        out.append(line(tx, ty, tx, ty + 40 + 3 * 44, LINE, 1))
        return "".join(out)

    body.append(table(74, [("0", "3", "30", "—"), ("1", "1", "10", "—"), ("2", "2", "20", "—")], AMBER, "#221B10"))
    body.append(table(494, [("1", "1", "10", "NaN"), ("2", "2", "20", "10.0"), ("0", "3", "30", "10.0")], AMBER, "#2A2117"))
    body.append(table(914, [("0", "1", "10", "NaN"), ("1", "2", "20", "10.0"), ("2", "3", "30", "10.0")], TEAL, "#0C2420"))

    body.append(arrow(454, 400, 490, 400, ACCENT, 3))
    body.append(arrow(874, 400, 910, 400, ACCENT, 3))

    body.append(t(94, 552, "看起來很正常。", 15, MUTED, SANS, 400))
    body.append(
        f'<path d="M 514 492 H 502 V 560 H 512" fill="none" stroke="{RED}" '
        f'stroke-width="1.4" stroke-dasharray="4 4" stroke-linecap="round"/>'
    )
    body.append(circle(514, 492, 3, fill=RED))
    body.append(rect(514, 534, 340, 52, fill="#201116", stroke=RED, rx=10, sw=1.3))
    body.append(t(534, 566, "df.loc[0] → timestamp = 3", 16, RED, MONO, 600))
    body.append(t(534, 606, "不是排序後的第一列。", 14, MUTED, SANS, 400))
    body.append(t(934, 560, "索引重設後，", 15, TEAL, SANS, 500))
    body.append(t(934, 584, "df.loc[0] 才是第一列。", 15, TEAL, SANS, 500))

    body.append(line(64, 660, 1312, 660, LINE, 1))
    body.append(
        t(64, 706, "排序只改變順序；索引要自己重設。", 24, INK, SERIF, 700)
    )
    body.append(
        t(64, 738, "程式沒有報錯，不代表它的行為符合你的假設。", 17, MUTED, SANS, 400)
    )
    return figure(
        idx,
        w,
        h,
        "程式沒有報錯，不代表 index 還是對的",
        "PYTHON · PANDAS · SORT_VALUES",
        "".join(body),
    )


def fig_05():
    idx = "05"
    w, h = 1376, 860
    body = []
    nw, nh = 200, 86

    def node(x, y, title, sub, color=LINE, fill=PANEL, title_color=INK, dash=None):
        return (
            rect(x, y, nw, nh, fill=fill, stroke=color, rx=12, sw=1.5, dash=dash)
            + t(x + nw / 2, y + 38, title, 19, title_color, SANS, 600, anchor="middle")
            + t(x + nw / 2, y + 64, sub, 12.5, MUTED, MONO, 400, anchor="middle")
        )

    body.append(t(90, 232, "BEFORE · 重構前", 14, DIM, MONO, 500, ls=2))
    xs = [90, 360, 630, 900]
    body.append(node(xs[0], 250, "讀取資料", "csv → DataFrame"))
    body.append(node(xs[1], 250, "依時間排序", "保留原始順序", AMBER, "#201A10", AMBER))
    body.append(node(xs[2], 250, "計算差值", "diff()"))
    body.append(node(xs[3], 250, "輸出結果", "report.json"))
    for a, b in zip(xs, xs[1:]):
        body.append(arrow(a + nw, 293, b, 293, ACCENT, 2.4))
    body.append(t(xs[1] + nw / 2, 230, "不明顯，但決定結果", 12.5, AMBER, SANS, 500, anchor="middle"))

    body.append(t(90, 452, "AFTER · 重構後", 14, DIM, MONO, 500, ls=2))
    body.append(node(xs[0], 470, "讀取資料", "csv → DataFrame"))
    body.append(node(xs[1], 470, "排序被移除", "假設消失", RED, "#1A1016", RED, "5 4"))
    body.append(node(xs[2], 470, "計算差值", "diff()"))
    body.append(node(xs[3], 470, "輸出結果", "report.json"))
    for a, b in zip(xs, xs[1:]):
        body.append(arrow(a + nw, 513, b, 513, ACCENT, 2.4))
    body.append(line(xs[1] + nw / 2, 558, xs[1] + nw / 2, 574, RED, 1.2, dash="3 4"))
    body.append(t(xs[1] + nw / 2, 596, "測試沒有涵蓋這裡", 12.5, RED, SANS, 500, anchor="middle"))

    px = 1130
    body.append(rect(px, 250, 182, 470, fill="url(#gPanel)", stroke=LINE, rx=14))
    body.append(t(px + 20, 286, "TEST REPORT", 12, MUTED, MONO, 500, ls=1.6))
    body.append(t(px + 20, 326, "12 passed", 19, TEAL, MONO, 600))
    for i in range(12):
        col = i % 4
        row = i // 4
        body.append(circle(px + 30 + col * 28, 354 + row * 26, 5, fill=TEAL, opacity=0.85))
    body.append(line(px + 20, 440, px + 162, 440, LINE, 1))
    body.append(t(px + 20, 474, "COVERAGE", 11, DIM, MONO, 500, ls=1.6))
    body.append(t(px + 20, 508, "columns", 14, TEAL, MONO, 500))
    body.append(t(px + 162, 508, "✓", 15, TEAL, MONO, 700, anchor="end"))
    body.append(t(px + 20, 536, "types", 14, TEAL, MONO, 500))
    body.append(t(px + 162, 536, "✓", 15, TEAL, MONO, 700, anchor="end"))
    body.append(rect(px + 14, 556, 154, 44, fill="#201116", stroke=RED, rx=8, sw=1.2))
    body.append(t(px + 26, 584, "order", 14, RED, MONO, 600))
    body.append(t(px + 156, 584, "✗", 15, RED, MONO, 700, anchor="end"))
    body.append(t(px + 20, 628, "12 tests · 0 failed", 11, MUTED, MONO, 400))
    body.append(t(px + 20, 648, "1 個假設沒被驗證", 10.5, RED, SANS, 400, opacity=0.85))

    body.append(
        t(64, 770, "程式能執行 ≠ 程式做對了事。", 26, INK, SERIF, 700)
    )
    return figure(
        idx,
        w,
        h,
        "測試全綠，但有一個假設被拿走了",
        "REFACTOR · WHAT THE TESTS DON'T SEE",
        "".join(body),
    )


def fig_06():
    idx = "06"
    w, h = 1376, 774
    body = []
    services = [
        ("CHATGPT", 178),
        ("CLAUDE", 448),
        ("GEMINI", 718),
        ("COPILOT", 988),
    ]
    sw, sh = 210, 88
    sy = 226
    for name, x in services:
        body.append(rect(x, sy, sw, sh, fill="#1A1016", stroke=RED, rx=12, sw=1.4))
        body.append(t(x + sw / 2, sy + 38, name, 18, INK, MONO, 600, anchor="middle"))
        body.append(t(x + sw / 2, sy + 64, "✕ unreachable", 12.5, RED, MONO, 500, anchor="middle"))

    body.append(line(178, 356, 1198, 356, RED, 1.2, dash="6 8", opacity=0.4))
    body.append(rect(596, 342, 184, 28, fill=BG, rx=6, sw=0))
    body.append(
        t(688, 362, "NETWORK UNAVAILABLE", 11, RED, MONO, 500, anchor="middle", ls=1.6)
    )

    body.append(rect(388, 390, 600, 270, fill=PANEL, stroke=TEAL, rx=14, sw=1.6))
    body.append(rect(388, 390, 600, 46, fill="#0C2420", rx=14, sw=0))
    body.append(rect(388, 420, 600, 16, fill="#0C2420", rx=0, sw=0))
    body.append(circle(414, 413, 6, fill=TEAL))
    body.append(t(432, 419, "LOCAL · IDE", 13, TEAL, MONO, 600, ls=1.4))
    body.append(t(966, 419, "NETWORK: OFFLINE", 11, RED, MONO, 500, anchor="end", ls=1.2))
    lines = [
        "> 讀完錯誤訊息",
        "> 追一次資料流",
        "> 查本機文件",
        "> 先寫一個測試",
        "> 自己下中斷點",
    ]
    for i, text in enumerate(lines):
        body.append(t(420, 476 + i * 34, text, 19, INK, MONO, 400))
    body.append(t(420, 640, "_", 19, TEAL, MONO, 700, opacity=0.9))

    body.append(
        t(688, 702, "效率當然會下降。但思考不該跟著一起離線。", 18, MUTED, SANS, 400, anchor="middle")
    )
    return figure(
        idx,
        w,
        h,
        "今天只能靠自己了",
        "09:00 · NETWORK OFFLINE",
        "".join(body),
    )


def fig_07():
    idx = "07"
    w, h = 1376, 860
    body = []
    left, right = 270, 1120
    top, bottom = 230, 650
    mid_x = (left + right) / 2
    mid_y = (top + bottom) / 2

    body.append(
        f'<defs><clipPath id="quadclip"><rect x="{left}" y="{top}" '
        f'width="{right - left}" height="{bottom - top}" rx="6"/></clipPath></defs>'
    )
    body.append('<g clip-path="url(#quadclip)">')
    body.append(rect(left, top, right - left, bottom - top, fill="#0B1220", rx=0, sw=0))
    body.append(rect(left, top, mid_x - left, mid_y - top, fill="#131F36", rx=0, sw=0))
    body.append(rect(mid_x, top, right - mid_x, mid_y - top, fill="#0C2420", rx=0, sw=0))
    body.append(rect(left, mid_y, mid_x - left, bottom - mid_y, fill="#0B1220", rx=0, sw=0))
    body.append(rect(mid_x, mid_y, right - mid_x, bottom - mid_y, fill="#201A10", rx=0, sw=0))
    body.append(line(mid_x, top, mid_x, bottom, LINE, 1.4))
    body.append(line(left, mid_y, right, mid_y, LINE, 1.4))
    body.append("</g>")
    body.append(rect(left, top, right - left, bottom - top, fill="none", stroke=LINE, rx=6, sw=1.4))

    body.append(t(left + 40, top + 58, "學徒", 34, INK, SERIF, 700))
    body.append(t(left + 40, top + 90, "慢，但每一步都算數", 16, MUTED, SANS, 400))
    body.append(t(right - 40, top + 58, "理想", 34, TEAL, SERIF, 700, anchor="end"))
    body.append(t(right - 40, top + 90, "快，而且知道為什麼", 16, TEAL, SANS, 400, anchor="end"))
    body.append(t(left + 40, bottom - 54, "罕見", 28, DIM, SERIF, 700))
    body.append(t(left + 40, bottom - 26, "慢又不懂，通常撐不久", 15, DIM, SANS, 400))
    body.append(t(right - 40, bottom - 54, "AI 紅利區", 32, AMBER, SERIF, 700, anchor="end"))
    body.append(t(right - 40, bottom - 26, "效率是真的，成長是借來的", 15, AMBER, SANS, 400, anchor="end"))

    body.append(arrow(560, 408, 840, 408, TEAL, 2.2, "7 6"))
    body.append(t(700, 394, "原本該走的路", 14, TEAL, SANS, 500, anchor="middle"))
    body.append(
        f'<path d="M 560 430 Q 760 560 900 512" fill="none" stroke="{AMBER}" stroke-width="2.2" '
        f'stroke-dasharray="7 7" stroke-linecap="round"/>'
    )
    body.append(arrow(880, 517, 906, 508, AMBER, 2.2))
    body.append(line(805, 534, 805, 519, AMBER, 1.2, dash="3 4"))
    body.append(rect(710, 534, 190, 32, fill=BG, stroke=AMBER, rx=8, sw=1.1))
    body.append(t(805, 555, "AI 把這條路拉直了", 14, AMBER, SANS, 500, anchor="middle"))

    body.append(
        f'<text x="{left - 42}" y="{mid_y}" transform="rotate(-90 {left - 42} {mid_y})" '
        f'font-family="{MONO}" font-size="13" fill="{MUTED}" letter-spacing="2" '
        f'text-anchor="middle">理解程度 ↑</text>'
    )
    body.append(t((left + right) / 2, bottom + 42, "產出速度 →", 13, MUTED, MONO, 500, anchor="middle", ls=2))
    body.append(t(left, bottom + 30, "慢", 14, DIM, MONO, 400, anchor="middle"))
    body.append(t(right, bottom + 30, "快", 14, DIM, MONO, 400, anchor="middle"))
    body.append(t(left - 28, bottom, "低", 14, DIM, MONO, 400, anchor="end"))
    body.append(t(left - 28, top + 10, "高", 14, DIM, MONO, 400, anchor="end"))

    body.append(
        t(688, 750, "問題不是快，而是快得不知道自己錯過了什麼。", 20, MUTED, SANS, 400, anchor="middle")
    )
    return figure(
        idx,
        w,
        h,
        "快，不一定代表走得比較遠",
        "SPEED × UNDERSTANDING",
        "".join(body),
    )


def fig_08():
    idx = "08"
    w, h = 1376, 900
    body = []
    tl_y = 310
    x0, x1 = 100, 1276
    body.append(line(x0, tl_y, x1, tl_y, LINE, 2))
    marks = [
        (0, "00:00", "讀完錯誤訊息", "above"),
        (0.25, "02:30", "確認上下文", "below"),
        (0.5, "05:00", "寫下一個假設", "above"),
        (0.75, "07:30", "設計驗證", "below"),
        (1.0, "10:00", "還是沒頭緒 → 問 AI", "above"),
    ]
    for pct, stamp, label, side in marks:
        x = x0 + (x1 - x0) * pct
        body.append(line(x, tl_y - 8, x, tl_y + 8, TEAL, 2))
        body.append(circle(x, tl_y, 9, fill=BG, stroke=TEAL, sw=2.5))
        anchor = "end" if pct == 1.0 else "middle"
        if side == "above":
            body.append(t(x, tl_y - 38, stamp, 15, TEAL, MONO, 600, anchor=anchor))
            body.append(t(x, tl_y - 70, label, 19, INK, SANS, 500, anchor=anchor))
        else:
            body.append(t(x, tl_y + 44, stamp, 15, TEAL, MONO, 600, anchor=anchor))
            body.append(t(x, tl_y + 74, label, 19, INK, SANS, 500, anchor=anchor))

    body.append(rect(100, 430, 1176, 330, fill=PANEL_ALT, stroke=LINE, rx=14))
    body.append(t(130, 474, "問 AI 的時候，我還會多問五件事", 22, INK, SERIF, 700))
    items = [
        ("01", "為什麼會發生這個錯誤？"),
        ("02", "有哪些證據支持這個解釋？"),
        ("03", "這個修改會不會影響其他功能？"),
        ("04", "有沒有其他可能的原因？"),
        ("05", "我應該怎麼設計測試？"),
    ]
    positions = [(130, 536), (130, 606), (130, 676), (700, 536), (700, 606)]
    for (num, text), (x, y) in zip(items, positions):
        body.append(circle(x + 20, y - 7, 20, fill="none", stroke=ACCENT, sw=1.5))
        body.append(t(x + 20, y, num, 13, ACCENT, MONO, 700, anchor="middle"))
        body.append(t(x + 58, y, text, 21, INK, SANS, 400))

    body.append(line(130, 716, 1246, 716, LINE, 1, dash="4 6"))
    body.append(t(130, 746, "//", 14, DIM, MONO, 500))
    body.append(
        t(158, 746, "目標不是更快得到答案，而是讓答案還能被驗證。", 15, MUTED, SANS, 400)
    )

    body.append(
        t(
            688,
            814,
            "十分鐘不是為了贏過 AI，是為了讓答案還找得到位置。",
            20,
            MUTED,
            SANS,
            400,
            anchor="middle",
        )
    )
    return figure(
        idx,
        w,
        h,
        "打開 ChatGPT 前的十分鐘",
        "PROTOCOL · 10 MINUTES",
        "".join(body),
    )


def cover():
    w, h = 1200, 630
    body = []
    grid_id = "coverdots"
    body.append(
        f'<pattern id="{grid_id}" width="26" height="26" patternUnits="userSpaceOnUse">'
        f'<circle cx="1" cy="1" r="1" fill="#FFFFFF" opacity="0.055"/></pattern>'
        f'<rect width="{w}" height="{h}" fill="url(#{grid_id})"/>'
    )
    body.append(rect(24, 24, w - 48, h - 48, fill="none", stroke=LINE, rx=0, sw=1, opacity=0.9))
    body.append(t(64, 92, "ENGINEERING NOTES / 2026", 13, ACCENT, MONO, 600, ls=3))
    body.append(t(w - 64, 92, "FIELD NOTE 00", 12, DIM, MONO, 500, anchor="end", ls=2.4))

    body.append(t(64, 194, "AI 把 Bug", 58, INK, SERIF, 700))
    body.append(t(64, 258, "修好了，", 58, INK, SERIF, 700))
    body.append(rect(64, 280, 76, 4, fill=ACCENT, rx=2, sw=0))
    body.append(t(64, 334, "我這工程師只剩", 34, MUTED, SANS, 500))
    body.append(t(58, 470, "BI", 132, ACCENT, SERIF, 700))
    body.append(rect(64, 494, 152, 7, fill=ACCENT, rx=3.5, sw=0))
    body.append(t(64, 546, "效率、理解，與那些被跳過的步驟", 18, MUTED, SANS, 400))
    body.append(t(64, 584, "JAY FU", 11, DIM, MONO, 500, ls=2.6))

    tx, ty, tw, th = 690, 104, 446, 424
    body.append(rect(tx, ty, tw, th, fill="#0D1524", stroke=LINE, rx=14, sw=1.4))
    body.append(rect(tx, ty, tw, 46, fill="#16213A", rx=14, sw=0))
    body.append(rect(tx, ty + 30, tw, 16, fill="#16213A", rx=0, sw=0))
    body.append(circle(tx + 24, ty + 23, 5, fill=RED))
    body.append(circle(tx + 42, ty + 23, 5, fill=AMBER))
    body.append(circle(tx + 60, ty + 23, 5, fill=TEAL))
    body.append(t(tx + tw - 20, ty + 28, "zsh · 80×24", 10.5, DIM, MONO, 400, anchor="end"))
    body.append(t(tx + 24, ty + 92, "$ pytest -q", 15, INK, MONO, 400))
    body.append(t(tx + 24, ty + 130, "..........", 20, TEAL, MONO, 700, ls=3))
    body.append(t(tx + 24, ty + 162, "10 passed in 0.42s", 13, TEAL, MONO, 500))
    body.append(t(tx + 24, ty + 216, "> 為什麼這樣會對？_", 15, INK, MONO, 400))
    body.append(rect(tx + 24, ty + 246, 300, 12, fill="#22314C", rx=3, sw=0))
    body.append(rect(tx + 24, ty + 272, 232, 12, fill="#22314C", rx=3, sw=0))
    body.append(rect(tx + 24, ty + 298, 268, 12, fill="#22314C", rx=3, sw=0))
    body.append(rect(tx + 24, ty + 340, 178, 32, fill="#0C2420", stroke=TEAL, rx=8, sw=1.2))
    body.append(t(tx + 113, ty + 362, "ALL TESTS PASSED", 11, TEAL, MONO, 600, anchor="middle", ls=1.4))
    body.append(t(tx + 24, ty + 400, "但你知道它為什麼通過嗎？", 12, AMBER, MONO, 400))

    body.append(t(tx + 320, ty + 380, "?", 190, "#FFFFFF", SERIF, 700, opacity=0.055))
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">'
        "<title>AI 把 Bug 修好了，我這工程師只剩 BI</title>"
        "<desc>Original cover art: a dark terminal with a passing test suite and an unanswered question.</desc>"
        + DEFS
        + f'<rect width="{w}" height="{h}" fill="{BG}"/>'
        + f'<rect width="{w}" height="{h}" fill="url(#gVignette)"/>'
        + "".join(body)
        + "</svg>"
    )


FIGURES = [
    ("01_speed_gap", fig_01),
    ("02_search_path", fig_02),
    ("03_assumption_spiral", fig_03),
    ("04_pandas_index", fig_04),
    ("05_silent_assumption", fig_05),
    ("06_offline", fig_06),
    ("07_quadrant", fig_07),
    ("08_ten_minutes", fig_08),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", action="store_true", help="render into a temp folder")
    args = parser.parse_args()

    target = PREVIEW_DIR if args.preview else BUNDLE_IMAGES
    target.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for name, maker in FIGURES:
        svg = maker()
        svg_path = OUT_DIR / f"{name}.svg"
        svg_path.write_text(svg, encoding="utf-8")
        dest = target / f"{name}.webp"
        svg_to_webp(svg_path, dest, width=1376)
        print(f"{svg_path.relative_to(ROOT)} -> {dest}")

    cover_svg = cover()
    cover_svg_path = OUT_DIR / "00_cover.svg"
    cover_svg_path.write_text(cover_svg, encoding="utf-8")
    cover_dest = target / "cover.jpg"
    svg_to_jpeg(cover_svg_path, cover_dest, width=1200)
    print(f"{cover_svg_path.relative_to(ROOT)} -> {cover_dest}")


if __name__ == "__main__":
    main()
