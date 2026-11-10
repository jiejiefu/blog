#!/usr/bin/env python3
"""Execute a Jupyter notebook and emit static Hugo assets."""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import platform
import re
import shutil
import sys
import time
from pathlib import Path
from tempfile import TemporaryDirectory

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))

from image_utils import png_to_webp

ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
TABLE_RE = re.compile(r"<table\b", re.IGNORECASE)


def _text(value):
    if isinstance(value, list):
        return "".join(str(part) for part in value)
    return "" if value is None else str(value)


def _strip_ansi(value):
    return ANSI_RE.sub("", _text(value))


def _sanitize_table_html(value):
    text = _text(value)
    text = re.sub(r"(?is)<(script|style)\b.*?</\1>", "", text)
    text = re.sub(r"(?is)<!--.*?-->", "", text)
    text = re.sub(r"(?i)\son\w+\s*=\s*(\"[^\"]*\"|'[^']*'|[^\s>]+)", "", text)
    text = re.sub(r"(?i)\sstyle\s*=\s*(\"[^\"]*\"|'[^']*'|[^\s>]+)", "", text)
    text = re.sub(r"(?i)javascript:", "", text)
    if not TABLE_RE.search(text):
        return ""
    return text.strip()


def _image_output(output, cell_index, output_index, image_dir, cell_meta):
    data = output.get("data", {})
    if "image/png" in data:
        mime = "image/png"
    elif "image/jpeg" in data:
        mime = "image/jpeg"
    else:
        return None

    raw = base64.b64decode(_text(data[mime]))
    name = f"cell-{cell_index:02d}-out-{output_index:02d}.webp"
    dest = image_dir / name

    with TemporaryDirectory(prefix="nb-img-") as tmp:
        tmp_dir = Path(tmp)
        raw_path = tmp_dir / ("raw.png" if mime == "image/png" else "raw.jpg")
        raw_path.write_bytes(raw)
        flat_path = tmp_dir / "flat.png"

        with Image.open(raw_path) as img:
            img.load()
            has_alpha = img.mode in ("RGBA", "LA") or (
                img.mode == "P" and "transparency" in img.info
            )
            if has_alpha:
                rgba = img.convert("RGBA")
                background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
                background.alpha_composite(rgba)
                flat = background.convert("RGB")
            else:
                flat = img.convert("RGB")
            flat.save(flat_path, "PNG")
            width, height = flat.size

        png_to_webp(flat_path, dest)

    return {
        "type": "image",
        "src": f"images/{name}",
        "alt": cell_meta.get("alt", f"Cell {cell_index} output {output_index}"),
        "caption": cell_meta.get("caption", ""),
        "width": width,
        "height": height,
    }


def _video_output(cell, cell_index, image_dir, video_dir, source_dir):
    cell_meta = cell.get("metadata", {})
    video_meta = cell_meta.get("video")
    if not video_meta:
        return None
    if isinstance(video_meta, str):
        video_meta = {"src": video_meta}

    src_name = Path(str(video_meta["src"])).name
    src_path = source_dir / src_name
    if not src_path.is_file():
        raise FileNotFoundError(
            f"notebook video not found: {src_path} (cell {cell_index})"
        )

    video_dir.mkdir(parents=True, exist_ok=True)
    dest = video_dir / src_name
    shutil.copy2(src_path, dest)

    poster_src = ""
    poster = video_meta.get("poster")
    if poster:
        poster_path = source_dir / Path(str(poster)).name
        if not poster_path.is_file():
            raise FileNotFoundError(
                f"notebook video poster not found: {poster_path} (cell {cell_index})"
            )
        poster_name = f"{Path(poster).stem}.webp"
        poster_dest = image_dir / poster_name
        png_to_webp(poster_path, poster_dest)
        poster_src = f"images/{poster_name}"

    return {
        "type": "video",
        "src": f"videos/{src_name}",
        "poster": poster_src,
        "alt": video_meta.get("alt", f"Cell {cell_index} video"),
        "caption": video_meta.get("caption", ""),
        "width": int(video_meta.get("width", 0) or 0),
        "height": int(video_meta.get("height", 0) or 0),
        "controls": bool(video_meta.get("controls", True)),
        "autoplay": bool(video_meta.get("autoplay", False)),
        "muted": bool(video_meta.get("muted", True)),
        "loop": bool(video_meta.get("loop", True)),
        "playsinline": bool(video_meta.get("playsinline", True)),
    }


