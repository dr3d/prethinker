#!/usr/bin/env python3
"""Run domain-bootstrap source compiles with explicit lane control.

This is an operator wrapper around run_domain_bootstrap_file.py. It keeps the
expensive source-reading work parallel and bounded while preserving the normal
single-fixture artifact format under one output directory per fixture.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_ROOT = REPO_ROOT / "datasets" / "story_worlds"
DEFAULT_OUT_ROOT = REPO_ROOT / "tmp" / "domain_bootstrap_compile_batch"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.semantic_ir import bootstrap_env_local  # noqa: E402
from scripts.audit_compile_surface_stability import (  # noqa: E402
    _contract_reports as _surface_contract_reports,
    _fact_rows as _surface_fact_rows,
    _facts_from_compile as _surface_facts_from_compile,
    _predicate_name as _surface_predicate_name,
    _source_text_atoms as _surface_source_text_atoms,
)

bootstrap_env_local()

FACT_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\((.*)\)\.\s*$")
TOKEN_RE = re.compile(r"[a-z0-9]+")
DATE_LIKE_ATOM_RE = re.compile(
    r"^(?:v_)?(?:\d{4}[_-]\d{1,2}[_-]\d{1,2}|\d{1,2}[_-]\d{1,2}[_-]\d{2,4}|"
    r"(?:jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|sept|september|"
    r"oct|october|nov|november|dec|december)[_-]\d{1,2}(?:[_-]\d{2,4})?)$",
    re.IGNORECASE,
)
VAGUE_DETAIL_WRAPPER_PREDICATES = {
    "amendment_event",
    "context",
    "detail",
    "event",
    "event_description",
    "event_detail",
    "event_note",
    "event_record",
    "explanation",
    "fact_detail",
    "fact_note",
    "general_event",
    "note",
    "record_event",
    "record_note",
    "source_detail",
    "summary",
    "type",
}
BACKBONE_SURFACE_SLOT_GROUPS: dict[str, tuple[str, ...]] = {
    "identity": ("id", "identifier", "key", "record", "document", "source"),
    "date_time": ("date", "time", "timestamp", "deadline", "duration", "interval", "start", "end"),
    "quantity": ("count", "total", "amount", "quantity", "value", "rate", "ratio", "threshold", "limit", "offset"),
    "state": (
        "status",
        "state",
        "result",
        "outcome",
        "phase",
        "decision",
        "finding",
        "classification",
        "contested",
        "uncontested",
    ),
    "role": ("role", "authority", "actor", "owner", "issuer", "approver", "recorder", "reporter", "compiler"),
    "location": ("location", "place", "site", "room", "address"),
}


@dataclass(frozen=True)
class CompileJob:
    fixture: str
    text_file: Path
    out_dir: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, default=DEFAULT_DATASET_ROOT)
    parser.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT)
    parser.add_argument("--fixture", action="append", default=[], help="Fixture name. Repeat to include multiple.")
    parser.add_argument("--model", default=os.environ.get("PRETHINKER_MODEL", "qwen/qwen3.6-35b-a3b"))
    parser.add_argument("--base-url", default=os.environ.get("PRETHINKER_BASE_URL", "http://127.0.0.1:1234"))
    parser.add_argument("--timeout", type=int, default=900, help="Base per-call LM timeout passed to compile runner.")
    parser.add_argument("--lanes", type=int, default=1, help="Concurrent compile runner processes.")
    parser.add_argument(
        "--timeout-scale",
        type=float,
        default=0.0,
        help="Per-call timeout multiplier. Default 0 means max(1, lanes).",
    )
    parser.add_argument("--domain-hint", default="")
    parser.add_argument("--profile-registry", type=Path, default=None)
    parser.add_argument("--use-profile-registry-direct", action="store_true")
    parser.add_argument("--profile-registry-palette-prior", action="store_true")
    parser.add_argument("--compile-source", action="store_true")
    parser.add_argument("--compile-plan-passes", action="store_true")
    parser.add_argument("--compile-flat-plus-plan-passes", action="store_true")
    parser.add_argument("--max-plan-passes", type=int, default=6)
    parser.add_argument("--focused-pass-ops-schema", action="store_true")
    parser.add_argument("--source-entity-ledger", action="store_true")
    parser.add_argument("--archival-identifier-ledger", action="store_true")
    parser.add_argument("--source-record-ledger", action="store_true")
    parser.add_argument("--source-record-ledger-facts", action="store_true")
    parser.add_argument("--intake-registry-context", action="store_true")
    parser.add_argument("--review-profile", action="store_true")
    parser.add_argument("--profile-review-retry", action="store_true")
    parser.add_argument("--quality-gate", action="store_true", help="Annotate compile summaries with stamp-readiness quality decisions.")
    parser.add_argument("--quality-gate-fail-on-hold", action="store_true", help="Return nonzero when --quality-gate holds any fixture.")
    parser.add_argument(
        "--quality-retry-on-hold",
        action="store_true",
        help=(
            "If the first compile hits a repairable quality-gate hold, rerun that fixture once "
            "with generic corrective compile context. This is a replay diagnostic, not a fact oracle."
        ),
    )
    parser.add_argument("--quality-min-rough-score", type=float, default=0.775)
    parser.add_argument("--quality-max-risk-count", type=int, default=5)
    parser.add_argument(
        "--extra-compile-context-line",
        action="append",
        default=[],
        help="Forward an additional compile-only context line to each fixture compile.",
    )
    parser.add_argument("--summarize-existing", action="store_true", help="Summarize latest existing compile artifacts without running jobs.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    lanes = max(1, int(args.lanes))
    timeout_scale = float(args.timeout_scale) if float(args.timeout_scale) > 0 else float(lanes)
    effective_timeout = max(1, int(round(int(args.timeout) * timeout_scale)))
    dataset_root = _abs(args.dataset_root)
    out_root = _abs(args.out_root)
    fixtures = [str(item) for item in args.fixture] or _discover_fixtures(dataset_root)
    jobs = [_build_job(name, dataset_root=dataset_root, out_root=out_root) for name in fixtures]
    commands = [
        _build_command(
            job,
            args=args,
            model=str(args.model),
            base_url=str(args.base_url),
            timeout=effective_timeout,
        )
        for job in jobs
    ]

    if args.dry_run:
        for command in commands:
            print(" ".join(command))
        return 0

    out_root.mkdir(parents=True, exist_ok=True)
    if bool(args.summarize_existing):
        results = [_summarize_existing_job(job) for job in jobs]
        for result in results:
            print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=lanes) as pool:
            future_map = {
                pool.submit(_run_job_with_optional_quality_retry, job, command, args): job
                for job, command in zip(jobs, commands)
            }
            for future in concurrent.futures.as_completed(future_map):
                result = future.result()
                results.append(result)
                print(json.dumps(result, ensure_ascii=False, sort_keys=True))

    results.sort(key=lambda item: str(item.get("fixture", "")))
    summary = _summarize(
        results,
        lanes=lanes,
        base_timeout=int(args.timeout),
        effective_timeout=effective_timeout,
        quality_gate=bool(args.quality_gate),
        quality_min_rough_score=float(args.quality_min_rough_score),
        quality_max_risk_count=int(args.quality_max_risk_count),
    )
    out_json = _abs(args.out_json) if args.out_json else out_root / "compile_batch_summary.json"
    out_md = _abs(args.out_md) if args.out_md else out_root / "compile_batch_summary.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out_md.write_text(_render_md(summary), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    if not all(int(item.get("returncode", 1)) == 0 for item in results):
        return 1
    quality = summary.get("quality_gate", {})
    if bool(args.quality_gate_fail_on_hold) and isinstance(quality, dict) and not bool(quality.get("passed")):
        return 2
    return 0


def _abs(path: Path | None) -> Path:
    if path is None:
        return REPO_ROOT
    return path if path.is_absolute() else REPO_ROOT / path


def _discover_fixtures(dataset_root: Path) -> list[str]:
    return sorted(path.name for path in dataset_root.iterdir() if (path / "source.md").exists())


def _build_job(name: str, *, dataset_root: Path, out_root: Path) -> CompileJob:
    fixture_root = dataset_root / name
    text_file = fixture_root / "source.md"
    if not text_file.exists():
        raise FileNotFoundError(f"Missing source file: {text_file}")
    return CompileJob(fixture=name, text_file=text_file, out_dir=out_root / name)


def _build_command(
    job: CompileJob,
    *,
    args: argparse.Namespace,
    model: str,
    base_url: str,
    timeout: int,
) -> list[str]:
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "run_domain_bootstrap_file.py"),
        "--text-file",
        str(job.text_file),
        "--model",
        model,
        "--base-url",
        base_url,
        "--timeout",
        str(timeout),
        "--out-dir",
        str(job.out_dir),
    ]
    if str(args.domain_hint or "").strip():
        command.extend(["--domain-hint", str(args.domain_hint).strip()])
    if args.profile_registry is not None:
        command.extend(["--profile-registry", str(_abs(args.profile_registry))])
    if bool(args.use_profile_registry_direct):
        command.append("--use-profile-registry-direct")
    if bool(args.profile_registry_palette_prior):
        command.append("--profile-registry-palette-prior")
    for flag in (
        "compile_source",
        "compile_plan_passes",
        "compile_flat_plus_plan_passes",
        "focused_pass_ops_schema",
        "source_entity_ledger",
        "archival_identifier_ledger",
        "source_record_ledger",
        "source_record_ledger_facts",
        "intake_registry_context",
        "review_profile",
        "profile_review_retry",
    ):
        if bool(getattr(args, flag, False)):
            command.append("--" + flag.replace("_", "-"))
    if int(args.max_plan_passes) > 0:
        command.extend(["--max-plan-passes", str(int(args.max_plan_passes))])
    for line in (str(item).strip() for item in getattr(args, "extra_compile_context_line", []) or []):
        if line:
            command.extend(["--extra-compile-context-line", line])
    return command


def _run_job(job: CompileJob, command: list[str]) -> dict[str, Any]:
    job.out_dir.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc)
    proc = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True)
    latest_json = _latest_compile_json(job.out_dir)
    summary: dict[str, Any] = {}
    if latest_json is not None:
        try:
            payload = json.loads(latest_json.read_text(encoding="utf-8"))
            summary = _extract_compile_summary(payload)
        except Exception as exc:  # pragma: no cover - operator diagnostic only.
            summary = {"summary_error": str(exc)}
    return {
        "fixture": job.fixture,
        "returncode": proc.returncode,
        "started": started.isoformat(),
        "finished": datetime.now(timezone.utc).isoformat(),
        "out_dir": str(job.out_dir),
        "compile_json": str(latest_json) if latest_json else "",
        "summary": summary,
        "stdout_tail": proc.stdout[-2000:],
        "stderr_tail": proc.stderr[-2000:],
    }


def _summarize_existing_job(job: CompileJob) -> dict[str, Any]:
    latest_json = _latest_compile_json(job.out_dir)
    summary: dict[str, Any] = {}
    returncode = 0
    if latest_json is None:
        returncode = 1
    else:
        try:
            payload = json.loads(latest_json.read_text(encoding="utf-8"))
            summary = _extract_compile_summary(payload)
        except Exception as exc:  # pragma: no cover - operator diagnostic only.
            returncode = 1
            summary = {"summary_error": str(exc)}
    return {
        "fixture": job.fixture,
        "returncode": returncode,
        "started": "",
        "finished": datetime.now(timezone.utc).isoformat(),
        "out_dir": str(job.out_dir),
        "compile_json": str(latest_json) if latest_json else "",
        "summary": summary,
        "stdout_tail": "",
        "stderr_tail": "",
    }


def _latest_compile_json(out_dir: Path) -> Path | None:
    paths = sorted(out_dir.glob("domain_bootstrap_file_*.json"), key=lambda path: path.stat().st_mtime)
    return paths[-1] if paths else None


def _extract_compile_summary(payload: dict[str, Any]) -> dict[str, Any]:
    source_compile = payload.get("source_compile", {})
    compile_payload = payload.get("compile", {})
    diagnostics = compile_payload.get("admission_diagnostics", {}) if isinstance(compile_payload, dict) else {}
    operations = diagnostics.get("operations", []) if isinstance(diagnostics, dict) else []
    compile_admitted = _optional_int(source_compile.get("admitted_count")) if isinstance(source_compile, dict) else None
    compile_skipped = _optional_int(source_compile.get("skipped_count")) if isinstance(source_compile, dict) else None
    if compile_admitted is None:
        compile_admitted = sum(1 for row in operations if isinstance(row, dict) and bool(row.get("admitted")))
    if compile_skipped is None:
        compile_skipped = sum(1 for row in operations if isinstance(row, dict) and not bool(row.get("admitted")))
    score = payload.get("score", {}) if isinstance(payload.get("score"), dict) else {}
    predicates = payload.get("candidate_predicates")
    if predicates is None and isinstance(payload.get("parsed"), dict):
        predicates = payload.get("parsed", {}).get("candidate_predicates")
    return {
        "parsed_ok": bool(payload.get("parsed_ok", False)),
        "candidate_predicates": len(predicates or []),
        "compile_admitted": compile_admitted,
        "compile_skipped": compile_skipped,
        "rough_score": score.get("rough_score"),
        "risk_count": score.get("risk_count"),
        "repeated_structure_count": score.get("repeated_structure_count"),
        "repeated_structure_id_only_record_refs": score.get("repeated_structure_id_only_record_refs", []),
        "repeated_structure_role_mismatch_refs": score.get("repeated_structure_role_mismatch_refs", []),
        "frontier_unknown_positive_predicate_count": score.get("frontier_unknown_positive_predicate_count"),
        "frontier_unknown_positive_predicate_refs": score.get("frontier_unknown_positive_predicate_refs", []),
        "generic_predicate_count": score.get("generic_predicate_count"),
        "detail_wrapper_drift_flags": _detail_wrapper_drift_flags(payload),
        "compile_surface_contract_flags": _compile_surface_contract_flags(payload),
        "profile_delivery_flags": _profile_delivery_flags(payload),
    }


def _run_job_with_optional_quality_retry(
    job: CompileJob,
    command: list[str],
    args: argparse.Namespace,
) -> dict[str, Any]:
    result = _run_job(job, command)
    if not bool(getattr(args, "quality_retry_on_hold", False)):
        return result
    gate = _quality_gate_result(
        result,
        min_rough_score=float(getattr(args, "quality_min_rough_score", 0.775)),
        max_risk_count=int(getattr(args, "quality_max_risk_count", 5)),
    )
    if bool(gate.get("passed")):
        return result
    context_lines = _quality_retry_context_lines(gate)
    if not context_lines:
        result["quality_retry"] = {
            "attempted": False,
            "reason": "no_generic_quality_retry_context",
            "initial_reasons": gate.get("reasons", []),
        }
        return result
    retry_command = list(command)
    for line in context_lines:
        retry_command.extend(["--extra-compile-context-line", line])
    retry_result = _run_job(job, retry_command)
    retry_result["quality_retry"] = {
        "attempted": True,
        "initial_reasons": gate.get("reasons", []),
        "context_lines": context_lines,
        "initial_compile_json": result.get("compile_json", ""),
    }
    return retry_result


def _quality_retry_context_lines(gate: dict[str, Any]) -> list[str]:
    reasons = [str(item).strip() for item in gate.get("reasons", []) if str(item).strip()]
    lines: list[str] = []
    seen: set[str] = set()

    def add(line: str) -> None:
        if line not in seen:
            seen.add(line)
            lines.append(line)

    for reason in reasons:
        if reason.startswith("detail_wrapper_drift:") and "_backbone_missing_with_wrapper:" in reason:
            body = reason.split("detail_wrapper_drift:", 1)[1]
            group = body.split("_backbone_missing_with_wrapper:", 1)[0].strip()
            if group:
                add(
                    "QUALITY GATE RETRY: the prior compile preserved a broad detail/event/source wrapper "
                    f"while source-record fields signaled a missing {group} backbone surface. In this retry, "
                    f"emit compatible direct {group} predicates before any wrapper rows. A source_detail, "
                    "event, context, note, or summary row is additive only and must not be the only carrier "
                    f"for source-stated {group} values."
                )
        if "operational_lifecycle_preservation:" in reason:
            add(
                "QUALITY GATE RETRY: the prior compile saw repeated dated lifecycle/status source lines "
                "but did not preserve complete direct lifecycle units. In this retry, for each stated dated "
                "received/filed/approved/denied/withdrawn/corrected/superseded/reopened/closed/current-status "
                "line, emit a compatible direct unit that keeps governed subject or item, lifecycle state/action, "
                "and date or turn joinable. Two-slot status/result rows without the date/event join are shallow."
            )
        if "source_authority_pair_preservation:" in reason:
            add(
                "QUALITY GATE RETRY: the prior compile saw source text where a rule, policy, order, authority, "
                "or authorized actor governs an action/status/scope, but no direct source-authority surface was "
                "delivered. In this retry, emit compatible direct source_authority/3 or equivalent rows that keep "
                "the governed subject or scope, authority/source, and authorized action/status joinable. A rule "
                "description, note, docket text, or source_record row is additive only and must not be the only "
                "carrier for an explicit authority constraint."
            )
        if "profile_delivery:source_authority_carrier_offered_but_undelivered:" in reason:
            add(
                "QUALITY GATE RETRY: the prior compile offered a direct source-authority carrier but emitted no "
                "matching rows. In this retry, populate source_authority/3 or an equivalent allowed carrier for "
                "source-stated authority/rule/order/policy constraints, keeping governed subject or scope, "
                "authority/source, and authorized action/status joinable."
            )
        if "profile_delivery:source_claim_carrier_offered_but_undelivered:" in reason:
            add(
                "QUALITY GATE RETRY: the prior compile offered a direct source-attributed claim carrier but emitted "
                "no matching rows. In this retry, populate source_attributed_claim/4 or an equivalent allowed carrier "
                "for source-stated reports, notes, statements, findings, opinions, or unresolved claims, keeping "
                "source/speaker, content/status/finding, and source row or scope joinable."
            )
        if "profile_delivery:status_state_carrier_offered_but_undelivered:" in reason:
            add(
                "QUALITY GATE RETRY: the prior compile offered a direct status/state carrier but emitted no matching "
                "rows. In this retry, populate status_state_at/4, *_status_at/3-4, *_state_at/3-4, or an equivalent "
                "allowed carrier for point-in-time status, current condition, availability, pending resolution, "
                "supersession, or scoped population state. Keep subject/subset, state value, and temporal/source scope "
                "together."
            )
        if "profile_delivery:quantity_carrier_offered_but_undelivered:" in reason:
            add(
                "QUALITY GATE RETRY: the prior compile offered a direct quantity/event carrier but emitted no matching "
                "rows. In this retry, populate event_measurement/4, event_quantity/4, reading_value/4, "
                "measurement_value/4, metric_observation/4, or an equivalent allowed carrier for source-stated "
                "numeric values, keeping event/record id, measure, value, and unit/basis together."
            )
    return lines


def _compile_surface_contract_flags(payload: dict[str, Any]) -> list[str]:
    facts = _surface_facts_from_compile(payload)
    source_facts = [fact for fact in facts if _surface_predicate_name(fact).startswith("source_record")]
    direct_facts = [fact for fact in facts if not _surface_predicate_name(fact).startswith("source_record")]
    if not source_facts or not direct_facts:
        return []

    source_rows = _surface_fact_rows(source_facts)
    direct_rows = _surface_fact_rows(direct_facts)
    source_texts = _surface_source_text_atoms(source_facts)
    flags: list[str] = []
    for report in _surface_contract_reports(source_texts=source_texts, source_rows=source_rows, direct_rows=direct_rows):
        status = str(report.get("status") or "")
        if status in {"pass", "not_applicable"}:
            continue
        contract = str(report.get("contract") or "unknown_contract")
        source_signal_count = _optional_int(report.get("source_signal_count")) or 0
        direct_surface_count = _optional_int(report.get("direct_surface_count")) or 0
        flags.append(f"{contract}:{status}:source={source_signal_count}:direct={direct_surface_count}")
    return flags


def _profile_delivery_flags(payload: dict[str, Any]) -> list[str]:
    source_compile = payload.get("source_compile", {}) if isinstance(payload.get("source_compile"), dict) else {}
    delivery = source_compile.get("profile_delivery", {}) if isinstance(source_compile.get("profile_delivery"), dict) else {}
    findings = delivery.get("findings", []) if isinstance(delivery.get("findings"), list) else []
    flags: list[str] = []
    for finding in findings:
        if not isinstance(finding, dict):
            continue
        cls = str(finding.get("class") or "").strip()
        if not cls:
            continue
        source_signal_count = _optional_int(finding.get("source_signal_count")) or 0
        offered = [
            str(item).strip()
            for item in finding.get("offered_carriers", [])
            if str(item).strip()
        ] if isinstance(finding.get("offered_carriers"), list) else []
        offered_label = ",".join(offered[:6]) if offered else "none"
        flags.append(f"{cls}:source={source_signal_count}:offered={offered_label}")
    return flags


def _detail_wrapper_drift_flags(payload: dict[str, Any]) -> list[str]:
    source_compile = payload.get("source_compile", {}) if isinstance(payload.get("source_compile"), dict) else {}
    facts = source_compile.get("facts", []) if isinstance(source_compile.get("facts"), list) else []
    source_facts = [str(fact) for fact in facts if _predicate_name(str(fact)).startswith("source_record")]
    direct_facts = [str(fact) for fact in facts if not _predicate_name(str(fact)).startswith("source_record")]
    direct_predicates = {_predicate_name(fact) for fact in direct_facts if _predicate_name(fact)}
    backbone_facts = [fact for fact in direct_facts if _predicate_name(fact) not in VAGUE_DETAIL_WRAPPER_PREDICATES]
    candidate_predicates = _candidate_predicate_names(payload)
    wrapper_hits = sorted((direct_predicates | candidate_predicates) & VAGUE_DETAIL_WRAPPER_PREDICATES)
    if not wrapper_hits:
        return []
    source_groups = _source_record_slot_groups(source_facts)
    direct_groups = _fact_slot_groups(backbone_facts)
    flags: list[str] = []
    for group in sorted(source_groups):
        if group in direct_groups:
            continue
        flags.append(f"{group}_backbone_missing_with_wrapper:{','.join(wrapper_hits[:4])}")
    return flags


def _predicate_name(fact: str) -> str:
    match = FACT_RE.match(str(fact).strip())
    return match.group(1) if match else ""


def _fact_args(fact: str) -> list[str]:
    match = FACT_RE.match(str(fact).strip())
    if not match:
        return []
    return [part.strip().strip("'\"") for part in match.group(2).split(",")]


def _tokens(text: str) -> set[str]:
    return set(TOKEN_RE.findall(str(text).casefold().replace("_", " ")))


def _slot_groups_for_text(text: str) -> set[str]:
    tokens = _tokens(text)
    groups: set[str] = set()
    for group, markers in BACKBONE_SURFACE_SLOT_GROUPS.items():
        if tokens.intersection(markers):
            groups.add(group)
    return groups


def _source_record_slot_groups(source_facts: list[str]) -> set[str]:
    groups: set[str] = set()
    for fact in source_facts:
        predicate = _predicate_name(fact)
        args = _fact_args(fact)
        if predicate == "source_record_field" and len(args) >= 2:
            groups.update(_slot_groups_for_text(args[1]))
        elif predicate == "source_record_cell" and len(args) >= 3:
            groups.update(_slot_groups_for_text(args[2]))
        elif predicate == "source_record_label" and len(args) >= 2:
            groups.update(_slot_groups_for_text(args[1]))
    return groups


def _fact_slot_groups(facts: list[str]) -> set[str]:
    groups: set[str] = set()
    for fact in facts:
        groups.update(_slot_groups_for_text(_predicate_name(fact)))
        for arg in _fact_args(fact):
            if DATE_LIKE_ATOM_RE.fullmatch(str(arg or "").strip()):
                groups.add("date_time")
            groups.update(_slot_groups_for_text(arg))
    return groups


def _candidate_predicate_names(payload: dict[str, Any]) -> set[str]:
    parsed = payload.get("parsed", {}) if isinstance(payload.get("parsed"), dict) else {}
    rows = parsed.get("candidate_predicates")
    names: set[str] = set()
    if not isinstance(rows, list):
        return names
    for row in rows:
        if isinstance(row, dict):
            raw = str(row.get("name") or row.get("predicate") or row.get("signature") or "")
        else:
            raw = str(row)
        name = raw.split("/", 1)[0].strip()
        if name:
            names.add(name)
    return names


def _optional_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _optional_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _quality_gate_result(
    result: dict[str, Any],
    *,
    min_rough_score: float,
    max_risk_count: int,
) -> dict[str, Any]:
    item = result.get("summary", {}) if isinstance(result, dict) else {}
    reasons: list[str] = []
    returncode = result.get("returncode")
    if returncode != 0:
        reasons.append(f"returncode={returncode}")
    if not bool(item.get("parsed_ok")):
        reasons.append("parsed_ok=false")
    rough_score = _optional_float(item.get("rough_score"))
    if rough_score is None:
        reasons.append("rough_score_missing")
    elif rough_score < min_rough_score:
        reasons.append(f"rough_score<{min_rough_score:g}")
    risk_count = _optional_int(item.get("risk_count"))
    if risk_count is None:
        reasons.append("risk_count_missing")
    elif risk_count > max_risk_count:
        reasons.append(f"risk_count>{max_risk_count}")
    detail_wrapper_flags = [
        str(flag)
        for flag in item.get("detail_wrapper_drift_flags", [])
        if str(flag).strip()
    ] if isinstance(item.get("detail_wrapper_drift_flags"), list) else []
    if detail_wrapper_flags:
        reasons.extend(f"detail_wrapper_drift:{flag}" for flag in detail_wrapper_flags)
    contract_flags = [
        str(flag)
        for flag in item.get("compile_surface_contract_flags", [])
        if str(flag).strip()
    ] if isinstance(item.get("compile_surface_contract_flags"), list) else []
    if contract_flags:
        reasons.extend(f"compile_surface_contract:{flag}" for flag in contract_flags)
    profile_delivery_flags = [
        str(flag)
        for flag in item.get("profile_delivery_flags", [])
        if str(flag).strip()
    ] if isinstance(item.get("profile_delivery_flags"), list) else []
    if profile_delivery_flags:
        reasons.extend(f"profile_delivery:{flag}" for flag in profile_delivery_flags)
    admitted = _optional_int(item.get("compile_admitted")) or 0
    skipped = _optional_int(item.get("compile_skipped")) or 0
    if admitted <= 0:
        reasons.append("compile_admitted<=0")
    return {
        "fixture": str(result.get("fixture", "")),
        "passed": not reasons,
        "decision": "pass" if not reasons else "hold",
        "reasons": reasons,
        "rough_score": rough_score,
        "risk_count": risk_count,
        "compile_admitted": admitted,
        "compile_skipped": skipped,
        "compile_skipped_share": round(skipped / max(1, admitted + skipped), 4),
        "candidate_predicates": _optional_int(item.get("candidate_predicates")) or 0,
        "compile_json": str(result.get("compile_json", "")),
        "detail_wrapper_drift_flags": detail_wrapper_flags,
        "compile_surface_contract_flags": contract_flags,
        "profile_delivery_flags": profile_delivery_flags,
    }


def _summarize(
    results: list[dict[str, Any]],
    *,
    lanes: int,
    base_timeout: int,
    effective_timeout: int,
    quality_gate: bool = False,
    quality_min_rough_score: float = 0.775,
    quality_max_risk_count: int = 5,
) -> dict[str, Any]:
    totals = {
        "candidate_predicates": 0,
        "compile_admitted": 0,
        "compile_skipped": 0,
    }
    parsed_ok_count = 0
    for result in results:
        summary = result.get("summary", {})
        if not isinstance(summary, dict):
            continue
        parsed_ok_count += 1 if bool(summary.get("parsed_ok")) else 0
        for key in totals:
            totals[key] += int(summary.get(key, 0) or 0)
    summary = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "lanes": lanes,
        "base_timeout": base_timeout,
        "effective_timeout": effective_timeout,
        "fixture_count": len(results),
        "parsed_ok_count": parsed_ok_count,
        "totals": totals,
        "results": results,
    }
    if quality_gate:
        gate_rows = [
            _quality_gate_result(
                result,
                min_rough_score=quality_min_rough_score,
                max_risk_count=quality_max_risk_count,
            )
            for result in results
        ]
        summary["quality_gate"] = {
            "schema_version": "compile_quality_gate_v1",
            "min_rough_score": quality_min_rough_score,
            "max_risk_count": quality_max_risk_count,
            "passed": all(row["passed"] for row in gate_rows),
            "pass_count": sum(1 for row in gate_rows if row["passed"]),
            "hold_count": sum(1 for row in gate_rows if not row["passed"]),
            "rows": gate_rows,
        }
    return summary


def _render_md(summary: dict[str, Any]) -> str:
    totals = summary.get("totals", {})
    lines = [
        "# Domain Bootstrap Compile Batch Summary",
        "",
        f"Generated: {summary.get('generated')}",
        "",
        f"- Lanes: `{summary.get('lanes')}`",
        f"- Base timeout: `{summary.get('base_timeout')}`",
        f"- Effective per-call timeout: `{summary.get('effective_timeout')}`",
        f"- Fixtures: `{summary.get('fixture_count')}`",
        f"- Parsed OK: `{summary.get('parsed_ok_count')}`",
        f"- Candidate predicates: `{totals.get('candidate_predicates', 0)}`",
        f"- Compile admitted / skipped: `{totals.get('compile_admitted', 0)} / {totals.get('compile_skipped', 0)}`",
        "",
        "| Fixture | Return | Predicates | Admitted | Skipped | Rough | Compile JSON |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for result in summary.get("results", []):
        item = result.get("summary", {}) if isinstance(result, dict) else {}
        lines.append(
            "| `{fixture}` | `{returncode}` | {predicates} | {admitted} | {skipped} | {rough} | `{compile_json}` |".format(
                fixture=result.get("fixture", ""),
                returncode=result.get("returncode", ""),
                predicates=item.get("candidate_predicates", 0),
                admitted=item.get("compile_admitted", 0),
                skipped=item.get("compile_skipped", 0),
                rough=item.get("rough_score", ""),
                compile_json=result.get("compile_json", ""),
            )
        )
    lines.append("")
    quality_gate = summary.get("quality_gate", {})
    if isinstance(quality_gate, dict):
        lines.extend(
            [
                "## Compile Quality Gate",
                "",
                f"- Decision: `{'pass' if quality_gate.get('passed') else 'hold'}`",
                f"- Passed / held: `{quality_gate.get('pass_count', 0)} / {quality_gate.get('hold_count', 0)}`",
                f"- Minimum rough score: `{quality_gate.get('min_rough_score')}`",
                f"- Maximum risk count: `{quality_gate.get('max_risk_count')}`",
                "",
                "| Fixture | Decision | Reasons | Rough | Risk | Admitted | Skipped | Skipped Share |",
                "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in quality_gate.get("rows", []):
            if not isinstance(row, dict):
                continue
            reasons = ", ".join(str(item) for item in row.get("reasons", [])) or "n/a"
            lines.append(
                "| `{fixture}` | `{decision}` | {reasons} | {rough} | {risk} | {admitted} | {skipped} | {share} |".format(
                    fixture=row.get("fixture", ""),
                    decision=row.get("decision", ""),
                    reasons=reasons,
                    rough=row.get("rough_score", ""),
                    risk=row.get("risk_count", ""),
                    admitted=row.get("compile_admitted", 0),
                    skipped=row.get("compile_skipped", 0),
                    share=row.get("compile_skipped_share", 0),
                )
            )
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
