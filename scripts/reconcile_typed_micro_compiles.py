#!/usr/bin/env python3
"""Reconcile governed typed facts across multiple micro-fixture compiles.

This is an experiment harness for the shared-atom lane. It deliberately operates
only on typed compile facts. It does not inspect source text, source-record
display fields, QA questions, or oracle answers.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.carrier_contract_registry import carrier_contract  # noqa: E402


FACT_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\((.*)\)\.\s*$")

DEFAULT_GOVERNED_SIGNATURES = {
    "claim_ground/4",
    "claim_range/4",
    "item_range/4",
    "legal_citation_detail/4",
    "list_member/4",
    "review_outcome/4",
}

SOURCE_SUBJECT_PREDICATES = {
    "claim_ground",
    "claim_range",
    "item_range",
    "legal_citation_detail",
    "list_member",
    "review_outcome",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture-id", required=True)
    parser.add_argument("--compile-json", action="append", required=True, type=Path)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument(
        "--min-support",
        type=int,
        default=1,
        help="Minimum distinct compile artifacts that must support a reconciled fact.",
    )
    parser.add_argument(
        "--support-mode",
        choices=["exact", "value"],
        default="exact",
        help=(
            "exact counts support only for identical facts; value ignores provenance/source slots "
            "for predicates whose last argument is source_or_scope."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_reconciliation(
        fixture_id=args.fixture_id,
        compile_paths=args.compile_json,
        min_support=args.min_support,
        support_mode=args.support_mode,
    )
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report["artifact"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not report["summary"]["blocking_errors"] else 1


def build_reconciliation(
    *,
    fixture_id: str,
    compile_paths: list[Path],
    min_support: int = 1,
    support_mode: str = "exact",
) -> dict[str, Any]:
    if min_support < 1:
        raise ValueError("min_support must be at least 1")
    if support_mode not in {"exact", "value"}:
        raise ValueError("support_mode must be 'exact' or 'value'")
    artifact_inputs: list[dict[str, Any]] = []
    supported: dict[str, set[str]] = {}
    representative_facts: dict[str, set[str]] = {}
    source_facts: dict[str, list[str]] = {}
    subject_keys_by_artifact: dict[str, dict[str, str]] = {}
    skipped: list[dict[str, str]] = []
    conflicts: list[dict[str, Any]] = []

    for path in compile_paths:
        path = Path(path)
        artifact_id = path.parent.name or path.name
        facts = _facts_from_compile_json(path)
        normalized_facts = [_normalize_fact_text(fact) for fact in facts]
        normalized_facts = [fact for fact in normalized_facts if fact]
        subject_keys = _subject_keys_for_artifact(normalized_facts)
        subject_keys_by_artifact[artifact_id] = subject_keys
        artifact_inputs.append(
            {
                "artifact_id": artifact_id,
                "path": str(path),
                "fact_count": len(facts),
                "governed_fact_count": sum(1 for fact in normalized_facts if _is_allowed_governed_fact(fact)),
                "subject_key_count": len(subject_keys),
            }
        )
        for fact in normalized_facts:
            parsed = _parse_fact(fact)
            if parsed is None:
                skipped.append({"artifact_id": artifact_id, "fact": fact, "reason": "unparseable_fact"})
                continue
            signature = f"{parsed['predicate']}/{len(parsed['args'])}"
            if signature not in DEFAULT_GOVERNED_SIGNATURES or carrier_contract(signature) is None:
                skipped.append({"artifact_id": artifact_id, "fact": fact, "reason": "ungoverned_signature"})
                continue
            reconciled = _rewrite_subject_to_governed_key(parsed, subject_keys)
            if reconciled is None:
                skipped.append({"artifact_id": artifact_id, "fact": fact, "reason": "unmapped_subject"})
                continue
            support_key = _fact_support_key(reconciled, support_mode=support_mode)
            supported.setdefault(support_key, set()).add(artifact_id)
            representative_facts.setdefault(support_key, set()).add(reconciled)
            source_facts.setdefault(support_key, []).append(fact)

    reconciled_facts = [
        _choose_representative_fact(representative_facts.get(support_key, {support_key}))
        for support_key, supporters in sorted(supported.items())
        if len(supporters) >= min_support
    ]
    conflicts.extend(_find_subject_conflicts(reconciled_facts))
    fact_support = [
        {
            "fact": _choose_representative_fact(representative_facts.get(support_key, {support_key})),
            "support_key": support_key,
            "support_count": len(supported.get(support_key, set())),
            "support_artifacts": sorted(supported.get(support_key, set())),
            "source_facts": sorted(set(source_facts.get(support_key, []))),
        }
        for support_key in sorted(supported)
        if len(supported.get(support_key, set())) >= min_support
    ]
    singleton_facts = [
        item["fact"]
        for item in fact_support
        if int(item["support_count"]) == 1
    ]
    blocking_errors = len(conflicts)
    artifact = {
        "schema_version": "governed_typed_micro_reconciliation_v1",
        "fixture_id": fixture_id,
        "source_compile": {
            "mode": "governed_typed_micro_reconciliation",
            "ok": blocking_errors == 0,
            "facts": reconciled_facts,
            "unique_fact_count": len(reconciled_facts),
            "governed_reconciliation": {
                "schema_version": "governed_typed_micro_reconciliation_v1",
                "fixture_id": fixture_id,
                "input_count": len(compile_paths),
                "min_support": min_support,
                "support_mode": support_mode,
                "authority": "typed_atom_reconciliation_only",
                "not_source_interpretation": True,
                "not_query_interpretation": True,
                "inputs": artifact_inputs,
                "fact_support": fact_support,
                "singleton_fact_count": len(singleton_facts),
                "singleton_facts": singleton_facts,
                "conflicts": conflicts,
                "skipped_count": len(skipped),
                "skipped": skipped[:200],
            },
        },
    }
    return {
        "schema_version": "governed_typed_micro_reconciliation_report_v1",
        "artifact": artifact,
        "summary": {
            "fixture_id": fixture_id,
            "input_count": len(compile_paths),
            "min_support": min_support,
            "support_mode": support_mode,
            "reconciled_fact_count": len(reconciled_facts),
            "singleton_fact_count": len(singleton_facts),
            "conflict_count": len(conflicts),
            "skipped_count": len(skipped),
            "blocking_errors": blocking_errors,
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    reconciliation = report["artifact"]["source_compile"]["governed_reconciliation"]
    lines = [
        "# Governed Typed Micro Reconciliation",
        "",
        f"- Fixture: `{summary['fixture_id']}`",
        f"- Inputs: `{summary['input_count']}`",
        f"- Minimum support: `{summary['min_support']}`",
        f"- Support mode: `{summary['support_mode']}`",
        f"- Reconciled facts: `{summary['reconciled_fact_count']}`",
        f"- Singleton facts retained: `{summary['singleton_fact_count']}`",
        f"- Conflicts: `{summary['conflict_count']}`",
        f"- Skipped facts: `{summary['skipped_count']}`",
        "",
        "## Inputs",
        "",
        "| Artifact | Governed facts | Subject keys | Path |",
        "| --- | ---: | ---: | --- |",
    ]
    for item in reconciliation.get("inputs", []):
        lines.append(
            "| `{}` | {} | {} | `{}` |".format(
                item.get("artifact_id", ""),
                item.get("governed_fact_count", 0),
                item.get("subject_key_count", 0),
                item.get("path", ""),
            )
        )
    lines.extend(["", "## Fact Support", "", "| Support | Fact |", "| ---: | --- |"])
    for item in reconciliation.get("fact_support", []):
        lines.append(f"| {item.get('support_count', 0)} | `{item.get('fact', '')}` |")
    conflicts = reconciliation.get("conflicts", [])
    if conflicts:
        lines.extend(["", "## Conflicts", ""])
        for conflict in conflicts:
            lines.append(f"- `{conflict}`")
    return "\n".join(lines) + "\n"


def _facts_from_compile_json(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    source_compile = data.get("source_compile")
    if isinstance(source_compile, dict) and isinstance(source_compile.get("facts"), list):
        return [str(fact).strip() for fact in source_compile.get("facts", []) if str(fact).strip()]
    if isinstance(data.get("facts"), list):
        return [str(fact).strip() for fact in data.get("facts", []) if str(fact).strip()]
    return []


def _subject_keys_for_artifact(facts: list[str]) -> dict[str, str]:
    features: dict[str, set[tuple[str, str, str]]] = {}
    for fact in facts:
        parsed = _parse_fact(fact)
        if parsed is None:
            continue
        if parsed["predicate"] != "claim_ground" or len(parsed["args"]) != 4:
            continue
        subject, ground, reference, status = [str(arg).strip() for arg in parsed["args"]]
        features.setdefault(subject, set()).add((ground, _governed_reference_atom(reference), status))
    out: dict[str, str] = {}
    for subject, keys in features.items():
        if len(keys) != 1:
            continue
        ground, reference, status = next(iter(keys))
        out[subject] = _canonical_subject_id("claim_issue", ground, reference, status)
    return out


def _rewrite_subject_to_governed_key(parsed: dict[str, Any], subject_keys: dict[str, str]) -> str | None:
    predicate = str(parsed.get("predicate") or "")
    args = [str(arg).strip() for arg in parsed.get("args") or []]
    if predicate not in SOURCE_SUBJECT_PREDICATES or not args:
        return _render_fact(predicate, args)
    canonical = subject_keys.get(args[0])
    if not canonical:
        return None
    args[0] = canonical
    if predicate == "claim_ground" and len(args) == 4:
        args[1] = _governed_ground_atom(args[1])
        args[2] = _governed_reference_atom(args[2])
    elif predicate == "legal_citation_detail" and len(args) == 4:
        args[1] = _governed_citation_atom(args[1])
        args[2] = _governed_legal_role_atom(args[2], args[1])
    elif predicate == "review_outcome" and len(args) == 4:
        args[1] = _governed_review_actor_atom(args[1])
        args[2] = _governed_review_outcome_atom(args[2])
    return _render_fact(predicate, args)


def _find_subject_conflicts(facts: list[str]) -> list[dict[str, Any]]:
    grounds: dict[str, set[tuple[str, str, str]]] = {}
    reviews: dict[str, set[tuple[str, str]]] = {}
    for fact in facts:
        parsed = _parse_fact(fact)
        if parsed is None:
            continue
        predicate = parsed["predicate"]
        args = list(parsed["args"])
        if predicate == "claim_ground" and len(args) == 4:
            grounds.setdefault(args[0], set()).add((args[1], args[2], args[3]))
        if predicate == "review_outcome" and len(args) == 4:
            reviews.setdefault(args[0], set()).add((args[1], args[2]))
    conflicts: list[dict[str, Any]] = []
    for subject, values in sorted(grounds.items()):
        if len(values) > 1:
            conflicts.append(
                {
                    "type": "multiple_claim_ground_values",
                    "subject": subject,
                    "values": sorted([list(value) for value in values]),
                }
            )
    for subject, values in sorted(reviews.items()):
        if len(values) > 1:
            conflicts.append(
                {
                    "type": "multiple_review_outcome_values",
                    "subject": subject,
                    "values": sorted([list(value) for value in values]),
                }
            )
    return conflicts


def _fact_support_key(fact: str, *, support_mode: str) -> str:
    if support_mode == "exact":
        return fact
    parsed = _parse_fact(fact)
    if parsed is None:
        return fact
    predicate = str(parsed.get("predicate") or "")
    args = [str(arg).strip() for arg in parsed.get("args") or []]
    if predicate in {"claim_range", "item_range", "legal_citation_detail", "list_member", "review_outcome"} and len(args) >= 4:
        return _render_fact(predicate, args[:-1] + ["_"])
    return fact


def _choose_representative_fact(facts: set[str]) -> str:
    # Prefer concrete source coordinates over the synthetic support key.
    concrete = [fact for fact in facts if not fact.endswith(", _).")]
    return sorted(concrete or list(facts))[0]


def _normalize_fact_text(fact: str) -> str:
    parsed = _parse_fact(fact)
    if parsed is None:
        return str(fact).strip()
    predicate = str(parsed["predicate"])
    args = [str(arg).strip() for arg in parsed["args"]]
    if predicate == "claim_ground" and len(args) == 4:
        args[1] = _governed_ground_atom(args[1])
        args[2] = _governed_reference_atom(args[2])
    elif predicate == "legal_citation_detail" and len(args) == 4:
        args[1] = _governed_citation_atom(args[1])
        args[2] = _governed_legal_role_atom(args[2], args[1])
    elif predicate == "review_outcome" and len(args) == 4:
        args[1] = _governed_review_actor_atom(args[1])
        args[2] = _governed_review_outcome_atom(args[2])
    return _render_fact(predicate, args)


def _is_allowed_governed_fact(fact: str) -> bool:
    parsed = _parse_fact(fact)
    if parsed is None:
        return False
    return f"{parsed['predicate']}/{len(parsed['args'])}" in DEFAULT_GOVERNED_SIGNATURES


def _parse_fact(fact: str) -> dict[str, Any] | None:
    match = FACT_RE.match(str(fact or "").strip())
    if not match:
        return None
    return {"predicate": match.group(1), "args": _split_args(match.group(2))}


def _split_args(raw: str) -> list[str]:
    args: list[str] = []
    current: list[str] = []
    quote: str | None = None
    escape = False
    depth = 0
    for char in raw:
        if quote:
            current.append(char)
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
            current.append(char)
            continue
        if char == "(":
            depth += 1
            current.append(char)
            continue
        if char == ")":
            depth = max(0, depth - 1)
            current.append(char)
            continue
        if char == "," and depth == 0:
            args.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    if current or raw.strip():
        args.append("".join(current).strip())
    return args


def _render_fact(predicate: str, args: list[str]) -> str:
    return f"{predicate}({', '.join(args)})."


def _canonical_subject_id(prefix: str, *parts: str) -> str:
    body = "_".join(_atom_part(part) for part in parts if _atom_part(part))
    return f"{prefix}_{body}" if body else prefix


def _atom_part(value: str) -> str:
    text = str(value or "").strip().casefold()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text


def _governed_reference_atom(value: str) -> str:
    text = str(value or "").strip()
    match = re.fullmatch(r"ref_([a-z0-9]+)", text.casefold())
    if match:
        return f"reference_{match.group(1)}"
    return text


def _governed_ground_atom(value: str) -> str:
    text = str(value or "").strip()
    normalized = text.casefold()
    if normalized in {"anticipated", "anticipates", "anticipation"}:
        return "anticipation"
    if normalized in {"obvious", "obviousness"}:
        return "obviousness"
    return text


def _governed_citation_atom(value: str) -> str:
    text = str(value or "").strip()
    normalized = text.casefold()
    if normalized in {"sec_102a1", "sec_102_a_1", "102a1", "102_a_1"}:
        return "section_102_a_1"
    if normalized in {"sec_103", "103"}:
        return "section_103"
    return text


def _governed_legal_role_atom(value: str, citation: str = "") -> str:
    text = str(value or "").strip()
    normalized = text.casefold()
    if normalized in {"statutory_basis", "statutory_ground", "statute", "legal_basis"}:
        return "statutory_ground"
    if str(citation or "").strip().casefold().startswith("section_") and normalized in {"anticipation", "obviousness"}:
        return "statutory_ground"
    return text


def _governed_review_actor_atom(value: str) -> str:
    text = str(value or "").strip()
    normalized = text.casefold()
    if normalized in {"actor_board", "board_role", "review_board_role"}:
        return "review_board"
    return text


def _governed_review_outcome_atom(value: str) -> str:
    normalized = str(value or "").strip().casefold()
    if normalized in {"affirmation_outcome", "affirmed_outcome", "affirmation", "affirm"}:
        return "affirmed"
    if normalized in {"reversal_outcome", "reversal", "reverse"}:
        return "reversed"
    return str(value or "").strip()


if __name__ == "__main__":
    raise SystemExit(main())
