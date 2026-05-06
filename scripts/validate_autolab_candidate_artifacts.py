#!/usr/bin/env python3
"""Validate Autolab source-hunter and QA-drafter candidate artifacts.

This gate checks schema shape and research-boundary hygiene only. It does not
judge source quality, infer answers, score QA, or interpret source prose.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_SCHEMA = "autolab_source_candidate_v1"
QA_SCHEMA = "autolab_candidate_qa_v1"
SOURCE_REQUIRED = ("schema_version", "candidate_id", "domain_label", "why_it_is_hard", "source_text_path")
QA_REQUIRED = ("schema_version", "source_candidate_id", "rows")
QA_ROW_REQUIRED = ("qid", "question", "surface_family", "expected_answer_mode", "why_this_is_hard")
ALLOWED_EXPECTED_MODES = {"exact", "uncertain", "not_established", "clarification"}
ANSWERISH_KEYS = {"answer", "answers", "reference_answer", "gold_answer", "expected_answer", "oracle_answer"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-candidate", action="append", type=Path, default=[])
    parser.add_argument("--qa-candidate", action="append", type=Path, default=[])
    parser.add_argument("--root", type=Path, default=None, help="Directory to scan for candidate JSON files.")
    parser.add_argument("--out-json", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_paths = [_resolve(path) for path in args.source_candidate]
    qa_paths = [_resolve(path) for path in args.qa_candidate]
    if args.root:
        root = _resolve(args.root)
        if root.exists():
            for path in sorted(root.rglob("*.json")):
                schema = _peek_schema(path)
                if schema == SOURCE_SCHEMA:
                    source_paths.append(path)
                elif schema == QA_SCHEMA:
                    qa_paths.append(path)
    report = build_report(source_paths=source_paths, qa_paths=qa_paths)
    if args.out_json:
        out = _resolve(args.out_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        print(f"Wrote {out}")
    print(render_text(report))
    return 0 if report["summary"]["failed_artifact_count"] == 0 else 1


def build_report(*, source_paths: list[Path], qa_paths: list[Path]) -> dict[str, Any]:
    artifacts = [validate_source_candidate(path) for path in source_paths]
    artifacts.extend(validate_qa_candidate(path) for path in qa_paths)
    status_counts = Counter(str(item.get("status", "unknown")) for item in artifacts)
    return {
        "schema_version": "autolab_candidate_artifact_validation_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "policy": [
            "Checks JSON shape, required fields, QA row hygiene, and oracle-boundary leaks only.",
            "Does not interpret source prose, infer answers, compile, query, judge, harvest, or promote.",
        ],
        "summary": {
            "artifact_count": len(artifacts),
            "passed_artifact_count": int(status_counts.get("pass", 0)),
            "warning_artifact_count": int(status_counts.get("warning", 0)),
            "failed_artifact_count": int(status_counts.get("fail", 0)),
            "status_counts": dict(status_counts),
        },
        "artifacts": artifacts,
    }


def validate_source_candidate(path: Path) -> dict[str, Any]:
    payload, load_errors = _read_object(path)
    errors = list(load_errors)
    warnings: list[str] = []
    if payload:
        if payload.get("schema_version") != SOURCE_SCHEMA:
            errors.append(f"schema_version_expected_{SOURCE_SCHEMA}")
        _require_keys(payload, SOURCE_REQUIRED, errors)
        if not _safe_slug(str(payload.get("candidate_id", ""))):
            errors.append("candidate_id_not_safe_slug")
        hard = payload.get("why_it_is_hard")
        if not isinstance(hard, list) or not all(str(item).strip() for item in hard):
            errors.append("why_it_is_hard_must_be_nonempty_string_list")
        elif len(hard) < 2:
            warnings.append("why_it_is_hard_has_fewer_than_two_surfaces")
        source_text_path = str(payload.get("source_text_path", "")).strip()
        if source_text_path and not source_text_path.endswith(".md"):
            warnings.append("source_text_path_not_markdown")
        if not str(payload.get("source_url", "")).strip():
            warnings.append("source_url_missing_or_blank")
        if str(payload.get("do_not_use_reason", "")).strip():
            warnings.append("candidate_marked_do_not_use")
    return _artifact_result(path, "source_candidate", payload, errors, warnings)


def validate_qa_candidate(path: Path) -> dict[str, Any]:
    payload, load_errors = _read_object(path)
    errors = list(load_errors)
    warnings: list[str] = []
    row_count = 0
    surface_counts: Counter[str] = Counter()
    mode_counts: Counter[str] = Counter()
    if payload:
        if payload.get("schema_version") != QA_SCHEMA:
            errors.append(f"schema_version_expected_{QA_SCHEMA}")
        _require_keys(payload, QA_REQUIRED, errors)
        rows = payload.get("rows")
        if not isinstance(rows, list):
            errors.append("rows_must_be_list")
            rows = []
        row_count = len(rows)
        if row_count < 10 or row_count > 25:
            errors.append(f"row_count_expected_10_to_25_got_{row_count}")
        ids: list[str] = []
        for index, row in enumerate(rows, start=1):
            if not isinstance(row, dict):
                errors.append(f"row_{index}_not_object")
                continue
            _require_keys(row, QA_ROW_REQUIRED, errors, prefix=f"row_{index}_")
            qid = str(row.get("qid", "")).strip()
            ids.append(qid)
            if not _safe_slug(qid):
                errors.append(f"row_{index}_qid_not_safe_slug")
            answer_keys = sorted(key for key in row if key in ANSWERISH_KEYS)
            if answer_keys:
                errors.append(f"row_{index}_contains_answer_key:{','.join(answer_keys)}")
            mode = str(row.get("expected_answer_mode", "")).strip()
            mode_counts[mode] += 1
            if mode and mode not in ALLOWED_EXPECTED_MODES:
                errors.append(f"row_{index}_bad_expected_answer_mode:{mode}")
            surface = str(row.get("surface_family", "")).strip()
            if surface:
                surface_counts[surface] += 1
        duplicate_ids = sorted(item for item, count in Counter(ids).items() if item and count > 1)
        if duplicate_ids:
            errors.append(f"duplicate_qids:{','.join(duplicate_ids[:8])}")
        if len(surface_counts) < 3 and row_count >= 10:
            warnings.append("fewer_than_three_surface_families")
        if not (mode_counts.get("not_established", 0) or mode_counts.get("clarification", 0) or mode_counts.get("uncertain", 0)):
            warnings.append("no_uncertainty_or_clarification_rows")
    result = _artifact_result(path, "qa_candidate", payload, errors, warnings)
    result["qa"] = {
        "row_count": row_count,
        "surface_counts": dict(sorted(surface_counts.items())),
        "mode_counts": dict(sorted(mode_counts.items())),
    }
    return result


def render_text(report: dict[str, Any]) -> str:
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    lines = [
        "Autolab candidate artifact validation",
        f"artifacts={summary.get('artifact_count', 0)} pass={summary.get('passed_artifact_count', 0)} warning={summary.get('warning_artifact_count', 0)} fail={summary.get('failed_artifact_count', 0)}",
    ]
    for artifact in report.get("artifacts", []):
        if not isinstance(artifact, dict):
            continue
        bits = [
            str(artifact.get("artifact", "")),
            str(artifact.get("kind", "")),
            str(artifact.get("status", "")),
        ]
        if artifact.get("qa"):
            bits.append(f"rows={artifact['qa'].get('row_count', 0)}")
        if artifact.get("errors"):
            bits.append("errors=" + ",".join(str(item) for item in artifact.get("errors", [])[:3]))
        if artifact.get("warnings"):
            bits.append("warnings=" + ",".join(str(item) for item in artifact.get("warnings", [])[:3]))
        lines.append(" | ".join(bits))
    return "\n".join(lines)


def _artifact_result(
    path: Path, kind: str, payload: dict[str, Any], errors: list[str], warnings: list[str]
) -> dict[str, Any]:
    status = "fail" if errors else "warning" if warnings else "pass"
    return {
        "artifact": path.name,
        "path": _display_path(path),
        "kind": kind,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "id": str(payload.get("candidate_id") or payload.get("source_candidate_id") or "").strip(),
    }


def _read_object(path: Path) -> tuple[dict[str, Any], list[str]]:
    if not path.exists():
        return {}, ["artifact_missing"]
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        return {}, [f"invalid_json:{exc.msg}"]
    if not isinstance(payload, dict):
        return {}, ["json_root_not_object"]
    return payload, []


def _peek_schema(path: Path) -> str:
    payload, _errors = _read_object(path)
    return str(payload.get("schema_version", "")).strip() if payload else ""


def _require_keys(payload: dict[str, Any], keys: tuple[str, ...], errors: list[str], *, prefix: str = "") -> None:
    for key in keys:
        if key not in payload or payload.get(key) in ("", None, []):
            errors.append(f"{prefix}missing_{key}")


def _safe_slug(value: str) -> bool:
    text = str(value).strip()
    return bool(text) and all(part.isalnum() or part in "_.-" for part in text)


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def _display_path(value: Path | str) -> str:
    path = value if isinstance(value, Path) else Path(str(value))
    try:
        return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
