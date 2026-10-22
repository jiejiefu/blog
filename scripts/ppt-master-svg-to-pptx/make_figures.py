#!/usr/bin/env python3
"""Generate the three inline figures for the PPT Master deep dive.

The editable SVG sources live next to this script. WebP files are written
straight into the post's page bundle; no PNG intermediate is published.

Usage:
    python3 scripts/ppt-master-svg-to-pptx/make_figures.py
"""

import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BUNDLE_IMAGES = ROOT / "content/zh-tw/posts/ppt-master-svg-to-pptx/images"

sys.path.insert(0, str(ROOT / "scripts"))
from image_utils import svg_to_webp  # noqa: E402

MONO = "'SF Mono','Menlo','DejaVu Sans Mono',monospace"
SANS = "'PingFang TC','Noto Sans TC','Heiti TC',sans-serif"

BG = "#0A0A0A"
PANEL = "#131313"
PANEL_2 = "#191919"
LINE = "#2B2B2B"
INK = "#F5F5F5"
MID = "#D1D5DB"
MUTED = "#9A9A9A"
DIM = "#5C5C5C"
ACCENT = "#938BFF"
ACCENT_SOFT = "#C7C2FF"
RED = "#FF7A7A"

PAGE_BINS = [
    ("6–9", 8),
    ("10–13", 18),
    ("14–17", 37),
    ("18–21", 5),
    ("22–25", 0),
    ("26–31", 2),
]

CANVASES = [
    ("16:9", 55),
    ("4:3", 3),
    ("A4", 2),
    ("故事卡", 2),
    ("小紅書", 2),
    ("微信橫幅", 2),
    ("方形貼文", 2),
    ("橫幅", 1),
    ("自訂", 1),
]


def esc(value):
    return html.escape(str(value), quote=True)


