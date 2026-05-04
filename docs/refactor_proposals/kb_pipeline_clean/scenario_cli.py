"""Legacy scenario CLI placeholder for the proposed split."""

from __future__ import annotations

import argparse
import json

from .parse_normalization import trace_plan


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect the proposed KB pipeline split.")
    parser.add_argument("--trace-plan", action="store_true", help="Print normalizer trace plan JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.trace_plan:
        print(json.dumps(trace_plan(), indent=2, sort_keys=True))
        return 0
    print("kb_pipeline_clean proposal is not wired into production.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

