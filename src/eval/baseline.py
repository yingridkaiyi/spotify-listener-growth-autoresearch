#!/usr/bin/env python3
"""Frozen baseline models for the listener-growth project."""

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

import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.eval.evaluator import evaluate_regression

BASELINE_FEATURES = [
    "listeners_today",
    "listeners_lag_7d",
    "listeners_lag_30d",
    "listener_change_prev_7d",
    "listener_change_prev_30d",
    "listener_growth_rate_prev_7d",
    "listener_growth_rate_prev_30d",
    "chartmetric_score",
    "spotify_followers",
    "spotify_playlist_reach",
    "spotify_fan_conversion_rate",
    "instagram_followers",
    "youtube_subscribers",
    "tiktok_followers",
    "concert_count_prev_30d",
    "release_count_prev_30d",
]

TARGET_COLUMN = "listener_growth_30d_abs"


def evaluate_zero_growth(train_df, eval_df) -> dict:
    y_true = eval_df[TARGET_COLUMN].to_numpy(dtype=float)
    y_pred = np.zeros(len(eval_df), dtype=float)
    metrics = evaluate_regression(y_true, y_pred)
    metrics["model_name"] = "zero_growth_baseline"
    return metrics


def evaluate_previous_30d_growth(train_df, eval_df) -> dict:
    y_true = eval_df[TARGET_COLUMN].to_numpy(dtype=float)
    y_pred = eval_df["listener_change_prev_30d"].fillna(0).to_numpy(dtype=float)
    metrics = evaluate_regression(y_true, y_pred)
    metrics["model_name"] = "previous_30d_growth_baseline"
    return metrics


def evaluate_ridge_baseline(train_df, eval_df) -> dict:
    X_train = train_df[BASELINE_FEATURES]
    y_train = train_df[TARGET_COLUMN].to_numpy(dtype=float)
    X_eval = eval_df[BASELINE_FEATURES]
    y_true = eval_df[TARGET_COLUMN].to_numpy(dtype=float)

    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("ridge", Ridge(alpha=1.0)),
    ])
    model.fit(X_train, y_train)
    y_pred = model.predict(X_eval)
    metrics = evaluate_regression(y_true, y_pred)
    metrics["model_name"] = "ridge_baseline"
    return metrics


def evaluate_baselines(train_df, eval_df) -> list[dict]:
    return [
        evaluate_zero_growth(train_df, eval_df),
        evaluate_previous_30d_growth(train_df, eval_df),
        evaluate_ridge_baseline(train_df, eval_df),
    ]
