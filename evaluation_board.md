# Evaluation Board

- Canonical dataset: `/Users/ingridyeung/Desktop/STAT390/spotify-listener-growth-autoresearch/data/processed/master_growth_dataset.csv`
- Rows in feature frame: `14512`
- Train cutoff: `2025-08-14`
- Validation cutoff: `2025-11-27`
- Test cutoff: `2026-03-13`
- Current agent model: `search_huber_week4_release_plus_regime_combo_v1`
- Current validation RMSE: `1328169.54`
- Current validation MAE: `875849.14`
- Current validation MAPE: `6.016124`
- Current validation Spearman: `0.455865`
- Best stored validation RMSE: `1328169.54`

## Frozen Files
- `src/eval/*`
- `src/pipeline/prepare.py`
- `src/pipeline/build_features.py`
- `src/run.py`

## Mutable Files
- `src/agent_loop/features.py`
- `src/agent_loop/model.py`
