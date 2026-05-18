# Week 2 Status Update

## Project Title

AutoResearch for K-pop Spotify Listener Growth Prediction

## This Week's Goal

Freeze a reproducible Week 2 baseline pipeline for predicting 30-day Spotify monthly listener growth, including the dataset, split rules, evaluation metric, and initial benchmark models.

## What I Completed

- Built the canonical processed dataset at `data/processed/master_growth_dataset.csv` with 14,512 artist-date rows.
- Locked the time-based split with train cutoff `2025-08-14`, validation cutoff `2025-11-27`, and test cutoff `2026-03-13`.
- Documented the frozen evaluation contract and mutable files in `evaluation_board.md`.
- Implemented the official simple ridge baseline policy, kept the frozen comparison baselines in the evaluation output, and recorded the first editable search-model run in `experiments/experiment_log.tsv`.
- Organized the project around frozen evaluation files under `src/eval/`, `src/pipeline/`, and `src/run.py`, with agent-editable files under `src/agent_loop/`.

## One Key Artifact

Validation benchmark table from `experiments/experiment_log.tsv`:

| Role | Model | Split | RMSE | MAE | Spearman |
|---|---|---|---:|---:|---:|
| Comparison baseline | `zero_growth_baseline` | validation | 1,567,991.67 | 967,837.32 | 0.0285 |
| Comparison baseline | `previous_30d_growth_baseline` | validation | 2,073,583.15 | 1,317,307.74 | 0.1680 |
| Official baseline | `ridge_baseline` | validation | 1,858,878.27 | 1,310,621.61 | 0.1507 |
| Current search model | `search_ridge_start_v1` | validation | 1,941,818.05 | 1,474,525.79 | 0.2740 |

Interpretation: the validation target is centered much closer to zero than the training target, so the conservative `zero_growth_baseline` is currently a safer RMSE guess than ridge. In the current split, the training target mean is about `+300,871`, the validation target mean is about `-9,854`, and the ridge model's average validation prediction is still about `+115,843`, which leads to larger signed errors when the later period shifts back toward zero or negative growth.

Supporting files:

- `evaluation_board.md`
- `experiments/experiment_log.tsv`
- `workflow_diagram_listener_growth.html`

## Biggest Blocker

The main blocker is distribution shift between the training and validation periods plus weak predictive signal in the current feature set. Ridge learned a more positive-growth regime from training, but the frozen validation window is much closer to zero and includes many negative outcomes, so a conservative zero prediction currently beats both the official `ridge_baseline` and the editable search model on RMSE. The next round therefore needs feature engineering that better captures near-zero and negative-growth periods before model search will be meaningful.

## Plan for Next Week

- Audit the discrepancy between `evaluation_board.md` and `experiments/experiment_log.tsv` so the benchmark record is fully consistent.
- Improve features in `src/agent_loop/features.py`, especially lagged growth, event timing, and scale-aware transformations that better capture near-zero or negative-growth periods and reduce overprediction in the later validation regime.
- Tune the editable search model in `src/agent_loop/model.py` against the frozen validation split.
- Produce one improved search model that clearly beats the official ridge baseline and document whether it also beats the comparison baselines.
- Keep the GitHub repository in sync as new results are added.

## Help Needed From the Instructor or TA

- Confirmation that the current Week 2 scope is appropriate for the pivot from concert-ticket resale forecasting to Spotify listener-growth prediction.
- Feedback on whether the project should stay focused on absolute listener growth RMSE or also report a scale-adjusted target next week.
- Advice on which feature families should be prioritized first to beat both the official ridge baseline and the strong zero-growth comparison baseline.
- Any recommendation on whether to keep reporting the comparison baselines in the weekly updates once the search model improves.

## GitHub URL

- <https://github.com/yingridkaiyi/spotify-listener-growth-autoresearch>
