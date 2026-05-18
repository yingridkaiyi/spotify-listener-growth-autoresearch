#!/usr/bin/env python3
"""Detailed companion logger for Week 4 experiments."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import json
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

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agent_loop.features import FEATURE_SET_REGISTRY, get_active_feature_spec, get_feature_spec
from src.agent_loop.model import (
    get_active_model_spec,
    get_model_spec,
    model_name,
)

EXPERIMENTS_DIR = ROOT / "experiments"
LOG_PATH = EXPERIMENTS_DIR / "experiment_log.tsv"
DETAIL_LOG_PATH = EXPERIMENTS_DIR / "experiment_detail_log.tsv"
MATRIX_PATH = ROOT / "deliverables" / "week4_experiment_result_matrix.md"

DETAIL_LOG_HEADER = [
    "logged_at",
    "validation_timestamp",
    "model_name",
    "feature_set_name",
    "feature_engineering_summary",
    "engineered_features_json",
    "model_variant_name",
    "model_summary",
    "estimator_family",
    "estimator_params_json",
    "preprocessor_spec_json",
    "blend_spec_json",
    "hypothesis",
    "changed_components",
    "why_this_should_help",
    "decision",
    "decision_reason",
    "validation_rmse",
    "validation_mae",
    "validation_mape",
    "validation_spearman",
    "test_rmse",
    "test_mae",
    "test_mape",
    "test_spearman",
    "notes",
]

ALLOWED_CHANGED_COMPONENTS = {
    "model",
    "features",
    "preprocessing",
    "target_transform",
    "ensemble_weight",
}

WEEK4_MODEL_NAME_BY_RUN = {
    1: "search_huber_week4_control_week3_features_v1",
    2: "search_huber_week4_release_timing_family_v1",
    3: "search_huber_week4_concert_timing_family_v1",
    4: "search_huber_week4_negative_regime_family_v1",
    5: "search_huber_week4_release_plus_regime_combo_v1",
    6: "search_huber_week4_momentum_gap_family_v1",
    7: "search_huber_week4_spike_flag_family_v1",
    8: "search_huber_week4_release_plus_momentum_family_v1",
    9: "search_huber_week4_breakout_full_combo_v1",
    10: "search_week4_release_plus_regime_combo_huber_eps_1_25_v1",
    11: "search_week4_release_plus_regime_combo_huber_eps_1_30_v1",
    12: "search_week4_release_plus_regime_combo_huber_eps_1_35_v1",
    13: "search_week4_release_plus_momentum_family_huber_eps_1_30_v1",
    14: "search_week4_release_plus_regime_combo_huber_eps_1_15_v1",
    15: "search_week4_release_plus_regime_combo_huber_eps_1_20_v1",
    16: "search_week4_ratio_family_huber_eps_1_25_v1",
    17: "search_week4_release_plus_regime_combo_huber_eps_1_22_v1",
    18: "search_week4_ratio_family_huber_eps_1_22_v1",
    19: "search_week4_ratio_family_huber_eps_1_20_v1",
    20: "search_week4_ratio_family_huber_eps_1_18_v1",
    21: "search_week4_ratio_family_blend_huber125_extra400l4_w62_v1",
    22: "search_week4_ratio_family_blend_huber125_extra400l4_w65_v1",
    23: "search_week4_ratio_family_blend_huber125_extra400_w65_v1",
    24: "search_week4_ratio_family_blend_huber125_extra400l4_w58_v1",
    25: "search_week4_ratio_family_blend_huber125_extra400l4_w60_v1",
}

WEEK4_CHANGED_COMPONENTS_BY_RUN = {
    1: "",
    2: "features",
    3: "features",
    4: "features",
    5: "features",
    6: "features",
    7: "features",
    8: "features",
    9: "features",
    10: "model",
    11: "model",
    12: "model",
    13: "model,features",
    14: "model",
    15: "model",
    16: "features",
    17: "model",
    18: "model",
    19: "model",
    20: "model",
    21: "model,preprocessing,ensemble_weight",
    22: "model,preprocessing,ensemble_weight",
    23: "model,preprocessing,ensemble_weight",
    24: "model,preprocessing,ensemble_weight",
    25: "model,preprocessing,ensemble_weight",
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Write detailed experiment metadata without modifying the frozen runner."
    )
    parser.add_argument("--hypothesis")
    parser.add_argument("--changed-components")
    parser.add_argument("--why")
    parser.add_argument("--decision")
    parser.add_argument("--decision-reason")
    parser.add_argument("--notes", default="")
    parser.add_argument("--sync-final-eval", action="store_true")
    parser.add_argument("--backfill-week4", action="store_true")
    return parser.parse_args()


def _read_tsv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader)


def _ensure_detail_log_header() -> None:
    EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)
    if DETAIL_LOG_PATH.exists():
        return
    with DETAIL_LOG_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=DETAIL_LOG_HEADER, delimiter="\t")
        writer.writeheader()


def _write_detail_rows(rows: list[dict]) -> None:
    _ensure_detail_log_header()
    with DETAIL_LOG_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=DETAIL_LOG_HEADER, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def _json_compact(value) -> str:
    return json.dumps(value, separators=(",", ":"), sort_keys=True)


def _normalize_changed_components(value: str) -> str:
    if not value.strip():
        return ""
    components = [component.strip() for component in value.split(",") if component.strip()]
    invalid = [component for component in components if component not in ALLOWED_CHANGED_COMPONENTS]
    if invalid:
        allowed = ", ".join(sorted(ALLOWED_CHANGED_COMPONENTS))
        raise ValueError(f"Invalid changed component(s): {', '.join(invalid)}. Expected subset of: {allowed}.")
    return ",".join(components)


def _is_week4_agent_model(model_label: str) -> bool:
    return model_label.startswith("search_huber_week4_") or model_label.startswith("search_week4_")


def _latest_matching_row(rows: list[dict], *, model_label: str, split_name: str) -> dict | None:
    for row in reversed(rows):
        if row["model_name"] == model_label and row["split"] == split_name:
            return row
    return None


def _parse_agent_model_name(model_label: str) -> tuple[str, str]:
    feature_sets = sorted(FEATURE_SET_REGISTRY, key=len, reverse=True)
    if model_label.startswith("search_huber_week4_") and model_label.endswith("_v1"):
        feature_set_name = model_label.removeprefix("search_huber_week4_").removesuffix("_v1")
        if feature_set_name not in FEATURE_SET_REGISTRY:
            raise ValueError(f"Unknown feature set parsed from model name: {model_label}")
        return feature_set_name, "huber_default"

    if not model_label.startswith("search_week4_") or not model_label.endswith("_v1"):
        raise ValueError(f"Unsupported Week 4 model name: {model_label}")

    body = model_label.removeprefix("search_week4_").removesuffix("_v1")
    for feature_set_name in feature_sets:
        prefix = f"{feature_set_name}_"
        if body.startswith(prefix):
            return feature_set_name, body.removeprefix(prefix)
    raise ValueError(f"Could not parse feature set and model variant from: {model_label}")


def _build_detail_row(
    *,
    validation_row: dict,
    model_label: str,
    hypothesis: str,
    changed_components: str,
    why_this_should_help: str,
    decision: str,
    decision_reason: str,
    notes: str,
    test_row: dict | None = None,
) -> dict:
    feature_set_name, model_variant_name = _parse_agent_model_name(model_label)
    feature_spec = get_feature_spec(feature_set_name)
    model_spec = get_model_spec(
        model_variant_name,
        feature_columns=feature_spec["feature_columns"],
    )
    return {
        "logged_at": datetime.now().isoformat(timespec="seconds"),
        "validation_timestamp": validation_row["timestamp"],
        "model_name": model_label,
        "feature_set_name": feature_spec["feature_set_name"],
        "feature_engineering_summary": feature_spec["summary"],
        "engineered_features_json": _json_compact(feature_spec["engineered_features"]),
        "model_variant_name": model_spec["model_variant_name"],
        "model_summary": model_spec["summary"],
        "estimator_family": model_spec["estimator_family"],
        "estimator_params_json": _json_compact(model_spec["estimator_params"]),
        "preprocessor_spec_json": _json_compact(model_spec["preprocessor_spec"]),
        "blend_spec_json": _json_compact(model_spec["blend_spec"]),
        "hypothesis": hypothesis,
        "changed_components": changed_components,
        "why_this_should_help": why_this_should_help,
        "decision": decision,
        "decision_reason": decision_reason,
        "validation_rmse": validation_row["rmse"],
        "validation_mae": validation_row["mae"],
        "validation_mape": validation_row["mape"],
        "validation_spearman": validation_row["spearman"],
        "test_rmse": "" if test_row is None else test_row["rmse"],
        "test_mae": "" if test_row is None else test_row["mae"],
        "test_mape": "" if test_row is None else test_row["mape"],
        "test_spearman": "" if test_row is None else test_row["spearman"],
        "notes": notes,
    }


def _detail_row_key(row: dict) -> tuple[str, str]:
    return row["validation_timestamp"], row["model_name"]


def _parse_markdown_table(path: Path) -> list[dict]:
    table_lines = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip().startswith("|")
    ]
    header = [cell.strip() for cell in table_lines[0].strip("|").split("|")]
    rows = []
    for line in table_lines[2:]:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != len(header):
            continue
        rows.append(dict(zip(header, cells)))
    return rows


def _build_week4_matrix_metadata() -> dict[int, dict]:
    rows = _parse_markdown_table(MATRIX_PATH)
    metadata = {}
    for row in rows:
        run_number = int(row["Run"])
        metadata[run_number] = {
            "experiment_name": row["Experiment Name"].strip("`"),
            "hypothesis": row["Hypothesis"],
            "decision": row["Keep/Discard Decision"],
            "decision_reason": row["Notes"],
            "notes": row["Variable Changed"],
        }
    return metadata


def _append_detail_row_if_missing(row: dict) -> tuple[bool, list[dict]]:
    existing_rows = _read_tsv(DETAIL_LOG_PATH)
    existing_keys = {_detail_row_key(existing_row) for existing_row in existing_rows}
    if _detail_row_key(row) in existing_keys:
        return False, existing_rows
    existing_rows.append(row)
    _write_detail_rows(existing_rows)
    return True, existing_rows


def _sync_final_eval() -> int:
    log_rows = _read_tsv(LOG_PATH)
    detail_rows = _read_tsv(DETAIL_LOG_PATH)
    active_model_name = model_name()
    test_row = _latest_matching_row(log_rows, model_label=active_model_name, split_name="test")
    if test_row is None:
        raise ValueError(f"No test row found for active model '{active_model_name}'.")

    matching_indexes = [
        index for index, row in enumerate(detail_rows) if row["model_name"] == active_model_name
    ]
    if not matching_indexes:
        raise ValueError(f"No detail-log row found for active model '{active_model_name}'.")

    target_index = matching_indexes[-1]
    detail_rows[target_index]["test_rmse"] = test_row["rmse"]
    detail_rows[target_index]["test_mae"] = test_row["mae"]
    detail_rows[target_index]["test_mape"] = test_row["mape"]
    detail_rows[target_index]["test_spearman"] = test_row["spearman"]
    _write_detail_rows(detail_rows)
    print({
        "mode": "sync_final_eval",
        "model_name": active_model_name,
        "updated_validation_timestamp": detail_rows[target_index]["validation_timestamp"],
        "detail_log": str(DETAIL_LOG_PATH),
    })
    return 0


def _backfill_week4() -> int:
    log_rows = _read_tsv(LOG_PATH)
    existing_rows = _read_tsv(DETAIL_LOG_PATH)
    existing_keys = {_detail_row_key(existing_row) for existing_row in existing_rows}
    week4_validation_rows = [
        row for row in log_rows if row["split"] == "validation" and _is_week4_agent_model(row["model_name"])
    ]
    rows_by_model: dict[str, list[dict]] = {}
    for row in week4_validation_rows:
        rows_by_model.setdefault(row["model_name"], []).append(row)

    matrix_metadata = _build_week4_matrix_metadata()
    appended = 0

    for run_number in range(1, 26):
        model_label = WEEK4_MODEL_NAME_BY_RUN[run_number]
        if model_label not in rows_by_model or not rows_by_model[model_label]:
            raise ValueError(f"Missing validation row for formal Week 4 run {run_number}: {model_label}")
        validation_row = rows_by_model[model_label].pop(0)
        test_row = _latest_matching_row(log_rows, model_label=model_label, split_name="test")
        metadata = matrix_metadata[run_number]
        detail_row = _build_detail_row(
            validation_row=validation_row,
            model_label=model_label,
            hypothesis=metadata["hypothesis"],
            changed_components=WEEK4_CHANGED_COMPONENTS_BY_RUN[run_number],
            why_this_should_help=metadata["hypothesis"],
            decision=metadata["decision"],
            decision_reason=metadata["decision_reason"],
            notes=f"Formal Week 4 run. Variable changed: {metadata['notes']}",
            test_row=test_row,
        )
        if _detail_row_key(detail_row) not in existing_keys:
            existing_rows.append(detail_row)
            existing_keys.add(_detail_row_key(detail_row))
            appended += 1

    for model_label, remaining_rows in rows_by_model.items():
        if not remaining_rows:
            continue
        source_rows = [row for row in existing_rows if row["model_name"] == model_label]
        if not source_rows:
            raise ValueError(f"Cannot backfill repeated validation row without source metadata: {model_label}")
        source_row = source_rows[0]
        test_row = _latest_matching_row(log_rows, model_label=model_label, split_name="test")
        for validation_row in remaining_rows:
            detail_row = dict(source_row)
            detail_row["logged_at"] = datetime.now().isoformat(timespec="seconds")
            detail_row["validation_timestamp"] = validation_row["timestamp"]
            detail_row["validation_rmse"] = validation_row["rmse"]
            detail_row["validation_mae"] = validation_row["mae"]
            detail_row["validation_mape"] = validation_row["mape"]
            detail_row["validation_spearman"] = validation_row["spearman"]
            detail_row["test_rmse"] = "" if test_row is None else test_row["rmse"]
            detail_row["test_mae"] = "" if test_row is None else test_row["mae"]
            detail_row["test_mape"] = "" if test_row is None else test_row["mape"]
            detail_row["test_spearman"] = "" if test_row is None else test_row["spearman"]
            detail_row["decision"] = "Reference"
            detail_row["decision_reason"] = "Repeated validation row produced by final-eval or verification rerun."
            detail_row["notes"] = "Repeated Week 4 validation row; not counted as a separate formal experiment."
            if _detail_row_key(detail_row) not in existing_keys:
                existing_rows.append(detail_row)
                existing_keys.add(_detail_row_key(detail_row))
                appended += 1

    _write_detail_rows(existing_rows)
    print({
        "mode": "backfill_week4",
        "rows_added": appended,
        "detail_log": str(DETAIL_LOG_PATH),
    })
    return 0


def _append_active_detail_row(args: argparse.Namespace) -> int:
    log_rows = _read_tsv(LOG_PATH)
    active_model_name = model_name()
    validation_row = _latest_matching_row(log_rows, model_label=active_model_name, split_name="validation")
    if validation_row is None:
        raise ValueError(f"No validation row found for active model '{active_model_name}'.")

    feature_spec = get_active_feature_spec()
    model_spec = get_active_model_spec()
    detail_row = {
        "logged_at": datetime.now().isoformat(timespec="seconds"),
        "validation_timestamp": validation_row["timestamp"],
        "model_name": active_model_name,
        "feature_set_name": feature_spec["feature_set_name"],
        "feature_engineering_summary": feature_spec["summary"],
        "engineered_features_json": _json_compact(feature_spec["engineered_features"]),
        "model_variant_name": model_spec["model_variant_name"],
        "model_summary": model_spec["summary"],
        "estimator_family": model_spec["estimator_family"],
        "estimator_params_json": _json_compact(model_spec["estimator_params"]),
        "preprocessor_spec_json": _json_compact(model_spec["preprocessor_spec"]),
        "blend_spec_json": _json_compact(model_spec["blend_spec"]),
        "hypothesis": args.hypothesis,
        "changed_components": _normalize_changed_components(args.changed_components),
        "why_this_should_help": args.why,
        "decision": args.decision,
        "decision_reason": args.decision_reason,
        "validation_rmse": validation_row["rmse"],
        "validation_mae": validation_row["mae"],
        "validation_mape": validation_row["mape"],
        "validation_spearman": validation_row["spearman"],
        "test_rmse": "",
        "test_mae": "",
        "test_mape": "",
        "test_spearman": "",
        "notes": args.notes,
    }
    appended, _ = _append_detail_row_if_missing(detail_row)
    print({
        "mode": "append",
        "appended": appended,
        "model_name": active_model_name,
        "validation_timestamp": validation_row["timestamp"],
        "detail_log": str(DETAIL_LOG_PATH),
    })
    return 0


def main() -> int:
    args = _parse_args()
    _ensure_detail_log_header()

    if args.sync_final_eval:
        return _sync_final_eval()
    if args.backfill_week4:
        return _backfill_week4()

    required = {
        "--hypothesis": args.hypothesis,
        "--changed-components": args.changed_components,
        "--why": args.why,
        "--decision": args.decision,
        "--decision-reason": args.decision_reason,
    }
    missing = [flag for flag, value in required.items() if not value]
    if missing:
        raise ValueError(f"Missing required arguments for append mode: {', '.join(missing)}")
    return _append_active_detail_row(args)


if __name__ == "__main__":
    raise SystemExit(main())
