#!/usr/bin/env python3
"""Summarize hard-clean results by answer class.

This is an analysis-only reporting tool. It may inspect question text,
reference answers, query intents, and returned predicates to label rows for
research triage. Those labels are not part of compile, query, scoring, or tier
assignment, and must not be copied into the runtime instrument.

The purpose is to answer the domain-wedge question:

    Are hard-clean wins mostly scaffolding, or do substantive classes survive?
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hard-road-json", type=Path, required=True)
    parser.add_argument("--qa-root", type=Path, required=True)
    parser.add_argument("--dataset-root", type=Path, default=None)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        hard_road_json=args.hard_road_json,
        qa_root=args.qa_root,
        dataset_root=args.dataset_root,
    )
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def build_report(*, hard_road_json: Path, qa_root: Path, dataset_root: Path | None = None) -> dict[str, Any]:
    hard = json.loads(hard_road_json.read_text(encoding="utf-8"))
    qa_rows = _load_qa_rows(qa_root)
    metadata = _load_fixture_metadata(dataset_root) if dataset_root else {}

    rows: list[dict[str, Any]] = []
    by_class: dict[str, Counter[str]] = defaultdict(Counter)
    by_family: dict[str, Counter[str]] = defaultdict(Counter)
    by_substance: dict[str, Counter[str]] = defaultdict(Counter)
    by_class_family: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    failure_by_class: dict[str, Counter[str]] = defaultdict(Counter)

    for hard_row in hard.get("rows", []) or []:
        if not isinstance(hard_row, dict):
            continue
        fixture = str(hard_row.get("fixture", "")).strip()
        row_id = str(hard_row.get("id", "")).strip()
        qa_row = qa_rows.get((fixture, row_id), {})
        family = str(metadata.get(fixture, {}).get("source_family") or _fixture_family(fixture))
        answer_class = classify_answer_class(qa_row=qa_row, hard_row=hard_row)
        substance = _substance_band(answer_class)
        product_exact = str(hard_row.get("product_verdict", "")).strip() == "exact"
        typed_full = str(hard_row.get("typed_plan_status", "")).strip() == "all_queries_success"
        redaction_survived = str(hard_row.get("redaction_thesis_verdict", "")).strip() == "survived"
        atom_clean = bool(hard_row.get("atom_shape_clean"))
        hard_clean = bool(hard_row.get("hard_clean"))
        failure_reasons = _failure_reasons(
            product_exact=product_exact,
            typed_full=typed_full,
            redaction_survived=redaction_survived,
            atom_clean=atom_clean,
        )

        row = {
            "fixture": fixture,
            "source_family": family,
            "id": row_id,
            "answer_class": answer_class,
            "substance_band": substance,
            "product_verdict": str(hard_row.get("product_verdict", "")).strip(),
            "typed_plan_status": str(hard_row.get("typed_plan_status", "")).strip(),
            "redaction_thesis_verdict": str(hard_row.get("redaction_thesis_verdict", "")).strip(),
            "atom_shape_clean": atom_clean,
            "hard_clean": hard_clean,
            "failure_reasons": failure_reasons,
            "question": str(qa_row.get("utterance", "")).strip(),
            "reference_answer": str(hard_row.get("reference_answer", "")).strip(),
        }
        rows.append(row)
        for counter in (
            by_class[answer_class],
            by_family[family],
            by_substance[substance],
            by_class_family[(answer_class, family)],
        ):
            _add_counts(
                counter,
                product_exact=product_exact,
                typed_full=typed_full,
                redaction_survived=redaction_survived,
                atom_clean=atom_clean,
                hard_clean=hard_clean,
            )
        for reason in failure_reasons:
            failure_by_class[answer_class][reason] += 1

    return {
        "schema_version": "hard_clean_answer_class_summary_v1",
        "hard_road_json": str(hard_road_json),
        "qa_root": str(qa_root),
        "dataset_root": str(dataset_root) if dataset_root else "",
        "summary": _summary(rows),
        "by_substance_band": {
            key: _counter_summary(counter) for key, counter in sorted(by_substance.items())
        },
        "by_answer_class": {
            key: {
                **_counter_summary(counter),
                "failure_reasons": dict(failure_by_class.get(key, Counter()).most_common()),
            }
            for key, counter in sorted(by_class.items(), key=lambda item: (-item[1]["row_count"], item[0]))
        },
        "by_source_family": {
            key: _counter_summary(counter)
            for key, counter in sorted(by_family.items(), key=lambda item: (-item[1]["row_count"], item[0]))
        },
        "by_answer_class_and_source_family": {
            f"{answer_class}::{family}": _counter_summary(counter)
            for (answer_class, family), counter in sorted(
                by_class_family.items(),
                key=lambda item: (-item[1]["row_count"], item[0][0], item[0][1]),
            )
        },
        "rows": rows,
    }


def classify_answer_class(*, qa_row: dict[str, Any], hard_row: dict[str, Any]) -> str:
    question = str(qa_row.get("utterance", ""))
    reference = str(hard_row.get("reference_answer", "") or qa_row.get("reference_answer", ""))
    text = f"{question}\n{reference}".casefold()
    intents = {
        str(item.get("intent_type", "")).strip()
        for item in qa_row.get("query_intents", []) or []
        if isinstance(item, dict)
    }
    predicates = _row_predicates(qa_row)
    has_identifier = _has(text, r"\b(identifier|docket|number|no\.|marcs|cms|fei|accession|application|warning letter|patent publication|ein|id)\b")
    has_date = _has(text, r"\b(date|dates|issued|filed|published|inspection|meeting|responded|effective)\b") or "date" in intents
    has_outcome = _has(text, r"\b(disposition|affirmed|denied|granted|dismissed|approved|rejected|status|outcome|decision|decided)\b")

    if _has(text, r"\b(contact|email|telephone|phone|fax)\b"):
        return "contact"
    if has_identifier and (has_date or has_outcome):
        return "document_metadata_bundle"
    if _has(
        text,
        r"\b(address|street address|street|postal|zip|principal place of business|place of business|"
        r"city and state|city, state|state of incorporation|state of formation|located \(city, state\))\b",
    ):
        return "address_location"
    if _has(text, r"\b(footnote|source|appendix|attachment|exhibit|underlying board|proceeding below|board number)\b"):
        return "source_provenance"
    if _has(text, r"\b(obligation|require|requires|required|must|shall|respond|response|corrective action|submit|provide|deadline|working days|business days|within how many)\b"):
        return "obligation_or_deadline"
    if _has(text, r"\b(violation|deficienc|cgmp|category|class|control area|failure|failed|adulterated)\b"):
        return "violation_or_deficiency"
    if _has(text, r"\b(citation|statute|statutory|cfr|u\.s\.c|jurisdiction|authority|legal basis|provision|section|article)\b"):
        return "legal_authority"
    if _has(text, r"\b(argument|argued|why|because|reason|explain|explained|conclude|concluded|treat|treated|theory|distinction|compare|comparison|forfeiture|anticipation|obviousness)\b"):
        return "finding_or_reasoning"
    if _has(text, r"\b(disposition|affirmed|denied|granted|dismissed|approved|rejected|status|outcome|decision|decided)\b"):
        return "outcome_or_status"
    if _has(text, r"\b(amount|payment|relief|fine|penalt|restitution|refund|reimburse|dollar|\\$|fee|cost)\b"):
        return "monetary"
    if _has(text, r"\b(numerical|parameter|percent|percentage|ratio|count|how many|number of|total|rate|quantity)\b"):
        return "numeric_quantity"
    if _has(text, r"\b(list|which specific|what are the|all |three numbered|four |categories|inventory|chronological order)\b"):
        if "document_chronology" in intents or _has(text, r"\b(chronological|dates?|events?|inspection|meeting|issued|filed|published)\b"):
            return "chronology"
        return "list_inventory"
    if has_date:
        return "date_metadata"
    if has_identifier:
        return "identifier_metadata"
    if _has(text, r"\b(who|recipient|salutation|signed|signatory|judge|panel|attorney|appellee|appellant|party|office|director|title|company|firm|individual)\b"):
        return "party_role_roster"
    if predicates.intersection({"document_identifier_occurrence", "document_identifier"}):
        return "identifier_metadata"
    if predicates.intersection({"document_date", "event_date"}):
        return "date_metadata"
    return "other"


def _substance_band(answer_class: str) -> str:
    if answer_class in {
        "legal_authority",
        "obligation_or_deadline",
        "violation_or_deficiency",
        "finding_or_reasoning",
        "outcome_or_status",
        "monetary",
    }:
        return "substantive"
    if answer_class in {"source_provenance", "chronology", "list_inventory", "numeric_quantity"}:
        return "mixed"
    return "scaffolding"


def _failure_reasons(
    *,
    product_exact: bool,
    typed_full: bool,
    redaction_survived: bool,
    atom_clean: bool,
) -> list[str]:
    if not product_exact:
        return ["product_not_exact"]
    reasons: list[str] = []
    if not typed_full:
        reasons.append("typed_plan_not_full")
    if not redaction_survived:
        reasons.append("redaction_not_survived")
    if not atom_clean:
        reasons.append("atom_shape_hit")
    return reasons or ["hard_clean"]


def _row_predicates(row: dict[str, Any]) -> set[str]:
    predicates: set[str] = set()
    for query_result in row.get("query_results", []) or []:
        if not isinstance(query_result, dict):
            continue
        result = query_result.get("result")
        if isinstance(result, dict):
            predicate = str(result.get("predicate", "")).strip()
            if predicate:
                predicates.add(predicate)
    return predicates


def _load_qa_rows(root: Path) -> dict[tuple[str, str], dict[str, Any]]:
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    for path in sorted(root.rglob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, dict) or not isinstance(data.get("rows"), list):
            continue
        fixture = path.parent.name
        for row in data.get("rows", []) or []:
            if isinstance(row, dict):
                row_id = str(row.get("id", "")).strip()
                if row_id:
                    rows[(fixture, row_id)] = row
    return rows


def _load_fixture_metadata(root: Path | None) -> dict[str, dict[str, Any]]:
    if not root or not root.exists():
        return {}
    out: dict[str, dict[str, Any]] = {}
    for path in root.glob("*/metadata.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(data, dict):
            fixture = str(data.get("fixture_id") or path.parent.name).strip()
            if fixture:
                out[fixture] = data
    return out


def _fixture_family(fixture: str) -> str:
    text = str(fixture or "")
    for suffix in ("_ugly_003", "_ugly_007", "_001", "_002", "_003", "_007"):
        if text.endswith(suffix):
            return text[: -len(suffix)]
    return text


def _add_counts(
    counter: Counter[str],
    *,
    product_exact: bool,
    typed_full: bool,
    redaction_survived: bool,
    atom_clean: bool,
    hard_clean: bool,
) -> None:
    counter["row_count"] += 1
    if product_exact:
        counter["product_exact"] += 1
    if product_exact and typed_full:
        counter["typed_plan_exact"] += 1
    if product_exact and redaction_survived:
        counter["redaction_survived_exact"] += 1
    if product_exact and atom_clean:
        counter["atom_shape_clean_product_exact"] += 1
    if hard_clean:
        counter["hard_clean_exact"] += 1


def _counter_summary(counter: Counter[str]) -> dict[str, Any]:
    total = counter["row_count"]
    return {
        "row_count": total,
        "product_exact": counter["product_exact"],
        "product_exact_rate": _share(counter["product_exact"], total),
        "typed_plan_exact": counter["typed_plan_exact"],
        "typed_plan_exact_rate": _share(counter["typed_plan_exact"], total),
        "redaction_survived_exact": counter["redaction_survived_exact"],
        "redaction_survived_exact_rate": _share(counter["redaction_survived_exact"], total),
        "atom_shape_clean_product_exact": counter["atom_shape_clean_product_exact"],
        "atom_shape_clean_product_exact_rate": _share(counter["atom_shape_clean_product_exact"], total),
        "hard_clean_exact": counter["hard_clean_exact"],
        "hard_clean_exact_rate": _share(counter["hard_clean_exact"], total),
    }


def _summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counter: Counter[str] = Counter()
    for row in rows:
        _add_counts(
            counter,
            product_exact=row["product_verdict"] == "exact",
            typed_full=row["typed_plan_status"] == "all_queries_success",
            redaction_survived=row["redaction_thesis_verdict"] == "survived",
            atom_clean=bool(row["atom_shape_clean"]),
            hard_clean=bool(row["hard_clean"]),
        )
    return _counter_summary(counter)


def _has(text: str, pattern: str) -> bool:
    return bool(re.search(pattern, text, flags=re.IGNORECASE))


def _share(count: int, total: int) -> float:
    return round(count / total, 6) if total else 0.0


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Hard-Clean Answer-Class Summary",
        "",
        f"- Schema: `{report['schema_version']}`",
        f"- Hard-road report: `{report['hard_road_json']}`",
        f"- QA root: `{report['qa_root']}`",
        f"- Dataset root: `{report['dataset_root']}`",
        "",
        "## Summary",
        "",
        _metric_line("Rows", summary["row_count"]),
        _metric_line("Product exact", summary["product_exact"], summary["row_count"], summary["product_exact_rate"]),
        _metric_line("Typed-plan exact", summary["typed_plan_exact"], summary["row_count"], summary["typed_plan_exact_rate"]),
        _metric_line(
            "Redaction-survived exact",
            summary["redaction_survived_exact"],
            summary["row_count"],
            summary["redaction_survived_exact_rate"],
        ),
        _metric_line(
            "Atom-shape-clean product exact",
            summary["atom_shape_clean_product_exact"],
            summary["row_count"],
            summary["atom_shape_clean_product_exact_rate"],
        ),
        _metric_line("Hard-clean exact", summary["hard_clean_exact"], summary["row_count"], summary["hard_clean_exact_rate"]),
        "",
        "## Substance Bands",
        "",
        "| Band | Rows | Product | Hard-clean |",
        "| --- | ---: | ---: | ---: |",
    ]
    for band, item in sorted(report["by_substance_band"].items()):
        lines.append(_table_summary_row(band, item))
    lines.extend(
        [
            "",
            "## Answer Classes",
            "",
            "| Class | Rows | Product | Hard-clean | Top failure reasons |",
            "| --- | ---: | ---: | ---: | --- |",
        ]
    )
    for answer_class, item in report["by_answer_class"].items():
        failures = ", ".join(f"{key}:{value}" for key, value in item.get("failure_reasons", {}).items())
        lines.append(
            "| `{}` | {} | {} ({:.1%}) | {} ({:.1%}) | {} |".format(
                answer_class,
                item["row_count"],
                item["product_exact"],
                item["product_exact_rate"],
                item["hard_clean_exact"],
                item["hard_clean_exact_rate"],
                _md_cell(failures),
            )
        )
    lines.extend(
        [
            "",
            "## Source Families",
            "",
            "| Family | Rows | Product | Hard-clean |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for family, item in report["by_source_family"].items():
        lines.append(_table_summary_row(family, item))
    lines.extend(
        [
            "",
            "## Substantive Rows That Survive",
            "",
            "| Fixture | Row | Class | Question |",
            "| --- | --- | --- | --- |",
        ]
    )
    survivors = [
        row
        for row in report["rows"]
        if row["hard_clean"] and row["substance_band"] == "substantive"
    ]
    for row in survivors[:40]:
        lines.append(
            f"| `{row['fixture']}` | `{row['id']}` | `{row['answer_class']}` | {_md_cell(row['question'])} |"
        )
    if not survivors:
        lines.append("|  |  |  | No substantive hard-clean rows. |")
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- These answer classes are analysis labels, not runtime predicates.",
            "- The table is for wedge selection and should not be used as a QA routing surface.",
            "- `substantive` means the row asks about obligations, legal authority, violations, findings, outcomes, reasoning, money, or similar claim-bearing content.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _metric_line(label: str, count: int, total: int | None = None, rate: float | None = None) -> str:
    if total is None or rate is None:
        return f"- {label}: `{count}`"
    return f"- {label}: `{count}` / `{total}` = `{rate:.2%}`"


def _table_summary_row(label: str, item: dict[str, Any]) -> str:
    return "| `{}` | {} | {} ({:.1%}) | {} ({:.1%}) |".format(
        label,
        item["row_count"],
        item["product_exact"],
        item["product_exact_rate"],
        item["hard_clean_exact"],
        item["hard_clean_exact_rate"],
    )


def _md_cell(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


if __name__ == "__main__":
    raise SystemExit(main())
