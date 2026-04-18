#!/usr/bin/env python3
"""Frozen raw-to-modeling-table builder for listener growth prediction."""

from __future__ import annotations

from pathlib import Path
import site
import sys

USER_SITE_CANDIDATES = [
    Path.home() / ".local" / "lib" / "python3.13" / "site-packages",
    Path.home() / "Library" / "Python" / "3.13" / "lib" / "python" / "site-packages",
    Path("/opt/miniconda3/lib/python3.13/site-packages"),
]

for candidate in USER_SITE_CANDIDATES:
    if candidate.exists() and str(candidate) not in sys.path:
        site.addsitedir(str(candidate))

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

LISTENERS = RAW / "artist_daily_listeners.csv"
DAILY_METRICS = RAW / "artist_daily_metrics.csv"
CONCERTS = RAW / "concert_events.csv"
RELEASES = RAW / "release_events.csv"
DEFAULT_OUTPUT_PATH = PROCESSED / "master_growth_dataset.csv"

OUTPUT_COLUMNS = [
    "artist_name",
    "as_of_date",
    "listeners_today",
    "listeners_lag_7d",
    "listeners_lag_30d",
    "listener_change_prev_7d",
    "listener_change_prev_30d",
    "listener_growth_rate_prev_7d",
    "listener_growth_rate_prev_30d",
    "listener_growth_30d_abs",
    "listener_growth_30d_pct",
    "concert_count_prev_7d",
    "concert_count_prev_30d",
    "concert_count_next_7d",
    "concert_count_next_30d",
    "days_since_last_concert",
    "days_until_next_concert",
    "multi_night_run_flag",
    "release_count_prev_30d",
    "album_release_prev_30d_flag",
    "single_release_prev_30d_flag",
    "mv_release_prev_30d_flag",
    "days_since_last_release",
    "days_until_next_release",
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
]

METRIC_COLUMNS = [
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
]


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def _prepare_listeners() -> pd.DataFrame:
    listeners = _read_csv(LISTENERS)
    listeners["as_of_date"] = pd.to_datetime(listeners["as_of_date"])
    listeners["spotify_monthly_listeners"] = pd.to_numeric(
        listeners["spotify_monthly_listeners"], errors="coerce"
    )
    listeners = listeners.sort_values(["artist_name", "as_of_date"]).reset_index(drop=True)
    listeners["listeners_today"] = listeners["spotify_monthly_listeners"]
    listeners["listeners_lag_7d"] = listeners.groupby("artist_name")["listeners_today"].shift(7)
    listeners["listeners_lag_30d"] = listeners.groupby("artist_name")["listeners_today"].shift(30)
    listeners["listeners_future_30d"] = listeners.groupby("artist_name")["listeners_today"].shift(-30)
    listeners["listener_change_prev_7d"] = listeners["listeners_today"] - listeners["listeners_lag_7d"]
    listeners["listener_change_prev_30d"] = listeners["listeners_today"] - listeners["listeners_lag_30d"]
    listeners["listener_growth_rate_prev_7d"] = (
        listeners["listener_change_prev_7d"] / listeners["listeners_lag_7d"]
    )
    listeners["listener_growth_rate_prev_30d"] = (
        listeners["listener_change_prev_30d"] / listeners["listeners_lag_30d"]
    )
    listeners["listener_growth_30d_abs"] = (
        listeners["listeners_future_30d"] - listeners["listeners_today"]
    )
    listeners["listener_growth_30d_pct"] = (
        listeners["listener_growth_30d_abs"] / listeners["listeners_today"]
    )
    return listeners[listeners["listeners_future_30d"].notna()].copy()


def _prepare_metrics() -> pd.DataFrame:
    metrics = _read_csv(DAILY_METRICS)
    if metrics.empty:
        return metrics
    metrics["as_of_date"] = pd.to_datetime(metrics["as_of_date"])
    for column in METRIC_COLUMNS:
        metrics[column] = pd.to_numeric(metrics[column], errors="coerce")
    return metrics.sort_values(["artist_name", "as_of_date"]).reset_index(drop=True)


