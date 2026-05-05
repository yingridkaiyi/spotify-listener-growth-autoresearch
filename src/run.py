#!/usr/bin/env python3
"""Frozen experiment runner for the listener-growth project."""

from __future__ import annotations

import argparse
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


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run listener-growth experiments in search or final-eval mode."
    )
    parser.add_argument(
        "--final-eval",
        action="store_true",
        help="Reveal and log test metrics after model selection.",
    )
    return parser.parse_args()


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
    try:
        with ARTIFACT_PATH.open("rb") as handle:
            payload = pickle.load(handle)
    except (AttributeError, EOFError, ModuleNotFoundError, pickle.UnpicklingError):
        return None
    return payload.get("validation_metrics", {}).get("rmse")


def _load_artifact_payload() -> dict | None:
    if not ARTIFACT_PATH.exists():
        return None
    try:
        with ARTIFACT_PATH.open("rb") as handle:
            return pickle.load(handle)
    except (AttributeError, EOFError, ModuleNotFoundError, pickle.UnpicklingError):
        return None


def _write_artifact_payload(payload: dict) -> None:
    with ARTIFACT_PATH.open("wb") as handle:
        pickle.dump(payload, handle)


def _strip_test_metrics_from_artifact() -> None:
    payload = _load_artifact_payload()
    if payload is None or "test_metrics" not in payload:
        return
    del payload["test_metrics"]
    _write_artifact_payload(payload)


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
    args = _parse_args()
    save_dataset(MASTER_PATH)
    feature_frame = load_feature_frame()
    split_data = time_based_split(feature_frame)

    train = split_data["train"]
    validation = split_data["validation"]

    estimator = build_estimator()
    estimator.fit(train[FEATURE_COLUMNS], train[TARGET_COLUMN])
    validation_pred = estimator.predict(validation[FEATURE_COLUMNS])
    validation_metrics = evaluate_regression(validation[TARGET_COLUMN], validation_pred)

    baseline_metrics = evaluate_baselines(train, validation)
    for baseline in baseline_metrics:
        _append_log(baseline["model_name"], "validation", baseline, len(validation))

    _append_log(model_name(), "validation", validation_metrics, len(validation))

    best_rmse = _load_best_rmse()
    is_best = best_rmse is None or validation_metrics["rmse"] < best_rmse
    if is_best:
        payload = {
            "model_name": model_name(),
            "estimator": estimator,
            "feature_columns": FEATURE_COLUMNS,
            "validation_metrics": validation_metrics,
        }
        _write_artifact_payload(payload)
        best_rmse = validation_metrics["rmse"]

    output = {
        "master_dataset": str(MASTER_PATH),
        "rows": len(feature_frame),
        "validation_metrics": validation_metrics,
        "log": str(LOG_PATH),
        "artifact": str(ARTIFACT_PATH),
        "mode": "final_eval" if args.final_eval else "search",
    }

    if args.final_eval:
        test = split_data["test"]
        test_pred = estimator.predict(test[FEATURE_COLUMNS])
        test_metrics = evaluate_regression(test[TARGET_COLUMN], test_pred)
        _append_log(model_name(), "test", test_metrics, len(test))
        output["test_metrics"] = test_metrics

        payload = _load_artifact_payload()
        if payload is not None and payload.get("model_name") == model_name():
            payload["test_metrics"] = test_metrics
            _write_artifact_payload(payload)
    else:
        _strip_test_metrics_from_artifact()

    _write_board(best_rmse, validation_metrics, split_data["cutoffs"], len(feature_frame))
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
