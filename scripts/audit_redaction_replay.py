#!/usr/bin/env python3
"""Audit whether QA exact rows survive source-prose redaction.

This audit prints two numbers:

- product exact: the normal QA judge verdict.
- thesis exact: exact rows whose support survives after source/display prose is
  removed from the evidence surface.

By default the thesis number uses a strict deterministic proxy: the reference
answer must be present in typed scalar values from non-prose query rows. With
``--rejudge-redacted`` the script re-runs the QA judge on redacted query
results, which is slower and spends model calls, but closer to the current QA
contract.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.run_domain_bootstrap_qa import (  # noqa: E402
    SemanticIRCallConfig,
    judge_reference_answer,
)
from src.model_path import openrouter_api_key  # noqa: E402


PROSE_FIELD_RE = re.compile(
    r"(?:"
    r"^utterance$|^question$|^raw_|"
    r"^note$|^message$|^purpose$|^policy$|^original_query$|^repaired_query$|^_?description$|^value$|"
    r"textdisplay$|windowtextdisplay$|definitiontext$|display$|displayvalue$|"
    r"_display$|text_atom$|textatom$|surface_text|snippet|passage|prose|narrative"
    r")",
    re.IGNORECASE,
)

TYPED_METADATA_FIELDS = {
    "predicate",
    "prolog_query",
    "result_type",
    "status",
    "num_rows",
    "variables",
    "query",
    "derived_from_queries",
}

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="QA JSON file(s) or directories containing QA JSON files.")
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--rejudge-redacted", action="store_true", help="Spend model calls to rejudge redacted evidence.")
    parser.add_argument("--model", default="qwen/qwen3.6-35b-a3b")
    parser.add_argument("--base-url", default="https://openrouter.ai/api/v1")
    parser.add_argument("--timeout", type=int, default=420)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--max-tokens", type=int, default=1200)
    parser.add_argument("--api-key", default=openrouter_api_key())
    parser.add_argument("--exit-zero", action="store_true", help="Report without failing. Do not use for gates.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    qa_files = sorted({file.resolve() for path in args.paths for file in _iter_qa_files(path)})
    config = None
    if args.rejudge_redacted:
        config = SemanticIRCallConfig(
            backend="lmstudio",
            base_url=str(args.base_url),
            model=str(args.model),
            timeout=int(args.timeout),
            temperature=float(args.temperature),
            top_p=float(args.top_p),
            max_tokens=int(args.max_tokens),
            api_key=str(args.api_key or ""),
            think_enabled=False,
            reasoning_effort="none",
        )
    report = build_report(qa_files=qa_files, config=config)
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    blocked = report["summary"]["prose_dependent_exact"] > 0 or bool(report["summary"]["unclassified_fields"])
    return 0 if args.exit_zero or not blocked else 1


def build_report(*, qa_files: list[Path], config: SemanticIRCallConfig | None = None) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    verdict_counts: Counter[str] = Counter()
    thesis_counts: Counter[str] = Counter()
    by_fixture: dict[str, Counter[str]] = defaultdict(Counter)
    predicate_counts: Counter[str] = Counter()
    redacted_predicates: Counter[str] = Counter()
    unclassified_fields: set[str] = set()

    for qa_file in qa_files:
        data = json.loads(qa_file.read_text(encoding="utf-8"))
        fixture_hint = qa_file.parent.name
        for row in data.get("rows", []) or []:
            if not isinstance(row, dict):
                continue
            fixture = str(row.get("fixture") or row.get("fixture_name") or fixture_hint)
            verdict = str((row.get("reference_judge") or {}).get("verdict", "")).strip() or "unjudged"
            verdict_counts[verdict] += 1
            if verdict != "exact":
                continue
            redacted_row, redaction = _redacted_row(row, unclassified_fields=unclassified_fields)
            for predicate in redaction["kept_predicates"]:
                predicate_counts[predicate] += 1
            for predicate in redaction["redacted_predicates"]:
                redacted_predicates[predicate] += 1
            survived, reason, redacted_verdict, redacted_judge = _row_survived(
                row,
                redacted_row=redacted_row,
                config=config,
            )
            thesis_counts["survived" if survived else "prose_dependent"] += 1
            by_fixture[fixture]["survived" if survived else "prose_dependent"] += 1
            rows.append(
                {
                    "fixture": fixture,
                    "id": row.get("id", ""),
                    "question": row.get("utterance", ""),
                    "reference_answer": row.get("reference_answer", ""),
                    "product_verdict": verdict,
                    "thesis_verdict": "survived" if survived else "prose_dependent",
                    "redacted_rejudge_verdict": redacted_verdict,
                    "redacted_rejudge": redacted_judge,
                    "reason": reason,
                    "kept_predicates": redaction["kept_predicates"],
                    "redacted_predicates": redaction["redacted_predicates"],
                }
            )

    total_rows = sum(verdict_counts.values())
    product_exact = verdict_counts.get("exact", 0)
    thesis_exact = thesis_counts.get("survived", 0)
    report = {
        "schema_version": "redaction_replay_audit_v1",
        "qa_file_count": len(qa_files),
        "mode": "redacted_rejudge" if config is not None else "strict_proxy",
        "summary": {
            "row_count": total_rows,
            "product_exact": product_exact,
            "product_exact_rate": _share(product_exact, total_rows),
            "thesis_exact": thesis_exact,
            "thesis_exact_rate": _share(thesis_exact, total_rows),
            "prose_dependent_exact": thesis_counts.get("prose_dependent", 0),
            "prose_crutch_points": _share(product_exact - thesis_exact, total_rows),
            "verdict_counts": dict(sorted(verdict_counts.items())),
            "unclassified_fields": sorted(unclassified_fields),
        },
        "by_fixture": {fixture: dict(counts) for fixture, counts in sorted(by_fixture.items())},
        "kept_predicate_counts": dict(predicate_counts.most_common(40)),
        "redacted_predicate_counts": dict(redacted_predicates.most_common(40)),
        "rows": rows,
    }
    return report


def _iter_qa_files(path: Path) -> list[Path]:
    if path.is_file() and path.suffix.lower() == ".json":
        return [path]
    if not path.exists():
        return []
    out: list[Path] = []
    for candidate in path.rglob("*.json"):
        if candidate.name.startswith("redaction_replay_"):
            continue
        try:
            text = candidate.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if '"rows"' in text and '"reference_judge"' in text:
            out.append(candidate)
    return out


def _redacted_row(row: dict[str, Any], *, unclassified_fields: set[str]) -> tuple[dict[str, Any], dict[str, list[str]]]:
    kept: list[dict[str, Any]] = []
    kept_predicates: list[str] = []
    redacted_predicates: list[str] = []
    for query_result in row.get("query_results", []) or []:
        result = query_result.get("result") if isinstance(query_result, dict) else None
        if not isinstance(result, dict):
            continue
        predicate = str(result.get("predicate", "")).strip()
        if _is_prose_predicate(predicate):
            redacted_predicates.append(predicate or "<unknown>")
            continue
        redacted_result = _redact_value(result, unclassified_fields=unclassified_fields)
        kept.append({**query_result, "result": redacted_result})
        if predicate:
            kept_predicates.append(predicate)
    redacted_row = {
        **row,
        "query_results": kept,
        "redaction_replay": {
            "redacted_predicates": sorted(set(redacted_predicates)),
            "kept_predicates": sorted(set(kept_predicates)),
        },
    }
    return redacted_row, {
        "kept_predicates": sorted(set(kept_predicates)),
        "redacted_predicates": sorted(set(redacted_predicates)),
    }


def _redact_value(value: Any, *, unclassified_fields: set[str], field_name: str = "") -> Any:
    if isinstance(value, list):
        return [_redact_value(item, unclassified_fields=unclassified_fields, field_name=field_name) for item in value]
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, inner in value.items():
            key_text = str(key)
            if _is_prose_field(key_text):
                continue
            if isinstance(inner, (dict, list)):
                out[key_text] = _redact_value(inner, unclassified_fields=unclassified_fields, field_name=key_text)
            elif _is_metadata_field(key_text) or _is_typed_scalar(inner):
                out[key_text] = inner
            else:
                unclassified_fields.add(key_text)
        return out
    return value


def _row_survived(
    row: dict[str, Any],
    *,
    redacted_row: dict[str, Any],
    config: SemanticIRCallConfig | None,
) -> tuple[bool, str, str, dict[str, Any]]:
    if config is not None:
        judge = judge_reference_answer(row=redacted_row, config=config, sign_clean_strict=True)
        verdict = str(judge.get("verdict", "")).strip()
        return verdict == "exact", f"redacted rejudge verdict={verdict or 'missing'}", verdict, judge
    reference = str(row.get("reference_answer", "")).strip()
    typed_values = set()
    for query_result in redacted_row.get("query_results", []) or []:
        typed_values.update(_collect_typed_result_row_scalars(query_result.get("result", {})))
    normalized_reference = _normalize(reference)
    if normalized_reference and normalized_reference in typed_values:
        return True, "full reference answer present as typed scalar", "proxy_exact", {}
    compact_reference = _compact_alnum(reference)
    if compact_reference and compact_reference in typed_values:
        return True, "full compact reference answer present as typed scalar", "proxy_exact", {}
    reference_parts = _reference_answer_parts(reference)
    if reference_parts and all(part in typed_values for part in reference_parts):
        return True, "all structured reference answer parts present as typed scalars", "proxy_exact", {}
    return False, "strict proxy did not find the full reference answer as a typed scalar", "proxy_miss", {}


def _collect_typed_result_row_scalars(result: Any) -> set[str]:
    if not isinstance(result, dict):
        return set()
    rows = result.get("rows")
    if not isinstance(rows, list):
        return set()
    out: set[str] = set()
    for row in rows:
        if isinstance(row, dict):
            out.update(_collect_typed_scalars(row))
    return out


def _collect_typed_scalars(value: Any, *, field_name: str = "") -> set[str]:
    out: set[str] = set()
    if isinstance(value, dict):
        for key, inner in value.items():
            out.update(_collect_typed_scalars(inner, field_name=str(key)))
    elif isinstance(value, list):
        for inner in value:
            out.update(_collect_typed_scalars(inner, field_name=field_name))
    elif _is_typed_scalar(value):
        if _is_prose_field(field_name):
            return out
        if _is_result_metadata_field(field_name):
            return out
        out.update(_typed_scalar_normalization_variants(value))
    return out


def _reference_answer_parts(reference: str) -> set[str]:
    parts: set[str] = set()
    for chunk in re.split(r"[;,]|\band\b|\balso\b", str(reference or ""), flags=re.IGNORECASE):
        normalized = _normalize(chunk).strip(".")
        if not normalized:
            continue
        if len(normalized) < 3:
            continue
        if normalized in {"the", "and", "also", "issued", "decided", "filed"}:
            continue
        identifier_tokens = _reference_identifier_tokens(chunk)
        if identifier_tokens and re.search(
            r"\b(?:ein|id|identifier|identification|number|no|file|docket|accession)\b",
            str(chunk or ""),
            flags=re.IGNORECASE,
        ):
            parts.update(identifier_tokens)
            continue
        parts.add(normalized)
    return parts


def _reference_identifier_tokens(value: str) -> set[str]:
    tokens: set[str] = set()
    for match in re.finditer(r"\b[A-Za-z]*\d[A-Za-z0-9_./#:-]*\b", str(value or "")):
        token = match.group(0).strip(".")
        normalized = _normalize(token)
        if normalized:
            tokens.add(normalized)
    return tokens


def _typed_scalar_normalization_variants(value: Any) -> set[str]:
    text = str(value or "").strip()
    candidates = {text}
    if "_" in text:
        candidates.add(text.replace("_", " "))
        candidates.add(text.replace("_", "-"))
    out = {_normalize(candidate) for candidate in candidates}
    compact = _compact_alnum(text)
    if compact:
        out.add(compact)
    return {item for item in out if item}


def _compact_alnum(value: Any) -> str:
    text = str(value or "").casefold().replace("_", " ")
    compact = re.sub(r"[^a-z0-9]+", "", text)
    if len(compact) < 8 or not re.search(r"\d", compact):
        return ""
    return compact


def _is_prose_predicate(predicate: str) -> bool:
    text = str(predicate or "").strip()
    if not text:
        return False
    return text.startswith("source_record_")


def _is_prose_field(field_name: str) -> bool:
    text = str(field_name or "")
    if re.fullmatch(r"BoundArg\d+Display", text):
        return False
    return bool(PROSE_FIELD_RE.search(text))


def _is_metadata_field(field_name: str) -> bool:
    text = str(field_name or "").strip()
    if text in TYPED_METADATA_FIELDS:
        return True
    if re.fullmatch(r"[A-Z][A-Za-z0-9_]*", text):
        return True
    if re.fullmatch(r"_[A-Z][A-Za-z0-9_]*", text):
        return True
    if text.startswith("BoundArg"):
        return True
    return False


def _is_result_metadata_field(field_name: str) -> bool:
    return str(field_name or "").strip() in TYPED_METADATA_FIELDS


def _is_typed_scalar(value: Any) -> bool:
    if isinstance(value, (int, float, bool)):
        return True
    if not isinstance(value, str):
        return False
    text = value.strip()
    if not text:
        return False
    if len(text) > 160:
        return False
    if " " in text and not re.fullmatch(r"[A-Za-z0-9_.:/#-]+", text):
        return False
    return True


def _normalize(value: Any) -> str:
    text = str(value or "").strip().casefold()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^a-z0-9_./#:-]+", " ", text)
    return " ".join(text.split())


def _share(count: int, total: int) -> float:
    return round(count / total, 6) if total else 0.0


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Redaction Replay Audit",
        "",
        f"- Schema: `{report['schema_version']}`",
        f"- Mode: `{report['mode']}`",
        f"- QA files: `{report['qa_file_count']}`",
        f"- Rows: `{summary['row_count']}`",
        f"- Product exact: `{summary['product_exact']}` / `{summary['row_count']}` = `{summary['product_exact_rate']:.2%}`",
        f"- Thesis exact: `{summary['thesis_exact']}` / `{summary['row_count']}` = `{summary['thesis_exact_rate']:.2%}`",
        f"- Prose-dependent exact rows: `{summary['prose_dependent_exact']}`",
        f"- Prose crutch points: `{summary['prose_crutch_points']:.2%}`",
        "",
        "## By Fixture",
        "",
        "| Fixture | Survived | Prose-dependent |",
        "| --- | ---: | ---: |",
    ]
    for fixture, counts in report["by_fixture"].items():
        lines.append(f"| `{fixture}` | {counts.get('survived', 0)} | {counts.get('prose_dependent', 0)} |")
    if summary["unclassified_fields"]:
        lines.extend(["", "## Unclassified Fields", ""])
        for field in summary["unclassified_fields"]:
            lines.append(f"- `{field}`")
    examples = [row for row in report["rows"] if row["thesis_verdict"] == "prose_dependent"][:40]
    if examples:
        lines.extend(["", "## Prose-Dependent Exact Rows", "", "| Fixture | Row | Reason |", "| --- | --- | --- |"])
        for row in examples:
            lines.append(f"| `{row['fixture']}` | `{row['id']}` | {_md_cell(row['reason'])} |")
    return "\n".join(lines).rstrip() + "\n"


def _md_cell(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


if __name__ == "__main__":
    raise SystemExit(main())