def _prepare_concert_features(listeners: pd.DataFrame) -> pd.DataFrame:
    concerts = _read_csv(CONCERTS)
    if concerts.empty:
        return pd.DataFrame(
            columns=[
                "artist_name",
                "as_of_date",
                "concert_count_prev_7d",
                "concert_count_prev_30d",
                "concert_count_next_7d",
                "concert_count_next_30d",
                "days_since_last_concert",
                "days_until_next_concert",
                "multi_night_run_flag",
            ]
        )

    concerts["event_date"] = pd.to_datetime(concerts["event_date"])
    base = listeners[["artist_name", "as_of_date"]].drop_duplicates().copy()
    dates_by_artist = {
        artist: sorted(group["event_date"].dropna().tolist())
        for artist, group in concerts.groupby("artist_name")
    }
    rows: list[dict] = []
    for row in base.itertuples(index=False):
        event_dates = dates_by_artist.get(row.artist_name, [])
        before = [d for d in event_dates if d < row.as_of_date]
        after = [d for d in event_dates if d > row.as_of_date]
        prev_7 = sum((row.as_of_date - pd.Timedelta(days=7)) <= d <= (row.as_of_date - pd.Timedelta(days=1)) for d in event_dates)
        prev_30 = sum((row.as_of_date - pd.Timedelta(days=30)) <= d <= (row.as_of_date - pd.Timedelta(days=1)) for d in event_dates)
        next_7 = sum((row.as_of_date + pd.Timedelta(days=1)) <= d <= (row.as_of_date + pd.Timedelta(days=7)) for d in event_dates)
        next_30 = sum((row.as_of_date + pd.Timedelta(days=1)) <= d <= (row.as_of_date + pd.Timedelta(days=30)) for d in event_dates)
        rows.append(
            {
                "artist_name": row.artist_name,
                "as_of_date": row.as_of_date,
                "concert_count_prev_7d": prev_7,
                "concert_count_prev_30d": prev_30,
                "concert_count_next_7d": next_7,
                "concert_count_next_30d": next_30,
                "days_since_last_concert": (row.as_of_date - max(before)).days if before else pd.NA,
                "days_until_next_concert": (min(after) - row.as_of_date).days if after else pd.NA,
                "multi_night_run_flag": int(prev_7 > 1 or next_7 > 1),
            }
        )
    return pd.DataFrame(rows)


def _prepare_release_features(listeners: pd.DataFrame) -> pd.DataFrame:
    releases = _read_csv(RELEASES)
    if releases.empty:
        return pd.DataFrame(
            columns=[
                "artist_name",
                "as_of_date",
                "release_count_prev_30d",
                "album_release_prev_30d_flag",
                "single_release_prev_30d_flag",
                "mv_release_prev_30d_flag",
                "days_since_last_release",
                "days_until_next_release",
            ]
        )

    releases["release_date"] = pd.to_datetime(releases["release_date"])
    base = listeners[["artist_name", "as_of_date"]].drop_duplicates().copy()
    by_artist = {artist: group.sort_values("release_date") for artist, group in releases.groupby("artist_name")}
    rows: list[dict] = []
    for row in base.itertuples(index=False):
        artist_releases = by_artist.get(row.artist_name)
        if artist_releases is None:
            release_dates = []
            window = None
        else:
            release_dates = artist_releases["release_date"].tolist()
            window = artist_releases[
                (artist_releases["release_date"] >= row.as_of_date - pd.Timedelta(days=30))
                & (artist_releases["release_date"] <= row.as_of_date - pd.Timedelta(days=1))
            ]
        before = [d for d in release_dates if d < row.as_of_date]
        after = [d for d in release_dates if d > row.as_of_date]
        rows.append(
            {
                "artist_name": row.artist_name,
                "as_of_date": row.as_of_date,
                "release_count_prev_30d": 0 if window is None else len(window),
                "album_release_prev_30d_flag": 0 if window is None else int((window["release_type"] == "album").any()),
                "single_release_prev_30d_flag": 0 if window is None else int((window["release_type"] == "single").any()),
                "mv_release_prev_30d_flag": 0 if window is None else int((window["release_type"] == "mv").any()),
                "days_since_last_release": (row.as_of_date - max(before)).days if before else pd.NA,
                "days_until_next_release": (min(after) - row.as_of_date).days if after else pd.NA,
            }
        )
    return pd.DataFrame(rows)


