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

- Calibration-focused Huber improvements:
  - add simple prediction-shape features that help the retained Huber model
    correct breakout underprediction without moving to a high-variance ensemble
  - prefer changes that improve RMSE while preserving or improving MAPE
  - treat any RMSE gain under `10,000` as insufficient if MAPE gets worse

- Magnitude-aware regime features:
  - split recent movement into signed magnitude features, not only binary flags
  - examples:
    - `positive_change_prev_7d_abs`
    - `positive_change_prev_30d_abs`
    - `negative_change_prev_7d_abs`
    - `negative_change_prev_30d_abs`
  - hypothesis: the model needs to distinguish mild negative drift from large
    listener collapses to reduce negative-regime overprediction

- Smooth release-timing features:
  - replace or supplement hard release-window flags with decay-style timing
    features
  - examples:
    - `release_recency_decay = 1 / (1 + days_since_last_release)`
    - `release_anticipation_decay = 1 / (1 + days_until_next_release)`
  - hypothesis: release impact likely fades smoothly rather than changing only
    at 7-day or 30-day cutoffs

- Small release-by-momentum interactions:
  - avoid the full breakout interaction set unless smaller interactions fail
  - test one narrow interaction family at a time
  - examples:
    - `release_within_last_30d_flag * listener_change_prev_7d_ratio`
    - `release_in_next_30d_flag * listener_change_prev_7d_ratio`
    - `release_within_last_30d_flag * listener_growth_rate_prev_7d`
  - hypothesis: the ratio-family signal is most useful when release context
    confirms that recent movement is music-event driven

- Conservative target-shape experiments:
  - try `TransformedTargetRegressor` only if it stays sklearn-compatible and
    finishes under the runtime limit
  - candidate transform:
    - signed log target: `sign(y) * log1p(abs(y))`
  - hypothesis: compressing rare extreme surges may reduce validation overfit
    while still preserving direction and magnitude ordering
  - discard immediately if absolute-scale RMSE clearly worsens

- Conservative sample-weighting experiments:
  - test simple target-magnitude or regime-based weights only inside
    `src/agent_loop/model.py`
  - avoid complex per-row rules that look like validation memorization
  - hypothesis: modestly reducing domination by rare extreme surge rows may
    improve generalization without losing the breakout signal entirely

Lower-priority directions:

- Additional Huber epsilon sweeps:
  - only revisit if paired with a clearly justified feature change
  - prior sweeps showed small MAE/MAPE gains but limited RMSE gains

- Additional Huber-plus-tree ensembles:
  - treat as suspicious unless they clear the complex-model guardrails by a
    wide margin
  - prior ensembles improved validation RMSE but generalized worse on final
    evaluation than the simpler ratio-family Huber anchor

- Ratio clipping or winsorization:
  - do not prioritize broad clipping of the existing ratio features
  - recent probes improved RMSE slightly but worsened MAPE, failing the
    simple-Huber tie-break guardrail

Current failure modes to target:

- **breakout underprediction**
  - rare very large positive surges remain the biggest RMSE driver
  - prioritize features that estimate burst magnitude only when release or
    momentum context supports it

- **negative-regime overprediction**
  - flat or negative periods can still be predicted too positively
  - prioritize signed magnitude and decay features that separate mild drift from
    large declines

Current generalization lesson:

- the strongest ensembles improved validation RMSE sharply, but their final
  test RMSE and Spearman were weaker than the simpler ratio-family Huber anchor
- use conservative ensembles only when they clear the explicit acceptance bar
- prefer simple Huber-family models with better feature calibration over
  additional nonlinear complexity

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
