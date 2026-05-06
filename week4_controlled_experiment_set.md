# Week 4 Controlled Experiment Set

## Goal

Advance the listener-growth repo into a logged Week 4 AutoResearch loop that
keeps the evaluation contract frozen while reducing validation error and
explicitly checking whether stronger models actually generalize.

## What Stayed Constant

- frozen split logic in `src/eval/*`
- frozen dataset build in `src/pipeline/prepare.py`
- frozen wrapper in `src/pipeline/build_features.py`
- frozen runner in `src/run.py`
- same target:
  validation RMSE on `listener_growth_30d_abs`
- same baseline comparison rows written by the frozen runner
- same metrics log:
  `experiments/experiment_log.tsv`

Every formal run was executed through `python3 src/run.py`. Detailed
reproducibility metadata for each agent run lives in
`experiments/experiment_detail_log.tsv`, including the model summary,
hyperparameters, changed feature engineering, and keep/discard rationale.

## Search Batches

### Batch 1: Controlled feature-family experiments

1. `control_week3_features`
2. `release_timing_family`
3. `concert_timing_family`
4. `negative_regime_family`
5. `release_plus_regime_combo`

Outcome:

- `release_plus_regime_combo` became the best feature-only result at
  validation RMSE `1,328,169.54`.

### Batch 2: Additional feature challengers

6. `momentum_gap_family`
7. `spike_flag_family`
8. `release_plus_momentum_family`
9. `breakout_full_combo`

Outcome:

- `release_plus_momentum_family` became the best secondary feature challenger
  at validation RMSE `1,331,647.51`, but it did not beat
  `release_plus_regime_combo`.

### Batch 3: Huber epsilon tuning on the retained feature set

10. `release_plus_regime_combo + huber_eps_1_25`
11. `release_plus_regime_combo + huber_eps_1_30`
12. `release_plus_regime_combo + huber_eps_1_35`
13. `release_plus_momentum_family + huber_eps_1_30`
14. `release_plus_regime_combo + huber_eps_1_15`
15. `release_plus_regime_combo + huber_eps_1_20`

Outcome:

- `huber_eps_1_25` on `release_plus_regime_combo` became the best tuned model
  at validation RMSE `1,326,596.55`.

### Batch 4: Ratio-family breakout-size features

16. `ratio_family + huber_eps_1_25`
17. `release_plus_regime_combo + huber_eps_1_22`
18. `ratio_family + huber_eps_1_22`
19. `ratio_family + huber_eps_1_20`
20. `ratio_family + huber_eps_1_18`

Outcome:

- `ratio_family + huber_eps_1_25` became the best simple model at validation
  RMSE `1,324,378.94`.
- Nearby lower-epsilon ratio runs improved MAE and MAPE, but they did not
  produce a clear RMSE win.

### Batch 5: Stronger ensemble-model challengers

21. `ratio_family + blend_huber125_extra400l4_w62`
22. `ratio_family + blend_huber125_extra400l4_w65`
23. `ratio_family + blend_huber125_extra400_w65`
24. `ratio_family + blend_huber125_extra400l4_w58`
25. `ratio_family + blend_huber125_extra400l4_w60`

Outcome:

- Weighted Huber-plus-ExtraTrees blends produced the strongest validation
  gains of the search.
- `blend_huber125_extra400l4_w58` reached the historical best validation RMSE
  `1,248,417.77`.
- That model was not retained after explicit final-eval checking because its
  test RMSE and Spearman were weaker than the simpler ratio-family Huber
  baseline.

### Batch 6: Generalization-focused conservative follow-up

26. `ratio_family + huber_eps_1_25` control rerun
27. `ratio_family + huber_eps_1_22`
28. `ratio_family + huber_eps_1_20`
29. `ratio_family + blend_huber125_extra400l4_w70`
30. `ratio_family + blend_huber125_extra400l6_w65`
31. `ratio_family + blend_huber125_extra400l6_w70`

Outcome:

- The control rerun reproduced the anchor exactly at validation RMSE
  `1,324,378.94`.
- The simple Huber challengers at `epsilon=1.22` and `epsilon=1.20` stayed
  within the `10,000` RMSE tie band and improved MAE/MAPE, so they remained
  acceptable simple-model challengers.
- Two conservative ensembles cleared the validation guardrails:
  `blend_huber125_extra400l4_w70` at `1,255,522.95` RMSE and
  `blend_huber125_extra400l6_w65` at `1,252,146.77` RMSE.
- The strongest conservative ensemble,
  `blend_huber125_extra400l6_w65`, still posted weaker final test RMSE
  `2,019,078.49` and weaker test Spearman `0.322881` than the ratio-family
  Huber anchor, so it was not retained.

## Retained Week 4 Configuration

Retained model:
`search_week4_ratio_family_huber_eps_1_25_v1`

Why it stayed retained:

- it is the generalization anchor under the updated Week 4 policy
- stronger ensembles improved validation RMSE but still failed to beat the
  anchor on final test RMSE and Spearman

Validation metrics:

- RMSE: `1,324,378.94`
- MAE: `859,645.95`
- MAPE: `5.184773`
- Spearman: `0.457998`

Final explicit test evaluation:

- Test RMSE: `2,003,204.16`
- Test MAE: `1,031,678.96`
- Test MAPE: `3.550610`
- Test Spearman: `0.373985`

Historical best validation-only run:
`search_week4_ratio_family_blend_huber125_extra400l4_w58_v1`

- Validation RMSE: `1,248,417.77`
- Test RMSE: `2,034,565.17`
- Status: historical best validation run, not retained

## Runtime Check

The new conservative batch completed locally in roughly `5-8` seconds per run,
well inside the `under 60 seconds` course constraint.

The summary matrix and plot now track the 31 formal Week 4 experiments.
Repeated validation rows produced by final-eval syncs or verification reruns
remain documented in `experiment_detail_log.tsv` without being counted as new
formal experiments.
