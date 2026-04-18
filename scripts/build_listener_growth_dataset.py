#!/usr/bin/env python3
"""Compatibility wrapper around src.pipeline.prepare."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.pipeline.prepare import load_dataset, save_dataset


def main() -> int:
    saved_path = save_dataset()
    dataset = load_dataset()
    print({"rows": len(dataset), "out": str(saved_path)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
