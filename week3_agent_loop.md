# Week 3 Agent Loop Deliverable

## Goal

Launch a project-specific AutoResearch loop for the Spotify listener-growth repo,
keep the frozen evaluation contract intact, and document a short dry experiment
sequence in the style of the demo repository's `program.md`.

## Loop Contract

- Objective: minimize validation RMSE on `listener_growth_30d_abs`
- Frozen files:
  - `src/eval/*`
  - `src/pipeline/prepare.py`
  - `src/pipeline/build_features.py`
  - `src/run.py`
- Mutable file during the loop:
  - `src/agent_loop/model.py`
- Command:
  - `python3 src/run.py`
- Decision rule:
  - keep a change only if validation RMSE improves over the current best kept run

See [`program.md`](/Users/ingridyeung/Desktop/STAT390/spotify-listener-growth-autoresearch/program.md) for the repo-specific loop instructions.

## Starting Point

Pre-loop retained agent model:

- `search_ridge_start_v1`
- Validation RMSE: `1,941,818.05`
- Validation MAE: `1,474,525.79`
- Validation Spearman: `0.273982`

Frozen comparison points:

- `ridge_baseline` validation RMSE: `1,858,878.27`
- `zero_growth_baseline` validation RMSE: `1,567,991.67`

Notes:

- The `2026-04-27T15:25:56` log entries were a verification rerun of the old ridge state and are **not** counted as Week 3 experiments.
- The final `2026-04-27T15:36:25` Huber rerun was used only to restore the kept model as the latest generated board state.

## Dry Experiments

| # | Timestamp | Model | Validation RMSE | Validation MAE | Spearman | Decision |
|---|---|---|---:|---:|---:|---|
| 1 | `2026-04-27T15:34:13` | `search_huber_v1` | `1,422,490.72` | `940,201.06` | `0.385037` | **KEEP** |
| 2 | `2026-04-27T15:34:46` | `search_random_forest_dry_v1` | `1,723,695.41` | `1,179,621.71` | `0.298738` | Discard |
| 3 | `2026-04-27T15:35:29` | `search_hgb_dry_v1` | `1,545,233.53` | `1,038,507.09` | `0.390962` | Discard |
| 4 | `2026-04-27T15:35:55` | `search_huber_robust_dry_v1` | `1,424,619.16` | `915,336.61` | `0.297139` | Discard |

### Experiment Notes

1. `HuberRegressor` with `StandardScaler()` was the first model to beat all three comparison points that mattered for Week 3:
   - it improved over `search_ridge_start_v1`
   - it beat the frozen `ridge_baseline`
   - it also beat the strong `zero_growth_baseline`

2. The random forest improved over the original ridge start but failed to beat the kept Huber run, so it was reverted.

3. The histogram gradient boosting model posted a decent RMSE and slightly higher Spearman than the kept Huber run, but the Week 3 decision rule was RMSE only, so it was still discarded.

4. The `RobustScaler()` Huber variant came very close on RMSE and improved MAE, but it did not beat the standard-scaled Huber model on the official optimization metric.

## Final Retained Model

Retained model after the dry loop:

- `search_huber_v1`
- Pipeline:
  - `SimpleImputer(strategy="median")`
  - `StandardScaler()`
  - `HuberRegressor()`

Final synced run at `2026-04-27T15:36:25`:

- Validation RMSE: `1,422,490.72`
- Validation MAE: `940,201.06`
- Validation MAPE: `7.789217`
- Validation Spearman: `0.385037`
- Test RMSE: `2,109,601.36`

## Main Blocker

The biggest remaining blocker is still regime shift across time. The train period has a much more positive target mean than the validation period, so the model needs to stay conservative when late-period growth compresses back toward zero or negative values. Robust regression helped, but Week 3 remained model-only and did not change the feature set.

## Next Step

Week 4 should expand the loop into controlled feature engineering in `src/agent_loop/features.py`, focusing on features that distinguish near-zero and negative-growth periods more clearly while leaving the frozen split and evaluation code untouched.
