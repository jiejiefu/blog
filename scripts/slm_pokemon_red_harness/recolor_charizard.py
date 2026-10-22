#!/usr/bin/env python3
"""Recolor the PokeAPI Dream World Charizard SVG with a shiny-inspired palette."""

import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "charizard.svg"
OUTPUT = HERE / "charizard_shiny.svg"

PALETTE = {
    "#0d131a": "#05060a",  # outline
    "#f29600": "#5a6170",  # body
    "#d18200": "#353b47",  # body shadow
    "#ffffff": "#f3e4b5",  # belly, claws, teeth
    "#dbdcdc": "#cdbd90",  # belly shadow
    "#008086": "#9e1b2e",  # wing membrane
    "#00666c": "#5f0e1a",  # wing membrane shadow
    "#ddd583": "#e2d0a0",  # secondary highlight
    "#e50020": "#ff5a1f",  # outer flame
    "#efe908": "#ffc93c",  # mid flame
    "#fff697": "#fff0b3",  # flame core
}
PALETTE = {key.lstrip("#"): value for key, value in PALETTE.items()}


def main() -> None:
    svg = SOURCE.read_text(encoding="utf-8")
    found: Counter[str] = Counter()

    def replace(match: re.Match[str]) -> str:
        color = match.group(1).lower()
        found[color] += 1
        try:
            return f'fill="{PALETTE[color]}"'
        except KeyError as exc:
            raise SystemExit(f"unmapped fill color in {SOURCE.name}: {color}") from exc

    recolored = re.sub(r'fill="#([0-9a-fA-F]{6})"', replace, svg)

    missing = sorted(set(PALETTE) - set(found))
    if missing:
        raise SystemExit(f"expected palette colors not found: {', '.join(missing)}")

    comment = (
        "<!-- Shiny palette derived from PokeAPI official-artwork/shiny/6.png "
        "and home/shiny/6.png; recolored from the Dream World SVG. -->\n"
    )
    recolored = recolored.replace("<svg ", comment + "<svg ", 1)

    OUTPUT.write_text(recolored, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(HERE.parent.parent)}")
    for color, count in found.most_common():
        print(f"  {color} -> {PALETTE[color]} ({count})")


if __name__ == "__main__":
    main()
