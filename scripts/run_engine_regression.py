#!/usr/bin/env python3
"""
One-command engine regression runner for onboarding and routine checks.

Usage:
    python scripts/run_engine_regression.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TESTS = [
    "tests/test_engine_baseline_suite.py",
    "tests/test_core_runtime.py",
    "tests/test_constraint_propagation.py",
]


def main() -> int:
    cmd = [sys.executable, "-m", "pytest", *DEFAULT_TESTS, "-v"]
    print("Running engine regression suite:", flush=True)
    print(" ".join(cmd), flush=True)
    result = subprocess.run(cmd, cwd=ROOT)
    return int(result.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
