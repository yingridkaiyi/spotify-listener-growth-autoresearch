# Week 4 Experiment-Result Matrix

| Run | Experiment Name | Control Condition | Variable Changed | Hypothesis | Validation RMSE | Validation MAE | Validation MAPE | Validation Spearman | Delta RMSE vs Control | Keep/Discard Decision | Notes |
|---:|---|---|---|---|---:|---:|---:|---:|---:|---|---|
| 1 | `control_week3_features` | Week 3 retained feature set | none | Reproduce the Week 3 benchmark before changing the feature surface. | 1,351,472.11 | 897,593.18 | 7.656134 | 0.424909 | 0.00 | Reference | Matched the retained Week 3 benchmark exactly. |
| 2 | `release_timing_family` | Same estimator, split, and dataset as control | Added release-window flags from `days_until_next_release` and `days_since_last_release` | Better release timing indicators should reduce the largest surge misses. | 1,334,444.15 | 870,481.28 | 6.524334 | 0.452583 | -17,027.96 | Keep | Strongest isolated improvement. |
| 3 | `concert_timing_family` | Same estimator, split, and dataset as control | Added upcoming-concert flags from `days_until_next_concert` | Short-horizon concert timing should capture medium-scale lift around event windows. | 1,351,472.11 | 897,593.18 | 7.656134 | 0.424909 | 0.00 | Discard | No measurable RMSE change. |
| 4 | `negative_regime_family` | Same estimator, split, and dataset as control | Added negative and flat regime indicators from prior listener changes | Explicit regime flags should reduce overprediction in flat or negative periods. | 1,347,488.14 | 896,915.01 | 7.306693 | 0.433551 | -3,983.97 | Keep for synthesis | Small RMSE gain, enough to justify the follow-up combination. |
| 5 | `release_plus_regime_combo` | Same estimator, split, and dataset as control | Combined release-window and negative-regime feature families | The two strongest Week 4 signals should complement each other better than either family alone. | 1,328,169.54 | 875,849.14 | 6.016124 | 0.455865 | -23,302.57 | Keep | Best overall RMSE and retained Week 4 feature set. |
| 6 | `momentum_gap_family` | Same estimator, split, and dataset as control | Added short-vs-long change and growth-rate gap features | Acceleration relative to the 30-day trend should help breakout calibration. | 1,349,804.53 | 897,326.07 | 7.912147 | 0.439875 | -1,667.58 | Discard | Helped Spearman more than RMSE. |
| 7 | `spike_flag_family` | Same estimator, split, and dataset as control | Added large-move and high-growth-rate flags | Explicit spike markers should help the fixed linear model react to emerging breakouts. | 1,350,523.48 | 896,105.79 | 7.963931 | 0.446326 | -948.63 | Discard | Slight ranking gain, weak RMSE gain. |
| 8 | `release_plus_momentum_family` | Same estimator, split, and dataset as control | Combined release-window indicators with momentum-gap features | Event timing plus local trend shape should outperform either signal alone. | 1,331,647.51 | 872,716.86 | 6.811662 | 0.465000 | -19,824.60 | Keep as challenger | Second-best RMSE and strongest Spearman, but still worse than the retained best. |
| 9 | `breakout_full_combo` | Same estimator, split, and dataset as control | Combined release, regime, momentum, spike, and interaction features | A larger breakout-oriented feature surface should reduce rare surge misses the most. | 1,349,521.80 | 889,148.61 | 6.712513 | 0.466598 | -1,950.31 | Discard | Added complexity improved ranking but not RMSE. |

## Final Selection

The retained Week 4 model remains
`search_huber_week4_release_plus_regime_combo_v1`.

Final explicit test evaluation from the resynced `python3 src/run.py --final-eval`:

- test RMSE: `2,001,850.16`
- test MAE: `1,042,305.42`
- test MAPE: `4.235544`
- test Spearman: `0.365231`
