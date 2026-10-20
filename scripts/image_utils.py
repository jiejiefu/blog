#!/usr/bin/env python3
"""Shared image helpers for article chart scripts.

Charts are written as WebP directly into the post's page bundle. The PNG
intermediate lives in a temporary directory, so Hugo never publishes it.
"""

from pathlib import Path
import shutil
import subprocess
import tempfile

from PIL import Image

QUALITY = 82
METHOD = 6


def _cwebp():
    exe = shutil.which("cwebp")
    if not exe:
        raise RuntimeError(
            "cwebp not found. Install it with: brew install webp"
        )
    return exe


def _verify_webp(path):
    with Image.open(path) as img:
        img.verify()


def png_to_webp(src, dest, quality=QUALITY):
    """Convert a PNG to WebP, preserving transparency and stripping metadata."""
    src = Path(src)
    dest = Path(dest)
    if not src.is_file():
        raise FileNotFoundError(src)
    dest.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="webp-") as tmp:
        tmp_webp = Path(tmp) / "out.webp"
        subprocess.run(
            [
                _cwebp(),
                "-quiet",
                "-q",
                str(quality),
                "-m",
                str(METHOD),
                "-metadata",
                "none",
                str(src),
                "-o",
                str(tmp_webp),
            ],
            check=True,
        )
        if not tmp_webp.is_file() or tmp_webp.stat().st_size == 0:
            raise RuntimeError(f"cwebp produced no output for {src}")
        _verify_webp(tmp_webp)
        shutil.move(str(tmp_webp), str(dest))
    return dest


def save_figure_webp(fig, out_path, dpi=None, facecolor="white", quality=QUALITY):
    """Save an opaque matplotlib figure as WebP inside a page bundle."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="chart-") as tmp:
        png_path = Path(tmp) / "chart.png"
        rgb_path = Path(tmp) / "chart-rgb.png"
        webp_path = Path(tmp) / "chart.webp"

        fig.savefig(png_path, dpi=dpi, facecolor=facecolor)
        with Image.open(png_path) as img:
            img.convert("RGB").save(rgb_path, "PNG")

        subprocess.run(
            [
                _cwebp(),
                "-quiet",
                "-q",
                str(quality),
                "-m",
                str(METHOD),
                "-metadata",
                "none",
                "-noalpha",
                str(rgb_path),
                "-o",
                str(webp_path),
            ],
            check=True,
        )
        if not webp_path.is_file() or webp_path.stat().st_size == 0:
            raise RuntimeError(f"cwebp produced no output for {out_path}")
        _verify_webp(webp_path)
        shutil.move(str(webp_path), str(out_path))
    return out_path