def text(x, y, value, *, size=20, fill=MUTED, family=SANS, weight=None,
         spacing=None, anchor=None, opacity=None, style=None):
    attrs = [f'x="{x}"', f'y="{y}"', f'font-family="{family}"',
             f'font-size="{size}"', f'fill="{fill}"']
    if weight:
        attrs.append(f'font-weight="{weight}"')
    if spacing:
        attrs.append(f'letter-spacing="{spacing}"')
    if anchor:
        attrs.append(f'text-anchor="{anchor}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    if style:
        attrs.append(f'font-style="{style}"')
    return f'<text {" ".join(attrs)}>{esc(value)}</text>'


def rect(x, y, w, h, *, fill=PANEL, stroke=None, sw=1, rx=0, opacity=None):
    attrs = [f'x="{x}"', f'y="{y}"', f'width="{w}"', f'height="{h}"',
             f'fill="{fill}"']
    if stroke:
        attrs += [f'stroke="{stroke}"', f'stroke-width="{sw}"']
    if rx:
        attrs.append(f'rx="{rx}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    return f'<rect {" ".join(attrs)}/>'


def line(x1, y1, x2, y2, *, stroke=LINE, sw=1, dash=None, opacity=None):
    attrs = [f'x1="{x1}"', f'y1="{y1}"', f'x2="{x2}"', f'y2="{y2}"',
             f'stroke="{stroke}"', f'stroke-width="{sw}"']
    if dash:
        attrs.append(f'stroke-dasharray="{dash}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    return f'<line {" ".join(attrs)}/>'


def circle(cx, cy, r, *, fill=ACCENT, stroke=None, sw=1, opacity=None):
    attrs = [f'cx="{cx}"', f'cy="{cy}"', f'r="{r}"', f'fill="{fill}"']
    if stroke:
        attrs += [f'stroke="{stroke}"', f'stroke-width="{sw}"']
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    return f'<circle {" ".join(attrs)}/>'


def arrow(x1, y1, x2, y2, *, stroke=ACCENT, sw=2):
    return "".join([
        line(x1, y1, x2, y2, stroke=stroke, sw=sw),
        f'<path d="M{x2} {y2}l-10 -5v10z" fill="{stroke}"/>',
    ])


def dotgrid(w, h, gap=24):
    return "".join([
        f'<pattern id="dots" width="{gap}" height="{gap}" '
        'patternUnits="userSpaceOnUse">'
        f'<circle cx="1" cy="1" r="1" fill="#FFFFFF" opacity="0.06"/>'
        "</pattern>",
        f'<rect width="{w}" height="{h}" fill="url(#dots)"/>',
    ])


def svg_doc(width, height, title, desc, body):
    return "".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {width} {height}">',
        f"<title>{esc(title)}</title>",
        f"<desc>{esc(desc)}</desc>",
        rect(0, 0, width, height, fill=BG),
        dotgrid(width, height),
        body,
        "</svg>",
    ])


def badge(x, y, number, *, accent=False):
    fill = ACCENT if accent else PANEL_2
    color = BG if accent else INK
    stroke = ACCENT if accent else LINE
    return "".join([
        circle(x, y, 27, fill=fill, stroke=stroke, sw=1.5),
        text(x, y + 8, str(number), size=23, fill=color, family=MONO,
             weight="700", anchor="middle"),
    ])


def build_route_matrix():
    parts = []
    parts.append(text(72, 88, "四種 AI 簡報做法", size=52, fill=INK, weight="700"))
    parts.append(text(72, 132, "版面自由度 × 可編輯性", size=28, fill=MUTED))
    parts.append(text(1304, 86, "QUALITATIVE MAP / 01", size=13, fill=DIM,
                      family=MONO, spacing="2", anchor="end"))
    parts.append(line(72, 154, 332, 154, stroke=ACCENT, sw=3))

    left, top, right, bottom = 150, 210, 1250, 720
    mid_x = (left + right) / 2
    mid_y = (top + bottom) / 2

    parts.append(rect(left, top, mid_x - left, mid_y - top, fill=PANEL,
                      opacity="0.72"))
    parts.append(rect(mid_x, top, right - mid_x, mid_y - top, fill=PANEL,
                      opacity="0.42"))
    parts.append(rect(left, mid_y, mid_x - left, bottom - mid_y, fill=PANEL,
                      opacity="0.28"))
    parts.append(rect(mid_x, mid_y, right - mid_x, bottom - mid_y,
                      fill=PANEL, opacity="0.52"))

    parts.append(line(left, bottom, right, bottom, stroke="#3A3A3A", sw=1.5))
    parts.append(line(left, top, left, bottom, stroke="#3A3A3A", sw=1.5))
    parts.append(line(mid_x, top, mid_x, bottom, stroke=LINE, dash="5 8",
                      opacity="0.8"))
    parts.append(line(left, mid_y, right, mid_y, stroke=LINE, dash="5 8",
                      opacity="0.8"))
    parts.append(f'<path d="M{right} {bottom}l-9 -4v8z" fill="#3A3A3A"/>')
    parts.append(f'<path d="M{left} {top}l-4 9h8z" fill="#3A3A3A"/>')

    parts.append(text(left + 28, top + 40, "自由，但難改", size=22, fill=DIM))
    parts.append(text(right - 28, top + 40, "自由且可編輯", size=22,
                      fill=ACCENT_SOFT, anchor="end"))
    parts.append(text(left + 28, bottom - 24, "兩邊都不足", size=22, fill=DIM))
    parts.append(text(right - 28, bottom - 24, "可編輯，但版面受限", size=22,
                      fill=DIM, anchor="end"))

    parts.append(
        f'<g transform="translate(96 {((top + bottom) / 2):.0f}) rotate(-90)">'
        + text(0, 0, "版面自由度", size=24, fill=MUTED, anchor="middle")
        + "</g>"
    )
    parts.append(text(left, bottom + 32, "低", size=20, fill=DIM))
    parts.append(text(right, bottom + 32, "高", size=20, fill=DIM,
                      anchor="end"))
    parts.append(text((left + right) / 2, bottom + 60, "可編輯性 →", size=24,
                      fill=MUTED, anchor="middle"))

    parts.append(badge(330, 300, 1))
    parts.append(text(365, 307, "截圖", size=22, fill=MID))
    parts.append(badge(480, 405, 2))
    parts.append(text(480, 357, "隱形文字", size=22, fill=MID, anchor="middle"))
    parts.append(badge(860, 585, 3))
    parts.append(text(860, 535, "python-pptx", size=22, fill=MID,
                      anchor="middle"))
    parts.append(circle(1055, 350, 43, fill=ACCENT, opacity="0.10"))
    parts.append(badge(1055, 350, 4, accent=True))
    parts.append(text(1055, 292, "PPT Master", size=22, fill=ACCENT_SOFT,
                      anchor="middle"))

    legend = [
        (1, "HTML／Playwright 截圖", "版面最自由，但文字與圖表不能改。", False),
        (2, "整頁圖片＋隱形文字", "demo 最像，改一個字就破功。", False),
        (3, "python-pptx 填空", "原生可編輯，複雜圖形要手寫座標。", False),
        (4, "PPT Master", "兩者兼顧，但需要來源材料與 review。", True),
    ]
    for i, (number, title, cost, accent) in enumerate(legend):
        x = 150 if i % 2 == 0 else 720
        y = 820 if i < 2 else 892
        parts.append(badge(x + 14, y - 8, number, accent=accent))
        parts.append(text(x + 54, y, title, size=26,
                          fill=ACCENT_SOFT if accent else INK,
                          weight="700"))
        parts.append(text(x + 54, y + 31, cost, size=22, fill=MUTED))

    parts.append(text(72, 958, "定位是相對的，不是評分。", size=18, fill=DIM))
    parts.append(text(1304, 958, "質性示意，非量測", size=18, fill=DIM,
                      anchor="end"))

    return svg_doc(
        1376,
        980,
        "四種 AI 簡報做法的 2×2 定位圖",
        "HTML／Playwright 截圖、整頁圖片加隱形文字、python-pptx 填空與 "
        "PPT Master，依版面自由度與可編輯性做質性定位。",
        "".join(parts),
    )


def build_svg_contract():
    parts = []
    parts.append(text(72, 88, "SVG 不是「任何 SVG 都收」", size=50, fill=INK,
                      weight="700"))
    parts.append(text(72, 132, "契約是海關：放行可對映的元素，擋下無法保證的表達。",
                      size=26, fill=MUTED))
    parts.append(text(1304, 86, "CONTRACT / 02", size=13, fill=DIM,
                      family=MONO, spacing="2", anchor="end"))
    parts.append(line(72, 154, 354, 154, stroke=ACCENT, sw=3))

    top, height = 182, 500

    # Left: arbitrary browser SVG
    parts.append(rect(72, top, 326, height, fill=PANEL))
    parts.append(text(96, top + 36, "BROWSER SVG", size=12, fill=DIM,
                      family=MONO, spacing="2"))
    parts.append(text(96, top + 78, "任意 SVG", size=34, fill=INK, weight="700"))
    parts.append(text(96, top + 108, "瀏覽器能畫 ≠ 編譯器能收。",
                      size=20, fill=MUTED))

    allowed = ["<text>", "<rect>", "<path>", "<image>", "<g>", "<use>"]
    for i, label in enumerate(allowed):
        x = 96 + (i % 2) * 150
        y = top + 132 + (i // 2) * 54
        parts.append(rect(x, y, 136, 40, fill=PANEL_2, stroke=LINE, rx=3))
        parts.append(text(x + 14, y + 27, label, size=20, fill=MID,
                          family=MONO))

    parts.append(line(96, top + 310, 374, top + 310, stroke=LINE))
    parts.append(text(96, top + 340, "契約外", size=20, fill=RED,
                      weight="700"))
    parts.append(rect(96, top + 352, 278, 116, fill="#1C1111", stroke="#5A2A2A",
                      rx=3))
    parts.append(text(110, top + 384, "× filter   × mask", size=18, fill=RED,
                      family=MONO))
    parts.append(text(110, top + 416, "× foreignObject", size=18, fill=RED,
                      family=MONO))
    parts.append(text(110, top + 448, "× 複雜文字排版", size=18, fill=RED))

    # Middle: contract gate
    parts.append(rect(438, top, 500, height, fill=PANEL_2, stroke=ACCENT,
                      sw=1.5))
    parts.append(text(462, top + 36, "CONTRACT GATE", size=12, fill=ACCENT,
                      family=MONO, spacing="2"))
    parts.append(text(462, top + 78, "專案契約", size=34, fill=INK,
                      weight="700"))
    parts.append(text(462, top + 108, "不是轉檔器，是一組可驗證的邊界。",
                      size=20, fill=MUTED))

    gates = [
        ("01", "元素白名單", "只允許可對映到 DrawingML 的元素。"),
        ("02", "屬性與單位", "座標、數值、transform 先正規化。"),
        ("03", "metadata／結構", "頁面、圖層、文字框有固定約定。"),
        ("04", "DrawingML 對映", "每個節點不是有目標物件，就是被拒絕。"),
    ]
    for i, (number, title, desc) in enumerate(gates):
        y = top + 132 + i * 82
        parts.append(rect(462, y, 452, 64, fill=BG, stroke=LINE, rx=3))
        parts.append(text(480, y + 41, number, size=18, fill=ACCENT,
                          family=MONO, weight="700"))
        parts.append(text(522, y + 27, title, size=24, fill=INK,
                          weight="700"))
        parts.append(text(522, y + 52, desc, size=18, fill=MUTED))

    # Right: DrawingML
    parts.append(rect(978, top, 326, height, fill=PANEL))
    parts.append(text(1002, top + 36, "NATIVE PPTX", size=12, fill=DIM,
                      family=MONO, spacing="2"))
    parts.append(text(1002, top + 78, "DrawingML", size=34, fill=INK,
                      weight="700"))
    parts.append(text(1002, top + 108, "文字、形狀、圖表、圖片。",
                      size=18, fill=MUTED))

    native = [
        ("文字", "text run"),
        ("形狀", "shape"),
        ("圖表", "native chart"),
        ("圖片", "picture"),
    ]
    for i, (label, sub) in enumerate(native):
        y = top + 132 + i * 82
        parts.append(rect(1002, y, 278, 64, fill=BG, stroke=LINE, rx=3))
        parts.append(text(1022, y + 41, label, size=26, fill=ACCENT_SOFT,
                          weight="700"))
        parts.append(text(1084, y + 41, "→  " + sub, size=20, fill=MID,
                          family=MONO))

    arrow(398, top + 250, 434, top + 250)
    arrow(938, top + 250, 974, top + 250)

    parts.append(text(72, 742,
                      "\"SVG adapts to PPT Master; PPT Master does not expand "
                      "to follow the entire SVG standard.\"",
                      size=24, fill=MID, style="italic"))
    parts.append(text(72, 772, "— 官方文件", size=18, fill=DIM))
    parts.append(text(72, 832,
                      "契約外不等於一定失敗：有些會被正規化，有些會在品質閘門被擋下。",
                      size=22, fill=MUTED))

    return svg_doc(
        1376,
        900,
        "任意 SVG、專案契約與 DrawingML 的邊界",
        "左側是瀏覽器可接受的任意 SVG，中間是專案契約與品質閘門，"
        "右側是可編輯的 DrawingML 物件；filter、mask、foreignObject 與"
        "複雜文字排版會被擋下或正規化。",
        "".join(parts),
    )


def build_examples_distribution():
    parts = []
    parts.append(text(72, 88, "70 份範例，不是 70 套模板", size=52, fill=INK,
                      weight="700"))
    parts.append(text(72, 132, "同一套編譯器，在不同長度與畫布上的測試集。",
                      size=28, fill=MUTED))
    parts.append(text(1304, 86, "EXAMPLE SET / 03", size=13, fill=DIM,
                      family=MONO, spacing="2", anchor="end"))
    parts.append(line(72, 154, 426, 154, stroke=ACCENT, sw=3))

    stats = [("70", "公開範例"), ("987", "總頁數"), ("9", "畫布格式"),
             ("14", "頁數中位數")]
    for i, (number, label) in enumerate(stats):
        x = 72 + i * 320
        parts.append(rect(x, 176, 300, 92, fill=PANEL, stroke=LINE, rx=4))
        parts.append(text(x + 24, 230, number, size=48, fill=ACCENT_SOFT,
                          weight="700"))
        parts.append(text(x + 122, 224, label, size=22, fill=MUTED))

    # Left: page count distribution
    parts.append(rect(72, 310, 620, 520, fill=PANEL))
    parts.append(text(96, 350, "頁數分布", size=28, fill=INK, weight="700"))
    parts.append(text(96, 380, "6–31 頁，4 頁一組；15 頁最常見。",
                      size=20, fill=MUTED))
    parts.append(text(668, 350, "中位數 14", size=22, fill=ACCENT_SOFT,
                      weight="700", anchor="end"))

    chart_left, chart_right = 120, 660
    baseline, chart_top = 760, 420
    y_max = 40
    for value in (0, 10, 20, 30, 40):
        y = baseline - (value / y_max) * (baseline - chart_top)
        parts.append(line(chart_left, y, chart_right, y,
                          stroke=LINE, sw=1, opacity="0.75"))
        parts.append(text(chart_left - 14, y + 7, str(value), size=18,
                          fill=DIM, family=MONO, anchor="end"))

    bar_w = 48
    centers = [155, 240, 325, 410, 495, 580]
    for i, ((label, value), cx) in enumerate(zip(PAGE_BINS, centers)):
        h = (value / y_max) * (baseline - chart_top)
        accent = label == "14–17"
        parts.append(rect(cx - bar_w / 2, baseline - h, bar_w, h,
                          fill=ACCENT if accent else "#343434", rx=2))
        parts.append(text(cx, baseline - h - 16, str(value), size=24,
                          fill=ACCENT_SOFT if accent else MID,
                          family=MONO, weight="700", anchor="middle"))
        parts.append(text(cx, baseline + 30, label, size=20, fill=MUTED,
                          family=MONO, anchor="middle"))

    parts.append(line(chart_left, baseline, chart_right, baseline,
                      stroke="#4A4A4A", sw=1.5))
    parts.append(text(chart_left, baseline + 58, "每組頁數", size=18, fill=DIM))

    # Right: canvas formats
    parts.append(rect(730, 310, 574, 520, fill=PANEL))
    parts.append(text(754, 350, "畫布格式", size=28, fill=INK, weight="700"))
    parts.append(text(754, 380, "其餘 15 份分散在 8 種格式。",
                      size=20, fill=MUTED))

    max_count = 55
    bar_x, bar_max = 864, 290
    for i, (label, value) in enumerate(CANVASES):
        y = 420 + i * 44
        width = max(4, (value / max_count) * bar_max)
        accent = label == "16:9"
        parts.append(text(754, y + 16, label, size=20, fill=MID))
        parts.append(rect(bar_x, y, bar_max, 16, fill="#202020", rx=3))
        parts.append(rect(bar_x, y, width, 16,
                          fill=ACCENT if accent else "#5C5C5C", rx=3))
        parts.append(text(bar_x + width + 12, y + 16, str(value), size=20,
                          fill=ACCENT_SOFT if accent else MUTED,
                          family=MONO, weight="700"))

    footer = ("資料來源：ppt-master-examples/examples.json 的 stats 與 "
              "slides 計數；頁數 bin 為 4 頁一組。")
    parts.append(text(72, 892, footer, size=18, fill=DIM))

    return svg_doc(
        1376,
        940,
        "70 份公開範例的頁數與畫布分布",
        "70 份範例合計 987 頁，頁數介於 6 到 31 頁，中位數 14；"
        "55 份是 16:9，其餘 15 份分布在 8 種畫布格式。",
        "".join(parts),
    )


FIGURES = [
    ("route-matrix", build_route_matrix),
    ("svg-contract", build_svg_contract),
    ("examples-distribution", build_examples_distribution),
]


def main():
    BUNDLE_IMAGES.mkdir(parents=True, exist_ok=True)
    for name, builder in FIGURES:
        svg = builder()
        svg_path = HERE / f"{name}.svg"
        svg_path.write_text(svg, encoding="utf-8")

        webp_path = BUNDLE_IMAGES / f"{name}.webp"
        svg_to_webp(svg_path, webp_path, width=1376, quality=86)
        print(f"svg:  {svg_path}")
        print(f"webp: {webp_path}")


if __name__ == "__main__":
    main()
