#!/usr/bin/env python3
"""Mutable model definition for AutoResearch experiments."""

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
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import HuberRegressor
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from src.agent_loop.features import FEATURE_COLUMNS, get_active_feature_set_name

LOG_SCALE_COLUMNS = [
    "listeners_today",
    "listeners_lag_7d",
    "listeners_lag_30d",
    "instagram_followers",
    "spotify_followers",
    "spotify_playlist_reach",
    "tiktok_followers",
    "tiktok_likes",
    "youtube_daily_video_views",
    "youtube_monthly_audience",
    "youtube_subscribers",
    "chartmetric_score",
]
OTHER_COLUMNS = [column for column in FEATURE_COLUMNS if column not in LOG_SCALE_COLUMNS]


def log1p_clip_nonnegative(X):
    return np.log1p(np.clip(X, a_min=0, a_max=None))


def model_name() -> str:
    return f"search_huber_week4_{get_active_feature_set_name()}_v1"


def build_estimator():
    return Pipeline([
        ("preprocess", ColumnTransformer([
            (
                "log_scale",
                Pipeline([
                    ("imputer", SimpleImputer(strategy="median")),
                    (
                        "log",
                        FunctionTransformer(
                            log1p_clip_nonnegative,
                            feature_names_out="one-to-one",
                        ),
                    ),
                    ("scaler", StandardScaler()),
                ]),
                LOG_SCALE_COLUMNS,
            ),
            (
                "other",
                Pipeline([
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                ]),
                OTHER_COLUMNS,
            ),
        ])),
        ("huber", HuberRegressor(max_iter=500)),
    ])
