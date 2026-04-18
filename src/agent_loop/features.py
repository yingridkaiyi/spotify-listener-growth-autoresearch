#!/usr/bin/env python3
"""Mutable feature selection layer for AutoResearch experiments."""

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

import pandas as pd

ID_COLUMNS = ["artist_name", "as_of_date"]
TARGET_COLUMN = "listener_growth_30d_abs"

FEATURE_COLUMNS = [
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


def build_feature_matrix(dataset):
    columns = [*ID_COLUMNS, TARGET_COLUMN, *FEATURE_COLUMNS]
    frame = dataset[columns].copy()
    for column in [TARGET_COLUMN, *FEATURE_COLUMNS]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame
