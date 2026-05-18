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

RATIO_FAMILY_COLUMNS = [
    "listener_change_prev_7d_ratio",
    "listener_change_prev_30d_ratio",
]

LOWER_CLIPPED_RATIO_FAMILY_COLUMNS = [
    "listener_change_prev_7d_ratio_lower_clip",
    "listener_change_prev_30d_ratio_lower_clip",
]

WINSORIZED_RATIO_FAMILY_COLUMNS = [
    "listener_change_prev_7d_ratio_winsor",
    "listener_change_prev_30d_ratio_winsor",
]

RELEASE_RATIO_INTERACTION_COLUMNS = [
    "release_last_30d_x_listener_change_prev_7d_ratio",
]

FEATURE_ENGINEERING_REGISTRY = {
    "control_week3_features": [],
    "release_timing_family": RELEASE_TIMING_COLUMNS,
    "concert_timing_family": CONCERT_TIMING_COLUMNS,
    "negative_regime_family": NEGATIVE_REGIME_COLUMNS,
    "release_plus_regime_combo": RELEASE_TIMING_COLUMNS + NEGATIVE_REGIME_COLUMNS,
    "momentum_gap_family": MOMENTUM_GAP_COLUMNS,
    "spike_flag_family": SPIKE_FLAG_COLUMNS,
    "release_plus_momentum_family": RELEASE_TIMING_COLUMNS + MOMENTUM_GAP_COLUMNS,
    "breakout_full_combo": (
        RELEASE_TIMING_COLUMNS
        + NEGATIVE_REGIME_COLUMNS
        + MOMENTUM_GAP_COLUMNS
        + SPIKE_FLAG_COLUMNS
        + RELEASE_MOMENTUM_INTERACTION_COLUMNS
    ),
    "ratio_family": RELEASE_TIMING_COLUMNS + NEGATIVE_REGIME_COLUMNS + RATIO_FAMILY_COLUMNS,
    "ratio_lower_clip_family": (
        RELEASE_TIMING_COLUMNS
        + NEGATIVE_REGIME_COLUMNS
        + LOWER_CLIPPED_RATIO_FAMILY_COLUMNS
    ),
    "ratio_winsor_family": (
        RELEASE_TIMING_COLUMNS + NEGATIVE_REGIME_COLUMNS + WINSORIZED_RATIO_FAMILY_COLUMNS
    ),
    "ratio_release_interaction_family": (
        RELEASE_TIMING_COLUMNS
        + NEGATIVE_REGIME_COLUMNS
        + RATIO_FAMILY_COLUMNS
        + RELEASE_RATIO_INTERACTION_COLUMNS
    ),
}

