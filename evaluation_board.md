# Evaluation Board

- Canonical dataset: `/Users/ingridyeung/Desktop/STAT390/spotify-listener-growth-autoresearch/data/processed/master_growth_dataset.csv`
- Rows in feature frame: `14512`
- Train cutoff: `2025-08-14`
- Validation cutoff: `2025-11-27`
- Test cutoff: `2026-03-13`
- Current agent model: `search_ridge_start_v1`
- Current validation RMSE: `1941818.05`
- Current validation MAE: `1474525.79`
- Current validation MAPE: `18.074705`
- Current validation Spearman: `0.273982`
- Best stored validation RMSE: `1941818.05`

## Frozen Files
- `src/eval/*`
- `src/pipeline/prepare.py`
- `src/pipeline/build_features.py`
- `src/run.py`

## Mutable Files
- `src/agent_loop/features.py`
- `src/agent_loop/model.py`
