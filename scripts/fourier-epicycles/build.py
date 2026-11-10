#!/usr/bin/env python3
"""Build the fourier-epicycles notebook."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from notebook_build import build


def main():
    result = build(
        source=Path(__file__).with_name("notebook.ipynb"),
        bundle=ROOT / "content/zh-tw/notebooks/fourier-epicycles",
    )
    meta = result["meta"]
    print(f"notebook: {meta['filename']}")
    print(f"cells: {meta['cell_count']} ({meta['code_cell_count']} code)")
    print(f"duration: {meta['duration_ms']} ms")
    print(f"json: {result['json']}")
    print(f"images: {len(result['images'])}")
    print(f"executed: {result['executed']}")
    print(f"markdown: {result['markdown']}")


if __name__ == "__main__":
    main()
