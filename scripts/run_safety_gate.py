#!/usr/bin/env python3
"""
Single-command safety gate for local regression confidence.

Runs:
1) Python syntax compile check for key modules
2) Full pytest suite with local repo import path

Usage:
    python scripts/run_safety_gate.py
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECK_FILES = [
    "kb_pipeline.py",
    "ingest_frontend.py",
    "scripts/run_story_progressive_gulp.py",
    "scripts/run_story_raw.py",
]


def _run(cmd: list[str], *, env: dict[str, str] | None = None) -> int:
    print("$ " + " ".join(cmd), flush=True)
    proc = subprocess.run(cmd, cwd=ROOT, env=env)
    return int(proc.returncode)


def main() -> int:
    print("=== Prethinker Safety Gate ===", flush=True)

    compile_targets: list[str] = []
    for rel in CHECK_FILES:
        path = (ROOT / rel).resolve()
        if path.exists():
            compile_targets.append(str(path))
        else:
            print(f"[warn] missing compile target: {rel}", flush=True)

    if compile_targets:
        rc = _run([sys.executable, "-m", "py_compile", *compile_targets])
        if rc != 0:
            print("[fail] syntax/compile gate failed", flush=True)
            return rc
    else:
        print("[warn] no compile targets found; skipping syntax gate", flush=True)

    env = os.environ.copy()
    existing_pythonpath = str(env.get("PYTHONPATH", "")).strip()
    env["PYTHONPATH"] = f".{os.pathsep}{existing_pythonpath}" if existing_pythonpath else "."

    rc = _run([sys.executable, "-m", "pytest", "-q"], env=env)
    if rc != 0:
        print("[fail] pytest gate failed", flush=True)
        return rc

    print("[pass] safety gate passed", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

