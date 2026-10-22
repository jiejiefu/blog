#!/usr/bin/env python3
"""Fail when a tracked content or scripts directory uses underscores.

Page bundle and script directory names become public URLs or are referenced
as slugs, so they must use hyphens. Only files tracked by git are inspected:
untracked work-in-progress bundles will be checked once they are committed.

Usage:
    python3 scripts/check_slug_style.py
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECK_ROOTS = ("content", "scripts")
SKIP_DIRS = {"__pycache__"}


def tracked_paths():
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", *CHECK_ROOTS],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return sorted({p for p in result.stdout.split("\0") if p})


def bad_directories(paths):
    bad = {}
    for raw in paths:
        path = Path(raw)
        parts = path.parts
        if not parts or parts[0] not in CHECK_ROOTS:
            continue
        for depth in range(2, len(parts)):
            directory = "/".join(parts[:depth])
            name = parts[depth - 1]
            if name in SKIP_DIRS:
                continue
            if "_" in name:
                bad.setdefault(directory, name)
    return bad


def main():
    try:
        paths = tracked_paths()
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(f"error: cannot list tracked files: {exc}", file=sys.stderr)
        return 2

    if not paths:
        print("slug style: no tracked files under content/ or scripts/")
        return 0

    bad = bad_directories(paths)
    if not bad:
        print("slug style: OK (no tracked directory contains '_')")
        return 0

    print("slug style: directory names must use hyphens, not underscores:", file=sys.stderr)
    for directory in sorted(bad):
        suggestion = directory.replace("_", "-")
        print(f"  {directory}  ->  {suggestion}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
