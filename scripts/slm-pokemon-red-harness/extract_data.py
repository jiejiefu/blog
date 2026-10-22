#!/usr/bin/env python3
"""Extract the local Pokémon harness logs into a small, reviewable snapshot.

The live project lives outside this repository. The chart scripts must not
depend on that path, so this script writes a derived CSV/JSON snapshot into
``scripts/slm-pokemon-red-harness/data/``. No ROM, screenshots, or game assets
are copied.

Usage:
    python3 scripts/slm-pokemon-red-harness/extract_data.py

Override the source directory with POKEMON_HARNESS_DIR if needed.
"""

import csv
import json
import os
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = Path(__file__).resolve().parent / "data"

SOURCE = Path(
    os.environ.get(
        "POKEMON_HARNESS_DIR",
        Path.home() / "Documents/Antigravity/gameboy_pokemon",
    )
)
NEW_DB = SOURCE / "data/pokemon_memory.db"
OLD_DB = SOURCE / "agent/data/pokemon_memory.db"
MEMORY_JSON = SOURCE / "data/cognitive_memory.json"

MAP_NAMES = {
    0: "Pallet Town",
    37: "Red's House 1F",
    38: "Red's House 2F",
}

LOCATION_RE = re.compile(r"^(?P<name>.+?) \(X:(?P<x>\d+), Y:(?P<y>\d+)\)(?: facing (?P<facing>\w+))?")


def parse_location(state_json):
    """Return (map_name, x, y, facing) from a state JSON blob."""
    try:
        state = json.loads(state_json)
    except json.JSONDecodeError:
        return "", "", "", ""
    match = LOCATION_RE.match(state.get("location", ""))
    if not match:
        return "", "", "", ""
    return (
        match.group("name"),
        int(match.group("x")),
        int(match.group("y")),
        match.group("facing") or "",
    )


def map_id_for_name(name):
    for map_id, map_name in MAP_NAMES.items():
        if map_name == name:
            return map_id
    return ""


def write_old(path):
    if not OLD_DB.is_file():
        raise FileNotFoundError(f"old episode DB not found: {OLD_DB}")

    conn = sqlite3.connect(OLD_DB)
    rows = conn.execute(
        "SELECT timestamp, action_json, state_before, outcome_json "
        "FROM episodes ORDER BY id"
    ).fetchall()
    conn.close()

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["step", "timestamp", "action", "stuck", "screen_type"])
        for step, (timestamp, action_json, state_before, outcome_json) in enumerate(rows, 1):
            action = json.loads(action_json).get("button", "")
            outcome = json.loads(outcome_json)
            screen = json.loads(state_before).get("screen_type", "")
            writer.writerow(
                [step, f"{timestamp:.6f}", action, int(bool(outcome.get("stuck_detected"))), screen]
            )
    return len(rows)


def write_new(path):
    if not NEW_DB.is_file():
        raise FileNotFoundError(f"new episode DB not found: {NEW_DB}")

    conn = sqlite3.connect(NEW_DB)
    rows = conn.execute(
        "SELECT timestamp, state_before, action_text, latency, stuck_detected "
        "FROM episodes ORDER BY id"
    ).fetchall()
    conn.close()

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "step",
                "timestamp",
                "action",
                "latency",
                "stuck",
                "screen_type",
                "map_id",
                "map_name",
                "x",
                "y",
                "facing",
            ]
        )
        for step, (timestamp, state_before, action, latency, stuck) in enumerate(rows, 1):
            state = json.loads(state_before)
            name, x, y, facing = parse_location(state_before)
            writer.writerow(
                [
                    step,
                    f"{timestamp:.6f}",
                    action,
                    f"{latency:.6f}",
                    int(stuck),
                    state.get("screen_type", ""),
                    map_id_for_name(name),
                    name,
                    x,
                    y,
                    facing,
                ]
            )
    return len(rows)


def write_memory(path):
    if not MEMORY_JSON.is_file():
        raise FileNotFoundError(f"memory snapshot not found: {MEMORY_JSON}")

    memory = json.loads(MEMORY_JSON.read_text(encoding="utf-8"))
    memory["map_names"] = {str(k): v for k, v in MAP_NAMES.items()}
    path.write_text(
        json.dumps(memory, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return memory


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    old_count = write_old(OUT_DIR / "episodes_old.csv")
    new_count = write_new(OUT_DIR / "episodes_new.csv")
    memory = write_memory(OUT_DIR / "memory_snapshot.json")

    print(f"wrote {old_count} old episodes")
    print(f"wrote {new_count} new episodes")
    print(
        "memory: "
        f"{len(memory.get('seen_coords', []))} seen, "
        f"{len(memory.get('blocked_moves', []))} blocked, "
        f"{sum(len(v) for v in memory.get('discovered_warps', {}).values())} warps"
    )


if __name__ == "__main__":
    main()
