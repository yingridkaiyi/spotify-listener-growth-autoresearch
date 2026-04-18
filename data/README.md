# Data Layout

## Raw Inputs
- `data/raw/artist_daily_listeners.csv`
- `data/raw/artist_daily_metrics.csv`
- `data/raw/concert_events.csv`
- `data/raw/release_events.csv`

## Processed Output
- `data/processed/master_growth_dataset.csv`

The master dataset is one row per `artist_name x as_of_date` and is rebuilt only by `src/pipeline/prepare.py`.