def _merge_metrics(dataset: pd.DataFrame, metrics: pd.DataFrame) -> pd.DataFrame:
    if metrics.empty:
        for column in METRIC_COLUMNS:
            dataset[column] = pd.NA
        return dataset

    metric_groups = {artist: group.copy() for artist, group in metrics.groupby("artist_name")}
    merged_parts: list[pd.DataFrame] = []
    for artist_name, group in dataset.groupby("artist_name", sort=False):
        left = group.sort_values("as_of_date").copy()
        right = metric_groups.get(artist_name)
        if right is None or right.empty:
            for column in METRIC_COLUMNS:
                left[column] = pd.NA
        else:
            right = right.sort_values("as_of_date").copy()
            left = pd.merge_asof(
                left,
                right[["as_of_date", *METRIC_COLUMNS]],
                on="as_of_date",
                direction="backward",
            )
        merged_parts.append(left)
    return pd.concat(merged_parts, ignore_index=True)


def build_dataset() -> pd.DataFrame:
    listeners = _prepare_listeners()
    metrics = _prepare_metrics()
    concerts = _prepare_concert_features(listeners)
    releases = _prepare_release_features(listeners)

    dataset = listeners[
        [
            "artist_name",
            "as_of_date",
            "listeners_today",
            "listeners_lag_7d",
            "listeners_lag_30d",
            "listener_change_prev_7d",
            "listener_change_prev_30d",
            "listener_growth_rate_prev_7d",
            "listener_growth_rate_prev_30d",
            "listener_growth_30d_abs",
            "listener_growth_30d_pct",
        ]
    ].copy()
    dataset = _merge_metrics(
        dataset.sort_values(["artist_name", "as_of_date"]).reset_index(drop=True),
        metrics.sort_values(["artist_name", "as_of_date"]).reset_index(drop=True),
    )
    dataset = dataset.merge(concerts, on=["artist_name", "as_of_date"], how="left")
    dataset = dataset.merge(releases, on=["artist_name", "as_of_date"], how="left")

    zero_fill_columns = [
        "concert_count_prev_7d",
        "concert_count_prev_30d",
        "concert_count_next_7d",
        "concert_count_next_30d",
        "multi_night_run_flag",
        "release_count_prev_30d",
        "album_release_prev_30d_flag",
        "single_release_prev_30d_flag",
        "mv_release_prev_30d_flag",
    ]
    for column in zero_fill_columns:
        dataset[column] = dataset[column].fillna(0)

    dataset = dataset[OUTPUT_COLUMNS].sort_values(["artist_name", "as_of_date"]).reset_index(drop=True)
    dataset["as_of_date"] = dataset["as_of_date"].dt.strftime("%Y-%m-%d")
    return dataset


def save_dataset(path: str | Path | None = None) -> Path:
    output_path = Path(path) if path is not None else DEFAULT_OUTPUT_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataset = build_dataset()
    dataset.to_csv(output_path, index=False, na_rep="")
    return output_path


def load_dataset() -> pd.DataFrame:
    return build_dataset()


if __name__ == "__main__":
    saved = save_dataset()
    print({"rows": len(load_dataset()), "out": str(saved)})
