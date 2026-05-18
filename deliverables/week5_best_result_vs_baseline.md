# Week 5 Best Result vs. Baseline

The official baseline for course reporting in this repository is
`ridge_baseline`. The comparison baselines `zero_growth_baseline` and
`previous_30d_growth_baseline` remain useful diagnostics, but they do not
replace the official baseline policy.

## Direct Comparison

Current retained best generalizing model:

- `search_week4_ratio_family_huber_eps_1_25_v1`

Official baseline:

- `ridge_baseline`

Validation comparison:

| Model | Validation RMSE | Validation MAE | Validation MAPE | Validation Spearman |
|---|---:|---:|---:|---:|
| `ridge_baseline` | `1,858,878.27` | `1,310,621.61` | `14.634026` | `0.150736` |
| `search_week4_ratio_family_huber_eps_1_25_v1` | `1,324,378.94` | `859,645.95` | `5.184773` | `0.457998` |

Observed gain over the official baseline:

- RMSE improved by `534,499.33` listeners, about `28.75%`
- MAE improved by `450,975.65` listeners, about `34.41%`
- MAPE improved by `9.449253`, about `64.57%`
- Spearman improved by `0.307262`

## Final-Eval Status

Stored final test metrics are available for the retained Week 4 model:

| Model | Test RMSE | Test MAE | Test MAPE | Test Spearman |
|---|---:|---:|---:|---:|
| `search_week4_ratio_family_huber_eps_1_25_v1` | `2,003,204.16` | `1,031,678.96` | `3.550610` | `0.373985` |

The current repository outputs do not include a matching final test row for
`ridge_baseline`, so the clean like-for-like baseline comparison available in
the stored artifacts is the validation comparison above.

## Retained Best vs. Historical Validation-Only Best

This project now distinguishes between:

- the current retained best generalizing model:
  `search_week4_ratio_family_huber_eps_1_25_v1`
- the historical best validation-only model:
  `search_week4_ratio_family_blend_huber125_extra400l4_w58_v1`

Why that distinction matters:

- the historical best validation-only run reached the lowest validation RMSE:
  `1,248,417.77`
- its stored final test RMSE was worse at `2,034,565.17`
- its stored test Spearman was also worse at `0.285365`

Relative to that validation-only winner, the retained model finished with:

- `31,361.01` lower test RMSE
- `0.088620` higher test Spearman

## Bottom Line

Yes, the current retained best clearly beats the starting official baseline.
The strongest trustworthy result in the stored Week 4 evidence is not the
lowest validation-only RMSE model; it is the simpler ratio-family Huber model
that held up better under final-eval generalization.
