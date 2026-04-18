# Week 1 Project Charter

## Project Title

AutoResearch for K-pop Spotify Listener Growth Prediction

## Problem

K-pop artist demand changes quickly because of releases, concerts, playlist exposure,
and cross-platform attention. The project goal is to predict how much an artist's
Spotify monthly listeners will increase over the next 30 days using only
information known on the observation date.

## Research Question

Can we predict 30-day Spotify monthly listener growth for K-pop artists using
artist popularity, platform demand signals, concert activity, and release activity
available on the observation date?

## Success Criterion

Primary metric:

- validation RMSE on `listener_growth_30d_abs`

Initial performance goal:

- beat a naive baseline such as `next_30d_growth = previous_30d_growth`

Secondary diagnostic metrics:

- MAE
- Spearman rank correlation
- error by artist scale bucket
- optional RMSE on `listener_growth_30d_pct`

## What the Agent Is Optimizing

The agent should optimize validation RMSE on a frozen time-based split.

## Data Source Plan

Use a time-series panel with one row per artist per observation date.

Recommended sources:

- Chartmetric comparison exports for daily artist metrics
- Spotify monthly listener history exports
- Ticketmaster or similar sources for concert-stop events
- release tables for albums, EPs, singles, and official MVs

Possible features:

- lagged Spotify monthly listeners
- prior 7-day and 30-day listener growth
- Chartmetric score
- Spotify followers
- Spotify fan conversion rate
- Spotify playlist reach
- Instagram followers and engagement rate
- TikTok followers and likes
- YouTube subscribers, daily video views, and monthly audience
- concert counts before and after the observation date
- release flags before and after the observation date

## Target Definition

Primary target:

- `listener_growth_30d_abs`

Secondary target:

- `listener_growth_30d_pct`

## Why This Is a Good AutoResearch Project

- The objective is numeric and clear.
- The target can be constructed from historical data.
- The model can be evaluated on a stable time-based holdout.
- The feature engineering and model search space are tractable.
- The scope is realistic with the exports already available.

## Files the Agent May Modify

For the real project repo, the agent should be allowed to modify only:

- `features.py`
- `model.py`

## Files That Must Remain Frozen

- `prepare.py`
- `split.py`
- `evaluation.py`
- `run.py`
- raw data snapshots
- target-construction logic after approval

## Baseline

Recommended baseline:

- linear regression or ridge regression using lagged listener features

Comparison baseline:

- naive previous-30-day-growth predictor
- zero-growth predictor

## Minimum Viable Project

If scope must be reduced, the MVP becomes:

- 20-25 K-pop artists only
- one target: `listener_growth_30d_abs`
- one row per artist per date
- one deterministic time-based train / validation split
- one editable modeling module for the agent

## Risk List

| # | Risk | Severity | Why It Matters | Mitigation |
|---|---|---|---|---|
| 1 | Leakage from future data | High | If features use information after `as_of_date`, results are invalid | Freeze target construction and all feature windows so predictors come from `<= as_of_date` |
| 2 | Misaligned time series across exports | High | Different metric files may have missing days or naming mismatches | Standardize artist names, normalize dates, and merge on exact `artist_name x as_of_date` |
| 3 | Sparse release history | Medium | Release-event features may be incomplete and weaken the model | Start with listener and platform metrics first, then add release rows incrementally |
| 4 | Incomplete concert history | Medium | Missing event rows can bias concert-derived features | Treat concert features as additive and allow zeros or blanks |
| 5 | Target skew and scale imbalance | Medium | Large artists dominate raw absolute growth | Track percent-growth diagnostics and consider transformed targets later |
| 6 | Small artist coverage | Medium | Too few artists may limit generalization | Use all available historical dates and expand artist coverage over time |
| 7 | Agent changes frozen logic | High | Results become incomparable | Freeze data prep, split, and evaluation files |

## First Draft Repository Structure

```text
spotify_listener_growth_autoresearch/
├── README.md
├── week1_project_charter.md
├── workflow_diagram_listener_growth.html
├── program.md
├── prepare.py
├── split.py
├── evaluation.py
├── features.py
├── model.py
├── run.py
├── research_log.md
├── evaluation_board.md
├── results.tsv
├── data/
│   ├── raw/
│   │   └── listener_growth/
│   └── processed/
└── .github/workflows/
```

## Week 1 Gate Summary

This project now answers the Week 1 questions clearly:

- what the agent optimizes:
  validation RMSE
- what metric determines success:
  RMSE, with MAE and rank correlation as diagnostics
- what data source will be used:
  Spotify monthly listener history + Chartmetric comparison exports + concert / release events
- what files the agent may modify:
  `features.py`, `model.py`
- what files are frozen:
  split, evaluation, run, raw data, and target construction
- what the baseline is:
  ridge regression or naive growth baseline
- what the MVP is:
  artist-date listener growth forecasting for K-pop artists