def _convert_outputs(cell, cell_index, image_dir, video_dir, source_dir):
    cell_meta = cell.get("metadata", {})
    outputs = []

    video = _video_output(cell, cell_index, image_dir, video_dir, source_dir)
    if video:
        outputs.append(video)

    for output_index, output in enumerate(cell.get("outputs", []), 1):
        kind = output.get("output_type")

        if kind == "stream":
            outputs.append(
                {
                    "type": "stream",
                    "name": output.get("name", "stdout"),
                    "text": _strip_ansi(output.get("text", "")).rstrip("\n"),
                }
            )
            continue

        if kind in ("execute_result", "display_data"):
            image = _image_output(
                output, cell_index, output_index, image_dir, cell_meta
            )
            if image:
                image["execution_count"] = cell.get("execution_count")
                outputs.append(image)
                continue

            data = output.get("data", {})
            table = _sanitize_table_html(data.get("text/html", ""))
            if table:
                outputs.append(
                    {
                        "type": "html",
                        "html": table,
                        "execution_count": cell.get("execution_count"),
                    }
                )
                continue

            text = _strip_ansi(data.get("text/plain", "")).rstrip()
            if text:
                outputs.append(
                    {
                        "type": "result",
                        "text": text,
                        "execution_count": cell.get("execution_count"),
                    }
                )
            continue

        if kind == "error":
            outputs.append(
                {
                    "type": "error",
                    "ename": output.get("ename", "Error"),
                    "evalue": output.get("evalue", ""),
                    "traceback": _strip_ansi(
                        "\n".join(output.get("traceback", []))
                    ),
                }
            )

    return outputs


def _build_cells(nb, image_dir, video_dir, source_dir):
    cells = []

    for cell_index, cell in enumerate(nb.cells, 1):
        metadata = cell.get("metadata", {})
        tags = [str(tag) for tag in metadata.get("tags", [])]
        if "remove-cell" in tags:
            continue

        if cell.cell_type == "markdown":
            cells.append(
                {
                    "type": "markdown",
                    "source": _text(cell.source).strip(),
                    "tags": tags,
                }
            )
            continue

        if cell.cell_type == "code":
            cells.append(
                {
                    "type": "code",
                    "source": _text(cell.source).rstrip(),
                    "execution_count": cell.get("execution_count"),
                    "tags": tags,
                    "outputs": _convert_outputs(
                        cell, cell_index, image_dir, video_dir, source_dir
                    ),
                }
            )

    return cells


