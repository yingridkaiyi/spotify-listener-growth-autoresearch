#!/usr/bin/env python3
"""Frozen deterministic time-based train/validation/test split."""

from __future__ import annotations

import math


def time_based_split(dataset, date_column: str = "as_of_date", train_frac: float = 0.7, val_frac: float = 0.15):
    unique_dates = sorted(dataset[date_column].unique().tolist())
    if len(unique_dates) < 3:
        raise ValueError("Need at least 3 distinct dates for train/validation/test split.")

    n_dates = len(unique_dates)
    train_end = max(1, math.floor(n_dates * train_frac))
    val_size = max(1, math.floor(n_dates * val_frac))
    val_end = min(n_dates - 1, train_end + val_size)
    if val_end >= n_dates:
        val_end = n_dates - 1
    if train_end >= val_end:
        train_end = max(1, val_end - 1)

    train_dates = set(unique_dates[:train_end])
    val_dates = set(unique_dates[train_end:val_end])
    test_dates = set(unique_dates[val_end:])

    train = dataset[dataset[date_column].isin(train_dates)].copy()
    validation = dataset[dataset[date_column].isin(val_dates)].copy()
    test = dataset[dataset[date_column].isin(test_dates)].copy()

    return {
        "train": train,
        "validation": validation,
        "test": test,
        "cutoffs": {
            "train_end": max(train_dates),
            "validation_end": max(val_dates),
            "test_end": max(test_dates),
        },
    }
