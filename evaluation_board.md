# Evaluation Board

- Canonical dataset: `/Users/ingridyeung/Desktop/STAT390/spotify-listener-growth-autoresearch/data/processed/master_growth_dataset.csv`
- Rows in feature frame: `14512`
- Train cutoff: `2025-08-14`
- Validation cutoff: `2025-11-27`
- Test cutoff: `2026-03-13`
- Current agent model: `search_week4_ratio_release_interaction_family_huber_eps_1_25_v1`
- Current validation RMSE: `1321827.56`
- Current validation MAE: `855576.66`
- Current validation MAPE: `4.773756`
- Current validation Spearman: `0.451507`
- Best stored validation RMSE: `1248417.77`

## Frozen Files
- `src/eval/*`
- `src/pipeline/prepare.py`
- `src/pipeline/build_features.py`
- `src/run.py`

## Mutable Files
- `src/agent_loop/features.py`
- `src/agent_loop/model.py`
