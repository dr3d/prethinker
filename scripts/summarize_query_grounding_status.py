#!/usr/bin/env python3
"""Summarize retained atom-library query-grounding measurements.

This report reads retained query/replay JSON artifacts only. It does not read
source prose, compile source-record rows, QA authoring files, or oracle prose.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.report_freshness import apply_markdown_freshness_check  # noqa: E402


DEFAULT_MANIFEST = REPO_ROOT / "datasets" / "domain_pack_measurements" / "current_query_grounding_manifest.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    parser.add_argument("--expect-md", type=Path)
    parser.add_argument("--exit-zero", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(args.manifest)
    rendered_md = render_markdown(report)
    if args.expect_md:
        apply_markdown_freshness_check(
            report=report,
            expected_path=args.expect_md,
            rendered_md=rendered_md,
        )
        rendered_md = render_markdown(report)
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(rendered_md, encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    blocked = report["summary"]["status"] != "pass"
    return 0 if args.exit_zero or not blocked else 1


def build_report(manifest_path: Path) -> dict[str, Any]:
    manifest = _load_json(_resolve_path(manifest_path))
    cells = manifest.get("cells") if isinstance(manifest, dict) else []
    rows = [_summarize_cell(cell) for cell in cells if isinstance(cell, dict)]
    errors = [error for row in rows for error in row.get("errors", [])]
    warnings = [warning for row in rows for warning in row.get("warnings", [])]
    return {
        "schema": "prethinker.query_grounding_status.v1",
        "manifest": str(_resolve_path(manifest_path)),
        "summary": {
            "cells": len(rows),
            "question_rows": sum(int(row.get("row_count", 0)) for row in rows),
            "product_exact": sum(int(row.get("product_exact", 0)) for row in rows),
            "typed_plan_exact": sum(int(row.get("typed_plan_exact", 0)) for row in rows),
            "redaction_survived": sum(int(row.get("redaction_survived", 0)) for row in rows),
            "prose_dependent_exact": sum(int(row.get("prose_dependent_exact", 0)) for row in rows),
            "unregistered_plan_exact_rows": sum(int(row.get("unregistered_plan_exact_rows", 0)) for row in rows),
            "blocked_source_record_plan_rows": sum(int(row.get("blocked_source_record_plan_rows", 0)) for row in rows),
            "runtime_load_error_rows": sum(int(row.get("runtime_load_error_rows", 0)) for row in rows),
            "errors": len(errors),
            "warnings": len(warnings),
            "status": "pass" if not errors else "fail",
        },
        "cells": rows,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Query Grounding Status",
        "",
        "Generated from retained atom-library query artifacts, typed-plan replay, and redaction replay.",
        "This report does not read source prose, source-record rows, or QA oracle prose.",
        "",
        "## Summary",
        "",
        f"- Status: `{summary['status']}`",
        f"- Cells: `{summary['cells']}`",
        f"- Query rows: `{summary['question_rows']}`",
        f"- Product exact: `{summary['product_exact']} / {summary['question_rows']}`",
        f"- Typed-plan exact: `{summary['typed_plan_exact']} / {summary['question_rows']}`",
        f"- Redaction-survived exact: `{summary['redaction_survived']} / {summary['question_rows']}`",
        f"- Prose-dependent exact rows: `{summary['prose_dependent_exact']}`",
        f"- Unregistered exact typed plans: `{summary['unregistered_plan_exact_rows']}`",
        f"- Blocked source-record plan rows: `{summary['blocked_source_record_plan_rows']}`",
        f"- Runtime load error rows: `{summary['runtime_load_error_rows']}`",
        f"- Errors / warnings: `{summary['errors']} / {summary['warnings']}`",
        "",
        "## Cells",
        "",
        "| Cell | Packet | Rows | Product | Typed replay | Redaction | Prose dep | Unregistered | Model / Settings |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for cell in report.get("cells", []):
        lines.append(
            "| `{}` | `{}` | {} | {}/{} | {}/{} | {}/{} | {} | {} | {} |".format(
                cell.get("id", ""),
                cell.get("query_packet", ""),
                cell.get("row_count", 0),
                cell.get("product_exact", 0),
                cell.get("row_count", 0),
                cell.get("typed_plan_exact", 0),
                cell.get("row_count", 0),
                cell.get("redaction_survived", 0),
                cell.get("row_count", 0),
                cell.get("prose_dependent_exact", 0),
                cell.get("unregistered_plan_exact_rows", 0),
                _settings_text(cell.get("metadata", {})),
            )
        )
    error_rows = [
        (cell.get("id", ""), error)
        for cell in report.get("cells", [])
        for error in cell.get("errors", [])
    ]
    if error_rows:
        lines.extend(["", "## Errors", ""])
        for cell_id, error in error_rows:
            lines.append(f"- `{cell_id}`: `{error}`")
    return "\n".join(lines) + "\n"


def _summarize_cell(cell: dict[str, Any]) -> dict[str, Any]:
    cell_id = str(cell.get("id") or "").strip()
    artifact_root = _resolve_path(Path(str(cell.get("artifact_root") or "")))
    typed_path = _resolve_path(Path(str(cell.get("typed_plan_replay_json") or artifact_root / "typed_plan_replay.json")))
    redaction_path = _resolve_path(Path(str(cell.get("redaction_replay_json") or artifact_root / "redaction_replay.json")))
    query_packet = str(cell.get("query_packet") or "").strip()
    errors: list[str] = []
    warnings: list[str] = []
    typed = _load_required_json(typed_path, errors, "missing_typed_plan_replay_json")
    redaction = _load_required_json(redaction_path, errors, "missing_redaction_replay_json")
    qa_jsons = _qa_json_paths(artifact_root)
    if not qa_jsons:
        warnings.append("no_query_qa_jsons_found")
    typed_rows = typed.get("rows") if isinstance(typed, dict) else []
    redaction_rows = redaction.get("rows") if isinstance(redaction, dict) else []
    if not isinstance(typed_rows, list):
        typed_rows = []
        errors.append("typed_plan_rows_not_list")
    if not isinstance(redaction_rows, list):
        redaction_rows = []
        errors.append("redaction_rows_not_list")

    row_count = len(redaction_rows) or len(typed_rows)
    product_exact = sum(1 for row in redaction_rows if row.get("product_verdict") == "exact")
    typed_plan_exact = sum(1 for row in typed_rows if _typed_row_survived(row))
    redaction_survived = sum(1 for row in redaction_rows if row.get("thesis_verdict") == "survived")
    prose_dependent = sum(1 for row in redaction_rows if row.get("product_verdict") == "exact" and row.get("thesis_verdict") != "survived")
    unregistered_rows = sum(1 for row in typed_rows if int(row.get("unregistered_query_signature_count") or 0) > 0)
    source_record_rows = sum(1 for row in typed_rows if _row_uses_source_record_plan(row))
    runtime_error_rows = sum(1 for row in typed_rows if row.get("runtime_load_errors"))

    expected = cell.get("expect") if isinstance(cell.get("expect"), dict) else {}
    actuals = {
        "row_count": row_count,
        "product_exact": product_exact,
        "typed_plan_exact": typed_plan_exact,
        "redaction_survived": redaction_survived,
        "prose_dependent_exact": prose_dependent,
        "unregistered_plan_exact_rows": unregistered_rows,
        "blocked_source_record_plan_rows": source_record_rows,
        "runtime_load_error_rows": runtime_error_rows,
    }
    for key, value in expected.items():
        if key not in actuals:
            errors.append(f"unknown_expectation:{key}")
            continue
        if int(value) != int(actuals[key]):
            errors.append(f"expectation_mismatch:{key}:expected_{value}:actual_{actuals[key]}")

    return {
        "id": cell_id,
        "query_packet": query_packet,
        "artifact_root": str(artifact_root),
        "typed_plan_replay_json": str(typed_path),
        "redaction_replay_json": str(redaction_path),
        "qa_json_count": len(qa_jsons),
        **actuals,
        "metadata": _metadata_from_qa_jsons(qa_jsons),
        "errors": errors,
        "warnings": warnings,
    }


def _typed_row_survived(row: dict[str, Any]) -> bool:
    if row.get("product_verdict") != "exact":
        return False
    if row.get("status") != "all_queries_success":
        return False
    if int(row.get("unregistered_query_signature_count") or 0):
        return False
    return not _row_uses_source_record_plan(row)


def _row_uses_source_record_plan(row: dict[str, Any]) -> bool:
    queries = row.get("queries")
    if not isinstance(queries, list):
        return False
    return any(str(query).strip().startswith("source_record_") for query in queries)


def _qa_json_paths(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*.json") if path.name.startswith("domain_bootstrap_qa_"))


def _metadata_from_qa_jsons(paths: list[Path]) -> dict[str, Any]:
    models: set[str] = set()
    provider_families: set[str] = set()
    quantizations: set[str] = set()
    temperatures: set[str] = set()
    top_ps: set[str] = set()
    context_lengths: set[str] = set()
    loaded_context_lengths: set[str] = set()
    for path in paths:
        payload = _load_json(path)
        serving = payload.get("model_serving_path") if isinstance(payload, dict) else {}
        if not isinstance(serving, dict):
            continue
        _add(models, serving.get("model") or payload.get("model"))
        _add(provider_families, serving.get("provider_family"))
        decoding = serving.get("decoding") if isinstance(serving.get("decoding"), dict) else {}
        _add(temperatures, decoding.get("temperature"))
        _add(top_ps, decoding.get("top_p"))
        _add(context_lengths, decoding.get("context_length"))
        runtime = serving.get("observed_runtime") if isinstance(serving.get("observed_runtime"), dict) else {}
        api_model = runtime.get("api_v0_model") if isinstance(runtime.get("api_v0_model"), dict) else {}
        _add(quantizations, api_model.get("quantization"))
        _add(loaded_context_lengths, api_model.get("loaded_context_length"))
    return {
        "models": sorted(models),
        "provider_families": sorted(provider_families),
        "quantizations": sorted(quantizations),
        "temperatures": sorted(temperatures),
        "top_ps": sorted(top_ps),
        "context_lengths": sorted(context_lengths),
        "loaded_context_lengths": sorted(loaded_context_lengths),
    }


def _settings_text(metadata: dict[str, Any]) -> str:
    return (
        f"`{_join(metadata.get('provider_families'))}` `{_join(metadata.get('models'))}`; "
        f"quant `{_join(metadata.get('quantizations'))}`; "
        f"temp `{_join(metadata.get('temperatures'))}`; "
        f"top_p `{_join(metadata.get('top_ps'))}`; "
        f"ctx `{_join(metadata.get('context_lengths'))}`; "
        f"loaded `{_join(metadata.get('loaded_context_lengths'))}`"
    )


def _join(value: Any) -> str:
    if isinstance(value, list) and value:
        return ",".join(str(item) for item in value)
    return "unknown"


def _add(target: set[str], value: Any) -> None:
    if value is None:
        return
    text = str(value).strip()
    if text:
        target.add(text)


def _load_required_json(path: Path, errors: list[str], missing_error: str) -> dict[str, Any]:
    if not path.exists():
        errors.append(f"{missing_error}:{path}")
        return {}
    payload = _load_json(path)
    if not isinstance(payload, dict):
        errors.append(f"json_not_object:{path}")
        return {}
    return payload


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _resolve_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return REPO_ROOT / path


if __name__ == "__main__":
    raise SystemExit(main())
