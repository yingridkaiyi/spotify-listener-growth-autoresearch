# Spotify Listener Growth AutoResearch Agent Instructions

## Objective

Minimize **validation RMSE** on `listener_growth_30d_abs`.

## Rules

1. You may **ONLY** modify `src/agent_loop/model.py` during the Week 3 dry loop.
2. `src/eval/*`, `src/pipeline/prepare.py`, `src/pipeline/build_features.py`, and `src/run.py` are **FROZEN**.
3. `build_estimator()` must return an sklearn-compatible estimator.
4. Training + evaluation must complete in **under 60 seconds** on CPU.
5. Do not access or simulate any hidden test set during search.
6. Do not add new dependencies or change the evaluation contract.

## Workflow

```text
1. Read current src/agent_loop/model.py
2. Propose one model change
3. Edit only src/agent_loop/model.py
4. Run: python3 src/run.py
5. Check validation RMSE in the output
6. If improved: keep the change and log it
7. If worse: revert src/agent_loop/model.py only
8. Repeat
```

## Week 3 Search Surface

- Frozen files:
  - `src/eval/*`
  - `src/pipeline/prepare.py`
  - `src/pipeline/build_features.py`
  - `src/run.py`
- Mutable file:
  - `src/agent_loop/model.py`
- Canonical dataset:
  - `data/processed/master_growth_dataset.csv`
- Run command:
  - `python3 src/run.py`

## Ideas To Explore

- Robust linear models such as `HuberRegressor`
- Tree ensembles such as `RandomForestRegressor`
- Gradient boosting such as `HistGradientBoostingRegressor`
- Alternative scaling choices such as `RobustScaler`

## What Not To Do

- Do not modify the split, metrics, or baseline policy
- Do not hard-code validation information into the model
- Do not edit generated logs or boards by hand
- Do not add features in Week 3 v1
