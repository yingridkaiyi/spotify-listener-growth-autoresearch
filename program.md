# Spotify Listener Growth AutoResearch Agent Instructions

## Locked Week 6 Direction

The final project direction is now locked around:

- model: `search_week4_ratio_release_interaction_family_huber_eps_1_25_v1`
- feature set: `ratio_release_interaction_family`
- model variant: `huber_eps_1_25`
- estimator: robust linear `HuberRegressor`

Final story:

> This project shows that Spotify 30-day listener-growth prediction improves
> most defensibly when the AutoResearch loop adds targeted event-aware feature
> engineering to a robust linear model. The locked final model keeps the simple
> Huber approach but adds one narrow recent-release by 7-day listener-ratio
> interaction, improving validation RMSE, MAE, and MAPE without returning to
> high-variance ensemble complexity.

Week 6 is the convergence point. No broad search expansion, metric changes, or
new model-family exploration should be performed after this point.

## Objective

Minimize **validation RMSE** on `listener_growth_30d_abs` while preferring
changes that generalize, not just changes that win a single validation split.

Secondary tie-breakers:

- lower validation **MAE**
- lower validation **MAPE**

For this repo, "ratio error" means **MAPE**, because that is the ratio-style
metric already logged by `src/run.py`.

## Current Retained Result

Current retained model:

- `search_week4_ratio_release_interaction_family_huber_eps_1_25_v1`

Validation metrics:

- RMSE: `1,321,827.56`
- MAE: `855,576.66`
- MAPE: `4.773756`
- Spearman: `0.451507`

Final-eval metrics:

- test RMSE: `2,000,778.69`
- test MAE: `1,033,663.07`
- test MAPE: `3.291145`
- test Spearman: `0.366157`

The retained model improves over the previous ratio-family Huber anchor on
validation RMSE, MAE, and MAPE. It also slightly improves final test RMSE and
test MAPE, while giving up a small amount of test Spearman. Spearman remains a
diagnostic metric, not the winner-selection metric.

## Decision Rule

Use an **RMSE-first with generalization guardrails** keep/discard rule:

1. The locked Week 6 default is the retained Huber release-interaction model:
   `search_week4_ratio_release_interaction_family_huber_eps_1_25_v1`.
2. Do not run additional exploratory challengers unless needed for
   reproducibility repair.
3. If a reproducibility repair run is required, it must use the same frozen
   split, target, evaluation metrics, and baseline policy.
4. Do not keep a change that improves one diagnostic metric while worsening the
   main Week 6 story.
5. Treat Spearman as a diagnostic metric, not the winner-selection metric.
6. Treat the earlier best-validation ensemble as a warning example, not the
   final target.

## Rules

1. `src/eval/*`, `src/pipeline/prepare.py`, `src/pipeline/build_features.py`,
   and `src/run.py` are **FROZEN**.
2. Do not modify split logic, evaluation metrics, target definition, or
   baseline policy.
3. Do not access or simulate any hidden test set during normal search.
4. Do not add new dependencies or change the evaluation contract.
5. Training + evaluation must complete in **under 60 seconds** on CPU.
6. Remaining work is final-report and presentation work, not broad search.

## Locked Search Surface

- Frozen files:
  - `src/eval/*`
  - `src/pipeline/prepare.py`
  - `src/pipeline/build_features.py`
  - `src/run.py`
- Current mutable implementation files:
  - `src/agent_loop/features.py`
  - `src/agent_loop/model.py`
- Canonical dataset:
  - `data/processed/master_growth_dataset.csv`
- Reproducibility command:
  - `python3 src/run.py`
- Final evaluation command, only for locked retained model verification:
  - `python3 src/run.py --final-eval`

## Dropped Directions

These directions are explicitly out of scope after Week 6:

- broad Huber-plus-tree ensembles as the final model
- full breakout feature combinations
- concert timing as a retained signal
- ratio clipping or winsorization
- signed magnitude feature expansion
- smooth release recency or anticipation decay features
- additional broad model-family search
- changing the evaluation metric after seeing favorable results

## Evidence Summary

| Direction Tested | Representative Run | Validation RMSE | Validation MAE | Validation MAPE | Decision |
|---|---|---:|---:|---:|---|
| Official baseline | `ridge_baseline` | 1,858,878.27 | 1,310,621.61 | 14.634026 | Baseline |
| Week 3 control | `control_week3_features` | 1,351,472.11 | 897,593.18 | 7.656134 | Reference |
| Release timing | `release_timing_family` | 1,334,444.15 | 870,481.28 | 6.524334 | Useful signal |
| Ratio-family Huber | `search_week4_ratio_family_huber_eps_1_25_v1` | 1,324,378.94 | 859,645.95 | 5.184773 | Former anchor |
| Ratio clipping | `search_week4_ratio_winsor_family_huber_eps_1_25_v1` | 1,314,521.98 | 854,959.39 | 5.800234 | Drop |
| Signed magnitude | `search_week4_ratio_signed_magnitude_family_huber_eps_1_25_v1` | 1,322,625.09 | 860,122.63 | 5.313988 | Drop |
| Release decay | `search_week4_ratio_release_decay_family_huber_eps_1_25_v1` | 1,331,631.37 | 866,539.54 | 5.178617 | Drop |
| Narrow release interaction | `search_week4_ratio_release_interaction_family_huber_eps_1_25_v1` | 1,321,827.56 | 855,576.66 | 4.773756 | Final retained model |
| Validation-winning ensemble | `search_week4_ratio_family_blend_huber125_extra400l4_w58_v1` | 1,248,417.77 | 836,902.52 | 5.018270 | Drop as final |

## Remaining Workflow

```text
1. Keep the locked release-interaction Huber model as the default.
2. Run python3 src/run.py only for reproducibility checks.
3. Do not add new feature families, ensembles, dependencies, or metrics.
4. Use experiments/experiment_log.tsv and experiments/experiment_detail_log.tsv
   as the source of truth for final-report metrics.
5. Prepare final figures and slides from existing evidence.
6. Finish the final report by May 27, 2026.
```

## Logging Expectations

Use the existing runner and experiment log for any required verification run.

Each verification run should be documented with:

- model or feature-set name
- feature engineering used for that run
- validation RMSE
- validation MAE
- validation MAPE
- validation Spearman
- final-eval metrics only for the locked retained model

Use:

- `experiments/experiment_log.tsv` as the frozen metrics-only runner log
- `experiments/experiment_detail_log.tsv` as the canonical reproducibility log

Do not change `src/run.py` just to add extra logging fields. Use
`src/log_experiment_details.py` for metadata-rich logging instead.

## What Not To Do

- Do not chase Spearman alone.
- Do not add many unrelated feature families in one run.
- Do not keep broad complexity just because validation RMSE improves.
- Do not hard-code validation information into the model.
- Do not edit generated logs or boards by hand.
- Do not reveal or reuse test metrics during normal search.
- Do not reopen the search space after Week 6.
