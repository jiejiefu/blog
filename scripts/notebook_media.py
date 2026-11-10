"""Helpers for notebook media builds.

Matplotlib shells out to ``ffmpeg`` when saving MP4s. Some Homebrew installs
end up with a broken ffmpeg link after dependency upgrades, so this module
finds the first working binary and puts it at the front of ``PATH``.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


def _works(candidate: Path) -> bool:
    try:
        subprocess.run(
            [str(candidate), "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return True


def ensure_ffmpeg() -> Path:
    """Return a working ffmpeg path and prepend its directory to PATH."""
    candidates = [
        os.environ.get("BLOG_FFMPEG"),
        shutil.which("ffmpeg"),
        str(Path.home() / "Library/REAL-Video-Enhancer/bin/ffmpeg"),
        "/opt/homebrew/bin/ffmpeg",
        "/usr/local/bin/ffmpeg",
    ]

    seen: set[Path] = set()
    for value in candidates:
        if not value:
            continue
        candidate = Path(value).expanduser()
        if candidate in seen or not candidate.is_file():
            continue
        seen.add(candidate)
        if _works(candidate):
            os.environ["PATH"] = (
                str(candidate.parent) + os.pathsep + os.environ.get("PATH", "")
            )
            return candidate

    raise RuntimeError(
        "No working ffmpeg found. Set BLOG_FFMPEG or install a functional ffmpeg."
    )
