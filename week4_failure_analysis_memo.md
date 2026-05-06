# Week 4 Failure Analysis Memo

## Controlled Experiment Summary

Week 4 began with a controlled feature-engineering loop, then expanded into a
logged AutoResearch search that still kept the evaluation contract frozen.
Release-window features and negative-regime flags were the first clear gains,
and audience-scaled ratio features produced the best simple-model result:
`search_week4_ratio_family_huber_eps_1_25_v1` at validation RMSE
`1,324,378.94`.

The search then tested stronger nonlinear models. The earlier 58/42
Huber-plus-ExtraTrees blend reached the historical best validation RMSE
`1,248,417.77`, which showed that nonlinear breakout correction is real.
However, its final test RMSE `2,034,565.17` and test Spearman `0.285365`
lagged the simpler ratio-family Huber anchor. A new conservative ensemble
batch repeated that pattern: the best follow-up ensemble,
`search_week4_ratio_family_blend_huber125_extra400l6_w65_v1`, improved
validation RMSE to `1,252,146.77` but still produced worse final test RMSE
`2,019,078.49` and worse test Spearman `0.322881` than the anchor.

Because Week 4 is now using explicit generalization guardrails, the retained
model is again `search_week4_ratio_family_huber_eps_1_25_v1`. The companion
file `experiments/experiment_detail_log.tsv` records the model description,
hyperparameters, changed feature engineering, and keep/discard reason for each
formal run.

## Dominant Failure Mode

The dominant failure mode is still `Breakout underprediction`. Rare very large
positive surges remain the biggest RMSE driver because even the stronger
models still often predict only modest growth on extreme jumps. The ensemble
experiments showed that tree-based nonlinear corrections can lower validation
error by reacting more strongly to these cases, but the final-eval results
show that those corrections are not yet generalizing reliably enough to
replace the simpler retained model.

## Error Taxonomy

| Category | Breakdown | Current Interpretation |
|---|---|---|
| `Breakout underprediction` | Actual growth is very large and positive, but prediction stays near zero or modestly positive. | Still the dominant RMSE driver. |
| `Negative-regime overprediction` | Actual growth is negative or flat, but prediction is too positive. | Still a broad recurring secondary pattern. |
| `Release-window timing miss` | Rows near a recent or upcoming release still receive inaccurate predictions. | Improved by the release-window features, but not eliminated. |
| `Medium-scale calibration error` | Mid-range moves are directionally reasonable but badly sized. | Less damaging than breakout misses, but still common. |

## Representative Findings

- Release-window features remain the most important feature-family
  improvement.
- Momentum and spike additions helped ranking more than RMSE.
- Tightening Huber loss improved MAE and MAPE, but did not produce a clear
  RMSE win over the retained `epsilon=1.25` ratio-family anchor.
- Ratio features based on recent listener change divided by current audience
  size were the first breakout-size proxy to clearly improve simple-model
  RMSE.
- The ensemble family revealed a useful nonlinear signal for breakout sizing,
  but both the historical best validation blend and the new conservative
  follow-up blends still weakened final test RMSE and Spearman relative to the
  anchor.

## Next-Step Recommendation

The next iteration should keep the retained `ratio_family` Huber model as the
search anchor and continue to treat ensembles as challengers rather than the
default. The most disciplined next step is to keep exploring conservative
ensembles and simple-model robustness before adding broader complexity:

- keep `ratio_family` fixed
- test one more layer of tree regularization or lower ensemble weight at a time
- continue engineering breakout-magnitude features for the simpler Huber model
- avoid broader model expansion until a nonlinear challenger beats the anchor
  on both validation and final-eval generalization behavior
