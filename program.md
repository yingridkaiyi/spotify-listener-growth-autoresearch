# Spotify Listener Growth AutoResearch Agent Instructions

## Objective

Minimize **validation RMSE** on `listener_growth_30d_abs`.

## Rules

1. Week 4 is a **feature-only controlled experiment loop**.
2. `src/eval/*`, `src/pipeline/prepare.py`, `src/pipeline/build_features.py`, and `src/run.py` are **FROZEN**.
3. The estimator architecture and hyperparameters in `src/agent_loop/model.py` are **FROZEN**.
4. `src/agent_loop/model.py` may only change to expose feature-set-specific experiment names through `model_name()`.
5. Week 4 feature edits belong in `src/agent_loop/features.py`.
6. `build_estimator()` must return an sklearn-compatible estimator.
7. Training + evaluation must complete in **under 60 seconds** on CPU.
8. Do not access or simulate any hidden test set during search.
9. Do not add new dependencies or change the evaluation contract.

## Workflow

```text
1. Start from the Week 3 retained feature set as the control.
2. Change exactly one feature family relative to control.
3. Edit only src/agent_loop/features.py (and model_name() in src/agent_loop/model.py if needed for labeling).
4. Run: python3 src/run.py
5. Record validation RMSE, MAE, MAPE, and Spearman.
6. Revert to the control feature set before the next isolated run.
7. Repeat for each controlled variant.
8. After the isolated runs, run one fixed synthesis experiment.
9. After selecting the retained Week 4 feature set, run: python3 src/run.py --final-eval
```

## Week 4 Search Surface

- Frozen files:
  - `src/eval/*`
  - `src/pipeline/prepare.py`
  - `src/pipeline/build_features.py`
  - `src/run.py`
- Frozen within mutable surface:
  - estimator architecture and hyperparameters in `src/agent_loop/model.py`
- Mutable files:
  - `src/agent_loop/features.py`
  - `src/agent_loop/model.py`
- Canonical dataset:
  - `data/processed/master_growth_dataset.csv`
- Search command:
  - `python3 src/run.py`
- Final evaluation command:
  - `python3 src/run.py --final-eval`
- Feature-set switch:
  - default constant: `ACTIVE_FEATURE_SET` in `src/agent_loop/features.py`
  - optional run override: `STAT390_WEEK4_FEATURE_SET=<feature_set> python3 src/run.py`

## Week 4 Controlled Set

- `control_week3_features`
  - current Week 3 retained feature set
- `release_timing_family`
  - add release-window indicator features derived from the existing release timing columns
- `concert_timing_family`
  - add upcoming-concert indicator features derived from `days_until_next_concert`
- `negative_regime_family`
  - add negative and flat regime indicators derived from prior listener changes
- `release_plus_regime_combo`
  - combine the release-window and negative-regime feature families as the synthesis run

## What Not To Do

- Do not modify the split, metrics, or baseline policy
- Do not hard-code validation information into the model
- Do not edit generated logs or boards by hand
- Do not change multiple feature families in a single isolated run
- Do not reveal test metrics during normal search runs
