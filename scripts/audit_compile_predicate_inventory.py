#!/usr/bin/env python3
"""Summarize candidate and admitted predicates across compile JSON artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.run_domain_bootstrap_qa import compiled_surface_alias_inventory


PREDICATE_RE = re.compile(r"^\s*(?P<name>[a-z][A-Za-z0-9_]*)\s*\((?P<args>.*)\)\s*\.?\s*$")


LEGACY_COMPAT_PREFIXES = (
    "roster_table_",
    "student_",
    "school_",
    "homeroom_",
)

LEGACY_COMPAT_NAMES = {
    "adult_role",
    "initial_group_assignment",
    "roster_member",
}

DOMAIN_OR_FIXTURE_TOKENS = {
    "adult",
    "bus",
    "chaperone",
    "clinic",
    "grant",
    "homeroom",
    "patient",
    "probate",
    "roster",
    "school",
    "sensor",
    "student",
}


def iter_compile_jsons(paths: list[str]) -> list[Path]:
    out: list[Path] = []
    for raw in paths:
        path = Path(raw)
        if path.is_file() and path.suffix.lower() == ".json":
            out.append(path)
        elif path.is_dir():
            out.extend(sorted(path.rglob("domain_bootstrap_file*.json")))
    return sorted(dict.fromkeys(out))


def signature_from_clause(clause: str) -> str:
    text = str(clause or "").strip()
    if ":-" in text:
        text = text.split(":-", 1)[0].strip()
    match = PREDICATE_RE.match(text)
    if not match:
        return ""
    args = match.group("args").strip()
    if not args:
        arity = 0
    else:
        arity = 1
        depth = 0
        for char in args:
            if char == "(":
                depth += 1
            elif char == ")":
                depth = max(0, depth - 1)
            elif char == "," and depth == 0:
                arity += 1
    return f"{match.group('name')}/{arity}"


def normalize_candidate(value: Any) -> str:
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return ""
        if "/" in text and "(" not in text:
            return text
        sig = signature_from_clause(text)
        if sig:
            return sig
        match = re.match(r"^\s*([a-z][A-Za-z0-9_]*)\s*/\s*(\d+)\s*$", text)
        if match:
            return f"{match.group(1)}/{match.group(2)}"
        return text
    if isinstance(value, dict):
        signature = str(value.get("signature") or "").strip()
        if signature:
            return normalize_candidate(signature)
        name = str(value.get("name") or value.get("predicate") or "").strip()
        arity = value.get("arity")
        if name and arity is not None:
            return f"{name}/{arity}"
        if name:
            return name
    return ""


def predicate_name(signature: str) -> str:
    return str(signature or "").split("/", 1)[0].strip()


def predicate_bucket(signature: str) -> str:
    """Classify predicate signatures by instrument layer.

    This is intentionally conservative. A bucket is not a promotion decision;
    it is a repeatable first-pass map for seeing how much of a compile is
    deterministic ledger, current semantic surface, or legacy compatibility
    residue.
    """

    name = predicate_name(signature)
    if not name:
        return "unparsed"
    if name.startswith("source_record_") or name.startswith("explicit_table_"):
        return "deterministic_ledger"
    if name.endswith("_support") or name.endswith("_helper") or name.endswith("_companion"):
        return "legacy_support_surface"
    if name in LEGACY_COMPAT_NAMES or any(name.startswith(prefix) for prefix in LEGACY_COMPAT_PREFIXES):
        return "legacy_compatibility_alias"
    return "semantic_compile_surface"


def predicate_risk_row(
    signature: str,
    *,
    occurrences: int,
    fixtures: int,
) -> dict[str, Any]:
    name = predicate_name(signature)
    bucket = predicate_bucket(signature)
    tokens = {part for part in re.split(r"_+", name) if part}
    flagged_tokens = sorted(tokens & DOMAIN_OR_FIXTURE_TOKENS)

    if bucket == "legacy_compatibility_alias":
        risk = "legacy_compatibility_alias"
        reason = "compatibility alias; keep out of new guidance unless explicitly scoped"
    elif bucket == "legacy_support_surface":
        risk = "legacy_support_surface"
        reason = "support-style predicate; verify it is not helper-era delivery"
    elif flagged_tokens and fixtures <= 2:
        risk = "domain_or_fixture_shaped_singleton"
        reason = "domain-shaped vocabulary with little transfer evidence"
    elif fixtures == 1 and occurrences >= 20:
        risk = "high_volume_single_fixture_surface"
        reason = "large local surface; check whether this is structure or corpus residue"
    elif fixtures >= 8:
        risk = "broad_structural_candidate"
        reason = "broad fixture spread; likely structural, still subject to slot-contract audit"
    elif fixtures >= 3:
        risk = "transfer_observed"
        reason = "appears in multiple fixtures; audit slot contracts before promotion"
    else:
        risk = "singleton_low_volume"
        reason = "low-volume singleton; usually fixture-local until unlike replay says otherwise"

    return {
        "predicate": signature,
        "bucket": bucket,
        "risk": risk,
        "reason": reason,
        "occurrences": occurrences,
        "fixtures": fixtures,
        "flagged_tokens": flagged_tokens,
    }


def fixture_name(path: Path, payload: dict[str, Any]) -> str:
    text_file = str(payload.get("text_file") or "")
    if text_file:
        parent = Path(text_file).parent.name
        if parent:
            return parent
    if path.parent.name:
        return path.parent.name
    return path.stem


def summarize(paths: list[str]) -> dict[str, Any]:
    compile_paths = iter_compile_jsons(paths)
    candidate_counter: Counter[str] = Counter()
    admitted_counter: Counter[str] = Counter()
    fixture_candidate_sets: dict[str, set[str]] = {}
    fixture_admitted_sets: dict[str, set[str]] = {}
    predicate_alias_families: dict[str, set[str]] = defaultdict(set)
    fixture_rows: list[dict[str, Any]] = []
    parse_failures: list[str] = []

    for path in compile_paths:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            parse_failures.append(str(path))
            continue
        fixture = fixture_name(path, payload)
        parsed = payload.get("parsed") if isinstance(payload.get("parsed"), dict) else {}
        source_compile = payload.get("source_compile") if isinstance(payload.get("source_compile"), dict) else {}
        candidates = [
            sig
            for raw in parsed.get("candidate_predicates", []) or []
            if (sig := normalize_candidate(raw))
        ]
        facts = source_compile.get("facts", []) if isinstance(source_compile.get("facts"), list) else []
        rules = source_compile.get("rules", []) if isinstance(source_compile.get("rules"), list) else []
        queries = source_compile.get("queries", []) if isinstance(source_compile.get("queries"), list) else []
        admitted = [sig for clause in [*facts, *rules, *queries] if (sig := signature_from_clause(str(clause)))]

        candidate_counter.update(candidates)
        admitted_counter.update(admitted)
        fixture_candidate_sets[fixture] = set(candidates)
        fixture_admitted_sets[fixture] = set(admitted)
        for family in compiled_surface_alias_inventory(sorted(set(admitted))):
            family_name = str(family.get("family", "")).strip()
            for signature in family.get("signatures", []) or []:
                if family_name and isinstance(signature, str):
                    predicate_alias_families[signature].add(family_name)
        fixture_rows.append(
            {
                "fixture": fixture,
                "path": str(path),
                "parsed_ok": bool(payload.get("parsed_ok")),
                "candidate_predicate_count": len(candidates),
                "unique_candidate_predicate_count": len(set(candidates)),
                "admitted_clause_predicate_count": len(admitted),
                "unique_admitted_predicate_count": len(set(admitted)),
                "admitted_count": source_compile.get("admitted_count"),
                "skipped_count": source_compile.get("skipped_count"),
                "rough_score": (payload.get("score") or {}).get("rough_score") if isinstance(payload.get("score"), dict) else None,
                "candidate_bucket_counts": dict(Counter(predicate_bucket(sig) for sig in candidates)),
                "unique_candidate_bucket_counts": dict(Counter(predicate_bucket(sig) for sig in set(candidates))),
                "admitted_bucket_counts": dict(Counter(predicate_bucket(sig) for sig in admitted)),
                "unique_admitted_bucket_counts": dict(Counter(predicate_bucket(sig) for sig in set(admitted))),
            }
        )

    candidate_fixture_counts: Counter[str] = Counter()
    admitted_fixture_counts: Counter[str] = Counter()
    for sigs in fixture_candidate_sets.values():
        candidate_fixture_counts.update(sigs)
    for sigs in fixture_admitted_sets.values():
        admitted_fixture_counts.update(sigs)

    def top_rows(counter: Counter[str], fixture_counter: Counter[str], limit: int) -> list[dict[str, Any]]:
        return [
            {"predicate": pred, "occurrences": count, "fixtures": fixture_counter.get(pred, 0)}
            for pred, count in counter.most_common(limit)
        ]

    unique_candidate = set(candidate_counter)
    unique_admitted = set(admitted_counter)

    def bucket_summary(counter: Counter[str], fixture_sets: dict[str, set[str]]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        all_buckets = sorted({predicate_bucket(sig) for sig in counter})
        for bucket in all_buckets:
            bucket_counter = Counter({sig: count for sig, count in counter.items() if predicate_bucket(sig) == bucket})
            fixtures = {
                fixture
                for fixture, sigs in fixture_sets.items()
                if any(predicate_bucket(sig) == bucket for sig in sigs)
            }
            rows.append(
                {
                    "bucket": bucket,
                    "mentions": sum(bucket_counter.values()),
                    "unique_predicates": len(bucket_counter),
                    "fixtures": len(fixtures),
                    "top_predicates": top_rows(bucket_counter, Counter({sig: sum(1 for fs in fixture_sets.values() if sig in fs) for sig in bucket_counter}), 20),
                }
            )
        return sorted(rows, key=lambda row: (-row["mentions"], row["bucket"]))

    return {
        "artifact_count": len(compile_paths),
        "parsed_artifact_count": len(fixture_rows),
        "parse_failures": parse_failures,
        "totals": {
            "candidate_predicate_mentions": sum(candidate_counter.values()),
            "unique_candidate_predicates": len(unique_candidate),
            "admitted_clause_predicate_mentions": sum(admitted_counter.values()),
            "unique_admitted_predicates": len(unique_admitted),
            "candidate_not_admitted_unique": len(unique_candidate - unique_admitted),
            "admitted_not_candidate_unique": len(unique_admitted - unique_candidate),
        },
        "fixtures": sorted(fixture_rows, key=lambda row: row["fixture"]),
        "candidate_predicates": top_rows(candidate_counter, candidate_fixture_counts, len(candidate_counter)),
        "admitted_predicates": top_rows(admitted_counter, admitted_fixture_counts, len(admitted_counter)),
        "candidate_buckets": bucket_summary(candidate_counter, fixture_candidate_sets),
        "admitted_buckets": bucket_summary(admitted_counter, fixture_admitted_sets),
        "admitted_semantic_risk_rows": sorted(
            [
                predicate_risk_row(
                    pred,
                    occurrences=count,
                    fixtures=admitted_fixture_counts.get(pred, 0),
                )
                | {"alias_families": sorted(predicate_alias_families.get(pred, set()))}
                for pred, count in admitted_counter.items()
                if predicate_bucket(pred) != "deterministic_ledger"
            ],
            key=lambda row: (
                {
                    "domain_or_fixture_shaped_singleton": 0,
                    "legacy_compatibility_alias": 1,
                    "legacy_support_surface": 2,
                    "high_volume_single_fixture_surface": 3,
                    "broad_structural_candidate": 4,
                    "transfer_observed": 5,
                    "singleton_low_volume": 6,
                }.get(row["risk"], 9),
                -int(row["occurrences"]),
                row["predicate"],
            ),
        ),
        "top_candidate_predicates": top_rows(candidate_counter, candidate_fixture_counts, 80),
        "top_admitted_predicates": top_rows(admitted_counter, admitted_fixture_counts, 120),
        "candidate_not_admitted": sorted(unique_candidate - unique_admitted),
        "admitted_not_candidate": sorted(unique_admitted - unique_candidate),
        "alias_family_coverage": {
            "non_ledger_unique_predicates": len([pred for pred in admitted_counter if predicate_bucket(pred) != "deterministic_ledger"]),
            "non_ledger_with_alias_family": len([
                pred
                for pred in admitted_counter
                if predicate_bucket(pred) != "deterministic_ledger" and predicate_alias_families.get(pred)
            ]),
            "families": {
                family: sorted(pred for pred, families in predicate_alias_families.items() if family in families)
                for family in sorted({family for families in predicate_alias_families.values() for family in families})
            },
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    totals = payload["totals"]
    lines = [
        "# Compile Predicate Inventory",
        "",
        f"- Compile artifacts scanned: `{payload['artifact_count']}`",
        f"- Parsed artifacts: `{payload['parsed_artifact_count']}`",
        f"- Candidate predicate mentions: `{totals['candidate_predicate_mentions']}`",
        f"- Unique candidate predicates: `{totals['unique_candidate_predicates']}`",
        f"- Admitted predicate mentions: `{totals['admitted_clause_predicate_mentions']}`",
        f"- Unique admitted predicates: `{totals['unique_admitted_predicates']}`",
        f"- Candidate predicates not admitted anywhere: `{totals['candidate_not_admitted_unique']}`",
        f"- Admitted predicates not listed as candidates anywhere: `{totals['admitted_not_candidate_unique']}`",
        "",
        "## Predicate Buckets",
        "",
        "These buckets are a first-pass layer map, not a promotion decision.",
        "",
        "### Admitted",
        "",
        "| Bucket | Clause mentions | Unique predicates | Fixtures | Top predicates |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for row in payload.get("admitted_buckets", []):
        top = ", ".join(f"`{item['predicate']}` ({item['occurrences']})" for item in row.get("top_predicates", [])[:6])
        lines.append(f"| `{row['bucket']}` | {row['mentions']} | {row['unique_predicates']} | {row['fixtures']} | {top} |")
    lines.extend(
        [
            "",
            "### Candidates",
            "",
            "| Bucket | Mentions | Unique predicates | Fixtures | Top predicates |",
            "| --- | ---: | ---: | ---: | --- |",
        ]
    )
    for row in payload.get("candidate_buckets", []):
        top = ", ".join(f"`{item['predicate']}` ({item['occurrences']})" for item in row.get("top_predicates", [])[:6])
        lines.append(f"| `{row['bucket']}` | {row['mentions']} | {row['unique_predicates']} | {row['fixtures']} | {top} |")
    coverage = payload.get("alias_family_coverage", {})
    if coverage:
        lines.extend(
            [
                "",
                "## Alias Family Coverage",
                "",
                f"- Non-ledger unique predicates: `{coverage.get('non_ledger_unique_predicates', 0)}`",
                f"- Non-ledger predicates with at least one generic alias family: `{coverage.get('non_ledger_with_alias_family', 0)}`",
                "",
                "| Family | Predicates covered | Examples |",
                "| --- | ---: | --- |",
            ]
        )
        for family, predicates in sorted((coverage.get("families") or {}).items()):
            examples = ", ".join(f"`{pred}`" for pred in predicates[:8])
            lines.append(f"| `{family}` | {len(predicates)} | {examples} |")
    lines.extend(
        [
            "",
            "## Admitted Semantic Risk Ranking",
            "",
            "| Predicate | Risk | Mentions | Fixtures | Alias families | Flagged tokens | Reason |",
            "| --- | --- | ---: | ---: | --- | --- | --- |",
        ]
    )
    for row in payload.get("admitted_semantic_risk_rows", [])[:80]:
        tokens = ", ".join(f"`{token}`" for token in row.get("flagged_tokens", []))
        families = ", ".join(f"`{family}`" for family in row.get("alias_families", []))
        lines.append(
            f"| `{row['predicate']}` | `{row['risk']}` | {row['occurrences']} | {row['fixtures']} | {families} | {tokens} | {row['reason']} |"
        )
    lines.extend(
        [
            "",
        "## Top Admitted Predicates",
        "",
        "| Predicate | Clause mentions | Fixtures |",
        "| --- | ---: | ---: |",
        ]
    )
    for row in payload["top_admitted_predicates"][:40]:
        lines.append(f"| `{row['predicate']}` | {row['occurrences']} | {row['fixtures']} |")
    lines.extend(["", "## Top Candidate Predicates", "", "| Predicate | Mentions | Fixtures |", "| --- | ---: | ---: |"])
    for row in payload["top_candidate_predicates"][:40]:
        lines.append(f"| `{row['predicate']}` | {row['occurrences']} | {row['fixtures']} |")
    lines.extend(["", "## Fixtures", "", "| Fixture | Candidates | Unique candidates | Admitted mentions | Unique admitted | Skipped | Rough score |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"])
    for row in payload["fixtures"]:
        rough = row.get("rough_score")
        rough_text = "" if rough is None else str(rough)
        lines.append(
            f"| `{row['fixture']}` | {row['candidate_predicate_count']} | {row['unique_candidate_predicate_count']} | "
            f"{row['admitted_clause_predicate_count']} | {row['unique_admitted_predicate_count']} | "
            f"{row.get('skipped_count') if row.get('skipped_count') is not None else ''} | {rough_text} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-md", required=True)
    args = parser.parse_args()

    payload = summarize(args.paths)
    out_json = Path(args.out_json)
    out_md = Path(args.out_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    out_md.write_text(render_markdown(payload), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
