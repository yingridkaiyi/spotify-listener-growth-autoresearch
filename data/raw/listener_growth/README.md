# Listener Growth Raw Files

This folder supports the `30-day Spotify monthly listener growth` project.

Files:

- `artist_daily_listeners.csv`: one row per artist-date listener observation
- `concert_events.csv`: one row per concert stop
- `release_events.csv`: one row per release event
- `artist_daily_metrics.csv`: one row per artist-date with Chartmetric comparison metrics

Event files are intentionally separate:

- concerts are event-level tour stops
- releases are event-level albums, EPs, singles, or official MVs

The final modeling dataset is artist-date level and should aggregate these event
tables into features around each observation date.
