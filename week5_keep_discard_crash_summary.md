# Week 5 Keep / Discard / Crash Summary

This summary accounts for the 31 formal Week 4 experiments only. Repeated
verification rows and final-eval sync rows recorded in
`experiments/experiment_detail_log.tsv` are documented for reproducibility, but
they are not counted as separate formal experiments.

## Totals

- Formal experiments: `31`
- Kept in some form: `12`
- Discarded: `17`
- Reference/control runs: `2`
- Formal crashes logged: `0`

For counting purposes, "kept in some form" includes `Keep`,
`Keep for synthesis`, and `Keep as challenger`.

## Retained / Kept

Kept runs:

- Run 2: `release_timing_family`
- Run 4: `negative_regime_family`
- Run 5: `release_plus_regime_combo`
- Run 8: `release_plus_momentum_family`
- Run 10: `release_plus_regime_combo + huber_eps_1_25`
- Run 16: `ratio_family + huber_eps_1_25`
- Run 21: `ratio_family + blend_huber125_extra400l4_w62`
- Run 24: `ratio_family + blend_huber125_extra400l4_w58`
- Run 27: `ratio_family + huber_eps_1_22`
- Run 28: `ratio_family + huber_eps_1_20`
- Run 29: `ratio_family + blend_huber125_extra400l4_w70`
- Run 30: `ratio_family + blend_huber125_extra400l6_w65`

Current retained model after the full Week 4 generalization check:

- `search_week4_ratio_family_huber_eps_1_25_v1`
- Formal anchor run: Run 16
- Reference restoration run: Run 26

## Discarded

Discarded runs:

- Runs 3, 6, 7, 9
- Runs 11, 12, 13, 14, 15
- Runs 17, 18, 19, 20
- Runs 22, 23, 25, 31

Why they were discarded:

- some feature families produced little or no RMSE gain
- some tuning variants improved MAE or MAPE but not the primary RMSE objective
- several ensembles improved validation RMSE but still lost on final test
  generalization relative to the retained ratio-family Huber anchor

## Reference / Control

Reference runs:

- Run 1: `control_week3_features`
- Run 26: `ratio_family + huber_eps_1_25` control rerun

These runs were kept to anchor comparisons, not to introduce a new challenger.

## Crash Result

Crash count for the formal Week 4 experiment set: `0`.

I did not find any formal Week 4 run logged as a crash or failed execution in:

- `week4_experiment_result_matrix.md`
- `week4_controlled_experiment_set.md`
- `week4_failure_analysis_memo.md`
- `experiments/experiment_detail_log.tsv`
