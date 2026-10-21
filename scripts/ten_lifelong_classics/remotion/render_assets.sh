#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
OUT="${REMOTION_PUBLIC:-$HOME/.config/opencode/remotion/public}/ten-classics"
TMP="$(mktemp -d)"

trap 'rm -rf "$TMP"' EXIT
mkdir -p "$OUT"

# The video supplies its own titles, so strip the cover chrome before rasterising:
#   * right-anchored labels (top-right brand, PAIR 0X, motif captions)
#   * anything in the left column (rank, medium, title, thesis, credits)
# The Matrix rain is <text> at x >= 626, so it survives.
python3 - "$ROOT" "$TMP" <<'PY'
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1])
out = pathlib.Path(sys.argv[2])

for svg in sorted((root / "scripts" / "ten_lifelong_classics").glob("[0-9]*.svg")):
    if svg.name.startswith("00_"):
        continue
    source = svg.read_text(encoding="utf-8")

    def strip(match: re.Match) -> str:
        attrs = match.group(1)
        if 'text-anchor="end"' in attrs:
            return ""
        x = re.search(r'\bx="([\d.]+)"', attrs)
        if x and float(x.group(1)) <= 100:
            return ""
        return match.group(0)

    cleaned = re.sub(r"<text\b([^>]*)>.*?</text>", strip, source, flags=re.S)
    (out / svg.name).write_text(cleaned, encoding="utf-8")
PY

for svg in "$TMP"/[0-9]*.svg; do
  base="$(basename "$svg" .svg)"
  rsvg-convert -w 2400 "$svg" -o "$OUT/$base.png"
done

ls -lh "$OUT"
