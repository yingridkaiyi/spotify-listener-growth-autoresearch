# Listener Growth Dataset Plan

This project variant predicts `30-day Spotify monthly listener growth` for K-pop
artists. The modeling unit is an `artist_name x as_of_date` row.

## Target

Recommended target:

- `listener_growth_30d_abs`

Optional alternatives:

- `listener_growth_30d_pct`
- `log_listener_growth_30d_abs`

## Row Definition

One row per artist per observation date.

Example:

- BTS on `2026-04-12`
- TWICE on `2026-04-12`
- BTS on `2026-04-11`

## Core Inputs

Store these under `/Users/ingridyeung/Desktop/STAT390/spotify-listener-growth-autoresearch/data/raw/listener_growth/`.

1. `artist_daily_listeners.csv`
   - one row per artist per date
   - includes the historical monthly listeners time series

2. `concert_events.csv`
   - one row per concert stop
   - include historical and upcoming stops for each artist
   - this is event-level, not artist-level

3. `release_events.csv`
   - one row per release event
   - include album, EP, single, and official MV releases as separate rows

4. `artist_daily_metrics.csv`
   - one row per artist per date from Chartmetric comparison exports

## Event Features To Derive

Concert features:

- `concert_count_prev_7d`
- `concert_count_prev_30d`
- `concert_count_next_7d`
- `concert_count_next_30d`
- `days_since_last_concert`
- `days_until_next_concert`
- `multi_night_run_flag`

Release features:

- `album_release_prev_30d_flag`
- `single_release_prev_30d_flag`
- `mv_release_prev_30d_flag`
- `release_count_prev_30d`
- `days_since_last_release`
- `days_until_next_release`

Artist features:

- `chartmetric_score`
- `instagram_engagement_rate`
- `instagram_followers`
- `spotify_fan_conversion_rate`
- `spotify_followers`
- `spotify_playlist_reach`
- `tiktok_followers`
- `tiktok_likes`
- `youtube_daily_video_views`
- `youtube_monthly_audience`
- `youtube_subscribers`

Listener history features:

- `listeners_today`
- `listeners_lag_1d`
- `listeners_lag_7d`
- `listeners_lag_30d`
- `listener_change_prev_7d`
- `listener_change_prev_30d`
- `listener_growth_rate_prev_7d`
- `listener_growth_rate_prev_30d`

## Output

Build:

- `data/processed/listener_growth_dataset.csv`

That file should contain one row per artist-date with both lagged listener
signals and event/release-derived features.
