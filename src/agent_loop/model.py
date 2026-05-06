#!/usr/bin/env python3
"""Mutable model definition for AutoResearch experiments."""

from __future__ import annotations

import os
from pathlib import Path
import site
import sys

for candidate in [
    Path.home() / ".local" / "lib" / "python3.13" / "site-packages",
    Path.home() / "Library" / "Python" / "3.13" / "lib" / "python" / "site-packages",
    Path("/opt/miniconda3/lib/python3.13/site-packages"),
]:
    if candidate.exists() and str(candidate) not in sys.path:
        site.addsitedir(str(candidate))

import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor, VotingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import HuberRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from src.agent_loop.features import FEATURE_COLUMNS, get_active_feature_set_name

LOG_SCALE_COLUMNS = [
    "listeners_today",
    "listeners_lag_7d",
    "listeners_lag_30d",
    "instagram_followers",
    "spotify_followers",
    "spotify_playlist_reach",
    "tiktok_followers",
    "tiktok_likes",
    "youtube_daily_video_views",
    "youtube_monthly_audience",
    "youtube_subscribers",
    "chartmetric_score",
]
MODEL_VARIANT_ENV_VAR = "STAT390_MODEL_VARIANT"
ACTIVE_MODEL_VARIANT = "huber_eps_1_25"


def log1p_clip_nonnegative(X):
    return np.log1p(np.clip(X, a_min=0, a_max=None))


def get_other_columns(feature_columns: list[str] | None = None) -> list[str]:
    columns = FEATURE_COLUMNS if feature_columns is None else feature_columns
    log_scale_columns = [column for column in LOG_SCALE_COLUMNS if column in columns]
    return [column for column in columns if column not in log_scale_columns]


def build_linear_preprocessor(feature_columns: list[str] | None = None) -> ColumnTransformer:
    columns = FEATURE_COLUMNS if feature_columns is None else feature_columns
    log_scale_columns = [column for column in LOG_SCALE_COLUMNS if column in columns]
    other_columns = get_other_columns(columns)
    return ColumnTransformer([
        (
            "log_scale",
            Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                (
                    "log",
                    FunctionTransformer(
                        log1p_clip_nonnegative,
                        feature_names_out="one-to-one",
                    ),
                ),
                ("scaler", StandardScaler()),
            ]),
            log_scale_columns,
        ),
        (
            "other",
            Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]),
            other_columns,
        ),
    ])


def build_tree_preprocessor(feature_columns: list[str] | None = None) -> ColumnTransformer:
    columns = FEATURE_COLUMNS if feature_columns is None else feature_columns
    log_scale_columns = [column for column in LOG_SCALE_COLUMNS if column in columns]
    other_columns = get_other_columns(columns)
    return ColumnTransformer([
        (
            "log_scale",
            Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                (
                    "log",
                    FunctionTransformer(
                        log1p_clip_nonnegative,
                        feature_names_out="one-to-one",
                    ),
                ),
            ]), log_scale_columns,
        ),
        (
            "other",
            Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
            ]),
            other_columns,
        ),
    ])


def get_linear_preprocessor_spec(feature_columns: list[str] | None = None) -> dict:
    columns = FEATURE_COLUMNS if feature_columns is None else feature_columns
    log_scale_columns = [column for column in LOG_SCALE_COLUMNS if column in columns]
    return {
        "name": "linear_log_standard",
        "type": "ColumnTransformer",
        "log_scale_columns": log_scale_columns,
        "other_columns": get_other_columns(columns),
        "transforms": {
            "log_scale": ["median_imputer", "log1p_clip_nonnegative", "standard_scaler"],
            "other": ["median_imputer", "standard_scaler"],
        },
    }


def get_tree_preprocessor_spec(feature_columns: list[str] | None = None) -> dict:
    columns = FEATURE_COLUMNS if feature_columns is None else feature_columns
    log_scale_columns = [column for column in LOG_SCALE_COLUMNS if column in columns]
    return {
        "name": "tree_log_impute",
        "type": "ColumnTransformer",
        "log_scale_columns": log_scale_columns,
        "other_columns": get_other_columns(columns),
        "transforms": {
            "log_scale": ["median_imputer", "log1p_clip_nonnegative"],
            "other": ["median_imputer"],
        },
    }


