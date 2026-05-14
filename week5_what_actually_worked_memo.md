# Week 5 "What Actually Worked" Memo

The changes that produced real, interpretable gains were not the flashy ones.
The reliable improvements came from making the linear Huber model see timing,
regime, and scale more clearly.

Release-window features were the first obvious win. They improved the model's
ability to react to recent and upcoming releases, and they were the strongest
isolated feature-family gain in the controlled Week 4 search.

Negative and near-flat regime flags also helped. They gave the model a better
way to recognize periods where growth was weak or reversing, which reduced some
of the broad overprediction behavior seen earlier in the project.

The best simple-model jump came from the ratio-family features. Scaling recent
listener change by current audience size gave the model a more useful proxy for
breakout magnitude than raw change alone. That is what moved the retained
anchor to `search_week4_ratio_family_huber_eps_1_25_v1`.

Tighter Huber tuning mattered, but only after the feature surface improved.
Lowering `epsilon` on the stronger feature families produced measurable gains,
and `epsilon=1.25` was the best clean RMSE improvement before the search moved
into ensemble challengers.

What did not earn trust was the ensemble story. The Huber-plus-ExtraTrees
blends absolutely lowered validation RMSE, and the 58/42 blend became the
historical best validation-only run. But the final test results were worse than
the simpler ratio-family Huber anchor, which means the extra complexity found a
signal that looked real on validation and then failed to generalize cleanly.

The blunt conclusion is this: interpretable feature engineering plus robust
linear modeling actually worked. More nonlinear complexity was interesting, and
it helped validation metrics, but it was not trustworthy enough to keep.
