# Week 2 Status Update

## Project Title

AutoResearch for K-pop Spotify Listener Growth Prediction

## This Week's Goal

Freeze a reproducible Week 2 baseline pipeline for predicting 30-day Spotify monthly listener growth, including the dataset, split rules, evaluation metric, and initial benchmark models.

## What I Completed

- Built the canonical processed dataset at `data/processed/master_growth_dataset.csv` with 14,512 artist-date rows.
- Locked the time-based split with train cutoff `2025-08-14`, validation cutoff `2025-11-27`, and test cutoff `2026-03-13`.
- Documented the frozen evaluation contract and mutable files in `evaluation_board.md`.
- Implemented and logged baseline comparisons plus a first agent model in `experiments/experiment_log.tsv`.
- Organized the project around frozen evaluation files under `src/eval/`, `src/pipeline/`, and `src/run.py`, with agent-editable files under `src/agent_loop/`.

## One Key Artifact

Validation benchmark table from `experiments/experiment_log.tsv`:

| Model | Split | RMSE | MAE | Spearman |
|---|---|---:|---:|---:|
| `zero_growth_baseline` | validation | 1,567,991.67 | 967,837.32 | 0.0285 |
| `previous_30d_growth_baseline` | validation | 2,073,583.15 | 1,317,307.74 | 0.1680 |
| `ridge_baseline` | validation | 1,858,878.27 | 1,310,621.61 | 0.1507 |
| `agent_ridge_v1` | validation | 1,941,818.05 | 1,474,525.79 | 0.2740 |

Supporting files:

- `evaluation_board.md`
- `experiments/experiment_log.tsv`
- `workflow_diagram_listener_growth.html`

## Biggest Blocker

The current agent-editable model and feature set have not yet outperformed the simple `zero_growth_baseline` on validation RMSE, so the next round needs stronger feature engineering before model search will be meaningful.

## Plan for Next Week

- Audit the discrepancy between `evaluation_board.md` and `experiments/experiment_log.tsv` so the benchmark record is fully consistent.
- Improve features in `src/agent_loop/features.py`, especially lagged growth, event timing, and scale-aware transformations.
- Tune the agent model in `src/agent_loop/model.py` against the frozen validation split.
- Produce one improved model that clearly beats the baseline and document the result.
- Push the listener-growth project to its own GitHub repository so the submission URL matches the actual capstone project.

## Help Needed From the Instructor or TA

- Confirmation that the current Week 2 scope is appropriate for the pivot from concert-ticket resale forecasting to Spotify listener-growth prediction.
- Guidance on whether a persistence-style baseline such as `zero_growth_baseline` is acceptable as the official benchmark for this checkpoint.
- Feedback on whether the project should stay focused on absolute listener growth RMSE or also report a scale-adjusted target next week.
- Clarification on whether submitting the demo scaffold GitHub repo is acceptable temporarily, or whether the listener-growth project must be pushed as a separate repository before grading.

## GitHub URL

This project now exists as a local git repository at `spotify-listener-growth-autoresearch`, but it does not yet have a GitHub remote configured.

The only GitHub remote I could verify elsewhere in this workspace is:

- <https://github.com/Than1you/demo-autoresearch>

If the required submission URL must match the listener-growth project above, this repo still needs to be pushed to GitHub.