def get_active_model_variant_name() -> str:
    selected = os.environ.get(MODEL_VARIANT_ENV_VAR, ACTIVE_MODEL_VARIANT)
    available = {
        "blend_huber125_extra400l4_w58",
        "blend_huber125_extra400l4_w60",
        "blend_huber125_extra400l4_w62",
        "blend_huber125_extra400l4_w65",
        "blend_huber125_extra400l4_w70",
        "blend_huber125_extra400l6_w65",
        "blend_huber125_extra400l6_w70",
        "blend_huber125_extra400_w65",
        "huber_default",
        "huber_eps_1_18",
        "huber_eps_1_15",
        "huber_eps_1_20",
        "huber_eps_1_22",
        "huber_eps_1_25",
        "huber_eps_1_30",
        "huber_eps_1_35",
    }
    if selected not in available:
        choices = ", ".join(sorted(available))
        raise ValueError(f"Unknown model variant '{selected}'. Expected one of: {choices}.")
    return selected


def build_huber_regressor(epsilon: float | None = None) -> HuberRegressor:
    kwargs = {"max_iter": 500}
    if epsilon is not None:
        kwargs["epsilon"] = epsilon
    return HuberRegressor(**kwargs)


def build_extra_trees_regressor(
    *,
    n_estimators: int,
    max_depth: int | None,
    min_samples_leaf: int,
) -> ExtraTreesRegressor:
    return ExtraTreesRegressor(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_leaf=min_samples_leaf,
        random_state=42,
        n_jobs=-1,
    )


def build_huber_extra_blend(
    *,
    huber_weight: float,
    extra_weight: float,
    n_estimators: int,
    max_depth: int | None,
    min_samples_leaf: int,
) -> VotingRegressor:
    return VotingRegressor(
        estimators=[
            ("huber", Pipeline([
                ("preprocess", build_linear_preprocessor()),
                ("regressor", build_huber_regressor(1.25)),
            ])),
            ("extra", Pipeline([
                ("preprocess", build_tree_preprocessor()),
                (
                    "regressor",
                    build_extra_trees_regressor(
                        n_estimators=n_estimators,
                        max_depth=max_depth,
                        min_samples_leaf=min_samples_leaf,
                    ),
                ),
            ])),
        ],
        weights=[huber_weight, extra_weight],
    )


