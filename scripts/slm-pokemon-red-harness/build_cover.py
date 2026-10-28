#!/usr/bin/env python3
"""Build cover.svg and cover.jpg for the SLM x Pokemon Red harness post."""

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TEMPLATE = HERE / "cover_template.svg"
SPRITE = HERE / "charizard_shiny.svg"
OUTPUT = HERE / "cover.svg"
COVER_JPG = ROOT / "content/zh-tw/posts/slm-pokemon-red-harness/images/cover.jpg"
MARKER = "  <!-- CHARIZARD_AURA_AND_SPRITE -->"

sys.path.insert(0, str(ROOT / "scripts"))
from image_utils import svg_to_jpeg  # noqa: E402


def main() -> None:
    template = TEMPLATE.read_text(encoding="utf-8")
    sprite = SPRITE.read_text(encoding="utf-8")

    match = re.search(r"<svg[^>]*>(.*)</svg>\s*$", sprite, re.S)
    if match is None:
        raise SystemExit(f"could not find SVG content in {SPRITE}")

    block = "\n".join(
        [
            '  <svg x="850" y="22" width="320" height="313.2" '
            'viewBox="-0.1 -0.25 361.75 354.1" aria-label="Shiny Charizard">',
            match.group(1).strip(),
            "  </svg>",
        ]
    )

    if MARKER not in template:
        raise SystemExit(f"marker not found in {TEMPLATE}")

    OUTPUT.write_text(template.replace(MARKER, block), encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")

    svg_to_jpeg(OUTPUT, COVER_JPG, width=1200, quality=85)
    print(f"wrote {COVER_JPG.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
