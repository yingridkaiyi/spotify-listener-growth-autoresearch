# Spotify Listener Growth AutoResearch

This repository predicts `30-day Spotify monthly listener growth` for K-pop artists from a frozen artist-date master dataset.

## Success Criterion
- Primary metric: validation RMSE on `listener_growth_30d_abs`
- Initial target: RMSE below `1,500,000` listeners on the held-out validation period

## Repository Rules
- Frozen evaluation and pipeline code lives under `src/eval/`, `src/pipeline/prepare.py`, `src/pipeline/build_features.py`, and `src/run.py`
- Agent-editable code lives under `src/agent_loop/features.py` and `src/agent_loop/model.py`
- Canonical processed dataset: `data/processed/master_growth_dataset.csv`

## Core Commands
```bash
python3 src/pipeline/prepare.py
python3 src/run.py
```