def get_model_spec(
    model_variant_name: str | None = None,
    feature_columns: list[str] | None = None,
) -> dict:
    variant = model_variant_name or get_active_model_variant_name()
    if variant == "blend_huber125_extra400l4_w58":
        return {
            "model_variant_name": variant,
            "estimator_family": "VotingRegressor",
            "estimator_params": {"weights": [0.58, 0.42]},
            "preprocessor_spec": {
                "huber": get_linear_preprocessor_spec(feature_columns),
                "extra": get_tree_preprocessor_spec(feature_columns),
            },
            "blend_spec": {
                "estimators": [
                    {
                        "name": "huber",
                        "family": "HuberRegressor",
                        "params": {"max_iter": 500, "epsilon": 1.25},
                    },
                    {
                        "name": "extra",
                        "family": "ExtraTreesRegressor",
                        "params": {
                            "n_estimators": 400,
                            "max_depth": 18,
                            "min_samples_leaf": 4,
                            "random_state": 42,
                        },
                    },
                ],
                "weights": [0.58, 0.42],
            },
            "summary": "Weighted blend of Huber(epsilon=1.25) and shallow ExtraTrees with 58/42 ensemble weights.",
        }
    if variant == "blend_huber125_extra400l4_w60":
        return {
            "model_variant_name": variant,
            "estimator_family": "VotingRegressor",
            "estimator_params": {"weights": [0.60, 0.40]},
            "preprocessor_spec": {
                "huber": get_linear_preprocessor_spec(feature_columns),
                "extra": get_tree_preprocessor_spec(feature_columns),
            },
            "blend_spec": {
                "estimators": [
                    {
                        "name": "huber",
                        "family": "HuberRegressor",
                        "params": {"max_iter": 500, "epsilon": 1.25},
                    },
                    {
                        "name": "extra",
                        "family": "ExtraTreesRegressor",
                        "params": {
                            "n_estimators": 400,
                            "max_depth": 18,
                            "min_samples_leaf": 4,
                            "random_state": 42,
                        },
                    },
                ],
                "weights": [0.60, 0.40],
            },
            "summary": "Weighted blend of Huber(epsilon=1.25) and shallow ExtraTrees with 60/40 ensemble weights.",
        }
    if variant == "blend_huber125_extra400l4_w62":
        return {
            "model_variant_name": variant,
            "estimator_family": "VotingRegressor",
            "estimator_params": {"weights": [0.62, 0.38]},
            "preprocessor_spec": {
                "huber": get_linear_preprocessor_spec(feature_columns),
                "extra": get_tree_preprocessor_spec(feature_columns),
            },
            "blend_spec": {
                "estimators": [
                    {
                        "name": "huber",
                        "family": "HuberRegressor",
                        "params": {"max_iter": 500, "epsilon": 1.25},
                    },
                    {
                        "name": "extra",
                        "family": "ExtraTreesRegressor",
                        "params": {
                            "n_estimators": 400,
                            "max_depth": 18,
                            "min_samples_leaf": 4,
                            "random_state": 42,
                        },
                    },
                ],
                "weights": [0.62, 0.38],
            },
            "summary": "Weighted blend of Huber(epsilon=1.25) and shallow ExtraTrees with 62/38 ensemble weights.",
        }
    if variant == "blend_huber125_extra400l4_w65":
        return {
            "model_variant_name": variant,
            "estimator_family": "VotingRegressor",
            "estimator_params": {"weights": [0.65, 0.35]},
            "preprocessor_spec": {
                "huber": get_linear_preprocessor_spec(feature_columns),
                "extra": get_tree_preprocessor_spec(feature_columns),
            },
            "blend_spec": {
                "estimators": [
                    {
                        "name": "huber",
                        "family": "HuberRegressor",
                        "params": {"max_iter": 500, "epsilon": 1.25},
                    },
                    {
                        "name": "extra",
                        "family": "ExtraTreesRegressor",
                        "params": {
                            "n_estimators": 400,
                            "max_depth": 18,
                            "min_samples_leaf": 4,
                            "random_state": 42,
                        },
                    },
                ],
                "weights": [0.65, 0.35],
            },
            "summary": "Weighted blend of Huber(epsilon=1.25) and shallow ExtraTrees with 65/35 ensemble weights.",
        }
    if variant == "blend_huber125_extra400l4_w70":
        return {
            "model_variant_name": variant,
            "estimator_family": "VotingRegressor",
            "estimator_params": {"weights": [0.70, 0.30]},
            "preprocessor_spec": {
                "huber": get_linear_preprocessor_spec(feature_columns),
                "extra": get_tree_preprocessor_spec(feature_columns),
            },
            "blend_spec": {
                "estimators": [
                    {
                        "name": "huber",
                        "family": "HuberRegressor",
                        "params": {"max_iter": 500, "epsilon": 1.25},
                    },
                    {
                        "name": "extra",
                        "family": "ExtraTreesRegressor",
                        "params": {
                            "n_estimators": 400,
                            "max_depth": 18,
                            "min_samples_leaf": 4,
                            "random_state": 42,
                        },
                    },
                ],
                "weights": [0.70, 0.30],
            },
            "summary": "Weighted blend of Huber(epsilon=1.25) and shallow ExtraTrees with 70/30 ensemble weights.",
        }
    if variant == "blend_huber125_extra400l6_w65":
        return {
            "model_variant_name": variant,
            "estimator_family": "VotingRegressor",
            "estimator_params": {"weights": [0.65, 0.35]},
            "preprocessor_spec": {
                "huber": get_linear_preprocessor_spec(feature_columns),
                "extra": get_tree_preprocessor_spec(feature_columns),
            },
            "blend_spec": {
                "estimators": [
                    {
                        "name": "huber",
                        "family": "HuberRegressor",
                        "params": {"max_iter": 500, "epsilon": 1.25},
                    },
                    {
                        "name": "extra",
                        "family": "ExtraTreesRegressor",
                        "params": {
                            "n_estimators": 400,
                            "max_depth": 18,
                            "min_samples_leaf": 6,
                            "random_state": 42,
                        },
                    },
                ],
                "weights": [0.65, 0.35],
            },
            "summary": "Weighted blend of Huber(epsilon=1.25) and more regularized ExtraTrees with 65/35 ensemble weights.",
        }
    if variant == "blend_huber125_extra400l6_w70":
        return {
            "model_variant_name": variant,
            "estimator_family": "VotingRegressor",
            "estimator_params": {"weights": [0.70, 0.30]},
            "preprocessor_spec": {
                "huber": get_linear_preprocessor_spec(feature_columns),
                "extra": get_tree_preprocessor_spec(feature_columns),
            },
            "blend_spec": {
                "estimators": [
                    {
                        "name": "huber",
                        "family": "HuberRegressor",
                        "params": {"max_iter": 500, "epsilon": 1.25},
                    },
                    {
                        "name": "extra",
                        "family": "ExtraTreesRegressor",
                        "params": {
                            "n_estimators": 400,
                            "max_depth": 18,
                            "min_samples_leaf": 6,
                            "random_state": 42,
                        },
                    },
                ],
                "weights": [0.70, 0.30],
            },
            "summary": "Weighted blend of Huber(epsilon=1.25) and more regularized ExtraTrees with 70/30 ensemble weights.",
        }
    if variant == "blend_huber125_extra400_w65":
        return {
            "model_variant_name": variant,
            "estimator_family": "VotingRegressor",
            "estimator_params": {"weights": [0.65, 0.35]},
            "preprocessor_spec": {
                "huber": get_linear_preprocessor_spec(feature_columns),
                "extra": get_tree_preprocessor_spec(feature_columns),
            },
            "blend_spec": {
                "estimators": [
                    {
                        "name": "huber",
                        "family": "HuberRegressor",
                        "params": {"max_iter": 500, "epsilon": 1.25},
                    },
                    {
                        "name": "extra",
                        "family": "ExtraTreesRegressor",
                        "params": {
                            "n_estimators": 400,
                            "max_depth": None,
                            "min_samples_leaf": 2,
                            "random_state": 42,
                        },
                    },
                ],
                "weights": [0.65, 0.35],
            },
            "summary": "Weighted blend of Huber(epsilon=1.25) and deeper ExtraTrees with 65/35 ensemble weights.",
        }

    epsilon_by_variant = {
        "huber_default": 1.35,
        "huber_eps_1_18": 1.18,
        "huber_eps_1_15": 1.15,
        "huber_eps_1_20": 1.20,
        "huber_eps_1_22": 1.22,
        "huber_eps_1_25": 1.25,
        "huber_eps_1_30": 1.30,
        "huber_eps_1_35": 1.35,
    }
    epsilon = epsilon_by_variant[variant]
    summary = "Default Week 4 Huber baseline with log-scaled linear preprocessing."
    if variant != "huber_default":
        summary = f"HuberRegressor with epsilon={epsilon:.2f} and the standard log-scaled linear preprocessing."
    return {
        "model_variant_name": variant,
        "estimator_family": "HuberRegressor",
        "estimator_params": {"max_iter": 500, "epsilon": epsilon},
        "preprocessor_spec": get_linear_preprocessor_spec(feature_columns),
        "blend_spec": {},
        "summary": summary,
    }


