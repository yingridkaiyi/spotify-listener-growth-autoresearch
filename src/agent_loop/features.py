#!/usr/bin/env python3
"""Mutable feature selection layer for AutoResearch experiments."""

from __future__ import annotations

import os
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

import pandas as pd

ID_COLUMNS = ["artist_name", "as_of_date"]
TARGET_COLUMN = "listener_growth_30d_abs"

WEEK3_CONTROL_COLUMNS = [
    "listeners_today",
    "listeners_lag_7d",
    "listeners_lag_30d",
    "listener_change_prev_7d",
    "listener_change_prev_30d",
    "listener_growth_rate_prev_7d",
    "listener_growth_rate_prev_30d",
    "chartmetric_score",
    "instagram_engagement_rate",
    "instagram_followers",
    "spotify_fan_conversion_rate",
    "spotify_followers",
    "spotify_playlist_reach",
    "tiktok_followers",
    "tiktok_likes",
    "youtube_daily_video_views",
    "youtube_monthly_audience",
    "youtube_subscribers",
    "concert_count_prev_7d",
    "concert_count_prev_30d",
    "concert_count_next_7d",
    "concert_count_next_30d",
    "days_until_next_concert",
    "multi_night_run_flag",
    "release_count_prev_30d",
    "album_release_prev_30d_flag",
    "single_release_prev_30d_flag",
    "mv_release_prev_30d_flag",
    "days_since_last_release",
    "days_until_next_release",
]

RELEASE_TIMING_COLUMNS = [
    "release_in_next_7d_flag",
    "release_in_next_30d_flag",
    "release_within_last_7d_flag",
    "release_within_last_30d_flag",
]

CONCERT_TIMING_COLUMNS = [
    "concert_in_next_7d_flag",
    "concert_in_next_30d_flag",
]

NEGATIVE_REGIME_COLUMNS = [
    "prev_7d_negative_flag",
    "prev_30d_negative_flag",
    "prev_7d_flat_flag",
    "prev_30d_flat_flag",
]

MOMENTUM_GAP_COLUMNS = [
    "change_gap_7d_vs_30d_scaled",
    "growth_rate_gap_7d_vs_30d",
]

SPIKE_FLAG_COLUMNS = [
    "prev_7d_positive_spike_flag",
    "prev_30d_positive_spike_flag",
    "prev_7d_strong_decline_flag",
    "prev_30d_strong_decline_flag",
    "prev_7d_high_growth_rate_flag",
    "prev_30d_high_growth_rate_flag",
]

RELEASE_MOMENTUM_INTERACTION_COLUMNS = [
    "release_next_30d_x_prev_7d_positive_spike",
    "release_last_30d_x_prev_7d_positive_spike",
    "release_next_30d_x_prev_30d_positive_spike",
    "release_last_30d_x_prev_30d_positive_spike",
]

FEATURE_SET_REGISTRY = {
    "control_week3_features": WEEK3_CONTROL_COLUMNS,
    "release_timing_family": WEEK3_CONTROL_COLUMNS + RELEASE_TIMING_COLUMNS,
    "concert_timing_family": WEEK3_CONTROL_COLUMNS + CONCERT_TIMING_COLUMNS,
    "negative_regime_family": WEEK3_CONTROL_COLUMNS + NEGATIVE_REGIME_COLUMNS,
    "release_plus_regime_combo": (
        WEEK3_CONTROL_COLUMNS + RELEASE_TIMING_COLUMNS + NEGATIVE_REGIME_COLUMNS
    ),
    "momentum_gap_family": WEEK3_CONTROL_COLUMNS + MOMENTUM_GAP_COLUMNS,
    "spike_flag_family": WEEK3_CONTROL_COLUMNS + SPIKE_FLAG_COLUMNS,
    "release_plus_momentum_family": (
        WEEK3_CONTROL_COLUMNS + RELEASE_TIMING_COLUMNS + MOMENTUM_GAP_COLUMNS
    ),
    "breakout_full_combo": (
        WEEK3_CONTROL_COLUMNS
        + RELEASE_TIMING_COLUMNS
        + NEGATIVE_REGIME_COLUMNS
        + MOMENTUM_GAP_COLUMNS
        + SPIKE_FLAG_COLUMNS
        + RELEASE_MOMENTUM_INTERACTION_COLUMNS
    ),
}

ACTIVE_FEATURE_SET = "release_plus_regime_combo"
FEATURE_SET_ENV_VAR = "STAT390_WEEK4_FEATURE_SET"


