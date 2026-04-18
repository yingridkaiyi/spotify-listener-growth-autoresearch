#!/usr/bin/env python3
"""Frozen experiment runner for the listener-growth project."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import csv
import pickle
import site
import sys

for candidate in [
    Path.home() / ".local" / "lib" / "python3.13" / "site-packages",
    Path.home() / "Library" / "Python" / "3.13" / "lib" / "python" / "site-packages",
    Path("/opt/miniconda3/lib/python3.13/site-packages"),
]:
    if candidate.exists() and str(candidate) not in sys.path:
        site.addsitedir(str(candidate))

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agent_loop.features import FEATURE_COLUMNS, TARGET_COLUMN
from src.agent_loop.model import build_estimator, model_name
from src.eval.baseline import evaluate_baselines
from src.eval.evaluator import evaluate_regression
from src.eval.split import time_based_split
from src.pipeline.build_features import load_feature_frame
from src.pipeline.prepare import save_dataset

EXPERIMENTS_DIR = ROOT / "experiments"
LOG_PATH = EXPERIMENTS_DIR / "experiment_log.tsv"
ARTIFACT_PATH = EXPERIMENTS_DIR / "best_model_artifact.pkl"
BOARD_PATH = ROOT / "evaluation_board.md"
MASTER_PATH = ROOT / "data" / "processed" / "master_growth_dataset.csv"


def _ensure_log_header() -> None:
    EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)
    if LOG_PATH.exists():
        return
    with LOG_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow([
            "timestamp",
            "model_name",
            "split",
            "rmse",
            "mae",
            "mape",
            "spearman",
            "rows",
        ])


def _append_log(model_label: str, split_name: str, metrics: dict, rows: int) -> None:
    _ensure_log_header()
    with LOG_PATH.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            model_label,
            split_name,
            f"{metrics['rmse']:.6f}",
            f"{metrics['mae']:.6f}",
            f"{metrics['mape']:.6f}" if metrics["mape"] == metrics["mape"] else "",
            f"{metrics['spearman']:.6f}" if metrics["spearman"] == metrics["spearman"] else "",
            rows,
        ])


def _load_best_rmse() -> float | None:
    if not ARTIFACT_PATH.exists():
        return None
    with ARTIFACT_PATH.open("rb") as handle:
        payload = pickle.load(handle)
    return payload.get("validation_metrics", {}).get("rmse")


def _write_board(best_rmse: float | None, current_metrics: dict, split_meta: dict, rows: int) -> None:
    lines = [
        "# Evaluation Board",
        "",
        f"- Canonical dataset: `{MASTER_PATH}`",
        f"- Rows in feature frame: `{rows}`",
        f"- Train cutoff: `{split_meta['train_end']}`",
        f"- Validation cutoff: `{split_meta['validation_end']}`",
        f"- Test cutoff: `{split_meta['test_end']}`",
        f"- Current agent model: `{model_name()}`",
        f"- Current validation RMSE: `{current_metrics['rmse']:.2f}`",
        f"- Current validation MAE: `{current_metrics['mae']:.2f}`",
        f"- Current validation MAPE: `{current_metrics['mape']:.6f}`" if current_metrics["mape"] == current_metrics["mape"] else "- Current validation MAPE: ``",
        f"- Current validation Spearman: `{current_metrics['spearman']:.6f}`" if current_metrics["spearman"] == current_metrics["spearman"] else "- Current validation Spearman: ``",
        f"- Best stored validation RMSE: `{best_rmse:.2f}`" if best_rmse is not None else "- Best stored validation RMSE: `none`",
        "",
        "## Frozen Files",
        "- `src/eval/*`",
        "- `src/pipeline/prepare.py`",
        "- `src/pipeline/build_features.py`",
        "- `src/run.py`",
        "",
        "## Mutable Files",
        "- `src/agent_loop/features.py`",
        "- `src/agent_loop/model.py`",
    ]
    BOARD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    save_dataset(MASTER_PATH)
    feature_frame = load_feature_frame()
    split_data = time_based_split(feature_frame)

    train = split_data["train"]
    validation = split_data["validation"]
    test = split_data["test"]

    estimator = build_estimator()
    estimator.fit(train[FEATURE_COLUMNS], train[TARGET_COLUMN])
    validation_pred = estimator.predict(validation[FEATURE_COLUMNS])
    validation_metrics = evaluate_regression(validation[TARGET_COLUMN], validation_pred)
    test_pred = estimator.predict(test[FEATURE_COLUMNS])
    test_metrics = evaluate_regression(test[TARGET_COLUMN], test_pred)

    baseline_metrics = evaluate_baselines(train, validation)
    for baseline in baseline_metrics:
        _append_log(baseline["model_name"], "validation", baseline, len(validation))

    _append_log(model_name(), "validation", validation_metrics, len(validation))
    _append_log(model_name(), "test", test_metrics, len(test))

    best_rmse = _load_best_rmse()
    if best_rmse is None or validation_metrics["rmse"] < best_rmse:
        with ARTIFACT_PATH.open("wb") as handle:
            pickle.dump(
                {
                    "model_name": model_name(),
                    "estimator": estimator,
                    "feature_columns": FEATURE_COLUMNS,
                    "validation_metrics": validation_metrics,
                    "test_metrics": test_metrics,
                },
                handle,
            )
        best_rmse = validation_metrics["rmse"]

    _write_board(best_rmse, validation_metrics, split_data["cutoffs"], len(feature_frame))
    print(
        {
            "master_dataset": str(MASTER_PATH),
            "rows": len(feature_frame),
            "validation_metrics": validation_metrics,
            "test_metrics": test_metrics,
            "log": str(LOG_PATH),
            "artifact": str(ARTIFACT_PATH),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
