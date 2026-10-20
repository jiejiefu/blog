#!/usr/bin/env python3
"""Check generated PNGs in script-managed post bundles.

Each scripts/<slug>/ folder is assumed to manage
content/{zh-tw,en}/posts/<slug>/images/. Bundles without a matching
scripts/<slug>/ folder (for example, slide exports) are ignored.

Usage:
    python3 scripts/check_generated_images.py --check
    python3 scripts/check_generated_images.py --fix --dry-run
    python3 scripts/check_generated_images.py --fix
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
CONTENT = ROOT / "content"
LANGS = ("zh-tw", "en")


def managed_bundles():
    for script_dir in sorted(SCRIPTS.iterdir()):
        if not script_dir.is_dir() or script_dir.name == "__pycache__":
            continue
        if not any(script_dir.glob("*.py")):
            continue
        slug = script_dir.name
        bundles = [
            bundle
            for bundle in (CONTENT / lang / "posts" / slug for lang in LANGS)
            if bundle.is_dir()
        ]
        if bundles:
            yield slug, bundles


def find_pngs(bundles):
    for bundle in bundles:
        images = bundle / "images"
        if images.is_dir():
            yield from sorted(images.glob("*.png"))


def markdown_refs(bundles, filename):
    hits = []
    for bundle in bundles:
        for md in sorted(bundle.rglob("*.md")):
            for lineno, line in enumerate(
                md.read_text(encoding="utf-8").splitlines(), 1
            ):
                if filename in line:
                    hits.append(f"{md.relative_to(ROOT)}:{lineno}")
    return hits


def collect_pngs():
    found = []
    for _, bundles in managed_bundles():
        for png in find_pngs(bundles):
            found.append((bundles, png))
    return found


def main():
    parser = argparse.ArgumentParser(
        description="Check generated PNGs in script-managed post bundles."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--check",
        action="store_true",
        help="exit 1 if any generated PNG remains",
    )
    group.add_argument(
        "--fix",
        action="store_true",
        help="convert unreferenced PNGs to WebP and delete them",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="with --fix, print actions without changing files",
    )
    args = parser.parse_args()

    if args.dry_run and not args.fix:
        parser.error("--dry-run requires --fix")

    pngs = collect_pngs()
    if not pngs:
        print("OK: no generated PNGs in script-managed bundles.")
        return 0

    if args.check:
        print("Found generated PNG(s) in script-managed bundles:")
        for _, png in pngs:
            print(f"  {png.relative_to(ROOT)}")
        print()
        print(
            "Run `python3 scripts/check_generated_images.py --fix` "
            "or regenerate the charts."
        )
        return 1

    from image_utils import png_to_webp

    changed = 0
    refused = 0
    for bundles, png in pngs:
        refs = markdown_refs(bundles, png.name)
        if refs:
            refused += 1
            print(f"SKIP (referenced): {png.relative_to(ROOT)}")
            for ref in refs:
                print(f"  {ref}")
            continue

        webp = png.with_suffix(".webp")
        if args.dry_run:
            print(
                f"WOULD CONVERT: {png.relative_to(ROOT)} "
                f"-> {webp.relative_to(ROOT)}"
            )
            print(f"WOULD DELETE:  {png.relative_to(ROOT)}")
            changed += 1
            continue

        png_to_webp(png, webp)
        png.unlink()
        print(
            f"CONVERTED: {png.relative_to(ROOT)} -> {webp.relative_to(ROOT)}"
        )
        changed += 1

    if args.dry_run:
        print(f"\nDry run: {changed} would change, {refused} refused.")
    else:
        print(f"\nDone: {changed} converted, {refused} refused.")
    return 1 if refused else 0


if __name__ == "__main__":
    sys.exit(main())
