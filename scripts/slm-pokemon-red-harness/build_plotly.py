#!/usr/bin/env python3
"""Build the interactive exploration chart spec from the episode log.

Writes ``data/exploration_plotly.json``. The JSON is meant to be pasted into
the ``{{< plotly >}}`` shortcode in the post; keeping the generator separate
makes the chart reproducible when the log changes.
"""

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

MAP_COLORS = {
    38: "#5b4bff",
    37: "#14b8a6",
    0: "#22c55e",
}
MAP_NAMES = {
    38: "Red's House 2F",
    37: "Red's House 1F",
    0: "Pallet Town",
}
INK = "#1a1a1f"
MUTED = "#6b6b76"
AMBER = "#f59e0b"
GREEN = "#22c55e"


def load_rows():
    with (DATA / "episodes_new.csv").open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def cumulative_and_segments(rows):
    seen = set()
    cumulative = []
    for row in rows:
        seen.add((int(row["map_id"]), int(row["x"]), int(row["y"])))
        cumulative.append(len(seen))

    segments = []
    start = 0
    for index in range(1, len(rows)):
        if rows[index]["map_id"] != rows[index - 1]["map_id"]:
            segments.append((start, index))
            start = index
    segments.append((start, len(rows) - 1))
    return cumulative, segments


def build_spec(rows, cumulative, segments):
    traces = []
    seen_maps = set()
    for start, end in segments:
        map_id = int(rows[start]["map_id"])
        map_name = MAP_NAMES[map_id]
        xs = [int(row["step"]) for row in rows[start : end + 1]]
        ys = cumulative[start : end + 1]
        customdata = [
            [
                int(row["step"]),
                MAP_NAMES[int(row["map_id"])],
                int(row["x"]),
                int(row["y"]),
                row["action"],
            ]
            for row in rows[start : end + 1]
        ]
        traces.append(
            {
                "type": "scatter",
                "mode": "lines",
                "name": map_name,
                "legendgroup": map_name,
                "showlegend": map_name not in seen_maps,
                "x": xs,
                "y": ys,
                "customdata": customdata,
                "line": {
                    "color": MAP_COLORS[map_id],
                    "width": 2.8,
                    "shape": "hv",
                },
                "hovertemplate": (
                    "Step %{customdata[0]}<br>%{customdata[1]}"
                    "<br>座標 (%{customdata[2]}, %{customdata[3]})"
                    "<br>動作：%{customdata[4]}"
                    "<br>累計 %{y} 格<extra></extra>"
                ),
            }
        )
        seen_maps.add(map_name)

    transitions = []
    for index in range(1, len(rows)):
        if rows[index]["map_id"] == rows[index - 1]["map_id"]:
            continue
        previous = MAP_NAMES[int(rows[index - 1]["map_id"])]
        current = MAP_NAMES[int(rows[index]["map_id"])]
        transitions.append(
            {
                "step": int(rows[index]["step"]),
                "y": cumulative[index],
                "label": f"{previous} → {current}",
            }
        )

    traces.append(
        {
            "type": "scatter",
            "mode": "markers",
            "name": "地圖切換",
            "showlegend": False,
            "x": [item["step"] for item in transitions],
            "y": [item["y"] for item in transitions],
            "text": [item["label"] for item in transitions],
            "marker": {
                "symbol": "diamond",
                "size": 9,
                "color": AMBER,
                "line": {"color": "white", "width": 1},
            },
            "hovertemplate": (
                "Step %{x}<br>%{text}<br>累計 %{y} 格<extra></extra>"
            ),
        }
    )

    first_pallet = next(
        index for index, row in enumerate(rows) if int(row["map_id"]) == 0
    )
    traces.append(
        {
            "type": "scatter",
            "mode": "markers",
            "name": "第一次抵達 Pallet Town",
            "showlegend": False,
            "x": [int(rows[first_pallet]["step"])],
            "y": [cumulative[first_pallet]],
            "marker": {
                "symbol": "star",
                "size": 17,
                "color": GREEN,
                "line": {"color": "white", "width": 1.2},
            },
            "hovertemplate": (
                "Step %{x}<br>第一次抵達 Pallet Town"
                "<br>累計 %{y} 格<extra></extra>"
            ),
        }
    )

    gap_index = max(
        range(1, len(rows)),
        key=lambda index: float(rows[index]["timestamp"])
        - float(rows[index - 1]["timestamp"]),
    )
    gap_seconds = float(rows[gap_index]["timestamp"]) - float(
        rows[gap_index - 1]["timestamp"]
    )
    gap_step = (int(rows[gap_index - 1]["step"]) + int(rows[gap_index]["step"])) / 2

    layout = {
        "margin": {"l": 84, "r": 24, "t": 76, "b": 64},
        "xaxis": {
            "title": {"text": "Episode（依執行順序）", "standoff": 10},
            "automargin": True,
            "range": [0, 600],
            "gridcolor": "rgba(128,128,128,0.15)",
            "zeroline": False,
            "showline": False,
        },
        "yaxis": {
            "title": {"text": "累計走過的格子", "standoff": 10},
            "automargin": True,
            "range": [0, 76],
            "gridcolor": "rgba(128,128,128,0.15)",
            "zeroline": False,
            "showline": False,
        },
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"family": "system-ui, sans-serif", "size": 13},
        "legend": {
            "orientation": "h",
            "x": 0,
            "y": 1.16,
            "xanchor": "left",
            "yanchor": "top",
            "bgcolor": "rgba(0,0,0,0)",
            "font": {"size": 11},
        },
        "hovermode": "x unified",
        "hoverlabel": {"font": {"size": 12}},
        "shapes": [
            {
                "type": "line",
                "x0": gap_step,
                "x1": gap_step,
                "y0": 0,
                "y1": 76,
                "line": {
                    "color": "rgba(107,107,118,0.35)",
                    "width": 1,
                    "dash": "dot",
                },
                "layer": "below",
            }
        ],
        "annotations": [
            {
                "x": gap_step,
                "y": 74.5,
                "text": "中斷 28 分鐘",
                "showarrow": False,
                "font": {"size": 9},
                "xanchor": "left",
                "align": "left",
            }
        ],
    }

    return {
        "data": traces,
        "layout": layout,
        "config": {"displayModeBar": False, "responsive": True},
    }


def main():
    rows = load_rows()
    cumulative, segments = cumulative_and_segments(rows)
    spec = build_spec(rows, cumulative, segments)
    out = DATA / "exploration_plotly.json"
    out.write_text(
        json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {out}")
    print(f"final cumulative={cumulative[-1]} segments={len(segments)} traces={len(spec['data'])}")


if __name__ == "__main__":
    main()
