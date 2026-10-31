#!/usr/bin/env python3
"""Build the phosphor-silhouette cover for the matrix rabbit article.

The silhouette is a self-made vector tracing kept next to this script. The
cover is composed as SVG, rendered with rsvg-convert, then resized to the
1200x630 JPEG that PaperMod expects.

Usage:
    python3 scripts/matrix-rabbit-canvas/make_cover.py
    python3 scripts/matrix-rabbit-canvas/make_cover.py --preview
"""

from __future__ import annotations

import argparse
import re
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SILHOUETTE = HERE / "silhouette.svg"
COVER_SVG = HERE / "cover.svg"
COVER_JPG = ROOT / "content/zh-tw/posts/matrix-rabbit-canvas/images/cover.jpg"

W, H = 2400, 1260

MONO = "'JetBrains Mono','Menlo',monospace"
CJK = "'PingFang TC','Noto Sans TC',sans-serif"


def silhouette_group() -> str:
    svg = SILHOUETTE.read_text(encoding="utf-8")
    match = re.search(r'<g[^>]*fill="#000000"[^>]*>.*?</g>', svg, re.S)
    if not match:
        raise SystemExit("silhouette.svg: no black-filled <g> found")
    return match.group(0).replace('fill="#000000"', 'fill="url(#phosphor)"', 1)


def build_svg() -> str:
    rabbit = silhouette_group()
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <pattern id="dots" width="32" height="32" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1.5" fill="#14251a"/>
    </pattern>
    <linearGradient id="phosphor" x1="0" y1="0" x2="0.25" y2="1">
      <stop offset="0" stop-color="#2f7a4a"/>
      <stop offset="0.45" stop-color="#6ee79a"/>
      <stop offset="0.78" stop-color="#b6ffcc"/>
      <stop offset="1" stop-color="#e2fff0"/>
    </linearGradient>
    <linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#6ee79a"/>
      <stop offset="1" stop-color="#b6ffcc"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#6ee79a" stop-opacity="0.20"/>
      <stop offset="0.55" stop-color="#3f8f5c" stop-opacity="0.08"/>
      <stop offset="1" stop-color="#0a110c" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <rect width="{W}" height="{H}" fill="#080f0a"/>
  <rect width="{W}" height="{H}" fill="url(#dots)"/>

  <rect x="90" y="70" width="2220" height="1120" rx="28" fill="#000000" opacity="0.45"/>
  <rect x="78" y="54" width="2220" height="1120" rx="28" fill="#0a130c" stroke="#22382a" stroke-width="2"/>

  <line x1="78" y1="170" x2="2298" y2="170" stroke="#1c2f22" stroke-width="2"/>
  <circle cx="126" cy="112" r="9" fill="#ff5f56"/>
  <circle cx="166" cy="112" r="9" fill="#ffbd2e"/>
  <circle cx="206" cy="112" r="9" fill="#27c93f"/>
  <text x="242" y="121" font-family="{MONO}" font-size="26" fill="#8fa895">jay fu blog — hero glyph</text>
  <text x="2260" y="121" text-anchor="end" font-family="{MONO}" font-size="26" fill="#6ee79a">● LIVE</text>

  <circle cx="1750" cy="690" r="540" fill="url(#glow)"/>

  <g transform="translate(1461 242) scale(1.006)">
    {rabbit}
  </g>

  <text x="180" y="330" font-family="{MONO}" font-size="30" fill="#6ee79a">$ ./hare --draw</text>

  <text x="168" y="520" font-family="{MONO}" font-size="208" font-weight="700" fill="#f2f7f3" letter-spacing="-8">RABBIT</text>
  <rect x="180" y="556" width="320" height="8" rx="4" fill="url(#rule)"/>

  <text x="180" y="652" font-family="{CJK}" font-size="46" fill="#b9c9be">用文字畫一隻兔子</text>
  <text x="180" y="716" font-family="{MONO}" font-size="28" fill="#8fa895">132 × 110 · 14,520 cells · 8 levels</text>

  <rect x="180" y="778" width="192" height="56" rx="8" fill="none" stroke="#2f7a4a" stroke-width="2"/>
  <text x="276" y="814" text-anchor="middle" font-family="{MONO}" font-size="24" fill="#cfe0d4">CANVAS</text>
  <rect x="392" y="778" width="292" height="56" rx="8" fill="none" stroke="#2c4636" stroke-width="2"/>
  <text x="538" y="814" text-anchor="middle" font-family="{MONO}" font-size="24" fill="#cfe0d4">MARTIAN MONO</text>
  <rect x="704" y="778" width="272" height="56" rx="8" fill="none" stroke="#2c4636" stroke-width="2"/>
  <text x="840" y="814" text-anchor="middle" font-family="{MONO}" font-size="24" fill="#cfe0d4">NO-JS FALLBACK</text>

  <line x1="180" y1="960" x2="1040" y2="960" stroke="#1c2f22" stroke-width="2"/>
  <text x="180" y="1026" font-family="{CJK}" font-size="26" fill="#7f9a88">首頁 hero · 只載入一次 · 尊重 prefers-reduced-motion</text>
  <text x="180" y="1070" font-family="{MONO}" font-size="24" fill="#4f6b58">document.fonts.load → draw → heat → idle</text>
</svg>
"""


def render(preview: bool) -> Path:
    COVER_SVG.write_text(build_svg(), encoding="utf-8")
    dest = Path(tempfile.mkdtemp(prefix="rabbit-cover-")) / "cover.jpg" if preview else COVER_JPG
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="rabbit-cover-") as tmp:
        png = Path(tmp) / "cover.png"
        subprocess.run(
            ["rsvg-convert", "-w", str(W), "-h", str(H), str(COVER_SVG), "-o", str(png)],
            check=True,
        )
        subprocess.run(
            [
                "magick",
                str(png),
                "-resize",
                "1200x630!",
                "-strip",
                "-quality",
                "85",
                str(dest),
            ],
            check=True,
        )
    return dest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true", help="write to a temp dir")
    args = parser.parse_args()
    print(render(args.preview))


if __name__ == "__main__":
    main()
