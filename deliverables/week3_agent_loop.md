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
- The original Week 3 loop exposed test metrics on every run; the corrected workflow now treats `python3 src/run.py` as search-only and reserves `python3 src/run.py --final-eval` for explicit final test evaluation.

## Dry Experiments

| # | Timestamp | Model | Validation RMSE | Validation MAE | Spearman | Decision |
|---|---|---|---:|---:|---:|---|
| 1 | `2026-04-27T15:34:13` | `search_huber_v1` | `1,422,490.72` | `940,201.06` | `0.385037` | **KEEP** |
| 2 | `2026-04-27T15:34:46` | `search_random_forest_dry_v1` | `1,723,695.41` | `1,179,621.71` | `0.298738` | Discard |
| 3 | `2026-04-27T15:35:29` | `search_hgb_dry_v1` | `1,545,233.53` | `1,038,507.09` | `0.390962` | Discard |
| 4 | `2026-04-27T15:35:55` | `search_huber_robust_dry_v1` | `1,424,619.16` | `915,336.61` | `0.297139` | Discard |
| 5 | `2026-04-30T17:21:51` | `search_huber_log_scale_cols_v1` | `1,351,472.11` | `897,593.18` | `0.424909` | **KEEP** |
| 6 | `2026-04-30T17:22:47` | `search_huber_quantile_normal_v1` | `1,416,420.92` | `937,177.76` | `0.389983` | Discard |
| 7 | `2026-04-30T17:23:14` | `search_huber_eps_1_1_v1` | `1,417,398.87` | `920,793.98` | `0.395916` | Discard |

### Experiment Notes

1. `HuberRegressor` with `StandardScaler()` was the first model to beat all three comparison points that mattered for Week 3:
   - it improved over `search_ridge_start_v1`
   - it beat the frozen `ridge_baseline`
   - it also beat the strong `zero_growth_baseline`

2. The random forest improved over the original ridge start but failed to beat the kept Huber run, so it was reverted.

3. The histogram gradient boosting model posted a decent RMSE and slightly higher Spearman than the kept Huber run, but the Week 3 decision rule was RMSE only, so it was still discarded.

4. The `RobustScaler()` Huber variant came very close on RMSE and improved MAE, but it did not beat the standard-scaled Huber model on the official optimization metric.

5. The log-scaled Huber pipeline improved the kept RMSE materially by shrinking very large positive feature scales before fitting Huber. It became the new best run and the new retained model.

6. The quantile-normalized Huber pipeline was still stronger than the old `search_huber_v1` baseline, but it was clearly worse than the new log-scaled Huber winner on RMSE, so it was discarded.

7. Tightening the Huber loss with `epsilon=1.1` improved on the original standard Huber baseline but still failed to beat the log-scaled Huber winner, so it was discarded.

## Final Retained Model

Retained model after the dry loop:

- `search_huber_log_scale_cols_v1`
- Pipeline:
  - `ColumnTransformer`
  - `log1p` + `StandardScaler()` on large positive scale columns
  - median imputation + `StandardScaler()` on the remaining columns
  - `HuberRegressor(max_iter=500)`

Final synced run at `2026-04-30T17:23:50`:

- Validation RMSE: `1,351,472.11`
- Validation MAE: `897,593.18`
- Validation MAPE: `7.656134`
- Validation Spearman: `0.424909`
- Test RMSE: `1,997,095.07`

Relative to the earlier kept `search_huber_v1`, this reduced validation RMSE by about
`71,018.62` listeners.

## Hidden-Test Fix

The Week 3 version of the loop leaked test metrics during normal search runs because
the runner printed and logged test results on every iteration. The corrected
workflow separates the two modes:

- `python3 src/run.py`
  - search mode
  - validation metrics only
  - no agent test rows added to the experiment log
- `python3 src/run.py --final-eval`
  - explicit final evaluation mode
  - validation plus test metrics
  - test rows appended only in this mode

The additional Experiments 5-7 followed this corrected workflow:

- Experiments 6 and 7 added validation rows only
- the retained Experiment 5 received one explicit final-eval test row after selection

## Main Blocker

The biggest remaining blocker is still regime shift across time. The train period has a much more positive target mean than the validation period, so the model needs to stay conservative when late-period growth compresses back toward zero or negative values. Robust regression helped, but Week 3 remained model-only and did not change the feature set.

## Next Step

Week 4 should expand the loop into controlled feature engineering in `src/agent_loop/features.py`, focusing on features that distinguish near-zero and negative-growth periods more clearly while leaving the frozen split and evaluation code untouched.
