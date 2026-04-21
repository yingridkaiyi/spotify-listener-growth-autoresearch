# Spotify Listener Growth AutoResearch

This repository predicts `30-day Spotify monthly listener growth` for K-pop artists from a frozen artist-date master dataset.

## Success Criterion
- Primary metric: validation RMSE on `listener_growth_30d_abs`
- Initial target: RMSE below `1,500,000` listeners on the held-out validation period

## Baseline Policy
- Official baseline for course reporting: `ridge_baseline`
- Official baseline estimator: median imputation + `StandardScaler` + `Ridge(alpha=1.0)`
- Comparison baselines that remain in frozen evaluation output: `zero_growth_baseline`, `previous_30d_growth_baseline`
- Editable search model: `src/agent_loop/model.py`, currently initialized as `search_ridge_start_v1`
- Reporting note: if a comparison baseline beats ridge on RMSE, treat that as a diagnostic result rather than a change to the official baseline policy

## Repository Rules
- Frozen evaluation and pipeline code lives under `src/eval/`, `src/pipeline/prepare.py`, `src/pipeline/build_features.py`, and `src/run.py`
- Agent-editable code lives under `src/agent_loop/features.py` and `src/agent_loop/model.py`
- Canonical processed dataset: `data/processed/master_growth_dataset.csv`

## Core Commands
```bash
python3 src/pipeline/prepare.py
python3 src/run.py
```

## Repository URL
- GitHub: <https://github.com/yingridkaiyi/spotify-listener-growth-autoresearch>
