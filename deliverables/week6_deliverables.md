# Week 6 Deliverables: Scope-Locked Listener Growth AutoResearch

## 1. Revised Project Statement

This project builds an AutoResearch loop for predicting 30-day absolute
Spotify listener growth from artist metrics, release timing, concert timing,
and recent listener movement. The project has now converged on a targeted
feature-engineering result: robust linear Huber modeling becomes more
defensible when recent listener-ratio momentum is conditioned on recent release
context.

Final locked story:

> This project shows that Spotify 30-day listener-growth prediction improves
> most defensibly when the AutoResearch loop adds targeted event-aware feature
> engineering to a robust linear model. The locked final model keeps the simple
> Huber approach but adds one narrow recent-release by 7-day listener-ratio
> interaction, improving validation RMSE, MAE, and MAPE without returning to
> high-variance ensemble complexity.

The strongest final claim is deliberately narrow. I am not claiming that the
largest or most complex model is best. I am claiming that the most defensible
improvement came from a small, interpretable release-by-momentum interaction
inside the robust Huber model.

## 2. Updated Program / Agent Strategy

The locked final model is:

- `search_week4_ratio_release_interaction_family_huber_eps_1_25_v1`

The locked feature set is:

- `ratio_release_interaction_family`

The locked model variant is:

- `huber_eps_1_25`

The strategy is now convergence-focused:

1. Keep the frozen data split, target, metrics, and baseline policy unchanged.
2. Use validation RMSE as the primary metric.
3. Use validation MAE and MAPE as secondary tie-breakers.
4. Treat Spearman as diagnostic, not as the selection metric.
5. Prefer simple Huber-family feature calibration over broad nonlinear
   complexity.
6. Stop broad search after Week 6.

The retained model adds one narrow feature to the earlier ratio-family Huber
anchor:

- `release_last_30d_x_listener_change_prev_7d_ratio`

This interaction lets the linear model treat 7-day audience-scaled momentum
differently when the artist has had a release in the last 30 days. That is a
small enough change to keep the model interpretable, but specific enough to
address the main failure mode of under-sizing release-driven listener surges.

## 3. Ablation / Comparison Table

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

Final-eval comparison:

| Model | Test RMSE | Test MAE | Test MAPE | Test Spearman |
|---|---:|---:|---:|---:|
| Old ratio-family Huber | 2,003,204.16 | 1,031,678.96 | 3.550610 | 0.373985 |
| Locked release-interaction Huber | 2,000,778.69 | 1,033,663.07 | 3.291145 | 0.366157 |
| Validation-winning ensemble | 2,034,565.17 | 1,073,935.45 | 2.956260 | 0.285365 |

The narrow release-interaction model is retained because it improves the old
Huber anchor on validation RMSE, validation MAE, and validation MAPE. It also
slightly improves final test RMSE and test MAPE relative to the old Huber
anchor. The ensemble remains the best validation-RMSE run, but it is dropped as
the final model because its final test RMSE and Spearman were worse.

## 4. Dropped Directions

The following directions are officially abandoned for the final project:

- broad Huber-plus-tree ensembles as the final model
- full breakout feature combinations
- concert timing as a retained signal
- ratio clipping or winsorization
- signed magnitude feature expansion
- smooth release recency or anticipation decay features
- additional broad model-family search
- changing evaluation metrics after seeing favorable results

These were dropped because Week 6 is for narrowing the project, not reopening
the search space. The remaining story is stronger if it focuses on the one
targeted interaction that improved the robust Huber anchor without returning to
high-variance model complexity.

## 5. Locked Final Two-Week Plan

| Date | Committed Work |
|---|---|
| May 18-20, 2026 | Finish the Week 6 deliverable and update `program.md` to lock the release-interaction Huber direction. |
| May 21-23, 2026 | Run reproducibility checks only for the locked model. Do not add new feature families, ensembles, or metrics. |
| May 24-25, 2026 | Prepare final figures and tables: baseline comparison, ablation table, final-eval comparison, and dropped-directions slide. |
| May 26-27, 2026 | Complete the final report, polish the narrative, verify artifact paths and metrics, and treat the report as done by May 27. |
| After May 27, 2026 | Only presentation polish or submission packaging. No substantive model or search changes. |

## 6. Story-Lock Worksheet

My project now shows that:

> A robust Huber model with targeted release-aware ratio features gives the
> most defensible Spotify listener-growth prediction result.

The strongest evidence is:

> The locked release-interaction Huber improves validation RMSE from
> 1,324,378.94 to 1,321,827.56, validation MAE from 859,645.95 to 855,576.66,
> and validation MAPE from 5.184773 to 4.773756 compared with the prior
> ratio-family Huber anchor.

I am no longer doing:

> broad ensemble chasing, full breakout combinations, concert timing, ratio
> clipping, signed magnitude expansion, release decay features, or any new
> search direction after Week 6.

My final 2-week plan is:

> Finish the Week 6 lock, run only reproducibility checks, prepare final
> tables and figures, and complete the final report by May 27, 2026.

## 7. Lightning Round Answers

Current best direction:

> Lock the ratio + recent-release interaction Huber model.

Supporting evidence:

> It improves validation RMSE, MAE, and MAPE over the old ratio-family Huber
> anchor, while avoiding the final-eval weakness of the validation-winning
> ensemble.

What I am dropping:

> broad ensembles, full breakout combinations, concert timing, clipping,
> winsorization, signed magnitude expansion, release decay features, and any
> further broad search.

Only 2-3 things left:

> verify reproducibility, prepare final tables/figures, and write the final
> report by May 27.
