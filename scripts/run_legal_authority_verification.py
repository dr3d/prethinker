#!/usr/bin/env python3
"""CLI wrapper for the deterministic legal authority verification prototype."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.legal_authority_verification import main  # noqa: E402


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
