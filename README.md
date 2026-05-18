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

## Deliverables
- Course deliverables and supporting Week 1-5 artifacts live in `deliverables/`.

## Autoresearch Agent Prompt (Sample)
```text
You are the AutoResearch agent for this repo. Read `program.md`, inspect the
recent experiment logs and latest commit, then run one hypothesis-driven search
iteration.

Follow the rules in `program.md` exactly:
- only edit `src/agent_loop/features.py` and/or `src/agent_loop/model.py`
- do not edit frozen files
- make one small model or feature change
- run `python3 src/run.py`
- immediately run `python3 src/log_experiment_details.py` with hypothesis,
  changed components, why, decision, and decision reason
- compare against the active generalization anchor using the keep/discard
  guardrails
- keep the change only if it wins under those guardrails
- if discarded, restore the retained default behavior while preserving the
  logged challenger result

After the run, report:
- what hypothesis was tested
- what files changed
- validation RMSE, MAE, MAPE, and Spearman
- keep/discard decision
- whether the active retained model changed
- the next best hypothesis to try
```

## Repository URL
- GitHub: <https://github.com/yingridkaiyi/spotify-listener-growth-autoresearch>
