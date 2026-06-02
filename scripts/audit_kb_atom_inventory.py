#!/usr/bin/env python3
"""Summarize the typed atom library emitted by compile artifacts.

This is a compile-only diagnostic. It does not read source prose, QA questions,
or oracle answers. Its job is to make the KB language visible before query work:

    Which predicates exist?
    With what arities?
    How stable is the predicate inventory across fixtures?
    What structural kinds of arguments do those atoms carry?

The report is intentionally not a query router. It must not be used to map
English questions to predicates.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.carrier_contract_registry import carrier_contract


FREE_TEXT_PREDICATE_HINTS = (
    "text",
    "display",
    "label",
    "summary",
    "description",
    "narrative",
    "quote",
    "raw",
)

SOURCE_RECORD_PREFIX = "source_record_"
SOURCE_COORD_RE = re.compile(r"^src_(?:line|row)_\d+$|^source_", re.IGNORECASE)
DATE_ATOM_RE = re.compile(r"^(?:v_)?\d{4}(?:[_-]\d{1,2}){0,2}$")
INTEGER_RE = re.compile(r"^-?\d+$")
DECIMAL_RE = re.compile(r"^-?\d+\.\d+$")
DEFAULT_MAX_PREDICATE_CHARS = 48
DEFAULT_MAX_PREDICATE_TOKENS = 7
DEFAULT_MAX_ATOM_CHARS = 96
DEFAULT_MAX_ATOM_TOKENS = 14
SENTENCE_STOPWORD_DENSITY = 0.35
SENTENCE_STOPWORD_MIN_TOKENS = 8
SENTENCE_STOPWORD_MIN_COUNT = 3
ATOM_SHAPE_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "been",
    "before",
    "being",
    "by",
    "for",
    "from",
    "had",
    "has",
    "have",
    "if",
    "in",
    "is",
    "may",
    "must",
    "of",
    "on",
    "or",
    "shall",
    "should",
    "that",
    "the",
    "then",
    "to",
    "under",
    "was",
    "were",
    "when",
    "which",
    "will",
    "with",
    "within",
    "without",
}


@dataclass(frozen=True)
class ParsedFact:
    predicate: str
    args: tuple[str, ...]
    clause: str

    @property
    def signature(self) -> str:
        return f"{self.predicate}/{len(self.args)}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compile-root", type=Path, required=True)
    parser.add_argument(
        "--fixture",
        action="append",
        default=[],
        help="Restrict the audit to one fixture directory name. May be supplied more than once.",
    )
    parser.add_argument(
        "--include-source-record",
        action="store_true",
        help="Include source_record_* atoms. Default excludes them from the typed inventory.",
    )
    parser.add_argument(
        "--include-prose-like",
        action="store_true",
        help="Include text/display/label/description-like predicates and long prose-like arguments.",
    )
    parser.add_argument("--max-examples", type=int, default=5)
    parser.add_argument("--max-predicate-chars", type=int, default=DEFAULT_MAX_PREDICATE_CHARS)
    parser.add_argument("--max-predicate-tokens", type=int, default=DEFAULT_MAX_PREDICATE_TOKENS)
    parser.add_argument("--max-atom-chars", type=int, default=DEFAULT_MAX_ATOM_CHARS)
    parser.add_argument("--max-atom-tokens", type=int, default=DEFAULT_MAX_ATOM_TOKENS)
    parser.add_argument(
        "--enforce-atom-shape",
        action="store_true",
        help="Fail when compiled typed atoms or predicate names look prose-shaped.",
    )
    parser.add_argument(
        "--enforce-registered-signatures",
        action="store_true",
        help="Fail when trusted typed facts use predicate signatures without carrier contracts.",
    )
    parser.add_argument(
        "--enforce-lens-scope",
        action="store_true",
        help=(
            "Fail when a compile artifact with active_profile_registry_lens emits trusted typed facts "
            "outside that lens's allowed_signatures."
        ),
    )
    parser.add_argument(
        "--exit-zero",
        action="store_true",
        help="Write the report but return 0 even when an enforcement option fails.",
    )
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        compile_root=args.compile_root,
        fixtures=set(args.fixture or []),
        include_source_record=bool(args.include_source_record),
        include_prose_like=bool(args.include_prose_like),
        max_examples=max(0, int(args.max_examples)),
        max_predicate_chars=max(1, int(args.max_predicate_chars)),
        max_predicate_tokens=max(1, int(args.max_predicate_tokens)),
        max_atom_chars=max(1, int(args.max_atom_chars)),
        max_atom_tokens=max(1, int(args.max_atom_tokens)),
    )
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    if not args.exit_zero:
        if args.enforce_atom_shape and report.get("atom_shape", {}).get("status") == "fail":
            return 1
        if args.enforce_registered_signatures and report.get("summary", {}).get("unregistered_fact_count", 0):
            return 1
        if args.enforce_lens_scope and report.get("lens_scope", {}).get("status") == "fail":
            return 1
    return 0


def build_report(
    *,
    compile_root: Path,
    fixtures: set[str] | None = None,
    include_source_record: bool = False,
    include_prose_like: bool = False,
    max_examples: int = 5,
    max_predicate_chars: int = DEFAULT_MAX_PREDICATE_CHARS,
    max_predicate_tokens: int = DEFAULT_MAX_PREDICATE_TOKENS,
    max_atom_chars: int = DEFAULT_MAX_ATOM_CHARS,
    max_atom_tokens: int = DEFAULT_MAX_ATOM_TOKENS,
) -> dict[str, Any]:
    fixture_reports: list[dict[str, Any]] = []
    global_signatures: Counter[str] = Counter()
    global_predicates: Counter[str] = Counter()
    global_registered_signatures: Counter[str] = Counter()
    global_unregistered_signatures: Counter[str] = Counter()
    global_arg_kinds: dict[str, list[Counter[str]]] = defaultdict(list)
    signature_fixtures: dict[str, set[str]] = defaultdict(set)
    signature_examples: dict[str, list[str]] = defaultdict(list)
    rejected_counts: Counter[str] = Counter()
    global_shape_issues: list[dict[str, Any]] = []
    global_shape_issue_counts: Counter[str] = Counter()
    global_lens_scope_issues: list[dict[str, Any]] = []
    global_lens_scope_issue_counts: Counter[str] = Counter()

    fixture_dirs = _fixture_dirs(compile_root, fixtures=fixtures)
    for fixture_dir in fixture_dirs:
        compile_json = _latest_compile_json(fixture_dir)
        data = _load_compile_json(compile_json)
        facts, rejected, shape_issues = _typed_facts(
            compile_json,
            include_source_record=include_source_record,
            include_prose_like=include_prose_like,
            max_predicate_chars=max_predicate_chars,
            max_predicate_tokens=max_predicate_tokens,
            max_atom_chars=max_atom_chars,
            max_atom_tokens=max_atom_tokens,
        )
        rejected_counts.update(rejected)
        lens_scope = _lens_scope_for_compile(data)
        lens_scope_issues = _lens_scope_issues(
            facts,
            fixture=fixture_dir.name,
            compile_json=compile_json,
            lens_scope=lens_scope,
        )
        for issue in lens_scope_issues:
            global_lens_scope_issues.append(issue)
            global_lens_scope_issue_counts[str(issue.get("signature", "unknown"))] += 1
        for issue in shape_issues:
            issue = {"fixture": fixture_dir.name, **issue}
            global_shape_issues.append(issue)
            global_shape_issue_counts[str(issue.get("issue_type", "unknown"))] += 1
        signature_counts: Counter[str] = Counter(fact.signature for fact in facts)
        predicate_counts: Counter[str] = Counter(fact.predicate for fact in facts)
        registered_counts: Counter[str] = Counter(
            fact.signature for fact in facts if _is_registered_signature(fact.signature)
        )
        unregistered_counts: Counter[str] = Counter(
            fact.signature for fact in facts if not _is_registered_signature(fact.signature)
        )
        arg_profiles: dict[str, list[Counter[str]]] = defaultdict(list)
        for fact in facts:
            global_signatures[fact.signature] += 1
            global_predicates[fact.predicate] += 1
            if _is_registered_signature(fact.signature):
                global_registered_signatures[fact.signature] += 1
            else:
                global_unregistered_signatures[fact.signature] += 1
            signature_fixtures[fact.signature].add(fixture_dir.name)
            if len(signature_examples[fact.signature]) < max_examples:
                signature_examples[fact.signature].append(fact.clause)
            while len(arg_profiles[fact.signature]) < len(fact.args):
                arg_profiles[fact.signature].append(Counter())
            while len(global_arg_kinds[fact.signature]) < len(fact.args):
                global_arg_kinds[fact.signature].append(Counter())
            for index, arg in enumerate(fact.args):
                kind = _arg_kind(arg)
                arg_profiles[fact.signature][index][kind] += 1
                global_arg_kinds[fact.signature][index][kind] += 1

        fixture_reports.append(
            {
                "fixture": fixture_dir.name,
                "compile_json": str(compile_json),
                "typed_fact_count": len(facts),
                "predicate_count": len(predicate_counts),
                "signature_count": len(signature_counts),
                "signature_names": sorted(signature_counts),
                "registered_fact_count": sum(registered_counts.values()),
                "registered_signature_count": len(registered_counts),
                "registered_fact_rate": _ratio(sum(registered_counts.values()), len(facts)),
                "registered_signature_rate": _ratio(len(registered_counts), len(signature_counts)),
                "unregistered_fact_count": sum(unregistered_counts.values()),
                "unregistered_signature_count": len(unregistered_counts),
                "top_signatures": dict(signature_counts.most_common(25)),
                "top_registered_signatures": dict(registered_counts.most_common(25)),
                "top_unregistered_signatures": dict(unregistered_counts.most_common(25)),
                "top_predicates": dict(predicate_counts.most_common(25)),
                "arg_profiles": _render_arg_profiles(arg_profiles),
                "rejected_counts": dict(sorted(rejected.items())),
                "atom_shape_blocker_count": len(shape_issues),
                "atom_shape_issue_counts": dict(
                    sorted(Counter(str(issue.get("issue_type", "unknown")) for issue in shape_issues).items())
                ),
                "active_profile_registry_lens": lens_scope,
                "lens_scope_blocker_count": len(lens_scope_issues),
                "lens_scope_blocker_signatures": dict(
                    sorted(Counter(str(issue.get("signature", "unknown")) for issue in lens_scope_issues).items())
                ),
            }
        )

    signature_reports: list[dict[str, Any]] = []
    for signature, count in global_signatures.most_common():
        fixture_names = sorted(signature_fixtures.get(signature, set()))
        signature_reports.append(
            {
                "signature": signature,
                "fact_count": count,
                "registered": _is_registered_signature(signature),
                "fixture_count": len(fixture_names),
                "fixtures": fixture_names,
                "arg_profile": [
                    dict(counter.most_common()) for counter in global_arg_kinds.get(signature, [])
                ],
                "examples": signature_examples.get(signature, []),
            }
        )

    overlap = _fixture_overlap(fixture_reports)
    shape_blockers = [issue for issue in global_shape_issues if issue.get("severity") == "blocker"]
    return {
        "schema_version": "kb_atom_inventory_v2",
        "compile_root": str(compile_root),
        "fixtures": sorted(fixtures) if fixtures else "all",
        "settings": {
            "include_source_record": include_source_record,
            "include_prose_like": include_prose_like,
            "max_examples": max_examples,
            "atom_shape": {
                "max_predicate_chars": max_predicate_chars,
                "max_predicate_tokens": max_predicate_tokens,
                "max_atom_chars": max_atom_chars,
                "max_atom_tokens": max_atom_tokens,
                "sentence_stopword_density": SENTENCE_STOPWORD_DENSITY,
                "sentence_stopword_min_tokens": SENTENCE_STOPWORD_MIN_TOKENS,
            },
        },
        "summary": {
            "fixture_count": len(fixture_reports),
            "typed_fact_count": sum(item["typed_fact_count"] for item in fixture_reports),
            "predicate_count": len(global_predicates),
            "signature_count": len(global_signatures),
            "registered_fact_count": sum(global_registered_signatures.values()),
            "registered_signature_count": len(global_registered_signatures),
            "registered_fact_rate": _ratio(
                sum(global_registered_signatures.values()),
                sum(item["typed_fact_count"] for item in fixture_reports),
            ),
            "registered_signature_rate": _ratio(
                len(global_registered_signatures),
                len(global_signatures),
            ),
            "unregistered_fact_count": sum(global_unregistered_signatures.values()),
            "unregistered_signature_count": len(global_unregistered_signatures),
            "rejected_counts": dict(sorted(rejected_counts.items())),
            "atom_shape_blocker_count": len(shape_blockers),
            "lens_scope_blocker_count": len(global_lens_scope_issues),
        },
        "atom_shape": {
            "schema_version": "kb_atom_shape_audit_v1",
            "status": "fail" if shape_blockers else "pass",
            "blocker_count": len(shape_blockers),
            "issue_type_counts": dict(sorted(global_shape_issue_counts.items())),
            "examples": global_shape_issues[:max_examples],
        },
        "lens_scope": {
            "schema_version": "kb_lens_scope_audit_v1",
            "status": "fail" if global_lens_scope_issues else "pass",
            "blocker_count": len(global_lens_scope_issues),
            "signature_counts": dict(sorted(global_lens_scope_issue_counts.items())),
            "examples": global_lens_scope_issues[:max_examples],
        },
        "top_predicates": dict(global_predicates.most_common(50)),
        "top_signatures": dict(global_signatures.most_common(50)),
        "top_registered_signatures": dict(global_registered_signatures.most_common(50)),
        "top_unregistered_signatures": dict(global_unregistered_signatures.most_common(50)),
        "signatures": signature_reports,
        "fixtures_detail": fixture_reports,
        "fixture_signature_overlap": overlap,
    }


def _fixture_dirs(compile_root: Path, *, fixtures: set[str] | None = None) -> list[Path]:
    dirs = [path for path in compile_root.iterdir() if path.is_dir()]
    if fixtures:
        dirs = [path for path in dirs if path.name in fixtures]
    return sorted(dirs, key=lambda path: path.name)


def _is_registered_signature(signature: str) -> bool:
    return carrier_contract(signature) is not None


def _ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def _latest_compile_json(path: Path) -> Path:
    candidates = sorted(path.glob("*.json"), key=lambda item: item.stat().st_mtime)
    if not candidates:
        raise FileNotFoundError(f"No compile JSON found under {path}")
    return candidates[-1]


def _load_compile_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _typed_facts(
    path: Path,
    *,
    include_source_record: bool,
    include_prose_like: bool,
    max_predicate_chars: int = DEFAULT_MAX_PREDICATE_CHARS,
    max_predicate_tokens: int = DEFAULT_MAX_PREDICATE_TOKENS,
    max_atom_chars: int = DEFAULT_MAX_ATOM_CHARS,
    max_atom_tokens: int = DEFAULT_MAX_ATOM_TOKENS,
) -> tuple[list[ParsedFact], Counter[str], list[dict[str, Any]]]:
    data = _load_compile_json(path)
    facts = data.get("source_compile", {}).get("facts", [])
    out: list[ParsedFact] = []
    rejected: Counter[str] = Counter()
    shape_issues: list[dict[str, Any]] = []
    for clause in facts:
        fact = _parse_fact(str(clause))
        if fact is None:
            rejected["unparsed"] += 1
            continue
        if not fact.predicate.startswith(SOURCE_RECORD_PREFIX):
            shape_issues.extend(
                _atom_shape_issues(
                    fact,
                    max_predicate_chars=max_predicate_chars,
                    max_predicate_tokens=max_predicate_tokens,
                    max_atom_chars=max_atom_chars,
                    max_atom_tokens=max_atom_tokens,
                )
            )
        if fact.predicate.startswith(SOURCE_RECORD_PREFIX) and not include_source_record:
            rejected["source_record"] += 1
            continue
        if _is_prose_like_fact(fact) and not include_prose_like:
            rejected["prose_like"] += 1
            continue
        out.append(fact)
    return out, rejected, shape_issues


def _lens_scope_for_compile(data: dict[str, Any]) -> dict[str, Any] | None:
    if isinstance(data.get("union_source_compile"), dict):
        return None
    if str(data.get("mode", "")).strip() == "deterministic_compile_union":
        return None
    active_lens = data.get("active_profile_registry_lens")
    if not isinstance(active_lens, dict):
        return None
    lens_id = str(active_lens.get("id", "")).strip()
    allowed = {
        str(signature).strip()
        for signature in active_lens.get("allowed_signatures", [])
        if str(signature).strip()
    }
    if not lens_id or not allowed:
        return None
    return {
        "id": lens_id,
        "allowed_signatures": sorted(allowed),
    }


def _lens_scope_issues(
    facts: list[ParsedFact],
    *,
    fixture: str,
    compile_json: Path,
    lens_scope: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if not lens_scope:
        return []
    allowed = {
        str(signature).strip()
        for signature in lens_scope.get("allowed_signatures", [])
        if str(signature).strip()
    }
    if not allowed:
        return []
    out: list[dict[str, Any]] = []
    for fact in facts:
        if fact.signature in allowed:
            continue
        out.append(
            {
                "severity": "blocker",
                "fixture": fixture,
                "compile_json": str(compile_json),
                "lens_id": str(lens_scope.get("id", "")),
                "signature": fact.signature,
                "allowed_signatures": sorted(allowed),
                "clause": fact.clause,
            }
        )
    return out


def _parse_fact(clause: str) -> ParsedFact | None:
    text = clause.strip()
    if text.endswith("."):
        text = text[:-1]
    match = re.match(r"^(?P<predicate>[a-z][a-zA-Z0-9_]*)\((?P<args>.*)\)$", text)
    if not match:
        return None
    return ParsedFact(
        predicate=match.group("predicate"),
        args=tuple(_split_args(match.group("args"))),
        clause=clause.strip(),
    )


def _split_args(text: str) -> list[str]:
    args: list[str] = []
    current: list[str] = []
    quote = ""
    depth = 0
    index = 0
    while index < len(text):
        char = text[index]
        if quote:
            current.append(char)
            if char == "\\" and index + 1 < len(text):
                index += 1
                current.append(text[index])
            elif char == quote:
                quote = ""
        else:
            if char in {"'", '"'}:
                quote = char
                current.append(char)
            elif char == "(":
                depth += 1
                current.append(char)
            elif char == ")":
                depth = max(0, depth - 1)
                current.append(char)
            elif char == "," and depth == 0:
                args.append("".join(current).strip())
                current = []
            else:
                current.append(char)
        index += 1
    if current or text:
        args.append("".join(current).strip())
    return args


def _atom_shape_issues(
    fact: ParsedFact,
    *,
    max_predicate_chars: int,
    max_predicate_tokens: int,
    max_atom_chars: int,
    max_atom_tokens: int,
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    predicate_tokens = _atom_tokens(fact.predicate)
    if len(fact.predicate) > max_predicate_chars:
        issues.append(
            _shape_issue(
                fact=fact,
                issue_type="predicate_name_too_long",
                field="predicate",
                value=fact.predicate,
                metrics={"chars": len(fact.predicate), "limit": max_predicate_chars},
            )
        )
    if len(predicate_tokens) > max_predicate_tokens:
        issues.append(
            _shape_issue(
                fact=fact,
                issue_type="predicate_name_too_many_tokens",
                field="predicate",
                value=fact.predicate,
                metrics={"tokens": len(predicate_tokens), "limit": max_predicate_tokens},
            )
        )
    if _sentence_like_tokens(predicate_tokens):
        issues.append(
            _shape_issue(
                fact=fact,
                issue_type="predicate_name_sentence_like",
                field="predicate",
                value=fact.predicate,
                metrics=_sentence_like_metrics(predicate_tokens),
            )
        )

    registered = _is_registered_signature(fact.signature)
    for index, raw_arg in enumerate(fact.args, start=1):
        value = str(raw_arg or "").strip().strip("'\"")
        if not value or _arg_kind(raw_arg) in {"integer", "decimal", "date_atom", "boolean_atom", "source_coord"}:
            continue
        tokens = _atom_tokens(value)
        base_issue_type = "registered_carrier_prose_shaped_value" if registered else "atom_value_prose_shaped"
        if len(value) > max_atom_chars:
            issues.append(
                _shape_issue(
                    fact=fact,
                    issue_type=base_issue_type,
                    field=f"arg{index}",
                    value=value,
                    metrics={"chars": len(value), "limit": max_atom_chars, "reason": "too_long"},
                )
            )
        if len(tokens) > max_atom_tokens:
            issues.append(
                _shape_issue(
                    fact=fact,
                    issue_type=base_issue_type,
                    field=f"arg{index}",
                    value=value,
                    metrics={"tokens": len(tokens), "limit": max_atom_tokens, "reason": "too_many_tokens"},
                )
            )
        if _sentence_like_tokens(tokens):
            issues.append(
                _shape_issue(
                    fact=fact,
                    issue_type=base_issue_type,
                    field=f"arg{index}",
                    value=value,
                    metrics={**_sentence_like_metrics(tokens), "reason": "sentence_like_stopwords"},
                )
            )
    return issues


def _shape_issue(
    *,
    fact: ParsedFact,
    issue_type: str,
    field: str,
    value: str,
    metrics: dict[str, Any],
) -> dict[str, Any]:
    return {
        "severity": "blocker",
        "issue_type": issue_type,
        "signature": fact.signature,
        "registered": _is_registered_signature(fact.signature),
        "field": field,
        "value": value,
        "metrics": metrics,
        "clause": fact.clause,
    }


def _atom_tokens(value: str) -> list[str]:
    return [token for token in re.split(r"[^A-Za-z0-9]+", str(value or "").casefold()) if token]


def _sentence_like_tokens(tokens: list[str]) -> bool:
    if len(tokens) < SENTENCE_STOPWORD_MIN_TOKENS:
        return False
    stopword_count = sum(1 for token in tokens if token in ATOM_SHAPE_STOPWORDS)
    density = stopword_count / len(tokens) if tokens else 0.0
    return stopword_count >= SENTENCE_STOPWORD_MIN_COUNT and density >= SENTENCE_STOPWORD_DENSITY


def _sentence_like_metrics(tokens: list[str]) -> dict[str, Any]:
    stopword_count = sum(1 for token in tokens if token in ATOM_SHAPE_STOPWORDS)
    density = round(stopword_count / len(tokens), 6) if tokens else 0.0
    return {
        "tokens": len(tokens),
        "stopword_count": stopword_count,
        "stopword_density": density,
        "limit": SENTENCE_STOPWORD_DENSITY,
    }


def _is_prose_like_fact(fact: ParsedFact) -> bool:
    predicate = fact.predicate.casefold()
    tokens = [token for token in re.split(r"[^a-z0-9]+", predicate) if token]
    if any(hint in tokens for hint in FREE_TEXT_PREDICATE_HINTS):
        return True
    return any(_arg_kind(arg) == "long_text" for arg in fact.args)


def _arg_kind(arg: str) -> str:
    raw = str(arg or "").strip()
    value = raw.strip("'\"")
    if SOURCE_COORD_RE.search(value):
        return "source_coord"
    if raw.startswith("'") or raw.startswith('"'):
        if _looks_long_text(value):
            return "long_text"
        return "quoted_atom"
    if INTEGER_RE.match(value):
        return "integer"
    if DECIMAL_RE.match(value):
        return "decimal"
    if DATE_ATOM_RE.match(value):
        return "date_atom"
    if value in {"true", "false", "yes", "no"}:
        return "boolean_atom"
    if _looks_long_text(value):
        return "long_text"
    if "_" in value:
        return "compound_atom"
    return "atom"


def _looks_long_text(value: str) -> bool:
    tokens = [token for token in re.split(r"[^A-Za-z0-9]+", value) if token]
    return len(value) > 90 and len(tokens) > 8 or len(tokens) > 14


def _render_arg_profiles(value: dict[str, list[Counter[str]]]) -> dict[str, list[dict[str, int]]]:
    return {
        signature: [dict(counter.most_common()) for counter in counters]
        for signature, counters in sorted(value.items())
    }


def _fixture_overlap(fixture_reports: list[dict[str, Any]]) -> list[dict[str, Any]]:
    fixture_sets: dict[str, set[str]] = {
        item["fixture"]: set(item.get("signature_names") or item["top_signatures"].keys())
        for item in fixture_reports
    }
    names = sorted(fixture_sets)
    rows: list[dict[str, Any]] = []
    for index, left in enumerate(names):
        for right in names[index + 1 :]:
            a = fixture_sets[left]
            b = fixture_sets[right]
            union = a | b
            rows.append(
                {
                    "left": left,
                    "right": right,
                    "intersection": len(a & b),
                    "union": len(union),
                    "jaccard": round(len(a & b) / len(union), 6) if union else 0.0,
                }
            )
    return rows


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# KB Atom Inventory",
        "",
        f"- Schema: `{report['schema_version']}`",
        f"- Compile root: `{report['compile_root']}`",
        f"- Fixtures: `{report['fixtures']}`",
        f"- Include source records: `{report['settings']['include_source_record']}`",
        f"- Include prose-like atoms: `{report['settings']['include_prose_like']}`",
        "",
        "## Summary",
        "",
        f"- Fixtures: `{summary['fixture_count']}`",
        f"- Typed facts: `{summary['typed_fact_count']}`",
        f"- Predicates: `{summary['predicate_count']}`",
        f"- Signatures: `{summary['signature_count']}`",
        f"- Registered facts: `{summary['registered_fact_count']}` (`{summary['registered_fact_rate']}`)",
        f"- Registered signatures: `{summary['registered_signature_count']}` (`{summary['registered_signature_rate']}`)",
        f"- Unregistered facts: `{summary['unregistered_fact_count']}`",
        f"- Unregistered signatures: `{summary['unregistered_signature_count']}`",
        f"- Rejected: `{summary['rejected_counts']}`",
        f"- Atom-shape status: `{report['atom_shape']['status']}` blockers=`{report['atom_shape']['blocker_count']}`",
        f"- Lens-scope status: `{report['lens_scope']['status']}` blockers=`{report['lens_scope']['blocker_count']}`",
        "",
        "## Atom Shape",
        "",
        f"- Status: `{report['atom_shape']['status']}`",
        f"- Blockers: `{report['atom_shape']['blocker_count']}`",
        f"- Issue types: `{report['atom_shape']['issue_type_counts']}`",
        "",
        "| Fixture | Signature | Field | Issue | Value |",
        "| --- | --- | --- | --- | --- |",
    ]
    for issue in report["atom_shape"].get("examples", []):
        value = str(issue.get("value", ""))
        if len(value) > 96:
            value = value[:93] + "..."
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                issue.get("fixture", ""),
                issue.get("signature", ""),
                issue.get("field", ""),
                issue.get("issue_type", ""),
                value.replace("|", "\\|"),
            )
        )
    lines.extend(
        [
            "",
            "## Lens Scope",
            "",
            f"- Status: `{report['lens_scope']['status']}`",
            f"- Blockers: `{report['lens_scope']['blocker_count']}`",
            f"- Signatures: `{report['lens_scope']['signature_counts']}`",
            "",
            "| Fixture | Lens | Signature | Clause |",
            "| --- | --- | --- | --- |",
        ]
    )
    for issue in report["lens_scope"].get("examples", []):
        clause = str(issue.get("clause", ""))
        if len(clause) > 120:
            clause = clause[:117] + "..."
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` |".format(
                issue.get("fixture", ""),
                issue.get("lens_id", ""),
                issue.get("signature", ""),
                clause.replace("|", "\\|"),
            )
        )
    lines.extend(
        [
            "",
        "## Top Registered Signatures",
        "",
        "| Signature | Facts |",
        "| --- | ---: |",
        ]
    )
    for signature, count in report.get("top_registered_signatures", {}).items():
        lines.append(f"| `{signature}` | {count} |")
    lines.extend(
        [
            "",
            "## Top Unregistered Signatures",
            "",
            "| Signature | Facts |",
            "| --- | ---: |",
        ]
    )
    for signature, count in report.get("top_unregistered_signatures", {}).items():
        lines.append(f"| `{signature}` | {count} |")
    lines.extend(
        [
            "",
            "## Top Signatures",
            "",
            "| Signature | Governance | Facts | Fixtures | Arg profile |",
            "| --- | --- | ---: | ---: | --- |",
        ]
    )
    for item in report["signatures"][:40]:
        governance = "registered" if item.get("registered") else "unregistered"
        lines.append(
            "| `{}` | {} | {} | {} | `{}` |".format(
                item["signature"],
                governance,
                item["fact_count"],
                item["fixture_count"],
                item["arg_profile"],
            )
        )
    lines.extend(
        [
            "",
            "## By Fixture",
            "",
            "| Fixture | Typed facts | Registered facts | Registered rate | Unregistered facts | Predicates | Signatures | Top registered | Top unregistered |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for item in report["fixtures_detail"]:
        top_registered = ", ".join(
            f"`{sig}`={count}" for sig, count in list(item["top_registered_signatures"].items())[:5]
        )
        top_unregistered = ", ".join(
            f"`{sig}`={count}" for sig, count in list(item["top_unregistered_signatures"].items())[:5]
        )
        lines.append(
            "| `{}` | {} | {} | {} | {} | {} | {} | {} | {} |".format(
                item["fixture"],
                item["typed_fact_count"],
                item["registered_fact_count"],
                item["registered_fact_rate"],
                item["unregistered_fact_count"],
                item["predicate_count"],
                item["signature_count"],
                top_registered,
                top_unregistered,
            )
        )
    lines.extend(
        [
            "",
            "## Predicate Overlap",
            "",
            "| Left | Right | Intersection | Union | Jaccard |",
            "| --- | --- | ---: | ---: | ---: |",
        ]
    )
    for item in report["fixture_signature_overlap"]:
        lines.append(
            "| `{}` | `{}` | {} | {} | {} |".format(
                item["left"],
                item["right"],
                item["intersection"],
                item["union"],
                item["jaccard"],
            )
        )
    lines.extend(
        [
            "",
            "## Note",
            "",
            "This report describes the compiled atom library only. It does not read source prose, QA questions, or oracle answers, and it is not a query router.",
        ]
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
