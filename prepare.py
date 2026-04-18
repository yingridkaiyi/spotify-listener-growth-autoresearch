#!/usr/bin/env python3
"""Compatibility wrapper for the frozen pipeline prepare module."""

from src.pipeline.prepare import build_dataset, load_dataset, save_dataset


if __name__ == "__main__":
    saved = save_dataset()
    print({"rows": len(load_dataset()), "out": str(saved)})