def _write_markdown(cells, path):
    lines = []

    for cell in cells:
        if cell["type"] == "markdown":
            lines.extend([cell["source"], ""])
            continue

        if "hide-input" not in cell["tags"]:
            lines.extend(["```python", cell["source"], "```", ""])

        if "hide-output" in cell["tags"]:
            continue

        for output in cell["outputs"]:
            if output["type"] in ("stream", "result"):
                lines.extend(["```text", output["text"], "```", ""])
            elif output["type"] == "html":
                lines.extend(["```html", output["html"], "```", ""])
            elif output["type"] == "image":
                lines.append(f"![{output['alt']}]({output['src']})")
                if output["caption"]:
                    lines.extend([f"*{output['caption']}*", ""])
            elif output["type"] == "video":
                lines.append(f"[影片：{output['alt']}]({output['src']})")
                if output["caption"]:
                    lines.extend([f"*{output['caption']}*", ""])
            elif output["type"] == "error":
                trace = output["traceback"] or (
                    f"{output['ename']}: {output['evalue']}"
                )
                lines.extend(["```text", trace, "```", ""])

    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def build(
    source,
    bundle,
    json_name="notebook.json",
    kernel="python3",
    timeout=120,
    allow_errors=False,
    executed=None,
    markdown=None,
):
    source = Path(source).resolve()
    bundle = Path(bundle).resolve()
    bundle.mkdir(parents=True, exist_ok=True)

    image_dir = bundle / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    for stale in image_dir.glob("cell-*-out-*.webp"):
        stale.unlink()

    video_dir = bundle / "videos"
    video_dir.mkdir(parents=True, exist_ok=True)
    for stale in list(video_dir.glob("*.mp4")) + list(video_dir.glob("*.webm")):
        stale.unlink()

    nb = nbformat.read(source, as_version=4)
    nbformat.validate(nb)

    for cell in nb.cells:
        if cell.cell_type == "code":
            cell.outputs = []
            cell.execution_count = None

    client = NotebookClient(
        nb,
        timeout=timeout,
        kernel_name=kernel,
        resources={"metadata": {"path": str(source.parent)}},
        allow_errors=allow_errors,
    )

    started = time.perf_counter()
    try:
        client.execute()
    except CellExecutionError:
        if not allow_errors:
            raise
    duration_ms = int((time.perf_counter() - started) * 1000)

    cells = _build_cells(nb, image_dir, video_dir, source.parent)
    kernelspec = nb.metadata.get("kernelspec", {})
    meta = {
        "title": nb.metadata.get("title", source.stem),
        "filename": source.name,
        "kernel": kernelspec.get("display_name", kernel),
        "language": kernelspec.get("language", "python"),
        "python_version": platform.python_version(),
        "executed_at": dt.datetime.now().astimezone().strftime(
            "%Y-%m-%d %H:%M %Z"
        ),
        "duration_ms": duration_ms,
        "cell_count": len(nb.cells),
        "code_cell_count": sum(
            1 for cell in nb.cells if cell.cell_type == "code"
        ),
        "readonly": True,
    }

    json_path = bundle / json_name
    json_path.write_text(
        json.dumps(
            {"schema": 1, "meta": meta, "cells": cells},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    executed_path = (
        Path(executed).resolve()
        if executed
        else source.with_name("executed.ipynb")
    )
    nbformat.write(nb, executed_path)

    markdown_path = (
        Path(markdown).resolve()
        if markdown
        else source.with_name("notebook.md")
    )
    _write_markdown(cells, markdown_path)

    return {
        "json": json_path,
        "images": sorted(image_dir.glob("cell-*-out-*.webp")),
        "executed": executed_path,
        "markdown": markdown_path,
        "meta": meta,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Execute a notebook and write static Hugo assets."
    )
    parser.add_argument("source", help="source .ipynb")
    parser.add_argument(
        "--bundle",
        required=True,
        help="Hugo page bundle directory",
    )
    parser.add_argument("--json-name", default="notebook.json")
    parser.add_argument("--kernel", default="python3")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--allow-errors", action="store_true")
    parser.add_argument("--executed", help="output executed.ipynb path")
    parser.add_argument("--markdown", help="output review markdown path")
    args = parser.parse_args()

    result = build(
        source=args.source,
        bundle=args.bundle,
        json_name=args.json_name,
        kernel=args.kernel,
        timeout=args.timeout,
        allow_errors=args.allow_errors,
        executed=args.executed,
        markdown=args.markdown,
    )

    meta = result["meta"]
    print(f"notebook: {meta['filename']}")
    print(f"cells: {meta['cell_count']} ({meta['code_cell_count']} code)")
    print(f"duration: {meta['duration_ms']} ms")
    print(f"json: {result['json']}")
    print(f"images: {len(result['images'])}")
    for image in result["images"]:
        print(f"  {image}")
    print(f"executed: {result['executed']}")
    print(f"markdown: {result['markdown']}")


if __name__ == "__main__":
    main()
