# Week 4 Controlled Experiment Set

## Goal

Advance the Week 3 listener-growth model into a Week 4 **feature-engineering**
loop with clear variable isolation while keeping the evaluation contract fixed.

## What Stayed Constant

- frozen split logic in `src/eval/*`
- frozen dataset build in `src/pipeline/prepare.py`
- frozen wrapper in `src/pipeline/build_features.py`
- frozen runner in `src/run.py`
- same estimator architecture and hyperparameters in `src/agent_loop/model.py`
  - `ColumnTransformer`
  - log-scale preprocessing on the large positive columns
  - standard scaling on the remaining columns
  - `HuberRegressor(max_iter=500)`
- same optimization target:
  validation RMSE on `listener_growth_30d_abs`

Each Week 4 run changed only the active feature family in
`src/agent_loop/features.py`.

## Experiment Sequence

| Run | Feature Set | Variable Changed | Why It Is Controlled |
|---|---|---|---|
| 1 | `control_week3_features` | none | Reference run using the retained Week 3 feature surface only. |
| 2 | `release_timing_family` | added release-window indicators | Isolates whether extra release timing flags improve surge handling beyond the existing raw release timing columns already present in control. |
| 3 | `concert_timing_family` | added upcoming-concert indicators | Isolates whether short-horizon concert timing adds signal beyond the existing raw `days_until_next_concert` field. |
| 4 | `negative_regime_family` | added negative/flat regime indicators | Isolates whether explicit sign and flat-period flags reduce overprediction when growth compresses toward zero or negative values. |
| 5 | `release_plus_regime_combo` | combined the two strongest first-round families | Fixed synthesis run after the isolated experiments; not treated as a pure isolation claim. |
| 6 | `momentum_gap_family` | added short-vs-long trend gap features | Tests whether recent acceleration relative to the 30-day trend helps breakout calibration. |
| 7 | `spike_flag_family` | added large-move and high-growth-rate flags | Tests whether explicit spike markers help the fixed linear Huber model recognize breakout candidates. |
| 8 | `release_plus_momentum_family` | combined release-window indicators with momentum-gap features | Tests whether event timing plus local trend shape works better than either idea alone. |
| 9 | `breakout_full_combo` | combined release, regime, momentum, spike, and release-spike interaction features | Tests a larger breakout-oriented synthesis surface after the isolated and smaller combo runs. |

## Observed Outcome

- The control rerun matched the retained Week 3 benchmark exactly:
  validation RMSE `1,351,472.11`.
- The release-timing family was the strongest isolated improvement:
  validation RMSE `1,334,444.15`.
- The concert-timing family was neutral:
  validation RMSE `1,351,472.11`.
- The negative-regime family produced a small standalone gain:
  validation RMSE `1,347,488.14`.
- The combined release-plus-regime feature set was the best Week 4 result:
  validation RMSE `1,328,169.54`.
- The momentum-gap family improved ranking quality more than RMSE:
  validation RMSE `1,349,804.53`.
- The spike-flag family also improved Spearman more than RMSE:
  validation RMSE `1,350,523.48`.
- The release-plus-momentum family became the strongest follow-up challenger:
  validation RMSE `1,331,647.51`.
- The larger breakout-focused combo did **not** beat the retained best:
  validation RMSE `1,349,521.80`.

## Retained Week 4 Configuration

Retained feature set:
`release_plus_regime_combo`

Search-mode validation metrics:

- RMSE: `1,328,169.54`
- MAE: `875,849.14`
- MAPE: `6.016124`
- Spearman: `0.455865`

Final explicit test evaluation:

- Test RMSE: `2,001,850.16`
- Test MAE: `1,042,305.42`
- Test MAPE: `4.235544`
- Test Spearman: `0.365231`

## Logging And Runtime Check

- Every search run was executed through `python3 src/run.py`, so each experiment
  appended one validation row for the active feature set plus the frozen
  baseline rows.
- After the extra exploration, `python3 src/run.py --final-eval` was rerun on
  the retained best feature set to resync `evaluation_board.md` and
  `experiments/best_model_artifact.pkl` with the chosen Week 4 winner.
- Each run completed locally in roughly `5-7` seconds, which stayed well within
  the `under 60 seconds` course constraint.
