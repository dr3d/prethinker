#!/usr/bin/env python3
"""Select whether a profile palette registry is safe enough for a pre-stamp run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
BROAD_ONLY_SIGNATURES = {"source_detail/4", "detail/2", "note/2", "summary/2"}


def select_registry(
    registry: dict[str, Any],
    prior_delivery: dict[str, Any],
    *,
    min_all_delivered_share: float = 0.5,
    max_zero_yield_compile_share: float = 0.0,
) -> dict[str, Any]:
    predicates = registry.get("predicates", []) if isinstance(registry.get("predicates"), list) else []
    signatures = [
        str(row.get("signature") or "").strip().casefold()
        for row in predicates
        if isinstance(row, dict) and str(row.get("signature") or "").strip()
    ]
    compile_rows = prior_delivery.get("compiles", []) if isinstance(prior_delivery.get("compiles"), list) else []
    compile_count = len(compile_rows)
    summary = prior_delivery.get("summary") if isinstance(prior_delivery.get("summary"), dict) else {}
    all_delivered = _to_int(summary.get("all_prior_delivered_compile_count"))
    zero_yield_compiles = sum(1 for row in compile_rows if _list(row.get("prior_zero_yield_signatures")))
    missing_compiles = sum(1 for row in compile_rows if _list(row.get("prior_missing_signatures")))
    delivered_share = round(all_delivered / max(1, compile_count), 4)
    zero_yield_share = round(zero_yield_compiles / max(1, compile_count), 4)
    missing_share = round(missing_compiles / max(1, compile_count), 4)

    reasons: list[str] = []
    if not signatures:
        reasons.append("empty_registry")
    if signatures and set(signatures).issubset(BROAD_ONLY_SIGNATURES):
        reasons.append("broad_only_registry")
    if compile_count <= 0:
        reasons.append("no_prior_delivery_audit_rows")
    if delivered_share < min_all_delivered_share:
        reasons.append(f"all_prior_delivered_share<{min_all_delivered_share:g}")
    if zero_yield_share > max_zero_yield_compile_share:
        reasons.append(f"zero_yield_compile_share>{max_zero_yield_compile_share:g}")

    decision = "pass" if not reasons else "hold"
    return {
        "schema": "prestamp_profile_registry_selection_v1",
        "fixture": str(registry.get("fixture") or prior_delivery.get("registry_fixture") or ""),
        "decision": decision,
        "reasons": reasons,
        "registry_signature_count": len(signatures),
        "registry_signatures": signatures,
        "compile_count": compile_count,
        "all_prior_delivered_compile_count": all_delivered,
        "all_prior_delivered_share": delivered_share,
        "missing_compile_count": missing_compiles,
        "missing_compile_share": missing_share,
        "zero_yield_compile_count": zero_yield_compiles,
        "zero_yield_compile_share": zero_yield_share,
        "thresholds": {
            "min_all_delivered_share": min_all_delivered_share,
            "max_zero_yield_compile_share": max_zero_yield_compile_share,
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Pre-Stamp Profile Registry Selection",
            "",
            f"- Fixture: `{report.get('fixture', '')}`",
            f"- Decision: `{report.get('decision', '')}`",
            f"- Reasons: `{report.get('reasons', [])}`",
            f"- Registry signatures: `{report.get('registry_signatures', [])}`",
            f"- All prior delivered share: `{report.get('all_prior_delivered_share', 0)}`",
            f"- Missing compile share: `{report.get('missing_compile_share', 0)}`",
            f"- Zero-yield compile share: `{report.get('zero_yield_compile_share', 0)}`",
            "",
        ]
    )


def _load_json(path: Path) -> dict[str, Any]:
    resolved = path if path.is_absolute() else (REPO_ROOT / path).resolve()
    payload = json.loads(resolved.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return payload


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _to_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry-json", type=Path, required=True)
    parser.add_argument("--prior-delivery-json", type=Path, required=True)
    parser.add_argument("--min-all-delivered-share", type=float, default=0.5)
    parser.add_argument("--max-zero-yield-compile-share", type=float, default=0.0)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path)
    parser.add_argument("--fail-on-hold", action="store_true")
    args = parser.parse_args()

    report = select_registry(
        _load_json(args.registry_json),
        _load_json(args.prior_delivery_json),
        min_all_delivered_share=float(args.min_all_delivered_share),
        max_zero_yield_compile_share=float(args.max_zero_yield_compile_share),
    )
    out_json = args.out_json if args.out_json.is_absolute() else (REPO_ROOT / args.out_json).resolve()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        out_md = args.out_md if args.out_md.is_absolute() else (REPO_ROOT / args.out_md).resolve()
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({"decision": report["decision"], "fixture": report["fixture"], "reasons": report["reasons"]}, sort_keys=True))
    if bool(args.fail_on_hold) and report["decision"] != "pass":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
