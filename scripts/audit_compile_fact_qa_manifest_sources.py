#!/usr/bin/env python3
"""Audit compile-fact QA manifest roots and run provenance.

This is a governance check for claim-bearing manifest cells. It does not rescore
fixtures. It verifies that each manifest cell points at retained compile
artifacts, that N>=3 run evidence is present, and that the effective inference
settings are recoverable and consistent across the run set.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = Path("datasets/domain_pack_measurements/current_compile_fact_qa_manifest.json")
MIN_RUN_COUNT = 3

REQUIRED_SETTINGS = (
    "backend",
    "model",
    "temperature",
    "top_p",
    "num_ctx",
    "support_threshold",
    "matcher",
)

COMPILE_JSON_SETTINGS = (
    "backend",
    "model",
    "base_url",
    "temperature",
    "top_p",
    "top_k_requested",
    "num_ctx",
    "max_tokens",
    "timeout",
    "provider_family",
    "transport_backend",
    "quantization",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--exit-zero", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = audit_manifest(args.manifest)
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(report_md(report), encoding="utf-8")
    blocked = bool(report["summary"]["blocking_reasons"])
    return 0 if args.exit_zero or not blocked else 1


def audit_manifest(manifest_path: Path) -> dict[str, Any]:
    manifest_abs = _resolve_path(manifest_path)
    payload = _load_json(manifest_abs)
    cells = payload.get("cells")
    if not isinstance(cells, list) or not cells:
        raise SystemExit(f"Manifest must contain a non-empty cells array: {manifest_abs}")

    cell_reports = [_audit_cell(cell, index=index + 1) for index, cell in enumerate(cells)]
    blockers = [reason for cell in cell_reports for reason in cell["blocking_reasons"]]
    warnings = [warning for cell in cell_reports for warning in cell["warnings"]]
    return {
        "schema": "prethinker.compile_fact_qa_manifest_source_audit.v1",
        "created_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "manifest_path": str(manifest_abs),
        "manifest_schema": payload.get("schema", ""),
        "settings_required": list(REQUIRED_SETTINGS),
        "settings_optional": [
            "base_url",
            "top_k_requested",
            "max_tokens",
            "timeout",
            "provider_family",
            "transport_backend",
            "quantization",
        ],
        "summary": {
            "cell_count": len(cell_reports),
            "blocking_reasons": blockers,
            "warning_count": len(warnings),
            "status": "pass" if not blockers else "fail",
        },
        "cells": cell_reports,
    }


def _audit_cell(cell: dict[str, Any], *, index: int) -> dict[str, Any]:
    cell_id = str(cell.get("id") or f"cell_{index}").strip()
    fixture_id = str(cell.get("fixture_id") or "").strip()
    blockers: list[str] = []
    warnings: list[str] = []
    if not fixture_id:
        blockers.append(f"{cell_id}:missing_fixture_id")

    if cell.get("domain_lens_bundle"):
        result = _audit_domain_lens_bundle(
            cell_id=cell_id,
            fixture_id=fixture_id,
            bundle_root=_resolve_path(Path(str(cell["domain_lens_bundle"]))),
            warnings=warnings,
            blockers=blockers,
        )
    elif isinstance(cell.get("fixture_runs"), list):
        result = _audit_fixture_runs(
            cell_id=cell_id,
            fixture_runs=cell["fixture_runs"],
            warnings=warnings,
            blockers=blockers,
        )
    else:
        result = {
            "source_kind": "unknown",
            "source_root": "",
            "run_count": 0,
            "run_jsons": [],
            "effective_settings": {},
            "setting_sources": {},
            "bundle_manifest_status": "not_applicable",
        }
        blockers.append(f"{cell_id}:missing_domain_lens_bundle_or_fixture_runs")

    settings = dict(result.get("effective_settings") or {})
    for key in REQUIRED_SETTINGS:
        if _is_missing(settings.get(key)):
            blockers.append(f"{cell_id}:missing_required_setting:{key}")
    if int(result.get("run_count") or 0) < MIN_RUN_COUNT:
        blockers.append(f"{cell_id}:run_count_lt_{MIN_RUN_COUNT}:{result.get('run_count')}")

    return {
        "id": cell_id,
        "fixture_id": fixture_id,
        "description": str(cell.get("description", "")),
        "source_kind": result["source_kind"],
        "source_root": result["source_root"],
        "bundle_manifest_status": result["bundle_manifest_status"],
        "run_count": result["run_count"],
        "run_jsons": result["run_jsons"],
        "effective_settings": settings,
        "setting_sources": result["setting_sources"],
        "blocking_reasons": blockers,
        "warnings": warnings,
    }


def _audit_domain_lens_bundle(
    *,
    cell_id: str,
    fixture_id: str,
    bundle_root: Path,
    warnings: list[str],
    blockers: list[str],
) -> dict[str, Any]:
    if not bundle_root.is_dir():
        blockers.append(f"{cell_id}:domain_lens_bundle_missing:{bundle_root}")
        return _empty_source_result("domain_lens_bundle", bundle_root)
    if _is_under_repo_tmp(bundle_root):
        blockers.append(f"{cell_id}:claim_bearing_bundle_under_repo_tmp:{bundle_root}")

    run_specs = _domain_lens_run_specs(bundle_root, blockers, cell_id)
    run_jsons = [Path(spec["compile_json"]) for spec in run_specs]
    score_report = _load_optional_json(bundle_root / "reports" / "typed_micro_series_summary.json")
    bundle_manifest_path = bundle_root / "manifest.json"
    bundle_manifest = _load_optional_json(bundle_manifest_path)

    compile_settings = _settings_from_compile_jsons(run_jsons, blockers, cell_id)
    report_settings = _settings_from_score_report(score_report)
    manifest_settings: dict[str, Any] = {}
    setting_sources: dict[str, str] = {}
    bundle_manifest_status = "present"
    if bundle_manifest is not None:
        manifest_settings = _settings_from_bundle_manifest(bundle_manifest)
        setting_sources.update({key: "bundle_manifest" for key in manifest_settings})
        _check_manifest_run_shape(
            cell_id=cell_id,
            manifest=bundle_manifest,
            run_count=len(run_specs),
            blockers=blockers,
        )
    else:
        bundle_manifest_status = "missing_recovered_from_compile_json"
        warnings.append(f"{cell_id}:missing_bundle_manifest_recovered_from_compile_json")

    effective = dict(manifest_settings)
    for key, value in compile_settings.items():
        if _is_missing(effective.get(key)):
            effective[key] = value
            setting_sources[key] = "compile_json"
        elif key in {"backend", "model", "temperature", "top_p", "num_ctx"} and not _same_scalar(effective[key], value):
            blockers.append(
                f"{cell_id}:manifest_compile_setting_mismatch:{key}:manifest={effective[key]}:compile={value}"
            )
    for key, value in report_settings.items():
        if _is_missing(effective.get(key)):
            effective[key] = value
            setting_sources[key] = "score_report"
        elif key in {"support_threshold", "matcher"} and not _same_scalar(effective[key], value):
            blockers.append(
                f"{cell_id}:manifest_score_setting_mismatch:{key}:manifest={effective[key]}:score={value}"
            )

    if score_report is None:
        warnings.append(f"{cell_id}:missing_typed_micro_series_score_report")

    return {
        "source_kind": "domain_lens_bundle",
        "source_root": str(bundle_root),
        "bundle_manifest_status": bundle_manifest_status,
        "run_count": len(run_specs),
        "run_jsons": [str(path) for path in run_jsons],
        "effective_settings": effective,
        "setting_sources": setting_sources,
    }


def _audit_fixture_runs(
    *,
    cell_id: str,
    fixture_runs: list[Any],
    warnings: list[str],
    blockers: list[str],
) -> dict[str, Any]:
    run_jsons: list[Path] = []
    for index, item in enumerate(fixture_runs, start=1):
        if not isinstance(item, dict):
            blockers.append(f"{cell_id}:fixture_run_{index}_not_object")
            continue
        compile_json = str(item.get("compile_json") or "").strip()
        if not compile_json:
            blockers.append(f"{cell_id}:fixture_run_{index}_missing_compile_json")
            continue
        path = _resolve_path(Path(compile_json))
        if not path.is_file():
            blockers.append(f"{cell_id}:fixture_run_{index}_compile_json_missing:{path}")
            continue
        run_jsons.append(path)
    settings = _settings_from_compile_jsons(run_jsons, blockers, cell_id)
    warnings.append(f"{cell_id}:fixture_runs_do_not_record_support_threshold_or_matcher_unless_supplied_elsewhere")
    return {
        "source_kind": "fixture_runs",
        "source_root": "",
        "bundle_manifest_status": "not_applicable",
        "run_count": len(run_jsons),
        "run_jsons": [str(path) for path in run_jsons],
        "effective_settings": settings,
        "setting_sources": {key: "compile_json" for key in settings},
    }


def _domain_lens_run_specs(bundle_root: Path, blockers: list[str], cell_id: str) -> list[dict[str, str]]:
    union_root = bundle_root / "unions"
    if not union_root.is_dir():
        blockers.append(f"{cell_id}:domain_lens_bundle_missing_unions:{union_root}")
        return []
    out: list[dict[str, str]] = []
    seen_run_ids: set[str] = set()
    for run_dir in sorted(path for path in union_root.iterdir() if path.is_dir()):
        json_files = sorted(run_dir.glob("*.json"))
        if not json_files:
            blockers.append(f"{cell_id}:missing_union_compile_json:{run_dir}")
            continue
        if len(json_files) > 1:
            blockers.append(f"{cell_id}:ambiguous_union_compile_jsons:{run_dir}")
            continue
        run_id = run_dir.name
        seen_run_ids.add(run_id)
        out.append({"run_id": run_id, "compile_json": str(json_files[0])})
    for json_file in sorted(union_root.glob("*.json")):
        run_id = _run_id_from_union_file(json_file)
        if run_id in seen_run_ids:
            blockers.append(f"{cell_id}:duplicate_union_run_id:{run_id}:{union_root}")
            continue
        seen_run_ids.add(run_id)
        out.append({"run_id": run_id, "compile_json": str(json_file)})
    return out


def _settings_from_bundle_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    settings = manifest.get("settings")
    if not isinstance(settings, dict):
        settings = {}
    out = {
        "backend": settings.get("backend"),
        "model": settings.get("model"),
        "base_url": settings.get("base_url"),
        "temperature": settings.get("temperature"),
        "top_p": settings.get("top_p"),
        "top_k_requested": settings.get("top_k"),
        "num_ctx": settings.get("num_ctx"),
        "max_tokens": settings.get("max_tokens"),
        "timeout": settings.get("timeout"),
        "support_threshold": settings.get("support_threshold"),
        "matcher": settings.get("matcher"),
    }
    return {key: value for key, value in out.items() if not _is_missing(value)}


def _settings_from_compile_jsons(paths: list[Path], blockers: list[str], cell_id: str) -> dict[str, Any]:
    observed: dict[str, list[Any]] = {key: [] for key in COMPILE_JSON_SETTINGS}
    for path in paths:
        payload = _load_optional_json(path)
        if payload is None:
            blockers.append(f"{cell_id}:compile_json_unreadable:{path}")
            continue
        settings = _settings_from_compile_json(payload)
        for key in COMPILE_JSON_SETTINGS:
            if not _is_missing(settings.get(key)):
                observed[key].append(settings[key])
    out: dict[str, Any] = {}
    for key, values in observed.items():
        if not values:
            continue
        unique = _unique_scalars(values)
        if len(unique) > 1:
            blockers.append(f"{cell_id}:mixed_compile_setting:{key}:{unique}")
        out[key] = unique[0]
    return out


def _settings_from_compile_json(payload: dict[str, Any]) -> dict[str, Any]:
    serving = payload.get("model_serving_path")
    if not isinstance(serving, dict):
        serving = {}
    decoding = serving.get("decoding")
    if not isinstance(decoding, dict):
        decoding = {}
    execution = serving.get("execution")
    if not isinstance(execution, dict):
        execution = {}
    observed = serving.get("observed_runtime")
    if not isinstance(observed, dict):
        observed = {}
    api_model = observed.get("api_v0_model")
    if not isinstance(api_model, dict):
        api_model = {}
    return {
        "backend": payload.get("backend") or serving.get("transport_backend"),
        "model": payload.get("model") or serving.get("model"),
        "base_url": serving.get("base_url"),
        "temperature": decoding.get("temperature"),
        "top_p": decoding.get("top_p"),
        "top_k_requested": decoding.get("top_k_requested"),
        "num_ctx": decoding.get("context_length"),
        "max_tokens": decoding.get("max_tokens"),
        "timeout": execution.get("timeout_seconds"),
        "provider_family": serving.get("provider_family"),
        "transport_backend": serving.get("transport_backend"),
        "quantization": api_model.get("quantization"),
    }


def _settings_from_score_report(report: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(report, dict):
        return {}
    return {
        key: value
        for key, value in {
            "support_threshold": report.get("support_threshold"),
            "matcher": report.get("matcher"),
        }.items()
        if not _is_missing(value)
    }


def _check_manifest_run_shape(
    *,
    cell_id: str,
    manifest: dict[str, Any],
    run_count: int,
    blockers: list[str],
) -> None:
    repeat = manifest.get("repeat")
    if isinstance(repeat, int) and repeat != run_count:
        blockers.append(f"{cell_id}:bundle_manifest_repeat_mismatch:repeat={repeat}:runs={run_count}")
    runs = manifest.get("runs")
    if isinstance(runs, list) and len(runs) != run_count:
        blockers.append(f"{cell_id}:bundle_manifest_runs_mismatch:manifest_runs={len(runs)}:runs={run_count}")


def report_md(report: dict[str, Any]) -> str:
    lines = [
        "# Compile-Fact QA Manifest Source Audit",
        "",
        f"Status: `{report['summary']['status']}`",
        f"Cells: `{report['summary']['cell_count']}`",
        f"Warnings: `{report['summary']['warning_count']}`",
        "",
    ]
    blockers = report["summary"]["blocking_reasons"]
    if blockers:
        lines.append("## Blocking Reasons")
        lines.append("")
        lines.extend(f"- `{reason}`" for reason in blockers)
        lines.append("")
    lines.extend(
        [
            "## Cells",
            "",
            "| Cell | Runs | Manifest | Backend | Model | Temp | Top-p | Context | Support | Matcher | Warnings |",
            "| --- | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: |",
        ]
    )
    for cell in report["cells"]:
        settings = cell.get("effective_settings") or {}
        lines.append(
            "| "
            f"`{cell['id']}` | "
            f"{cell.get('run_count', 0)} | "
            f"`{cell.get('bundle_manifest_status', '')}` | "
            f"`{settings.get('backend', '')}` | "
            f"`{settings.get('model', '')}` | "
            f"{settings.get('temperature', '')} | "
            f"{settings.get('top_p', '')} | "
            f"{settings.get('num_ctx', '')} | "
            f"{settings.get('support_threshold', '')} | "
            f"`{settings.get('matcher', '')}` | "
            f"{len(cell.get('warnings') or [])} |"
        )
    lines.append("")
    return "\n".join(lines)


def _empty_source_result(source_kind: str, source_root: Path) -> dict[str, Any]:
    return {
        "source_kind": source_kind,
        "source_root": str(source_root),
        "bundle_manifest_status": "unknown",
        "run_count": 0,
        "run_jsons": [],
        "effective_settings": {},
        "setting_sources": {},
    }


def _resolve_path(path: Path) -> Path:
    return path if path.is_absolute() else (REPO_ROOT / path).resolve()


def _is_under_repo_tmp(path: Path) -> bool:
    try:
        resolved = path.resolve()
    except OSError:
        resolved = path
    tmp_root = (REPO_ROOT / "tmp").resolve()
    return resolved == tmp_root or tmp_root in resolved.parents


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"Cannot read JSON file {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Cannot parse JSON file {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"JSON file must contain an object: {path}")
    return payload


def _load_optional_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _run_id_from_union_file(path: Path) -> str:
    match = re.search(r"(?:^|[-_])run(\d+)(?:[-_.]|$)", path.name)
    if match:
        return f"run{match.group(1)}"
    return path.stem


def _is_missing(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _same_scalar(left: Any, right: Any) -> bool:
    return str(left) == str(right)


def _unique_scalars(values: list[Any]) -> list[Any]:
    out: list[Any] = []
    seen: set[str] = set()
    for value in values:
        key = str(value)
        if key in seen:
            continue
        seen.add(key)
        out.append(value)
    return out


if __name__ == "__main__":
    raise SystemExit(main())
