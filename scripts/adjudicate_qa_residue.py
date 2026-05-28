#!/usr/bin/env python3
"""Classify QA residue before spending compile-repair effort.

The script reads QA artifacts plus optional batch-validation details. It does
not inspect source prose and does not score answers. Its job is narrower:
separate rows that look like instrument repair targets from rows whose oracle
or fixture packaging already declares source-support risk.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qa-root", action="append", default=[], type=Path, help="Directory containing QA JSON artifacts.")
    parser.add_argument("--qa-json", action="append", default=[], type=Path, help="Individual QA JSON artifact.")
    parser.add_argument("--validation-json", type=Path, default=None, help="Fresh-batch validation JSON with warning_details.")
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(
        qa_roots=tuple(args.qa_root),
        qa_jsons=tuple(args.qa_json),
        validation_json=args.validation_json,
    )
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def build_report(
    *,
    qa_roots: tuple[Path, ...] = (),
    qa_jsons: tuple[Path, ...] = (),
    validation_json: Path | None = None,
) -> dict[str, Any]:
    runs = _load_qa_runs(qa_roots=qa_roots, qa_jsons=qa_jsons)
    selected_rows = _select_latest_rows(runs)
    validation = _load_validation_details(validation_json) if validation_json else {}
    residue: list[dict[str, Any]] = []
    fixture_counts: dict[str, Counter[str]] = defaultdict(Counter)
    verdict_counts: Counter[str] = Counter()
    classification_counts: Counter[str] = Counter()
    surface_counts: Counter[str] = Counter()
    hygiene = Counter()
    selected_artifacts: dict[Path, dict[str, Any]] = {}
    for fixture, row_id, qa_path, row, data in selected_rows:
        selected_artifacts[qa_path] = data
        verdict = _verdict(row)
        verdict_counts[verdict] += 1
        fixture_counts[fixture][verdict] += 1
        if verdict == "exact":
            continue
        details = validation.get(fixture, {}).get(row_id, [])
        classification = _classify(row, details)
        surface = _surface(row)
        residue.append(
            {
                "fixture": fixture,
                "row_id": row_id,
                "verdict": verdict,
                "surface": surface,
                "response_status": _response_status(row),
                "classification": classification,
                "signals": _signals(row, details),
                "qa_json": str(qa_path),
            }
        )
        classification_counts[classification] += 1
        surface_counts[surface or "unknown"] += 1
    for data in selected_artifacts.values():
        summary = data.get("summary") if isinstance(data.get("summary"), dict) else {}
        hygiene["runtime_load_error_count"] += int(summary.get("runtime_load_error_count") or 0)
        hygiene["write_proposal_rows"] += int(summary.get("write_proposal_rows") or 0)
        compatibility_summary = summary.get("compatibility_row_summary")
        if isinstance(compatibility_summary, dict):
            hygiene["compatibility_rows"] += int(compatibility_summary.get("row_count") or 0)
    return {
        "schema_version": "qa_residue_adjudication_v1",
        "generated": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "qa_artifact_count": len(runs),
            "selected_qa_artifact_count": len(selected_artifacts),
            "question_count": sum(verdict_counts.values()),
            "residue_count": len(residue),
            "verdict_counts": dict(sorted(verdict_counts.items())),
            "classification_counts": dict(sorted(classification_counts.items())),
            "surface_counts": dict(sorted(surface_counts.items())),
            "hygiene": dict(sorted(hygiene.items())),
        },
        "fixtures": [
            {
                "fixture": fixture,
                "verdict_counts": dict(sorted(counts.items())),
            }
            for fixture, counts in sorted(fixture_counts.items())
        ],
        "residue": sorted(residue, key=lambda item: (item["fixture"], item["row_id"])),
    }


def _load_qa_runs(*, qa_roots: tuple[Path, ...], qa_jsons: tuple[Path, ...]) -> list[tuple[int, float, str, Path, dict[str, Any]]]:
    runs: list[tuple[int, float, str, Path, dict[str, Any]]] = []
    order = 0
    for root in qa_roots:
        for path in sorted(_absolute(root).rglob("domain_bootstrap_qa_*.json")):
            loaded = _load_qa_run(path, order)
            if loaded is not None:
                runs.append(loaded)
        order += 1
    for path in qa_jsons:
        loaded = _load_qa_run(_absolute(path), order)
        if loaded is not None:
            runs.append(loaded)
        order += 1
    return sorted(runs, key=lambda item: (item[0], item[1], item[3].as_posix()))


def _load_qa_run(path: Path, order: int) -> tuple[int, float, str, Path, dict[str, Any]] | None:
    if not path.exists():
        raise FileNotFoundError(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("rows"), list):
        return None
    fixture = _fixture_name(path, data)
    mtime = path.stat().st_mtime
    return (order, mtime, fixture, path, data)


def _select_latest_rows(
    runs: list[tuple[int, float, str, Path, dict[str, Any]]]
) -> list[tuple[str, str, Path, dict[str, Any], dict[str, Any]]]:
    selected: dict[tuple[str, str], tuple[int, float, Path, dict[str, Any], dict[str, Any]]] = {}
    for order, mtime, fixture, qa_path, data in runs:
        for row in data.get("rows", []) or []:
            if not isinstance(row, dict):
                continue
            row_id = _compact_row_id(fixture, row.get("id") or row.get("number") or "")
            if not row_id:
                continue
            key = (fixture, row_id)
            current = selected.get(key)
            if current is None or (order, mtime) >= (current[0], current[1]):
                selected[key] = (order, mtime, qa_path, row, data)
    return [
        (fixture, row_id, qa_path, row, data)
        for (fixture, row_id), (_order, _mtime, qa_path, row, data) in sorted(selected.items())
    ]


def _load_validation_details(path: Path | None) -> dict[str, dict[str, list[dict[str, Any]]]]:
    if path is None:
        return {}
    data = json.loads(_absolute(path).read_text(encoding="utf-8"))
    out: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for fixture_row in data.get("fixtures", []) or []:
        if not isinstance(fixture_row, dict):
            continue
        fixture = str(fixture_row.get("fixture") or "").strip()
        if not fixture:
            continue
        for detail in fixture_row.get("warning_details", []) or []:
            if not isinstance(detail, dict):
                continue
            row_id = _compact_row_id(fixture, detail.get("row_id") or "")
            out[fixture][row_id].append(detail)
    return {fixture: dict(rows) for fixture, rows in out.items()}


def _fixture_name(path: Path, data: dict[str, Any]) -> str:
    qa_file = str(data.get("qa_file") or "").strip()
    if qa_file:
        qa_path = Path(qa_file)
        if qa_path.name == "qa.md" and qa_path.parent.name:
            return qa_path.parent.name
    return path.parent.name


def _compact_row_id(fixture: str, row_id: Any) -> str:
    text = str(row_id or "").strip()
    if not text:
        return ""
    prefix = f"{fixture}_"
    if text.startswith(prefix):
        text = text[len(prefix) :]
    if text[:1].casefold() == "q":
        digits = "".join(char for char in text[1:] if char.isdigit())
        if digits:
            return f"q{int(digits):03d}"
    return text


def _classify(row: dict[str, Any], details: list[dict[str, Any]]) -> str:
    detail_kinds = {str(detail.get("kind") or "") for detail in details}
    tags = _pressure_tags(row)
    if _has_source_limit_tag(tags) or "oracle_declares_incomplete_source" in detail_kinds:
        return "declared_source_or_oracle_limit"
    if "reference_terms_absent_from_source_but_in_notes_or_metadata" in detail_kinds:
        return "source_support_adjudication_needed"
    judge = row.get("reference_judge") if isinstance(row.get("reference_judge"), dict) else {}
    if "reference_terms_absent_from_source" in detail_kinds and judge.get("answer_supported") is False:
        return "source_support_adjudication_needed"
    surface = _surface(row)
    if surface == "compile_surface_gap":
        return "repairable_compile_gap"
    if surface == "query_surface_gap":
        return "query_planning_gap"
    if surface == "hybrid_join_gap":
        return "join_or_selection_gap"
    if surface == "answer_surface_gap":
        return "answer_rendering_gap"
    if surface == "judge_uncertain":
        return "judge_uncertain"
    return "needs_adjudication"


def _signals(row: dict[str, Any], details: list[dict[str, Any]]) -> list[str]:
    signals: list[str] = []
    tags = _pressure_tags(row)
    if tags:
        signals.append("pressure_tags:" + ",".join(tags))
    for detail in details:
        kind = str(detail.get("kind") or "").strip()
        if kind:
            signals.append(f"validation:{kind}")
    judge = row.get("reference_judge") if isinstance(row.get("reference_judge"), dict) else {}
    if judge.get("answer_supported") is False:
        signals.append("judge_answer_supported:false")
    return signals


def _pressure_tags(row: dict[str, Any]) -> list[str]:
    oracle = row.get("oracle") if isinstance(row.get("oracle"), dict) else {}
    raw_tags = oracle.get("pressure_tags")
    if not isinstance(raw_tags, list):
        return []
    return sorted(str(tag).strip().casefold() for tag in raw_tags if str(tag).strip())


def _has_source_limit_tag(tags: list[str]) -> bool:
    return any(tag in {"incomplete_in_source", "external", "external_source"} for tag in tags)


def _verdict(row: dict[str, Any]) -> str:
    judge = row.get("reference_judge") if isinstance(row.get("reference_judge"), dict) else {}
    return str(judge.get("verdict") or row.get("oracle_match") or "unknown").strip() or "unknown"


def _surface(row: dict[str, Any]) -> str:
    failure = row.get("failure_surface") if isinstance(row.get("failure_surface"), dict) else {}
    surface = str(failure.get("surface") or "").strip()
    if surface:
        return surface
    envelope = row.get("response_envelope") if isinstance(row.get("response_envelope"), dict) else {}
    return str(envelope.get("failure_surface") or "").strip()


def _response_status(row: dict[str, Any]) -> str:
    envelope = row.get("response_envelope") if isinstance(row.get("response_envelope"), dict) else {}
    return str(envelope.get("status") or "").strip()


def _absolute(path: Path) -> Path:
    return path if path.is_absolute() else Path.cwd() / path


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {})
    lines = [
        "# QA Residue Adjudication",
        "",
        f"- Generated: `{report.get('generated', '')}`",
        f"- QA artifacts: `{summary.get('qa_artifact_count', 0)}`",
        f"- Selected QA artifacts: `{summary.get('selected_qa_artifact_count', 0)}`",
        f"- Questions: `{summary.get('question_count', 0)}`",
        f"- Residue rows: `{summary.get('residue_count', 0)}`",
        f"- Verdicts: `{_format_counts(summary.get('verdict_counts', {}))}`",
        f"- Classifications: `{_format_counts(summary.get('classification_counts', {}))}`",
        f"- Surfaces: `{_format_counts(summary.get('surface_counts', {}))}`",
        f"- Hygiene: `{_format_counts(summary.get('hygiene', {}))}`",
        "",
        "| Fixture | Row | Verdict | Surface | Status | Classification | Signals |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in report.get("residue", []) or []:
        lines.append(
            "| `{fixture}` | `{row_id}` | `{verdict}` | `{surface}` | `{status}` | `{classification}` | {signals} |".format(
                fixture=row.get("fixture", ""),
                row_id=row.get("row_id", ""),
                verdict=row.get("verdict", ""),
                surface=row.get("surface", "") or "-",
                status=row.get("response_status", "") or "-",
                classification=row.get("classification", ""),
                signals=", ".join(f"`{signal}`" for signal in row.get("signals", []) or []) or "-",
            )
        )
    return "\n".join(lines).rstrip() + "\n"


def _format_counts(counts: Any) -> str:
    if not isinstance(counts, dict) or not counts:
        return "-"
    return ", ".join(f"{key}:{value}" for key, value in sorted(counts.items()))


if __name__ == "__main__":
    raise SystemExit(main())
