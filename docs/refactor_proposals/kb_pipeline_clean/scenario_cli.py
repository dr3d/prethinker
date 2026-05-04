"""Legacy scenario CLI placeholder for the proposed split."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from .parity_harness import (
        compare_signatures,
        load_json,
        normalizer_inventory_audit,
        signature_from_payload,
    )
    from .parse_normalization import trace_plan
except ImportError:
    ROOT = Path(__file__).resolve().parents[3]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from docs.refactor_proposals.kb_pipeline_clean.parity_harness import (
        compare_signatures,
        load_json,
        normalizer_inventory_audit,
        signature_from_payload,
    )
    from docs.refactor_proposals.kb_pipeline_clean.parse_normalization import trace_plan


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect the proposed KB pipeline split.")
    parser.add_argument("--trace-plan", action="store_true", help="Print normalizer trace plan JSON.")
    parser.add_argument(
        "--audit-normalizers",
        action="store_true",
        help="Check proposal legacy symbols against kb_pipeline.",
    )
    parser.add_argument(
        "--canonicalize",
        type=Path,
        default=None,
        help="Canonicalize a JSON result payload for parity comparison.",
    )
    parser.add_argument(
        "--kind",
        default="process_result",
        choices=[
            "process_result",
            "apply_result",
            "parse_result",
            "compiler_trace",
            "query_result",
        ],
        help="Payload kind for --canonicalize.",
    )
    parser.add_argument(
        "--compare",
        nargs=2,
        metavar=("BASELINE_SIGNATURE", "CANDIDATE_SIGNATURE"),
        help="Compare two already-canonical JSON signatures.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.trace_plan:
        print(json.dumps(trace_plan(), indent=2, sort_keys=True))
        return 0
    if args.audit_normalizers:
        print(json.dumps(normalizer_inventory_audit(), indent=2, sort_keys=True))
        return 0
    if args.canonicalize is not None:
        payload = load_json(args.canonicalize)
        print(json.dumps(signature_from_payload(args.kind, payload), indent=2, sort_keys=True))
        return 0
    if args.compare:
        baseline = load_json(args.compare[0])
        candidate = load_json(args.compare[1])
        print(json.dumps(compare_signatures(baseline, candidate), indent=2, sort_keys=True))
        return 0
    print("kb_pipeline_clean proposal is not wired into production.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

