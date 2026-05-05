# Week 4 Failure Analysis Memo

## Controlled Experiment Summary

Week 4 kept the Week 3 Huber pipeline fixed and changed only the feature
surface. The initial five-run controlled set showed that release-window
indicators were the strongest isolated improvement, negative-regime indicators
gave a smaller standalone lift, and the concert-window flags were neutral. A
second four-run extension tested momentum-gap features, spike flags, and two
breakout-oriented combinations. None of the extension runs beat the earlier
`release_plus_regime_combo`, which remains the retained Week 4 model with
validation RMSE `1,328,169.54`, an improvement of `23,302.57` listeners over
the control.

## Dominant Failure Mode

The dominant failure mode is still **breakout underprediction**. Even after the
Week 4 improvement, rare very large positive surges remain the biggest RMSE
driver because the model often stays near zero or only modestly positive during
extreme jumps. In the retained Week 4 model, breakout-underprediction rows made
up `177` of the validation rows with absolute error at least `750,000`, but
they accounted for about `58.6%` of the squared error inside that high-error
slice. The clearest example is `j-hope` from `2025-10-20` through
`2025-10-24`, where actual growth ranged from about `6.28M` to `6.91M` while
the model predicted roughly `-301k` to `+236k`.

The extra experiments sharpened that conclusion. Momentum-gap features and
spike flags improved Spearman more than RMSE, which suggests the model can
better rank likely breakout rows than it can size the breakout magnitude. That
is why `release_plus_momentum_family` became a strong challenger on Spearman
(`0.465000`) without displacing the release-plus-regime winner on RMSE.

## Error Taxonomy

Threshold used for the taxonomy below:
validation rows with absolute error at least `750,000` listeners.

| Category | Breakdown | Week 4 Pattern |
|---|---|---|
| `Breakout underprediction` | Actual growth is very large and positive, but prediction stays near zero or modestly positive. | `177` rows; highest-impact category by far. |
| `Negative-regime overprediction` | Actual growth is negative or flat, but prediction is too positive. | `102` rows; broad recurring secondary failure mode. |
| `Release-window timing miss` | Rows near a recent or upcoming release still receive inaccurate predictions. | `76` rows; a narrower but still meaningful subtype. |
| `Medium-scale calibration error` | Mid-range moves are directionally reasonable or partially correct but badly sized. | `524` rows; most common category by count among large misses, but lower per-row impact than breakout misses. |

Representative examples:

- `Breakout underprediction`:
  `j-hope` on `2025-10-23` had actual growth `6,909,003` and prediction
  `48,124`.
- `Negative-regime overprediction`:
  `Stray Kids` on `2025-11-27` had actual growth `-383,493` and prediction
  `1,691,360`.
- `Release-window timing miss`:
  `Hearts2Hearts` on `2025-10-19` had actual growth `614,185`, prediction
  `3,536,276`, and `1` day until the next release.
- `Medium-scale calibration error`:
  `ROSÉ` on `2025-11-01` had actual growth `-4,325,606` and prediction
  `-811,257`.

## Next-Step Recommendation

The next iteration should target the breakout problem directly. The current Week
4 feature gains show that event timing matters, but timing flags alone do not
capture **release magnitude** or **artist-specific burst potential**. The extra
momentum and spike experiments suggest the model already sees some of the right
ordering signal, but it still compresses large positive outcomes too hard. The
most useful next step is therefore to engineer features that quantify burst
size, not just burst presence, then combine those with release-window signals.
That should directly target the main reason the retained model still falls back
toward conservative predictions during large surges, while the negative-regime
indicators can continue to guard against overprediction in flat or declining
periods.
