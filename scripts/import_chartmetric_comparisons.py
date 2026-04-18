#!/usr/bin/env python3
"""Import daily Chartmetric comparison CSV exports into listener-growth raw tables."""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = Path("/Users/ingridyeung/Downloads")
RAW = ROOT / "data" / "raw"

METRIC_FILES = {
    "Chartmetric Score": "chartmetric_score",
    "Instagram Engagement Rate": "instagram_engagement_rate",
    "Instagram Followers": "instagram_followers",
    "Spotify Fan Conversion Rate": "spotify_fan_conversion_rate",
    "Spotify Followers": "spotify_followers",
    "Spotify Monthly Listeners": "spotify_monthly_listeners",
    "Spotify Playlist Reach": "spotify_playlist_reach",
    "TikTok Followers": "tiktok_followers",
    "TikTok Likes": "tiktok_likes",
    "YouTube Daily Video Views": "youtube_daily_video_views",
    "YouTube Monthly Audience": "youtube_monthly_audience",
    "YouTube Subscribers": "youtube_subscribers",
}

ARTIST_DAILY_LISTENERS = RAW / "artist_daily_listeners.csv"
ARTIST_DAILY_METRICS = RAW / "artist_daily_metrics.csv"


def parse_date(raw: str) -> str:
    return datetime.strptime(raw, "%b %d, %Y").date().isoformat()


def normalize_value(raw: str) -> str:
    value = raw.strip().replace(",", "").replace("%", "")
    return value


def find_metric_file(prefix: str) -> Path:
    matches = sorted(DOWNLOADS.glob(f"{prefix}*Comparison.csv"))
    if not matches:
        raise FileNotFoundError(f"No comparison CSV found for {prefix}")
    return matches[-1]


def load_wide_series(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    all_rows: dict[tuple[str, str], dict] = {}
    listeners_rows: list[dict] = []
    metric_columns: list[str] = []

    for prefix, column_name in METRIC_FILES.items():
        path = find_metric_file(prefix)
        rows = load_wide_series(path)
        if column_name != "spotify_monthly_listeners":
            metric_columns.append(column_name)

        for row in rows:
            as_of_date = parse_date(row["Date"])
            for artist_name, raw_value in row.items():
                if artist_name == "Date":
                    continue
                value = normalize_value(raw_value)
                if value == "":
                    continue

                key = (artist_name, as_of_date)
                out = all_rows.setdefault(
                    key, {"artist_name": artist_name, "as_of_date": as_of_date}
                )

                if column_name == "spotify_monthly_listeners":
                    listeners_rows.append(
                        {
                            "artist_name": artist_name,
                            "as_of_date": as_of_date,
                            "spotify_monthly_listeners": value,
                        }
                    )
                else:
                    out[column_name] = value

    metric_columns = sorted(metric_columns)
    metric_rows = []
    for key in sorted(all_rows, key=lambda item: (item[0], item[1]), reverse=False):
        row = all_rows[key]
        metric_rows.append(
            {
                "artist_name": row["artist_name"],
                "as_of_date": row["as_of_date"],
                **{column: row.get(column, "") for column in metric_columns},
            }
        )

    write_csv(
        ARTIST_DAILY_LISTENERS,
        ["artist_name", "as_of_date", "spotify_monthly_listeners"],
        sorted(listeners_rows, key=lambda r: (r["artist_name"], r["as_of_date"])),
    )
    write_csv(ARTIST_DAILY_METRICS, ["artist_name", "as_of_date", *metric_columns], metric_rows)

    print(
        {
            "listeners_rows": len(listeners_rows),
            "metric_rows": len(metric_rows),
            "artist_daily_listeners": str(ARTIST_DAILY_LISTENERS),
            "artist_daily_metrics": str(ARTIST_DAILY_METRICS),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
