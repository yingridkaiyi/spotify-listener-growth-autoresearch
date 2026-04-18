#!/usr/bin/env python3
"""Frozen wrapper between the master dataset and agent feature logic."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.pipeline.prepare import load_dataset
from src.agent_loop.features import build_feature_matrix


def load_feature_frame():
    dataset = load_dataset()
    return build_feature_matrix(dataset)
