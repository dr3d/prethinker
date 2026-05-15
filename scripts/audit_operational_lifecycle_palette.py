"""Audit operational lifecycle palette shape in compile artifacts.

This is a diagnostic audit only. It does not judge QA correctness and does not
propose repairs. It looks for recurring lifecycle-shape pressures that broad
compile guidance can otherwise hide: alias splits, repeated-verb layer
ambiguity, supersession target collapse, and missing status phase surfaces.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


FACT_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\((.*)\)\.\s*$")
TOKEN_RE = re.compile(r"[a-z0-9]+")
STATUS_TOKENS = {
    "active",
    "approved",
    "closed",
    "completed",
    "denied",
    "final",
    "open",
    "pending",
    "reinstated",
    "resolved",
    "satisfied",
    "withdrawn",
}
TARGET_OBJECT_TOKENS = {
    "document",
    "entry",
    "evt",
    "event",
    "finding",
    "letter",
    "memo",
    "note",
    "notice",
    "order",
    "plan",
    "record",
    "report",
}
LIFECYCLE_VERBS = {
    "received",
    "filed",
    "logged",
    "assigned",
    "approved",
    "denied",
    "withdrawn",
    "superseded",
    "reopened",
    "closed",
    "corrected",
}
LAYER_TOKENS = {
    "actor",
    "desk",
    "event",
    "field",
    "lab",
    "layer",
    "phase",
    "record",
    "role",
    "source",
    "type",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--compile-json",
        action="append",
        type=Path,
        default=[],
        help="Compile JSON file or directory containing domain_bootstrap_file_*.json. Repeatable.",
    )
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = expand_compile_paths(args.compile_json)
    if not paths:
        raise SystemExit("No compile JSON files found.")
    reports = [audit_compile(path) for path in paths]
    payload = {
        "schema": "operational_lifecycle_palette_audit_v1",
        "compile_count": len(reports),
        "summary": summarize_reports(reports),
        "reports": reports,
    }
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(payload), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def expand_compile_paths(inputs: list[Path]) -> list[Path]:
    out: list[Path] = []
    for item in inputs:
        if item.is_dir():
            matches = sorted(item.glob("domain_bootstrap_file_*.json"))
            if matches:
                out.append(matches[-1])
                continue
            out.extend(sorted(item.glob("*/domain_bootstrap_file_*.json")))
        elif item.is_file():
            out.append(item)
    return sorted(dict.fromkeys(path.resolve() for path in out))


def audit_compile(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    facts = facts_from_compile(data)
    rows = fact_rows(facts)
    direct_rows = [row for row in rows if not str(row["predicate"]).startswith("source_record")]
    source_rows = [row for row in rows if str(row["predicate"]).startswith("source_record")]
    source_texts = source_text_atoms(source_rows)
    findings = [
        *detect_alias_splits(direct_rows, source_rows),
        *detect_ambiguous_repeated_verbs(direct_rows, source_texts),
        *detect_supersession_target_collapse(direct_rows, source_texts),
        *detect_phase_classification_missing(direct_rows, source_texts),
    ]
    return {
        "compile_json": str(path),
        "run": path.parent.parent.name if path.parent.parent != path.parent else "",
        "fixture": path.parent.name,
        "parsed_ok": bool(data.get("parsed_ok")),
        "direct_fact_count": len(direct_rows),
        "source_record_fact_count": len(source_rows),
        "finding_counts": dict(Counter(item["class"] for item in findings)),
        "findings": findings,
    }


def detect_alias_splits(direct_rows: list[dict[str, Any]], source_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, set[str]] = defaultdict(set)
    direct_atoms = {
        arg
        for row in direct_rows
        if str(row["predicate"]) not in {"recorded_in", "source_recorded"}
        for arg in row["args"]
        if is_compact_identity_atom(arg)
    }
    label_atoms = {
        row["args"][1]
        for row in source_rows
        if str(row["predicate"]) == "source_record_label" and len(row["args"]) >= 2
    }
    for atom in sorted(direct_atoms | label_atoms):
        code = identity_code(atom)
        if code:
            grouped[code].add(atom)
    findings: list[dict[str, Any]] = []
    for code, variants in sorted(grouped.items()):
        direct_variants = sorted(variants & direct_atoms)
        if len(direct_variants) < 2:
            continue
        findings.append(
            {
                "class": "alias_split",
                "code": code,
                "variants": direct_variants[:8],
                "evidence": [f"identity code `{code}` appears as {', '.join(direct_variants[:8])}"],
            }
        )
    return findings


def detect_ambiguous_repeated_verbs(direct_rows: list[dict[str, Any]], source_texts: list[str]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    direct_by_verb: dict[str, list[str]] = defaultdict(list)
    for row in direct_rows:
        row_text = " ".join([str(row["predicate"]), *map(str, row["args"])]).lower()
        row_tokens = set(TOKEN_RE.findall(row_text))
        for verb in LIFECYCLE_VERBS:
            if verb in row_tokens or verb.rstrip("ed") in row_tokens:
                direct_by_verb[verb].append(row["fact"])
    for verb in sorted(LIFECYCLE_VERBS):
        source_hits = [text for text in source_texts if verb in set(TOKEN_RE.findall(text.lower()))]
        if len(source_hits) < 2:
            continue
        predicates = {predicate_name(fact) for fact in direct_by_verb.get(verb, [])}
        layered = any(set(TOKEN_RE.findall(pred)) & LAYER_TOKENS for pred in predicates)
        if len(predicates) <= 1 and not layered:
            findings.append(
                {
                    "class": "ambiguous_repeated_verb",
                    "verb": verb,
                    "predicate_surfaces": sorted(predicates),
                    "evidence": source_hits[:3],
                }
            )
    return findings


def detect_supersession_target_collapse(direct_rows: list[dict[str, Any]], source_texts: list[str]) -> list[dict[str, Any]]:
    source_supersession = [text for text in source_texts if "superseded" in text.lower() or "supersedes" in text.lower()]
    if not source_supersession:
        return []
    source_codes = {code for text in source_supersession for code in identity_codes_in_text(text)}
    findings: list[dict[str, Any]] = []
    for row in direct_rows:
        predicate = str(row["predicate"]).lower()
        if "supersed" not in predicate and not any("supersed" in str(arg).lower() for arg in row["args"]):
            continue
        target = str(row["args"][1]).lower() if len(row["args"]) >= 2 else ""
        target_code = identity_code(target)
        target_tokens = set(TOKEN_RE.findall(target))
        target_is_object = bool(target_tokens & TARGET_OBJECT_TOKENS)
        collapsed_to_status = (
            bool(target_tokens & STATUS_TOKENS)
            and not target_is_object
            and (not target_code or target_code not in source_codes)
        )
        missing_source_target = bool(source_codes) and target_code not in source_codes and collapsed_to_status
        if collapsed_to_status or missing_source_target:
            findings.append(
                {
                    "class": "supersession_target_collapse",
                    "fact": row["fact"],
                    "source_target_codes": sorted(source_codes),
                    "evidence": source_supersession[:2],
                }
            )
    return findings


def detect_phase_classification_missing(direct_rows: list[dict[str, Any]], source_texts: list[str]) -> list[dict[str, Any]]:
    direct_text = "\n".join(row["fact"].lower() for row in direct_rows)
    findings: list[dict[str, Any]] = []
    for phase in ("initial", "current", "final"):
        source_hits = [
            text
            for text in source_texts
            if f"{phase}_status" in text.lower()
            or f"{phase} status" in text.lower()
            or (phase == "initial" and "filed" in text.lower() and "status" in text.lower())
        ]
        if not source_hits:
            continue
        has_phase = phase in set(TOKEN_RE.findall(direct_text)) or f"{phase}_status" in direct_text
        if not has_phase:
            findings.append(
                {
                    "class": "phase_classification_missing",
                    "phase": phase,
                    "evidence": source_hits[:3],
                }
            )
    return findings


def summarize_reports(reports: list[dict[str, Any]]) -> dict[str, Any]:
    class_counts: Counter[str] = Counter()
    fixture_counts: dict[str, dict[str, int]] = {}
    for report in reports:
        counts = Counter(item["class"] for item in report["findings"])
        class_counts.update(counts)
        fixture_counts[str(report["fixture"])] = dict(counts)
    return {
        "class_counts": dict(class_counts),
        "fixture_counts": fixture_counts,
        "fixtures_with_findings": sum(1 for report in reports if report["findings"]),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Operational Lifecycle Palette Audit",
        "",
        f"- Schema: `{payload['schema']}`",
        f"- Compiles: `{payload['compile_count']}`",
        f"- Class counts: `{payload['summary']['class_counts']}`",
        f"- Fixtures with findings: `{payload['summary']['fixtures_with_findings']}`",
        "",
        "## Fixture Summary",
        "",
        "| Fixture | Alias Split | Ambiguous Verb | Supersession Collapse | Phase Missing |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for report in payload["reports"]:
        counts = Counter(item["class"] for item in report["findings"])
        lines.append(
            "| `{fixture}` | {alias} | {verb} | {super} | {phase} |".format(
                fixture=report["fixture"],
                alias=counts.get("alias_split", 0),
                verb=counts.get("ambiguous_repeated_verb", 0),
                super=counts.get("supersession_target_collapse", 0),
                phase=counts.get("phase_classification_missing", 0),
            )
        )
    lines.extend(["", "## Findings", ""])
    for report in payload["reports"]:
        if not report["findings"]:
            continue
        lines.append(f"### `{report['fixture']}`")
        lines.append("")
        for finding in report["findings"]:
            detail = ", ".join(f"`{key}`={value!r}" for key, value in finding.items() if key not in {"class", "evidence"})
            lines.append(f"- `{finding['class']}`: {detail}")
            for evidence in finding.get("evidence", [])[:2]:
                lines.append(f"  - {evidence}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def facts_from_compile(data: dict[str, Any]) -> list[str]:
    source_compile = data.get("source_compile") if isinstance(data.get("source_compile"), dict) else {}
    facts = source_compile.get("facts")
    if isinstance(facts, list):
        return [str(fact).strip() for fact in facts if str(fact).strip()]
    parsed = data.get("parsed") if isinstance(data.get("parsed"), dict) else {}
    parsed_facts = parsed.get("facts")
    if isinstance(parsed_facts, list):
        return [str(fact).strip() for fact in parsed_facts if str(fact).strip()]
    return []


def fact_rows(facts: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for fact in facts:
        match = FACT_RE.match(fact)
        if not match:
            continue
        rows.append({"predicate": match.group(1), "args": split_fact_args(match.group(2)), "fact": fact})
    return rows


def split_fact_args(raw_args: str) -> list[str]:
    args: list[str] = []
    current: list[str] = []
    in_quote = False
    escape = False
    depth = 0
    for char in raw_args:
        if escape:
            current.append(char)
            escape = False
            continue
        if char == "\\":
            current.append(char)
            escape = True
            continue
        if char == '"':
            current.append(char)
            in_quote = not in_quote
            continue
        if not in_quote and char == "(":
            depth += 1
        elif not in_quote and char == ")" and depth:
            depth -= 1
        if char == "," and not in_quote and depth == 0:
            args.append(clean_atom("".join(current).strip()))
            current = []
            continue
        current.append(char)
    if current:
        args.append(clean_atom("".join(current).strip()))
    return args


def source_text_atoms(source_rows: list[dict[str, Any]]) -> list[str]:
    return [
        str(row["args"][1])
        for row in source_rows
        if str(row["predicate"]) == "source_record_text_atom" and len(row["args"]) >= 2
    ]


def predicate_name(fact: str) -> str:
    match = FACT_RE.match(str(fact))
    return match.group(1) if match else ""


def clean_atom(value: str) -> str:
    return str(value).strip().strip("'\"").lower().replace("-", "_")


def identity_code(value: str) -> str:
    tokens = TOKEN_RE.findall(clean_atom(value))
    if (
        len(tokens) >= 2
        and tokens[-1].isdigit()
        and tokens[-2].isalpha()
        and tokens[-2] != "on"
        and 1 <= len(tokens[-2]) <= 4
        and not _looks_like_date_tail(tokens[-2:])
    ):
        return f"{tokens[-2]}{tokens[-1]}"
    for token in reversed(tokens):
        if re.fullmatch(r"[a-z]{1,4}\d{1,4}", token):
            return token
    return ""


def identity_codes_in_text(text: str) -> set[str]:
    tokens = TOKEN_RE.findall(clean_atom(text))
    codes: set[str] = set()
    for index in range(1, len(tokens)):
        if tokens[index].isdigit() and tokens[index - 1].isalpha() and tokens[index - 1] != "on" and 1 <= len(tokens[index - 1]) <= 4:
            code = f"{tokens[index - 1]}{tokens[index]}"
            if not _looks_like_date_tail([tokens[index - 1], tokens[index]]):
                codes.add(code)
    for token in tokens:
        if re.fullmatch(r"[a-z]{1,4}\d{1,4}", token):
            codes.add(token)
    return codes


def is_compact_identity_atom(value: str) -> bool:
    tokens = TOKEN_RE.findall(clean_atom(value))
    return bool(tokens) and len(tokens) <= 3 and len(clean_atom(value)) <= 32


def _looks_like_date_tail(tokens: list[str]) -> bool:
    return len(tokens) == 2 and tokens[0].isdigit() and len(tokens[0]) == 4


if __name__ == "__main__":
    raise SystemExit(main())