def get_active_feature_set_name() -> str:
    selected = os.environ.get(FEATURE_SET_ENV_VAR, ACTIVE_FEATURE_SET)
    if selected not in FEATURE_SET_REGISTRY:
        available = ", ".join(sorted(FEATURE_SET_REGISTRY))
        raise ValueError(
            f"Unknown feature set '{selected}'. Expected one of: {available}."
        )
    return selected


FEATURE_COLUMNS = FEATURE_SET_REGISTRY[get_active_feature_set_name()]


def _flag_within_days(series: pd.Series, max_days: int) -> pd.Series:
    return series.notna().astype(float) * series.le(max_days).astype(float)


def _flag_abs_below(series: pd.Series, max_abs: float) -> pd.Series:
    return series.abs().le(max_abs).astype(float)


def build_feature_matrix(dataset):
    columns = [*ID_COLUMNS, TARGET_COLUMN, *WEEK3_CONTROL_COLUMNS]
    frame = dataset[columns].copy()
    for column in [TARGET_COLUMN, *WEEK3_CONTROL_COLUMNS]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    frame["release_in_next_7d_flag"] = _flag_within_days(
        frame["days_until_next_release"], max_days=7
    )
    frame["release_in_next_30d_flag"] = _flag_within_days(
        frame["days_until_next_release"], max_days=30
    )
    frame["release_within_last_7d_flag"] = _flag_within_days(
        frame["days_since_last_release"], max_days=7
    )
    frame["release_within_last_30d_flag"] = _flag_within_days(
        frame["days_since_last_release"], max_days=30
    )
    frame["concert_in_next_7d_flag"] = _flag_within_days(
        frame["days_until_next_concert"], max_days=7
    )
    frame["concert_in_next_30d_flag"] = _flag_within_days(
        frame["days_until_next_concert"], max_days=30
    )
    frame["prev_7d_negative_flag"] = frame["listener_change_prev_7d"].lt(0).astype(float)
    frame["prev_30d_negative_flag"] = frame["listener_change_prev_30d"].lt(0).astype(float)
    frame["prev_7d_flat_flag"] = _flag_abs_below(
        frame["listener_change_prev_7d"], max_abs=100_000
    )
    frame["prev_30d_flat_flag"] = _flag_abs_below(
        frame["listener_change_prev_30d"], max_abs=250_000
    )
    frame["change_gap_7d_vs_30d_scaled"] = (
        frame["listener_change_prev_7d"] - (frame["listener_change_prev_30d"] / 4.0)
    )
    frame["growth_rate_gap_7d_vs_30d"] = (
        frame["listener_growth_rate_prev_7d"] - frame["listener_growth_rate_prev_30d"]
    )
    frame["prev_7d_positive_spike_flag"] = (
        frame["listener_change_prev_7d"].ge(500_000)
        | frame["listener_growth_rate_prev_7d"].ge(0.04)
    ).astype(float)
    frame["prev_30d_positive_spike_flag"] = (
        frame["listener_change_prev_30d"].ge(1_500_000)
        | frame["listener_growth_rate_prev_30d"].ge(0.15)
    ).astype(float)
    frame["prev_7d_strong_decline_flag"] = (
        frame["listener_change_prev_7d"].le(-400_000)
    ).astype(float)
    frame["prev_30d_strong_decline_flag"] = (
        frame["listener_change_prev_30d"].le(-1_500_000)
    ).astype(float)
    frame["prev_7d_high_growth_rate_flag"] = (
        frame["listener_growth_rate_prev_7d"].ge(0.04)
    ).astype(float)
    frame["prev_30d_high_growth_rate_flag"] = (
        frame["listener_growth_rate_prev_30d"].ge(0.15)
    ).astype(float)
    frame["release_next_30d_x_prev_7d_positive_spike"] = (
        frame["release_in_next_30d_flag"] * frame["prev_7d_positive_spike_flag"]
    )
    frame["release_last_30d_x_prev_7d_positive_spike"] = (
        frame["release_within_last_30d_flag"] * frame["prev_7d_positive_spike_flag"]
    )
    frame["release_next_30d_x_prev_30d_positive_spike"] = (
        frame["release_in_next_30d_flag"] * frame["prev_30d_positive_spike_flag"]
    )
    frame["release_last_30d_x_prev_30d_positive_spike"] = (
        frame["release_within_last_30d_flag"] * frame["prev_30d_positive_spike_flag"]
    )

    return frame[[*ID_COLUMNS, TARGET_COLUMN, *FEATURE_COLUMNS]]