def get_active_model_spec() -> dict:
    return get_model_spec()


def model_name() -> str:
    feature_set = get_active_feature_set_name()
    variant = get_active_model_variant_name()
    return f"search_week4_{feature_set}_{variant}_v1"


def build_estimator():
    variant = get_active_model_variant_name()
    if variant == "blend_huber125_extra400l4_w58":
        return build_huber_extra_blend(
            huber_weight=0.58,
            extra_weight=0.42,
            n_estimators=400,
            max_depth=18,
            min_samples_leaf=4,
        )
    if variant == "blend_huber125_extra400l4_w60":
        return build_huber_extra_blend(
            huber_weight=0.60,
            extra_weight=0.40,
            n_estimators=400,
            max_depth=18,
            min_samples_leaf=4,
        )
    if variant == "blend_huber125_extra400l4_w62":
        return build_huber_extra_blend(
            huber_weight=0.62,
            extra_weight=0.38,
            n_estimators=400,
            max_depth=18,
            min_samples_leaf=4,
        )
    if variant == "blend_huber125_extra400l4_w65":
        return build_huber_extra_blend(
            huber_weight=0.65,
            extra_weight=0.35,
            n_estimators=400,
            max_depth=18,
            min_samples_leaf=4,
        )
    if variant == "blend_huber125_extra400l4_w70":
        return build_huber_extra_blend(
            huber_weight=0.70,
            extra_weight=0.30,
            n_estimators=400,
            max_depth=18,
            min_samples_leaf=4,
        )
    if variant == "blend_huber125_extra400l6_w65":
        return build_huber_extra_blend(
            huber_weight=0.65,
            extra_weight=0.35,
            n_estimators=400,
            max_depth=18,
            min_samples_leaf=6,
        )
    if variant == "blend_huber125_extra400l6_w70":
        return build_huber_extra_blend(
            huber_weight=0.70,
            extra_weight=0.30,
            n_estimators=400,
            max_depth=18,
            min_samples_leaf=6,
        )
    if variant == "blend_huber125_extra400_w65":
        return build_huber_extra_blend(
            huber_weight=0.65,
            extra_weight=0.35,
            n_estimators=400,
            max_depth=None,
            min_samples_leaf=2,
        )

    epsilon_by_variant = {
        "huber_eps_1_18": 1.18,
        "huber_eps_1_15": 1.15,
        "huber_eps_1_20": 1.20,
        "huber_eps_1_22": 1.22,
        "huber_eps_1_25": 1.25,
        "huber_eps_1_30": 1.30,
        "huber_eps_1_35": 1.35,
    }
    return Pipeline([
        ("preprocess", build_linear_preprocessor()),
        ("huber", build_huber_regressor(epsilon_by_variant.get(variant))),
    ])
