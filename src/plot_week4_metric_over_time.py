#!/usr/bin/env python3
"""Regenerate the Week 4 validation-RMSE plot from the summary matrix."""

from __future__ import annotations

from pathlib import Path
import site
import sys

for candidate in [
    Path.home() / ".local" / "lib" / "python3.13" / "site-packages",
    Path.home() / "Library" / "Python" / "3.13" / "lib" / "python" / "site-packages",
    Path("/opt/miniconda3/lib/python3.13/site-packages"),
]:
    if candidate.exists() and str(candidate) not in sys.path:
        site.addsitedir(str(candidate))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "week4_experiment_result_matrix.md"
OUTPUT_PATH = ROOT / "week4_metric_over_time.png"

RETAINED_RUN = 26
HISTORICAL_BEST_RUN = 24
BEST_CONSERVATIVE_RUN = 30
ANNOTATED_RUNS = [1, 5, 10, 16, 24, 26, 30, 31]


def _parse_matrix_rows() -> list[dict[str, str]]:
    table_lines = [
        line.strip()
        for line in MATRIX_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip().startswith("|")
    ]
    header = [cell.strip() for cell in table_lines[0].strip("|").split("|")]
    rows: list[dict[str, str]] = []
    for line in table_lines[2:]:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != len(header):
            continue
        row = dict(zip(header, cells))
        try:
            run = int(row["Run"])
        except ValueError:
            continue
        if run > 31:
            continue
        rows.append(row)
    return rows


def main() -> int:
    rows = _parse_matrix_rows()
    runs = [int(row["Run"]) for row in rows]
    rmse = [float(row["Validation RMSE"].replace(",", "")) for row in rows]
    labels = [row["Experiment Name"].strip("`") for row in rows]

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(15, 8))
    ax.plot(runs, rmse, color="#2f5d50", linewidth=2.2, marker="o", markersize=5)
    ax.set_title("Week 4 Validation RMSE Across Formal Experiments", fontsize=16, pad=14)
    ax.set_xlabel("Formal Run Order", fontsize=12)
    ax.set_ylabel("Validation RMSE", fontsize=12)
    ax.ticklabel_format(style="plain", axis="y")

    for x, y in zip(runs, rmse):
        ax.scatter([x], [y], color="#2f5d50", s=28, zorder=3)

    highlights = [
        (RETAINED_RUN, "#1b9e77", "*", "Retained model under policy"),
        (HISTORICAL_BEST_RUN, "#d95f02", "D", "Historical best validation-only run"),
        (BEST_CONSERVATIVE_RUN, "#7570b3", "s", "Best conservative ensemble"),
    ]
    for run, color, marker, legend_label in highlights:
        index = runs.index(run)
        ax.scatter(
            [runs[index]],
            [rmse[index]],
            color=color,
            s=180,
            marker=marker,
            zorder=4,
            label=legend_label,
        )

    for run in ANNOTATED_RUNS:
        index = runs.index(run)
        ax.annotate(
            f"{run}: {labels[index]}",
            (runs[index], rmse[index]),
            textcoords="offset points",
            xytext=(6, -12 if run in {24, 30} else 8),
            fontsize=8,
            color="#222222",
        )

    retained_rmse = rmse[runs.index(RETAINED_RUN)]
    ax.axhline(retained_rmse, color="#1b9e77", linestyle="--", linewidth=1.2, alpha=0.85)
    ax.text(
        31.25,
        retained_rmse,
        " retained policy winner",
        color="#1b9e77",
        va="center",
        fontsize=9,
    )
    ax.legend(loc="upper right", frameon=True)
    ax.set_xlim(1, 31.8)
    fig.tight_layout()
    fig.savefig(OUTPUT_PATH, dpi=200)
    print(OUTPUT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
