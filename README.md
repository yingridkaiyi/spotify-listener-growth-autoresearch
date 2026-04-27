# Spotify Listener Growth AutoResearch

This repository predicts `30-day Spotify monthly listener growth` for K-pop artists from a frozen artist-date master dataset.

## Success Criterion
- Primary metric: validation RMSE on `listener_growth_30d_abs`
- Initial target: RMSE below `1,500,000` listeners on the held-out validation period

## Baseline Policy
- Official baseline for course reporting: `ridge_baseline`
- Official baseline estimator: median imputation + `StandardScaler` + `Ridge(alpha=1.0)`
- Comparison baselines that remain in frozen evaluation output: `zero_growth_baseline`, `previous_30d_growth_baseline`
- Editable search model: `src/agent_loop/model.py`, currently initialized as `search_huber_v1`
- Reporting note: if a comparison baseline beats ridge on RMSE, treat that as a diagnostic result rather than a change to the official baseline policy

## Repository Rules
- Frozen evaluation and pipeline code lives under `src/eval/`, `src/pipeline/prepare.py`, `src/pipeline/build_features.py`, and `src/run.py`
- Agent-editable code lives under `src/agent_loop/features.py` and `src/agent_loop/model.py`
- Canonical processed dataset: `data/processed/master_growth_dataset.csv`

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The project was validated locally with `Python 3.13.3`.

## Core Commands
```bash
python3 src/pipeline/prepare.py
python3 src/run.py
```

## Reproducibility Notes
- The repository includes the processed dataset, so no external data download is required for the baseline run.
- A full run of `python3 src/run.py` completed successfully in `11.75` seconds wall-clock time in a local test environment.
- See `research_log.md` for the runtime assessment entry.

## Week 3 Artifacts
- Agent loop contract: `program.md`
- Week 3 dry-run deliverable: `week3_agent_loop.md`

## Repository URL
- GitHub: <https://github.com/yingridkaiyi/spotify-listener-growth-autoresearch>
