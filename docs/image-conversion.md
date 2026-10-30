# 圖片轉檔指令

> 只在產圖、轉檔時讀。回到 [AGENTS.md](../AGENTS.md)。
> 浮水印指令與本機素材路徑見 `AGENTS.local.md`。

## sips（macOS 內建）

PNG 支援透明背景，最適合 SVG 轉換。

```sh
for f in *.svg; do sips -s format png "$f" --out "${f%.svg}.png"; done
```

JPEG 不支援透明背景，透明區域預設會變黑（要白底需另外處理）。

```sh
for f in *.svg; do sips -s format jpeg "$f" --out "${f%.svg}.jpg"; done
```

WebP 兼具壓縮率與透明度支援。

```sh
for f in *.svg; do sips -s format webp "$f" --out "${f%.svg}.webp"; done
```

SVG 是向量圖，預設轉出來的尺寸可能太小。固定 2000px 寬並保持比例：

```sh
for f in *.svg; do sips -s format png --resampleWidth 2000 "$f" --out "${f%.svg}.png"; done
```

## rsvg-convert

```sh
brew install librsvg
for f in *.svg; do rsvg-convert "$f" -o "${f%.svg}.png"; done
```

## Inkscape

```sh
brew install --cask inkscape

# SVG → PNG
for f in *.svg; do inkscape --export-type=png "$f"; done

# SVG → JPG（借 sips 轉檔）
for f in *.svg; do inkscape --export-type=png "$f" && sips -s format jpeg "${f%.svg}.png" --out "${f%.svg}.jpg" && rm "${f%.svg}.png"; done
```

## GIF（FFmpeg 雙通道調色盤）

```sh
ffmpeg -i intro.mp4 -vf "fps=30,scale=1080:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse" -loop 0 output.gif
```