FEATURE_SET_SUMMARIES = {
    "control_week3_features": "Week 3 retained control feature set with no additional engineered flags.",
    "release_timing_family": "Week 3 control plus release-window proximity flags for recent and upcoming releases.",
    "concert_timing_family": "Week 3 control plus upcoming concert-window proximity flags.",
    "negative_regime_family": "Week 3 control plus negative-growth and near-flat regime indicators.",
    "release_plus_regime_combo": "Week 3 control plus release-window flags and negative/flat regime indicators.",
    "momentum_gap_family": "Week 3 control plus short-vs-long momentum gap features.",
    "spike_flag_family": "Week 3 control plus spike, decline, and high-growth-rate indicators.",
    "release_plus_momentum_family": "Week 3 control plus release-window flags and momentum-gap features.",
    "breakout_full_combo": "Week 3 control plus release/regime/momentum/spike features and release-spike interactions.",
    "ratio_family": "Release/regime feature family plus audience-scaled recent-change ratio features.",
    "ratio_lower_clip_family": "Ratio family variant that lower-clips audience-scaled recent-change ratios at -1.0 to reduce tiny-denominator artifacts.",
    "ratio_winsor_family": "Ratio family variant that broadly winsorizes audience-scaled recent-change ratios to reduce tiny-denominator artifacts and extreme surge leverage.",
    "ratio_release_interaction_family": "Ratio family plus a narrow recent-release by 7-day audience-scaled momentum interaction.",
}

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
    "ratio_family": (
        WEEK3_CONTROL_COLUMNS
        + RELEASE_TIMING_COLUMNS
        + NEGATIVE_REGIME_COLUMNS
        + RATIO_FAMILY_COLUMNS
    ),
    "ratio_lower_clip_family": (
        WEEK3_CONTROL_COLUMNS
        + RELEASE_TIMING_COLUMNS
        + NEGATIVE_REGIME_COLUMNS
        + LOWER_CLIPPED_RATIO_FAMILY_COLUMNS
    ),
    "ratio_winsor_family": (
        WEEK3_CONTROL_COLUMNS
        + RELEASE_TIMING_COLUMNS
        + NEGATIVE_REGIME_COLUMNS
        + WINSORIZED_RATIO_FAMILY_COLUMNS
    ),
    "ratio_release_interaction_family": (
        WEEK3_CONTROL_COLUMNS
        + RELEASE_TIMING_COLUMNS
        + NEGATIVE_REGIME_COLUMNS
        + RATIO_FAMILY_COLUMNS
        + RELEASE_RATIO_INTERACTION_COLUMNS
    ),
}

ACTIVE_FEATURE_SET = "ratio_release_interaction_family"
FEATURE_SET_ENV_VAR = "STAT390_WEEK4_FEATURE_SET"


def get_active_feature_set_name() -> str:
    selected = os.environ.get(FEATURE_SET_ENV_VAR, ACTIVE_FEATURE_SET)
    if selected not in FEATURE_SET_REGISTRY:
        available = ", ".join(sorted(FEATURE_SET_REGISTRY))
        raise ValueError(
            f"Unknown feature set '{selected}'. Expected one of: {available}."
        )
    return selected


def get_feature_spec(feature_set_name: str | None = None) -> dict:
    selected = feature_set_name or get_active_feature_set_name()
    if selected not in FEATURE_SET_REGISTRY:
        available = ", ".join(sorted(FEATURE_SET_REGISTRY))
        raise ValueError(
            f"Unknown feature set '{selected}'. Expected one of: {available}."
        )
    return {
        "feature_set_name": selected,
        "feature_columns": list(FEATURE_SET_REGISTRY[selected]),
        "engineered_features": list(FEATURE_ENGINEERING_REGISTRY[selected]),
        "summary": FEATURE_SET_SUMMARIES[selected],
    }


def get_active_feature_spec() -> dict:
    return get_feature_spec()


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
    frame["listener_change_prev_7d_ratio"] = frame["listener_change_prev_7d"].div(
        frame["listeners_today"].replace(0, pd.NA)
    )
    frame["listener_change_prev_30d_ratio"] = frame["listener_change_prev_30d"].div(
        frame["listeners_today"].replace(0, pd.NA)
    )
    frame["listener_change_prev_7d_ratio_lower_clip"] = frame[
        "listener_change_prev_7d_ratio"
    ].clip(lower=-1.0)
    frame["listener_change_prev_30d_ratio_lower_clip"] = frame[
        "listener_change_prev_30d_ratio"
    ].clip(lower=-1.0)
    frame["listener_change_prev_7d_ratio_winsor"] = frame[
        "listener_change_prev_7d_ratio"
    ].clip(lower=-0.10, upper=0.40)
    frame["listener_change_prev_30d_ratio_winsor"] = frame[
        "listener_change_prev_30d_ratio"
    ].clip(lower=-0.35, upper=0.80)
    frame["release_last_30d_x_listener_change_prev_7d_ratio"] = (
        frame["release_within_last_30d_flag"] * frame["listener_change_prev_7d_ratio"]
    )

    return frame[[*ID_COLUMNS, TARGET_COLUMN, *FEATURE_COLUMNS]]
