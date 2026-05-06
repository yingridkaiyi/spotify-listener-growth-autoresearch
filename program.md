# Spotify Listener Growth AutoResearch Agent Instructions

## Objective

Minimize **validation RMSE** on `listener_growth_30d_abs` while preferring
changes that generalize, not just changes that win a single validation split.

Secondary tie-breakers:

- lower validation **MAE**
- lower validation **MAPE**

For this repo, “ratio error” means **MAPE**, because that is the ratio-style
metric already logged by `src/run.py`.

## Decision Rule

Use an **RMSE-first with generalization guardrails** keep/discard rule:

1. The active default is the generalization anchor:
   `search_week4_ratio_family_huber_eps_1_25_v1`.
2. For any simple Huber-family challenger:
   - keep it if validation RMSE improves by a clear amount over the anchor
   - if validation RMSE is within `10,000`, prefer the lower-MAE and
     lower-MAPE run
3. For any ensemble or tree-assisted challenger:
   - keep it only if validation RMSE improves by at least `10,000` over the
     anchor
   - and validation MAE is not worse by more than `5,000`
   - and validation MAPE is not worse by more than `0.10`
4. If a complex challenger is within `10,000` RMSE of the simpler Huber
   anchor, prefer the simpler Huber model.
5. Treat Spearman as a diagnostic metric, not the winner-selection metric.
6. Treat the earlier best-validation ensemble as a warning example, not the
   default target.

## Rules

1. This is a broader **AutoResearch search loop** across both model space and
   feature space.
2. `src/eval/*`, `src/pipeline/prepare.py`, `src/pipeline/build_features.py`,
   and `src/run.py` are **FROZEN**.
3. Do not modify split logic, evaluation metrics, or baseline policy.
4. `src/agent_loop/features.py` and `src/agent_loop/model.py` are the editable
   search surface.
5. `build_estimator()` must return an sklearn-compatible estimator.
6. Training + evaluation must complete in **under 60 seconds** on CPU.
7. Do not access or simulate any hidden test set during search.
8. Do not add new dependencies or change the evaluation contract.

## Workflow

```text
1. Start from the active generalization anchor model and feature set.
2. Propose one small hypothesis-driven change.
3. Change either:
   - one model or preprocessing component, or
   - one feature family, or
   - one small combination if it is explicitly justified.
4. Run: python3 src/run.py
5. Immediately run:
   python3 src/log_experiment_details.py --hypothesis ... --changed-components ... --why ... --decision ... --decision-reason ...
6. Record validation RMSE, MAE, MAPE, and Spearman.
7. Compare the run against the Huber anchor using the explicit guardrails
   above.
8. Keep the change only if it wins under those guardrails.
9. Prefer simpler Huber-family updates when a more complex model wins only by
   a small validation margin.
10. After selecting the best validation run, run: python3 src/run.py --final-eval
11. Immediately run: python3 src/log_experiment_details.py --sync-final-eval
```

Every run description should name:

- the hypothesis
- what changed
- why that change should help breakout underprediction or
  negative-regime overprediction

## Search Surface

- Frozen files:
  - `src/eval/*`
  - `src/pipeline/prepare.py`
  - `src/pipeline/build_features.py`
  - `src/run.py`
- Mutable files:
  - `src/agent_loop/features.py`
  - `src/agent_loop/model.py`
- Canonical dataset:
  - `data/processed/master_growth_dataset.csv`
- Search command:
  - `python3 src/run.py`
- Final evaluation command:
  - `python3 src/run.py --final-eval`
- Current generalization anchor:
  - `search_week4_ratio_family_huber_eps_1_25_v1`
- Historical best validation-only run:
  - `search_week4_ratio_family_blend_huber125_extra400l4_w58_v1`

Model changes are allowed in:

- estimator family
- preprocessing layout
- feature grouping
- robust loss settings
- target-transform strategy, as long as it stays within the sklearn-compatible
  estimator contract and does not change frozen evaluation code

## Ideas To Explore

High-priority directions:

- Robust or heteroskedastic-friendly linear models:
  - `HuberRegressor`
  - `ElasticNet`
  - `QuantileRegressor` if runtime stays acceptable
- Better preprocessing:
  - log-scaling
  - clipped scaling
  - robust scaling
  - selective transforms by feature family
- Target handling:
  - target transforms
  - weighted objectives that reduce domination by rare extreme surges while
    still protecting RMSE
- Feature engineering:
  - release-window indicators
  - regime flags
  - momentum-gap features
  - breakout-size proxies
  - interactions between release timing and recent trend
- Calibration-focused changes:
  - features that estimate burst magnitude, not just burst timing

Current failure modes to target:

- **breakout underprediction**
  - rare very large positive surges are still the biggest RMSE driver
- **negative-regime overprediction**
  - flat or negative periods can still be predicted too positively

Current generalization lesson:

- the strongest ensemble improved validation RMSE sharply, but its final test
  RMSE and Spearman were weaker than the simpler ratio-family Huber anchor
- use conservative ensembles only when they clear the explicit acceptance bar

## Logging Expectations

Use the existing runner and experiment log for every run.

Each experiment should be documented with:

- model or feature-set name
- model description
- model family and hyperparameters
- feature engineering used for that run, not the full unchanged feature list
- hypothesis
- changed components
- why the change should help
- keep or discard decision
- decision reason under the current guardrails
- validation RMSE
- validation MAE
- validation MAPE
- optional synced test metrics for the retained winner only

Use:

- `experiments/experiment_log.tsv` as the frozen metrics-only runner log
- `experiments/experiment_detail_log.tsv` as the canonical reproducibility log

Do not change `src/run.py` just to add extra logging fields. Use
`src/log_experiment_details.py` for metadata-rich logging instead.

## What Not To Do

- Do not chase Spearman alone.
- Do not add many unrelated feature families in one run.
- Do not keep a run just because MAE, MAPE, or Spearman improved if RMSE
  clearly got worse.
- Do not retain a complex model that fails the explicit RMSE, MAE, and MAPE
  guardrails against the Huber anchor.
- Do not hard-code validation information into the model.
- Do not edit generated logs or boards by hand.
- Do not reveal test metrics during normal search runs.
