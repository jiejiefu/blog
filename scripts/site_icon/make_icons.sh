#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SRC="$ROOT/assets/images/brand/djfj-logo.png"
OUT="$ROOT/static"

BG="#0B1220"
RADIUS=224          # 22% of 1024
LOGO_WIDTH=942      # 92% of 1024, keeps ~4% breathing room per side

if ! command -v magick >/dev/null 2>&1; then
  echo "error: ImageMagick 7 (magick) is required" >&2
  exit 1
fi

if [ ! -f "$SRC" ]; then
  echo "error: source logo not found: ${SRC#"$ROOT"/}" >&2
  exit 1
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

mkdir -p "$OUT"

# Trim the 7px transparent border, then upscale once to the master size.
magick "$SRC" -trim +repage "$tmp/logo.png"

# Rounded tile: favicons. Square tile: apple-touch / Android (OS masks them).
magick -size 1024x1024 xc:none \
  -fill "$BG" -draw "roundrectangle 0,0 1023,1023 $RADIUS,$RADIUS" \
  "$tmp/rounded-bg.png"
magick -size 1024x1024 "xc:$BG" "$tmp/square-bg.png"

magick "$tmp/rounded-bg.png" \
  \( "$tmp/logo.png" -filter Lanczos -resize "${LOGO_WIDTH}x" \) \
  -gravity center -composite "PNG32:$tmp/rounded-1024.png"
magick "$tmp/square-bg.png" \
  \( "$tmp/logo.png" -filter Lanczos -resize "${LOGO_WIDTH}x" \) \
  -gravity center -composite "PNG32:$tmp/square-1024.png"

for size in 16 32; do
  magick "$tmp/rounded-1024.png" -filter Lanczos -resize "${size}x${size}" \
    -strip "PNG32:$OUT/favicon-${size}x${size}.png"
done
# Square icons are fully opaque: an 8-bit palette cuts ~70% of the bytes with
# imperceptible banding (RMSE ~0.9% on the metallic gradient).
magick "$tmp/square-1024.png" -filter Lanczos -resize 180x180 \
  -alpha off -colors 256 -strip "PNG8:$OUT/apple-touch-icon.png"
for size in 192 512; do
  magick "$tmp/square-1024.png" -filter Lanczos -resize "${size}x${size}" \
    -alpha off -colors 256 -strip "PNG8:$OUT/android-chrome-${size}x${size}.png"
done

for size in 16 32 48 64 128 256; do
  if [ "$size" -le 48 ]; then
    magick "$tmp/rounded-1024.png" -filter Lanczos -resize "${size}x${size}" \
      -strip "PNG32:$tmp/ico-${size}.png"
  else
    magick "$tmp/rounded-1024.png" -filter Lanczos -resize "${size}x${size}" \
      -colors 256 -strip "PNG8:$tmp/ico-${size}.png"
  fi
done
magick "$tmp/ico-16.png" "$tmp/ico-32.png" "$tmp/ico-48.png" \
  "$tmp/ico-64.png" "$tmp/ico-128.png" "$tmp/ico-256.png" \
  "$OUT/favicon.ico"

# Safari pinned-tab mask: best-effort raster silhouette inside an SVG.
# ImageMagick's SVG writer delegates to potrace; embed the PNG ourselves instead.
magick "$tmp/logo.png" -fill black -colorize 100% "$tmp/silhouette.png"
sil_w="$(magick identify -format '%w' "$tmp/silhouette.png")"
sil_h="$(magick identify -format '%h' "$tmp/silhouette.png")"
sil_b64="$(base64 < "$tmp/silhouette.png" | tr -d '\n')"
cat > "$OUT/safari-pinned-tab.svg" <<SVG
<svg xmlns="http://www.w3.org/2000/svg" width="$sil_w" height="$sil_h" viewBox="0 0 $sil_w $sil_h">
  <image width="$sil_w" height="$sil_h" href="data:image/png;base64,$sil_b64"/>
</svg>
SVG

cat > "$OUT/site.webmanifest" <<'JSON'
{
  "name": "Jay Fu Blog",
  "short_name": "Jay Fu",
  "description": "Algorithm | Edge Computing | Software Engineer",
  "start_url": "./",
  "scope": "./",
  "display": "standalone",
  "background_color": "#0B1220",
  "theme_color": "#0B1220",
  "icons": [
    {
      "src": "android-chrome-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "android-chrome-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any"
    }
  ]
}
JSON

echo "generated:"
magick identify "$OUT/favicon.ico" "$OUT"/favicon-*.png \
  "$OUT/apple-touch-icon.png" "$OUT"/android-chrome-*.png
