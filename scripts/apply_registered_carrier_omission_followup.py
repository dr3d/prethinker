#!/usr/bin/env python3
"""Apply registered-carrier omission follow-up to an existing compile artifact.

This is a compile-side postprocess: it reads an existing
``domain_bootstrap_file_*.json`` artifact, runs the bounded registered-carrier
omission follow-up pass when accountability-required carrier rows are missing,
and writes a new artifact. It does not re-bootstrap the profile or redraw the
base source compile.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.run_domain_bootstrap_file import (  # noqa: E402
    OPENROUTER_CALL_METADATA_LOG,
    _apply_profile_identifier_occurrence_repair_pass,
    _apply_profile_registered_carrier_omission_followup_pass,
    _apply_governed_obligation_detail_atom_reduction,
    _attach_registered_carrier_delivery_report,
    _ensure_obligation_detail_predicate,
    _ensure_procedural_rule_detail_predicate,
    _slug,
    _write_summary,
)
from src.model_path import refresh_openrouter_generation_metadata_entries  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-json", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--model", default=os.environ.get("PRETHINKER_MODEL", "qwen/qwen3.6-35b-a3b"))
    parser.add_argument("--base-url", default=os.environ.get("PRETHINKER_BASE_URL", "http://127.0.0.1:1234"))
    parser.add_argument("--api-key", default="")
    parser.add_argument("--timeout", type=int, default=420)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=0.82)
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument("--num-ctx", type=int, default=32768)
    parser.add_argument("--max-tokens", type=int, default=12000)
    parser.add_argument("--focused-pass-operation-target", type=int, default=32)
    parser.add_argument(
        "--obligation-detail-profile-extension",
        action="store_true",
        help=(
            "Before the follow-up pass, add the vocabulary-only obligation_detail/5 profile extension "
            "to artifacts created before that carrier existed."
        ),
    )
    parser.add_argument(
        "--procedural-rule-detail-profile-extension",
        action="store_true",
        help=(
            "Before the follow-up pass, add the vocabulary-only procedural_rule_detail/5 profile extension "
            "to artifacts created before that carrier existed."
        ),
    )
    parser.add_argument(
        "--profile-identifier-occurrence-repair-pass",
        action="store_true",
        help="Run the bounded identifier-occurrence repair pass before registered-carrier omission follow-up.",
    )
    parser.add_argument("--openrouter-provider-order", default="")
    parser.add_argument("--openrouter-provider-only", default="")
    parser.add_argument("--openrouter-provider-ignore", default="")
    parser.add_argument("--openrouter-quantizations", default="")
    parser.add_argument("--openrouter-allow-fallbacks", choices=["", "true", "false"], default="")
    parser.add_argument("--openrouter-require-parameters", choices=["", "true", "false"], default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_path = args.run_json if args.run_json.is_absolute() else (REPO_ROOT / args.run_json).resolve()
    record = json.loads(run_path.read_text(encoding="utf-8"))
    parsed_profile = record.get("parsed") if isinstance(record.get("parsed"), dict) else {}
    source_compile = record.get("source_compile") if isinstance(record.get("source_compile"), dict) else {}
    if not parsed_profile or not source_compile:
        raise SystemExit("run-json must contain parsed profile and source_compile")
    source_path = Path(str(record.get("text_file", "")))
    if not source_path.is_absolute():
        source_path = (REPO_ROOT / source_path).resolve()
    source_text = source_path.read_text(encoding="utf-8")
    profile_extension_metadata = (
        record.get("profile_extension_metadata")
        if isinstance(record.get("profile_extension_metadata"), dict)
        else None
    )
    extension_rows: list[dict[str, Any]] = []
    if bool(args.obligation_detail_profile_extension):
        extension_rows.append(_ensure_obligation_detail_predicate(parsed_profile))
    if bool(args.procedural_rule_detail_profile_extension):
        extension_rows.append(_ensure_procedural_rule_detail_predicate(parsed_profile))
    if extension_rows:
        if profile_extension_metadata is None:
            profile_extension_metadata = {"schema_version": "profile_extensions_v1", "extensions": []}
        extensions = profile_extension_metadata.get("extensions")
        if not isinstance(extensions, list):
            extensions = []
            profile_extension_metadata["extensions"] = extensions
        extensions.extend(extension_rows)
        record["profile_extension_metadata"] = profile_extension_metadata
    intake_plan_payload = record.get("intake_plan") if isinstance(record.get("intake_plan"), dict) else {}
    intake_plan = intake_plan_payload.get("parsed") if isinstance(intake_plan_payload.get("parsed"), dict) else {}

    identifier_repair: dict[str, Any] | None = None
    if bool(args.profile_identifier_occurrence_repair_pass):
        identifier_repair = _apply_profile_identifier_occurrence_repair_pass(
            source_compile=source_compile,
            parsed_profile=parsed_profile,
            source_text=source_text,
            intake_plan=intake_plan,
            args=args,
            extra_context=[],
        )

    initial_report = _attach_registered_carrier_delivery_report(
        source_compile=source_compile,
        parsed_profile=parsed_profile,
        profile_extension_metadata=profile_extension_metadata,
        mark_health=False,
    )
    followup = _apply_profile_registered_carrier_omission_followup_pass(
        source_compile=source_compile,
        parsed_profile=parsed_profile,
        source_text=source_text,
        intake_plan=intake_plan,
        args=args,
        extra_context=[],
        profile_extension_metadata=profile_extension_metadata,
        registered_delivery_report=initial_report,
    )
    _apply_governed_obligation_detail_atom_reduction(source_compile)
    final_report = _attach_registered_carrier_delivery_report(
        source_compile=source_compile,
        parsed_profile=parsed_profile,
        profile_extension_metadata=profile_extension_metadata,
    )
    record["source_compile"] = source_compile
    record["registered_carrier_omission_followup_postprocess"] = {
        "schema_version": "registered_carrier_omission_followup_postprocess_v1",
        "parent_run_json": str(run_path),
        "identifier_repair": identifier_repair,
        "initial_findings": initial_report.get("findings", []),
        "followup": followup,
        "final_findings": final_report.get("findings", []),
    }
    if OPENROUTER_CALL_METADATA_LOG:
        record["openrouter_generation_metadata"] = refresh_openrouter_generation_metadata_entries(
            OPENROUTER_CALL_METADATA_LOG,
            api_key=str(args.api_key or ""),
            timeout=min(int(args.timeout), 30),
        )

    out_dir = args.out_dir if args.out_dir.is_absolute() else (REPO_ROOT / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}_{_slug(source_path.stem)}_{_slug(str(args.model))}_registered-carrier-followup"
    json_path = out_dir / f"domain_bootstrap_file_{slug}.json"
    md_path = json_path.with_suffix(".md")
    json_path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    _write_summary(record, md_path)
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(
        json.dumps(
            {
                "attempted": bool(followup.get("attempted")),
                "new_fact_count": int(followup.get("new_fact_count", 0) or 0),
                "initial_finding_count": len(initial_report.get("findings", [])),
                "final_finding_count": len(final_report.get("findings", [])),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
