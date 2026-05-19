"""Build a bounded multi-draw compile preservation candidate.

This is an experiment tool, not default admission behavior. It preserves direct
facts for carrier signatures that a stability audit classified as volatile
profile-delivery surfaces, while keeping the anchor compile's source-record
ledger and unrelated direct rows intact.
"""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.audit_compile_surface_invariants import _facts_from_compile, _predicate_name


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compile-json", action="append", type=Path, default=[])
    parser.add_argument("--stability-json", type=Path)
    parser.add_argument("--fixture", default="")
    parser.add_argument("--signature", action="append", default=[])
    parser.add_argument("--anchor-index", type=int, default=0)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    signatures = set(args.signature)
    if args.stability_json:
        signatures.update(_signatures_from_stability(args.stability_json, fixture=args.fixture))
    payload = build_preservation_candidate(
        compile_paths=args.compile_json,
        signatures=sorted(signatures),
        anchor_index=args.anchor_index,
    )
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload["compile"], indent=2, sort_keys=True), encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["metadata"], sort_keys=True))
    return 0


def build_preservation_candidate(
    *,
    compile_paths: list[Path],
    signatures: list[str],
    anchor_index: int = 0,
) -> dict[str, Any]:
    if not compile_paths:
        raise ValueError("At least one compile JSON is required.")
    if anchor_index < 0 or anchor_index >= len(compile_paths):
        raise ValueError("anchor_index is outside the compile path list.")

    payloads = [json.loads(path.read_text(encoding="utf-8")) for path in compile_paths]
    anchor = deepcopy(payloads[anchor_index])
    selected_signatures = sorted({str(signature).strip() for signature in signatures if str(signature).strip()})

    anchor_facts = _facts_from_compile(anchor)
    anchor_source, anchor_direct = _split_source_direct(anchor_facts)
    preserved_direct: list[str] = []
    for payload in payloads:
        for fact in _facts_from_compile(payload):
            if _fact_signature(fact) in selected_signatures:
                preserved_direct.append(fact)

    merged_direct = _dedupe([*anchor_direct, *preserved_direct])
    merged_facts = [*anchor_source, *merged_direct]
    source_compile = anchor.setdefault("source_compile", {})
    source_compile["facts"] = merged_facts
    _merge_candidate_predicates(anchor, payloads)

    metadata = {
        "schema_version": "compile_preservation_candidate_v1",
        "compile_count": len(compile_paths),
        "anchor_compile": str(compile_paths[anchor_index]),
        "selected_signatures": selected_signatures,
        "anchor_direct_fact_count": len(anchor_direct),
        "preserved_direct_candidate_count": len(_dedupe(preserved_direct)),
        "merged_direct_fact_count": len(merged_direct),
        "added_direct_fact_count": len(merged_direct) - len(anchor_direct),
        "source_record_fact_count": len(anchor_source),
    }
    anchor["preservation_metadata"] = metadata
    return {"compile": anchor, "metadata": metadata}


def _signatures_from_stability(path: Path, *, fixture: str = "") -> list[str]:
    report = json.loads(path.read_text(encoding="utf-8"))
    signatures: set[str] = set()
    for fixture_row in report.get("fixtures", []):
        if not isinstance(fixture_row, dict):
            continue
        if fixture and fixture_row.get("fixture") != fixture:
            continue
        for row in fixture_row.get("profile_delivery_telemetry", []):
            if not isinstance(row, dict):
                continue
            if row.get("response_hint") != "multi_draw_preservation_candidate":
                continue
            for delivery in row.get("carrier_delivery", []):
                if not isinstance(delivery, dict):
                    continue
                carrier = str(delivery.get("carrier") or "").strip()
                if carrier and int(delivery.get("draws_with_rows") or 0) > 0:
                    signatures.add(carrier)
    return sorted(signatures)


def _split_source_direct(facts: list[str]) -> tuple[list[str], list[str]]:
    source: list[str] = []
    direct: list[str] = []
    for fact in facts:
        if _predicate_name(fact).startswith("source_record"):
            source.append(fact)
        else:
            direct.append(fact)
    return source, direct


def _fact_signature(fact: str) -> str:
    predicate = _predicate_name(fact)
    if not predicate:
        return ""
    inside = str(fact).split("(", 1)[1].rsplit(")", 1)[0] if "(" in fact and ")" in fact else ""
    arity = 0 if not inside.strip() else len([part for part in inside.split(",")])
    return f"{predicate}/{arity}"


def _dedupe(facts: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for fact in facts:
        key = str(fact).strip()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


def _merge_candidate_predicates(anchor: dict[str, Any], payloads: list[dict[str, Any]]) -> None:
    rows: list[Any] = []
    for payload in payloads:
        parsed = payload.get("parsed") if isinstance(payload.get("parsed"), dict) else {}
        candidates = parsed.get("candidate_predicates")
        if isinstance(candidates, list):
            rows.extend(candidates)
    seen: set[str] = set()
    merged: list[Any] = []
    for row in rows:
        key = json.dumps(row, sort_keys=True) if isinstance(row, dict) else str(row)
        if key in seen:
            continue
        seen.add(key)
        merged.append(row)
    if merged:
        anchor.setdefault("parsed", {})["candidate_predicates"] = merged


def render_markdown(payload: dict[str, Any]) -> str:
    meta = payload["metadata"]
    return "\n".join(
        [
            "# Compile Preservation Candidate",
            "",
            f"- Schema: `{meta['schema_version']}`",
            f"- Compiles: `{meta['compile_count']}`",
            f"- Anchor compile: `{meta['anchor_compile']}`",
            f"- Selected signatures: `{meta['selected_signatures']}`",
            f"- Source-record facts: `{meta['source_record_fact_count']}`",
            f"- Direct facts: `{meta['anchor_direct_fact_count']}` anchor -> `{meta['merged_direct_fact_count']}` merged",
            f"- Added direct facts: `{meta['added_direct_fact_count']}`",
            "",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
