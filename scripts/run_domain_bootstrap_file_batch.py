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
from scripts.run_domain_bootstrap_file import _attach_profile_admission_report  # noqa: E402

bootstrap_env_local()

FACT_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\((.*)\)\.\s*$")
TOKEN_RE = re.compile(r"[a-z0-9]+")
DATE_LIKE_ATOM_RE = re.compile(
    r"^(?:v_)?(?:\d{4}[_-]\d{1,2}[_-]\d{1,2}|\d{1,2}[_-]\d{1,2}[_-]\d{2,4}|"
    r"(?:jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|sept|september|"
    r"oct|october|nov|november|dec|december)[_-]\d{1,2}(?:[_-]\d{2,4})?)$",
    re.IGNORECASE,
)
MONTH_DATE_RE = re.compile(
    r"\b(?P<month>jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|"
    r"sep|sept|september|oct|october|nov|november|dec|december)[_\-\s]+"
    r"(?P<day>\d{1,2}),?[_\-\s]+(?P<year>(?:19|20)\d{2})\b",
    re.IGNORECASE,
)
ISO_DATE_ATOM_RE = re.compile(r"\b(?:v_)?(?P<year>(?:19|20)\d{2})[_-](?P<month>\d{1,2})[_-](?P<day>\d{1,2})\b")
PUBLIC_RECALL_PRIOR_DATE_TEXT_RE = re.compile(
    r"\b(?:expand(?:ing|s|ed)?|expansion|amend(?:ing|s|ed)?|updat(?:ing|es|ed)?|"
    r"supersed(?:ing|es|ed)?|revis(?:ing|es|ed)?)\b"
    r"[^\n]{0,80}\b(?P<date1>(?:jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|"
    r"sep|sept|september|oct|october|nov|november|dec|december)\s+\d{1,2},?\s+(?:19|20)\d{2})\b"
    r"[^\n]{0,60}\b(?:recall|notice|announcement|advisory)\b|"
    r"\b(?:original|prior|previous|earlier|initial)\s+(?:recall|notice|announcement|advisory)\b"
    r"[^\n]{0,80}\b(?P<date2>(?:jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|"
    r"sep|sept|september|oct|october|nov|november|dec|december)\s+\d{1,2},?\s+(?:19|20)\d{2})\b",
    re.IGNORECASE,
)
MONTH_ALIASES: dict[str, int] = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}
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
US_STATE_ALIASES: dict[str, tuple[str, ...]] = {
    "al": ("alabama", "al"),
    "ak": ("alaska", "ak"),
    "az": ("arizona", "az"),
    "ar": ("arkansas", "ar"),
    "ca": ("california", "ca"),
    "co": ("colorado", "co"),
    "ct": ("connecticut", "ct"),
    "de": ("delaware", "de"),
    "dc": ("district of columbia", "dc"),
    "fl": ("florida", "fl"),
    "ga": ("georgia", "ga"),
    "hi": ("hawaii", "hi"),
    "ia": ("iowa", "ia"),
    "id": ("idaho", "id"),
    "il": ("illinois", "il"),
    "in": ("indiana", "in"),
    "ks": ("kansas", "ks"),
    "ky": ("kentucky", "ky"),
    "la": ("louisiana", "la"),
    "ma": ("massachusetts", "ma"),
    "md": ("maryland", "md"),
    "me": ("maine", "me"),
    "mi": ("michigan", "mi"),
    "mn": ("minnesota", "mn"),
    "mo": ("missouri", "mo"),
    "ms": ("mississippi", "ms"),
    "mt": ("montana", "mt"),
    "nc": ("north carolina", "nc"),
    "nd": ("north dakota", "nd"),
    "ne": ("nebraska", "ne"),
    "nh": ("new hampshire", "nh"),
    "nj": ("new jersey", "nj"),
    "nm": ("new mexico", "nm"),
    "nv": ("nevada", "nv"),
    "ny": ("new york", "ny"),
    "oh": ("ohio", "oh"),
    "ok": ("oklahoma", "ok"),
    "or": ("oregon", "or"),
    "pa": ("pennsylvania", "pa"),
    "ri": ("rhode island", "ri"),
    "sc": ("south carolina", "sc"),
    "sd": ("south dakota", "sd"),
    "tn": ("tennessee", "tn"),
    "tx": ("texas", "tx"),
    "ut": ("utah", "ut"),
    "va": ("virginia", "va"),
    "vt": ("vermont", "vt"),
    "wa": ("washington", "wa"),
    "wi": ("wisconsin", "wi"),
    "wv": ("west virginia", "wv"),
    "wy": ("wyoming", "wy"),
}
DISTRIBUTION_TABLE_MARKERS = {
    "aldi",
    "distribution",
    "distributor",
    "foodland",
    "kroger",
    "location",
    "locations",
    "retail",
    "retailer",
    "retailers",
    "save",
    "shop",
    "sold",
    "store",
    "stores",
    "walmart",
}
DISTRIBUTION_DIRECT_PREDICATE_MARKERS = (
    "distributed",
    "distribution",
    "retail",
    "retailer",
    "restricted",
    "sold",
    "state",
    "store",
)
IDENTITY_NAME_PREDICATES = {
    "asset_name",
    "artifact_name",
    "device_name",
    "item_name",
    "object_name",
    "product_name",
    "record_name",
}
IDENTITY_EQUIVALENCE_PREDICATE_MARKERS = (
    "alias",
    "canonical",
    "equivalent",
    "same_as",
    "synonym",
)
IDENTITY_JOIN_RISK_PREDICATE_MARKERS = (
    "distribution",
    "retail",
    "retailer",
    "restriction",
    "sold",
    "state",
    "store",
)


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
    parser.add_argument("--allow-global-first-profile-registry-palette-prior", action="store_true")
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
    parser.add_argument(
        "--quality-retry-max-attempts",
        type=int,
        default=1,
        help=(
            "Maximum bounded quality-retry attempts per fixture when --quality-retry-on-hold is set. "
            "Default 1 preserves the historical single retry."
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
        results = [
            _summarize_existing_job(
                job,
                quality_select=bool(args.quality_gate),
                quality_min_rough_score=float(args.quality_min_rough_score),
                quality_max_risk_count=int(args.quality_max_risk_count),
            )
            for job in jobs
        ]
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
    if bool(getattr(args, "allow_global_first_profile_registry_palette_prior", False)):
        command.append("--allow-global-first-profile-registry-palette-prior")
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


def _summarize_existing_job(
    job: CompileJob,
    *,
    quality_select: bool = False,
    quality_min_rough_score: float = 0.775,
    quality_max_risk_count: int = 5,
) -> dict[str, Any]:
    selected_json = _select_existing_compile_json(
        job,
        quality_select=quality_select,
        quality_min_rough_score=quality_min_rough_score,
        quality_max_risk_count=quality_max_risk_count,
    )
    summary: dict[str, Any] = {}
    returncode = 0
    if selected_json is None:
        returncode = 1
    else:
        try:
            payload = json.loads(selected_json.read_text(encoding="utf-8"))
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
        "compile_json": str(selected_json) if selected_json else "",
        "summary": summary,
        "stdout_tail": "",
        "stderr_tail": "",
    }


def _select_existing_compile_json(
    job: CompileJob,
    *,
    quality_select: bool,
    quality_min_rough_score: float,
    quality_max_risk_count: int,
) -> Path | None:
    paths = sorted(job.out_dir.glob("domain_bootstrap_file_*.json"), key=lambda path: path.stat().st_mtime)
    if not paths:
        return None
    if not quality_select:
        return paths[-1]
    ranked: list[tuple[tuple[int, int, int, int, int, float, float], Path]] = []
    for path in paths:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            summary = _extract_compile_summary(payload)
        except Exception:
            continue
        result = {
            "fixture": job.fixture,
            "returncode": 0,
            "compile_json": str(path),
            "summary": summary,
        }
        gate = _quality_gate_result(
            result,
            min_rough_score=quality_min_rough_score,
            max_risk_count=quality_max_risk_count,
        )
        ranked.append((_quality_gate_rank_tuple(gate), path))
    if not ranked:
        return paths[-1]
    return min(ranked, key=lambda item: item[0])[1]


def _latest_compile_json(out_dir: Path) -> Path | None:
    paths = sorted(out_dir.glob("domain_bootstrap_file_*.json"), key=lambda path: path.stat().st_mtime)
    return paths[-1] if paths else None


def _diagnostic_rejected_flat_pass_skipped_count(source_compile: dict[str, Any]) -> int:
    explicit = _optional_int(source_compile.get("diagnostic_rejected_flat_pass_skipped_count"))
    if explicit is not None:
        return max(0, explicit)
    flat = source_compile.get("flat_pass")
    focused = source_compile.get("focused_passes")
    if not isinstance(flat, dict) or not isinstance(focused, dict):
        return 0
    projected_decision = str(flat.get("projected_decision", "")).strip().lower()
    flat_admitted = _optional_int(flat.get("admitted_count")) or 0
    flat_skipped = _optional_int(flat.get("skipped_count")) or 0
    focused_admitted = _optional_int(focused.get("admitted_count")) or 0
    if projected_decision == "reject" and flat_admitted == 0 and flat_skipped > 0 and focused_admitted > 0:
        return flat_skipped
    return 0


def _extract_compile_summary(payload: dict[str, Any]) -> dict[str, Any]:
    _refresh_profile_delivery_reports(payload)
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
    effective_admitted = _optional_int(source_compile.get("effective_admitted_count")) if isinstance(source_compile, dict) else None
    effective_skipped = _optional_int(source_compile.get("effective_skipped_count")) if isinstance(source_compile, dict) else None
    diagnostic_rejected_skipped = (
        _diagnostic_rejected_flat_pass_skipped_count(source_compile)
        if isinstance(source_compile, dict)
        else 0
    )
    if effective_admitted is None:
        effective_admitted = compile_admitted
    if effective_skipped is None:
        effective_skipped = max(0, compile_skipped - diagnostic_rejected_skipped)
    score = payload.get("score", {}) if isinstance(payload.get("score"), dict) else {}
    predicates = payload.get("candidate_predicates")
    if predicates is None and isinstance(payload.get("parsed"), dict):
        predicates = payload.get("parsed", {}).get("candidate_predicates")
    return {
        "parsed_ok": bool(payload.get("parsed_ok", False)),
        "candidate_predicates": len(predicates or []),
        "compile_admitted": compile_admitted,
        "compile_skipped": compile_skipped,
        "compile_effective_admitted": effective_admitted,
        "compile_effective_skipped": effective_skipped,
        "compile_diagnostic_rejected_skipped": diagnostic_rejected_skipped,
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
        "public_recall_surface_flags": _public_recall_surface_flags(payload),
        "table_list_surface_coverage_flags": _table_list_surface_coverage_flags(payload),
        "table_list_surface_flags": _table_list_surface_flags(payload),
        "identity_canonicality_flags": _identity_canonicality_flags(payload),
    }


def _refresh_profile_delivery_reports(payload: dict[str, Any]) -> None:
    source_compile = payload.get("source_compile")
    parsed_profile = payload.get("parsed")
    if not isinstance(source_compile, dict) or not isinstance(parsed_profile, dict):
        return
    text_path = Path(str(payload.get("text_file") or ""))
    if not text_path.is_file():
        return
    try:
        source_text = text_path.read_text(encoding="utf-8")
    except OSError:
        return
    _attach_profile_admission_report(
        source_compile=source_compile,
        domain_hint=str(payload.get("domain_hint") or ""),
        intake_plan=payload.get("intake_plan") if isinstance(payload.get("intake_plan"), dict) else None,
        source_text=source_text,
        parsed_profile=parsed_profile,
    )


def _run_job_with_optional_quality_retry(
    job: CompileJob,
    command: list[str],
    args: argparse.Namespace,
) -> dict[str, Any]:
    result = _run_job(job, command)
    if not bool(getattr(args, "quality_retry_on_hold", False)):
        return result
    max_attempts = max(1, int(getattr(args, "quality_retry_max_attempts", 1) or 1))
    first_compile_json = str(result.get("compile_json", ""))
    first_reasons: list[str] = []
    attempts: list[dict[str, Any]] = []
    current = result
    best_result = result
    best_gate: dict[str, Any] | None = None
    final_gate: dict[str, Any] | None = None
    accumulated_context_lines: list[str] = []
    for attempt_index in range(1, max_attempts + 1):
        gate = _quality_gate_result(
            current,
            min_rough_score=float(getattr(args, "quality_min_rough_score", 0.775)),
            max_risk_count=int(getattr(args, "quality_max_risk_count", 5)),
        )
        final_gate = gate
        if best_gate is None or _quality_gate_rank_tuple(gate) < _quality_gate_rank_tuple(best_gate):
            best_gate = gate
            best_result = current
        if attempt_index == 1:
            first_reasons = [str(item) for item in gate.get("reasons", [])]
        if bool(gate.get("passed")):
            if attempts:
                current["quality_retry"] = _quality_retry_metadata(
                    attempts=attempts,
                    first_reasons=first_reasons,
                    first_compile_json=first_compile_json,
                    final_gate=gate,
                )
            return current
        new_context_lines = _quality_retry_context_lines(gate)
        context_lines = _merge_quality_retry_context_lines(accumulated_context_lines, new_context_lines)
        if not context_lines:
            current["quality_retry"] = _quality_retry_metadata(
                attempts=attempts,
                first_reasons=first_reasons,
                first_compile_json=first_compile_json,
                final_gate=gate,
                blocked_reason="no_generic_quality_retry_context",
            )
            return current
        retry_command = list(command)
        for line in context_lines:
            retry_command.extend(["--extra-compile-context-line", line])
        retry_result = _run_job(job, retry_command)
        attempts.append(
            {
                "attempt": attempt_index,
                "input_compile_json": current.get("compile_json", ""),
                "reasons": gate.get("reasons", []),
                "context_lines": context_lines,
                "output_compile_json": retry_result.get("compile_json", ""),
            }
        )
        accumulated_context_lines = context_lines
        current = retry_result
    final_gate = _quality_gate_result(
        current,
        min_rough_score=float(getattr(args, "quality_min_rough_score", 0.775)),
        max_risk_count=int(getattr(args, "quality_max_risk_count", 5)),
    )
    if best_gate is None or _quality_gate_rank_tuple(final_gate) < _quality_gate_rank_tuple(best_gate):
        best_gate = final_gate
        best_result = current
    selected = best_result
    selected_gate = best_gate or final_gate
    blocked_reason = "max_attempts_exhausted" if not bool(final_gate.get("passed")) else ""
    if selected is not current and not bool(final_gate.get("passed")):
        blocked_reason = "max_attempts_exhausted_best_attempt_selected"
    selected["quality_retry"] = _quality_retry_metadata(
        attempts=attempts,
        first_reasons=first_reasons,
        first_compile_json=first_compile_json,
        final_gate=selected_gate,
        blocked_reason=blocked_reason,
    )
    if selected is not current:
        selected["quality_retry"]["last_decision"] = final_gate.get("decision", "")
        selected["quality_retry"]["last_reasons"] = final_gate.get("reasons", [])
        selected["quality_retry"]["last_compile_json"] = current.get("compile_json", "")
    return selected


def _quality_gate_rank_tuple(gate: dict[str, Any]) -> tuple[int, int, int, int, int, int, int, int, int, float, float]:
    reasons = [str(item) for item in gate.get("reasons", []) if str(item).strip()]
    detail_count = sum(1 for reason in reasons if reason.startswith("detail_wrapper_drift:"))
    contract_count = sum(1 for reason in reasons if reason.startswith("compile_surface_contract:"))
    profile_count = sum(1 for reason in reasons if reason.startswith("profile_delivery:"))
    public_recall_count = sum(1 for reason in reasons if reason.startswith("public_recall_surface:"))
    table_count = sum(1 for reason in reasons if reason.startswith("table_list_surface:"))
    identity_count = sum(1 for reason in reasons if reason.startswith("identity_canonicality:"))
    surface_severity = sum(_quality_gate_reason_severity(reason) for reason in reasons)
    risk_count = _optional_int(gate.get("risk_count"))
    rough_score = _optional_float(gate.get("rough_score"))
    skipped_share = _optional_float(gate.get("compile_skipped_share")) or 0.0
    return (
        0 if bool(gate.get("passed")) else 1,
        surface_severity,
        len(reasons),
        detail_count,
        contract_count,
        profile_count,
        public_recall_count,
        table_count,
        identity_count,
        float(risk_count if risk_count is not None else 9999),
        -float(rough_score if rough_score is not None else -1.0) + skipped_share,
    )


def _quality_gate_reason_severity(reason: str) -> int:
    text = str(reason or "")
    if text.startswith("public_recall_surface:"):
        match = re.search(r":missing=([^:]+)", text)
        if match:
            return len([item for item in match.group(1).split(",") if item.strip()])
    if text.startswith("table_list_surface:"):
        match = re.search(r":missing=(\d+)", text)
        if match:
            return int(match.group(1))
    if text.startswith("identity_canonicality:"):
        match = re.search(r":groups=(\d+)", text)
        if match:
            return int(match.group(1))
    return 0


def _merge_quality_retry_context_lines(previous: list[str], current: list[str]) -> list[str]:
    lines: list[str] = []
    seen: set[str] = set()
    for line in [*previous, *current]:
        text = str(line).strip()
        if text and text not in seen:
            seen.add(text)
            lines.append(text)
    return lines


def _quality_retry_active_reasons(reasons: list[str]) -> list[str]:
    clean = [str(reason).strip() for reason in reasons if str(reason).strip()]
    table_reasons = [reason for reason in clean if reason.startswith("table_list_surface:")]
    if not table_reasons:
        return clean
    table_severity = sum(_quality_gate_reason_severity(reason) for reason in table_reasons)
    if table_severity <= 8:
        return clean
    state_table_reasons = [
        reason
        for reason in table_reasons
        if (
            "distribution_state_table_underpreserved:" in reason
            or "distribution_subject_granularity_split:" in reason
        )
    ]
    return state_table_reasons


def _quality_retry_metadata(
    *,
    attempts: list[dict[str, Any]],
    first_reasons: list[str],
    first_compile_json: str,
    final_gate: dict[str, Any],
    blocked_reason: str = "",
) -> dict[str, Any]:
    first_attempt = attempts[0] if attempts else {}
    metadata = {
        "attempted": bool(attempts),
        "attempt_count": len(attempts),
        "initial_reasons": first_reasons,
        "context_lines": first_attempt.get("context_lines", []) if isinstance(first_attempt, dict) else [],
        "initial_compile_json": first_compile_json,
        "attempts": attempts,
        "final_decision": final_gate.get("decision", ""),
        "final_reasons": final_gate.get("reasons", []),
    }
    if blocked_reason:
        metadata["reason"] = blocked_reason
    return metadata


def _quality_retry_context_lines(gate: dict[str, Any]) -> list[str]:
    reasons = [str(item).strip() for item in gate.get("reasons", []) if str(item).strip()]
    reasons = _quality_retry_active_reasons(reasons)
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
        if "scheduled_maintenance_due_date_preservation:" in reason:
            add(
                "QUALITY GATE RETRY: the prior compile saw source-record labels or text with scheduled calibration, "
                "maintenance, service, or inspection due dates but no direct scheduled-event surface. In this retry, "
                "emit compatible scheduled_event/4, scheduled_maintenance/2-4, calibration_due/2-4, or equivalent "
                "rows that keep subject/device, event type, due date, and source/basis joinable. A source_record row, "
                "sensor id, or ticket reference is additive only and must not be the only carrier for the due date."
            )
        if "source_authority_pair_preservation:" in reason:
            add(
                "QUALITY GATE RETRY: the prior compile saw source text where a rule, policy, order, authority, "
                "or authorized actor governs an action/status/scope, but no direct source-authority surface was "
                "delivered. In this retry, emit compatible direct source_authority/3 or equivalent rows that keep "
                "the governed subject or scope, authority/source, and authorized action/status joinable. Emit one "
                "direct authority row for every distinct stated authority coordinate, not only a representative "
                "example. A rule description, note, docket text, or source_record row is additive only and must not "
                "be the only carrier for an explicit authority constraint."
            )
        if "table_list_surface:distribution_state_table_underpreserved:" in reason:
            missing_states = _table_missing_states_from_reason(reason)
            missing_tail = (
                f" The prior compile specifically missed these source-stated states: {', '.join(missing_states[:8])}."
                if missing_states
                else ""
            )
            add(
                "QUALITY GATE RETRY: the prior compile saw a dense state/retailer distribution table in the "
                "source-record ledger, but fewer state surfaces were delivered as direct facts. In this retry, "
                "preserve each table row as joinable direct distribution facts: state or region, each retailer or "
                "location, the governed product/item/category, and any row-specific product restriction or carve-out. "
                "If the profile offers distributed_in_state/2, sold_at_retailer/3, product_restriction/3, "
                "recall_distribution/2, or equivalent carriers, populate those direct predicates from "
                "source_record_cell_item and source_record_cell_item_qualifier rows. "
                "Do not stop after a long or semicolon-heavy table cell; trailing short rows and single-retailer "
                "rows still require their own direct distribution carriers. "
                "Use stable product/item atoms that also appear in product_name/item_name, recall-item, count, and "
                "source-detail rows; if a row-level distribution id is necessary, link it to the governed product or "
                "category with an explicit alias, equivalence, or governed-category row. "
                "A source_record_cell/source_record_text_atom row is provenance only and must not be the only carrier "
                "for the table's state-by-retailer surface." + missing_tail
            )
        if "identity_canonicality:duplicate_named_subjects_without_alias:" in reason:
            add(
                "QUALITY GATE RETRY: the prior compile emitted the same product/item/object name for multiple "
                "subject atoms without an alias, same-as, or canonical-equivalence row. In this retry, reuse one "
                "stable subject atom for the same named item across product_name/item_name, recall-item, distribution, "
                "retailer, state, restriction, count, and source-detail facts. If the source truly needs separate "
                "atoms for category, UPC, package, or row-level entries, emit explicit alias/equivalence or "
                "governed-category rows so the facts can join. Identity repair must preserve existing repeated-table "
                "coverage: do not drop direct state/retailer/restriction rows while consolidating atoms. For dense "
                "distribution tables, continue promoting every source_record_cell_item and "
                "source_record_cell_item_qualifier row into compatible direct distribution carriers."
            )
        if "table_list_surface:distribution_subject_granularity_split:" in reason:
            add(
                "QUALITY GATE RETRY: the prior compile represented one dense distribution table through multiple "
                "granularity subjects, such as a broad category subject for early states and individual product "
                "subjects for later states. In this retry, keep one stable governed distribution subject for the "
                "whole table or emit explicit category-to-product/governed-product rows that let category questions "
                "join to product-specific retailer rows. Do not let bulk_retail_items, cucumber_whole, green_bell_pepper, "
                "and pickling_cucumber become disconnected answer surfaces for the same table."
            )
        if "table_list_surface:distribution_state_retailer_pair_underpreserved:" in reason:
            add(
                "QUALITY GATE RETRY: the prior compile saw state-by-retailer table rows in the source-record ledger, "
                "but direct facts did not preserve enough paired state plus retailer coordinates. In this retry, emit "
                "one compatible direct distribution carrier for each source row's state/retailer pair, including "
                "single-retailer rows and retailer-specific product restrictions. A state-only row and a retailer-only "
                "row are not equivalent to a paired state-retailer surface unless another direct fact joins them through "
                "the same governed item or table subject."
            )
        if "public_recall_surface:prior_recall_date_underpreserved:" in reason:
            add(
                "QUALITY GATE RETRY: the prior compile saw a public recall/notice source with an original, prior, "
                "previous, or earlier recall date but did not preserve that date as a direct temporal recall/event "
                "surface. In this retry, emit a distinct prior/original recall event-date row for the earlier date, "
                "using recall_date/2, event_date/2, notice_date/2, publication_date/2, or the closest allowed "
                "temporal carrier. Keep it separate from the current expansion, update, publication, or content-current "
                "date. A source_record_text_atom or source detail row is provenance only and must not be the only "
                "carrier for the prior recall date."
            )
        if "profile_delivery:source_authority_carrier_offered_but_undelivered:" in reason:
            add(
                "QUALITY GATE RETRY: the prior compile offered a direct source-authority carrier but emitted no "
                "matching rows. In this retry, populate source_authority/3 or an equivalent allowed carrier for "
                "source-stated authority/rule/order/policy constraints, keeping governed subject or scope, "
                "authority/source, and authorized action/status joinable. Emit one direct authority row for every "
                "distinct stated authority coordinate, not only a representative example."
            )
        if "profile_delivery:source_authority_carrier_partially_delivered:" in reason:
            add(
                "QUALITY GATE RETRY: the prior compile populated some source-authority carrier rows but fewer than "
                "the source-signal count. In this retry, emit one direct source-authority row for every distinct "
                "stated authority/rule/order/policy coordinate, not only a representative example."
            )
        if "profile_delivery:source_claim_carrier_offered_but_undelivered:" in reason:
            missing_claim_keys = _profile_delivery_missing_keys_from_reason(reason)
            add(
                "QUALITY GATE RETRY: the prior compile offered a direct source-attributed claim carrier but emitted "
                "no matching rows. In this retry, populate source_attributed_claim/4 or an equivalent allowed carrier "
                "for source-stated reports, notes, statements, findings, opinions, or unresolved claims, keeping "
                "source/speaker, content/status/finding, and source row or scope joinable. Quoted notes, letters, "
                "opinions, and statements that say a draft has no effect, is not binding, remains under review, "
                "or supports/objects to a position need their own source-attributed row; a description/source_detail "
                "row may be additive but does not replace the source-to-claim carrier."
            )
            add(
                "QUALITY GATE RETRY: source-attributed claim rows are additive evidence, not substitutes for core "
                "compile surfaces. Preserve ordinary backbone rows in the same retry: event/date/status rows, vote "
                "rows, survey or measurement rows, permit/application status rows, appeal/filing rows, board finding "
                "rows, participant/role rows, and repeated-record detail rows."
            )
            if missing_claim_keys:
                add(
                    "QUALITY GATE RETRY: missing source-attributed claim kinds from the prior compile were "
                    f"{', '.join(missing_claim_keys[:4])}. Emit one direct source-to-claim carrier for each kind, "
                    "using the allowed predicate palette; do not satisfy these with unrelated quoted notes."
                )
                if any(key.endswith(":objection") or ":objection" in key for key in missing_claim_keys):
                    add(
                        "QUALITY GATE RETRY: missing objection source-claim keys require a direct row for the "
                        "source-stated objection itself, including phrases such as 'note the objection', "
                        "'written objection', 'objects', or 'opposes'. A ruling that proceeds despite the objection "
                        "is a separate backbone/ruling fact and does not deliver the objection claim unless the "
                        "objection content remains joinable to the speaker/source."
                    )
                if any(key.endswith(":concern") or ":concern" in key for key in missing_claim_keys):
                    add(
                        "QUALITY GATE RETRY: missing concern source-claim keys require a direct row for the stated "
                        "concern itself, including 'concern', 'concerns', or 'concerned about' language. Keep the "
                        "speaker/source, concern content, and source row or event scope joinable."
                    )
                if any(
                    key.startswith(("statement:", "opinion:", "note:", "testimony:", "report:", "memo:", "comment:", "source:"))
                    for key in missing_claim_keys
                ):
                    add(
                        "QUALITY GATE RETRY: the missing source-attributed claim kinds include speaker/document-framed "
                        "statements. When source_attributed_claim/4 is in the allowed palette, use that 4-slot carrier "
                        "for these rows so the speaker or document, content/status/finding, and source row or scope stay "
                        "joinable. A shorter source_claim/3 row is additive but does not replace the source-attributed "
                        "row for statement:, opinion:, note:, testimony:, report:, memo:, or comment: keys."
                    )
        if "profile_delivery:source_claim_carrier_partially_delivered:" in reason:
            missing_claim_keys = _profile_delivery_missing_keys_from_reason(reason)
            add(
                "QUALITY GATE RETRY: the prior compile populated some source-attributed claim rows but fewer than "
                "the source-signal count. In this retry, preserve each distinct source-stated report, note, statement, "
                "finding, opinion, or unresolved claim as a direct source-attributed claim carrier row when allowed. "
                "Do not hide quoted no-effect, non-binding, under-review, support, objection, or recommendation "
                "language only inside broad description/detail text."
            )
            add(
                "QUALITY GATE RETRY: source-attributed claim rows are additive evidence, not substitutes for core "
                "compile surfaces. Preserve ordinary backbone rows in the same retry: event/date/status rows, vote "
                "rows, survey or measurement rows, permit/application status rows, appeal/filing rows, board finding "
                "rows, participant/role rows, and repeated-record detail rows."
            )
            if missing_claim_keys:
                add(
                    "QUALITY GATE RETRY: missing source-attributed claim kinds from the prior compile were "
                    f"{', '.join(missing_claim_keys[:4])}. Emit one direct source-to-claim carrier for each kind, "
                    "using the allowed predicate palette; do not satisfy these with unrelated quoted notes."
                )
                if any(key.endswith(":objection") or ":objection" in key for key in missing_claim_keys):
                    add(
                        "QUALITY GATE RETRY: missing objection source-claim keys require a direct row for the "
                        "source-stated objection itself, including phrases such as 'note the objection', "
                        "'written objection', 'objects', or 'opposes'. A ruling that proceeds despite the objection "
                        "is a separate backbone/ruling fact and does not deliver the objection claim unless the "
                        "objection content remains joinable to the speaker/source."
                    )
                if any(key.endswith(":concern") or ":concern" in key for key in missing_claim_keys):
                    add(
                        "QUALITY GATE RETRY: missing concern source-claim keys require a direct row for the stated "
                        "concern itself, including 'concern', 'concerns', or 'concerned about' language. Keep the "
                        "speaker/source, concern content, and source row or event scope joinable."
                    )
                if any(
                    key.startswith(("statement:", "opinion:", "note:", "testimony:", "report:", "memo:", "comment:", "source:"))
                    for key in missing_claim_keys
                ):
                    add(
                        "QUALITY GATE RETRY: the missing source-attributed claim kinds include speaker/document-framed "
                        "statements. When source_attributed_claim/4 is in the allowed palette, use that 4-slot carrier "
                        "for these rows so the speaker or document, content/status/finding, and source row or scope stay "
                        "joinable. A shorter source_claim/3 row is additive but does not replace the source-attributed "
                        "row for statement:, opinion:, note:, testimony:, report:, memo:, or comment: keys."
                    )
        if "profile_delivery:source_claim_backbone_coexistence_missing:" in reason:
            missing_backbone_groups = _profile_delivery_missing_keys_from_reason(reason)
            group_label = (
                f" The missing backbone groups were {', '.join(missing_backbone_groups[:6])}."
                if missing_backbone_groups
                else ""
            )
            add(
                "QUALITY GATE RETRY: the prior compile delivered source-attributed claim rows while losing "
                "independent source-stated backbone surfaces."
                f"{group_label} In this retry, keep source_attributed_claim/4 rows additive and also emit direct "
                "allowed backbone rows for any stated vote/tally, survey/measurement, permit/application status, "
                "appeal/filing, board finding, and quorum facts. Quoted statements, source_claim rows, and broad "
                "source_detail/note/context rows do not replace those ordinary queryable facts."
            )
        if "profile_delivery:status_state_carrier_offered_but_undelivered:" in reason:
            add(
                "QUALITY GATE RETRY: the prior compile offered a direct status/state carrier but emitted no matching "
                "rows. In this retry, populate status_state_at/4, *_status_at/3-4, *_state_at/3-4, or an equivalent "
                "allowed carrier for point-in-time status, current condition, availability, pending resolution, "
                "supersession, or scoped population state. Keep subject/subset, state value, and temporal/source scope "
                "together."
            )
        if "profile_delivery:status_state_carrier_partially_delivered:" in reason:
            add(
                "QUALITY GATE RETRY: the prior compile populated some status/state carrier rows but fewer than the "
                "source-signal count. In this retry, emit direct status/state rows for every distinct source-stated "
                "subject, state value, and temporal/source scope."
            )
        if "profile_delivery:vote_tally_carrier_offered_but_undelivered:" in reason:
            missing_vote_keys = _profile_delivery_missing_keys_from_reason(reason)
            add(
                "QUALITY GATE RETRY: the prior compile offered a direct vote-tally carrier but emitted no matching "
                "rows. In this retry, populate vote_tally/5 or an equivalent allowed carrier for source-stated "
                "votes, roll calls, final approvals/denials, and corrected minutes, keeping voting body, decision "
                "subject, result, tally, and member votes or source scope joinable. Individual member voting rows "
                "and hearing notes are additive but do not replace a stated final or corrected tally."
            )
            if missing_vote_keys:
                add(
                    "QUALITY GATE RETRY: missing vote-tally kinds from the prior compile were "
                    f"{', '.join(missing_vote_keys[:4])}. Emit one direct vote carrier for each missing tally."
                )
        if "profile_delivery:vote_tally_carrier_partially_delivered:" in reason:
            missing_vote_keys = _profile_delivery_missing_keys_from_reason(reason)
            add(
                "QUALITY GATE RETRY: the prior compile populated some vote rows but missed stated vote tallies. "
                "In this retry, preserve every explicit source-stated vote count, final approval/denial tally, "
                "and corrected minutes tally as a direct vote_tally/5 or equivalent row. Do not rely only on "
                "individual member vote rows when the source states an aggregate tally."
            )
            if missing_vote_keys:
                add(
                    "QUALITY GATE RETRY: missing vote-tally kinds from the prior compile were "
                    f"{', '.join(missing_vote_keys[:4])}. Emit one direct vote carrier for each missing tally."
                )
        if "profile_delivery:event_identifier_date_only:" in reason:
            add(
                "QUALITY GATE RETRY: the prior compile used event identifiers that embed dates or timestamps but did "
                "not emit explicit temporal rows for those same events. In this retry, keep the stable event id and "
                "emit direct event timestamp/date rows such as event_time/2, event_timestamp/2, event_corrected_time/2, "
                "event_wall_time/2, or the closest allowed temporal carrier. A source_detail row or an event id like "
                "ev_10_2026_04_22_15_14_08 is additive only; the date/time must also be a joinable argument in a "
                "direct temporal predicate for that event."
            )
        if "profile_delivery:quantity_carrier_offered_but_undelivered:" in reason:
            missing_quantity_keys = _profile_delivery_missing_keys_from_reason(reason)
            add(
                "QUALITY GATE RETRY: the prior compile offered a direct quantity/event carrier but emitted no matching "
                "rows. In this retry, populate event_measurement/4, event_quantity/4, reading_value/4, "
                "measurement_value/4, metric_observation/4, or an equivalent allowed carrier for source-stated "
                "numeric values, keeping event/record id, measure, value, and unit/basis together. Numeric event "
                "details include setpoint before/after values, feed rates, drift offsets, elapsed durations, totals, "
                "rates, ratios, thresholds, and percentages. Event descriptions, timestamps, and start/end intervals "
                "are additive only; they do not replace the direct numeric value row. For changed/reverted/increased/"
                "decreased values stated as X to Y, emit separate before and after carrier rows for each event."
            )
            if missing_quantity_keys:
                add(
                    "QUALITY GATE RETRY: missing quantity/event kinds from the prior compile were "
                    f"{', '.join(missing_quantity_keys[:4])}. Emit one direct numeric carrier for each missing "
                    "kind; for duration:line_stop, preserve the stated duration total as a direct duration or "
                    "event_measurement row."
                )
                duration_keys = [key for key in missing_quantity_keys if key.startswith("duration:")]
                if duration_keys:
                    add(
                        "QUALITY GATE RETRY: missing duration keys require a row whose arguments include both "
                        f"the interval subject ({', '.join(duration_keys[:4])}) and the exact stated elapsed total. "
                        "Start/end event links, timestamps, state-transition rows, or source_detail/source_record "
                        "text are useful anchors but do not deliver the duration unless the duration value itself is "
                        "a joinable argument in event_measurement/4, event_duration/3, line_stop_duration/2, "
                        "interval_duration/3, duration_between/3, or an equivalent allowed carrier."
                    )
        if "profile_delivery:quantity_carrier_partially_delivered:" in reason:
            missing_quantity_keys = _profile_delivery_missing_keys_from_reason(reason)
            add(
                "QUALITY GATE RETRY: the prior compile populated some quantity/event carrier rows but fewer than the "
                "source-signal count. In this retry, preserve every distinct source-stated measurement, quantity, "
                "rate, ratio, threshold, or duration as a direct carrier row when allowed. Numeric event details "
                "include setpoint before/after values, feed rates, drift offsets, elapsed durations, totals, rates, "
                "ratios, thresholds, and percentages. Event descriptions, timestamps, and start/end intervals are "
                "additive only; they do not replace the direct numeric value row. For changed/reverted/increased/"
                "decreased values stated as X to Y, emit separate before and after carrier rows for each event; for "
                "line-stop or response durations, emit the stated duration total as event_measurement/4, "
                "event_duration/3, or the allowed source-local duration carrier."
            )
            if missing_quantity_keys:
                add(
                    "QUALITY GATE RETRY: missing quantity/event kinds from the prior compile were "
                    f"{', '.join(missing_quantity_keys[:4])}. Emit one direct numeric carrier for each missing "
                    "kind; for duration:line_stop, preserve the stated duration total as a direct duration or "
                    "event_measurement row."
                )
                duration_keys = [key for key in missing_quantity_keys if key.startswith("duration:")]
                if duration_keys:
                    add(
                        "QUALITY GATE RETRY: missing duration keys require a row whose arguments include both "
                        f"the interval subject ({', '.join(duration_keys[:4])}) and the exact stated elapsed total. "
                        "Start/end event links, timestamps, state-transition rows, or source_detail/source_record "
                        "text are useful anchors but do not deliver the duration unless the duration value itself is "
                        "a joinable argument in event_measurement/4, event_duration/3, line_stop_duration/2, "
                        "interval_duration/3, duration_between/3, or an equivalent allowed carrier."
                    )
    return lines


def _profile_delivery_missing_keys_from_reason(reason: str) -> list[str]:
    text = str(reason or "")
    if ":missing=" not in text:
        return []
    tail = text.split(":missing=", 1)[1]
    return [item.strip() for item in tail.split(",") if item.strip()]


def _table_missing_states_from_reason(reason: str) -> list[str]:
    text = str(reason or "")
    if ":missing_states=" not in text:
        return []
    tail = text.split(":missing_states=", 1)[1]
    tail = tail.split(":", 1)[0]
    return [item.strip() for item in tail.split(",") if item.strip()]


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
        required_carrier_row_count = _optional_int(finding.get("required_carrier_row_count"))
        offered = [
            str(item).strip()
            for item in finding.get("offered_carriers", [])
            if str(item).strip()
        ] if isinstance(finding.get("offered_carriers"), list) else []
        offered_label = ",".join(offered[:6]) if offered else "none"
        required_label = (
            f":required={required_carrier_row_count}"
            if required_carrier_row_count and required_carrier_row_count != source_signal_count
            else ""
        )
        missing_keys = [
            str(item).strip()
            for item in finding.get("missing_signal_keys", [])
            if str(item).strip()
        ] if isinstance(finding.get("missing_signal_keys"), list) else []
        missing_label = f":missing={','.join(missing_keys[:4])}" if missing_keys else ""
        flags.append(f"{cls}:source={source_signal_count}{required_label}:offered={offered_label}{missing_label}")
    return flags


def _public_recall_surface_flags(payload: dict[str, Any]) -> list[str]:
    source_dates = _public_recall_prior_date_atoms(_source_text_from_payload(payload))
    if not source_dates:
        return []
    facts = [str(fact) for fact in _surface_facts_from_compile(payload)]
    source_facts = [fact for fact in facts if _predicate_name(fact).startswith("source_record")]
    direct_facts = [fact for fact in facts if not _predicate_name(fact).startswith("source_record")]
    direct_dates = _direct_public_recall_date_atoms(direct_facts)
    source_record_dates = _source_record_public_recall_date_atoms(source_facts)
    covered_dates = source_dates & (direct_dates | source_record_dates)
    missing_dates = sorted(source_dates - covered_dates)
    if not missing_dates:
        return []
    return [
        "prior_recall_date_underpreserved:"
        f"source_dates={len(source_dates)}:direct_dates={len(covered_dates)}:missing={','.join(missing_dates[:4])}"
    ]


def _source_text_from_payload(payload: dict[str, Any]) -> str:
    text_path = Path(str(payload.get("text_file") or ""))
    if text_path.is_file():
        try:
            return text_path.read_text(encoding="utf-8")
        except OSError:
            return ""
    raw_text = payload.get("source_text")
    return str(raw_text or "")


def _public_recall_prior_date_atoms(source_text: str) -> set[str]:
    atoms: set[str] = set()
    for match in PUBLIC_RECALL_PRIOR_DATE_TEXT_RE.finditer(str(source_text or "")):
        raw = str(match.group("date1") or match.group("date2") or "").strip()
        atom = _date_atom_from_text(raw)
        if atom:
            atoms.add(atom)
    return atoms


def _direct_public_recall_date_atoms(direct_facts: list[str]) -> set[str]:
    atoms: set[str] = set()
    for fact in direct_facts:
        predicate = _predicate_name(fact)
        args = _fact_args(fact)
        if not predicate or not args:
            continue
        if not _fact_carries_public_recall_temporal_surface(predicate, args):
            continue
        for arg in args:
            atom = _date_atom_from_text(arg)
            if atom and _fact_preserves_prior_public_recall_date(predicate, args, date_atom=atom):
                atoms.add(atom)
    return atoms


def _source_record_public_recall_date_atoms(source_facts: list[str]) -> set[str]:
    atoms: set[str] = set()
    for fact in source_facts:
        predicate = _predicate_name(fact)
        if predicate not in {"source_record_text_atom", "source_record_row_context"}:
            continue
        args = _fact_args(fact)
        if len(args) < 2:
            continue
        text = " ".join(args[1:])
        tokens = _tokens(text)
        if not tokens & {"recall", "notice", "announcement", "advisory"}:
            continue
        if not tokens & {"original", "prior", "previous", "earlier", "expanding", "expanded", "expansion"}:
            continue
        atoms.update(_date_atoms_from_text(text))
    return atoms


def _fact_carries_public_recall_temporal_surface(predicate: str, args: list[str]) -> bool:
    predicate_tokens = _tokens(predicate)
    arg_tokens = _tokens(" ".join(args))
    all_tokens = predicate_tokens | arg_tokens
    temporal = {"date", "dated", "time", "timestamp", "publication", "published", "posted"}
    recallish = {"recall", "notice", "announcement", "advisory", "event", "publication", "published"}
    priorish = {"original", "prior", "previous", "earlier", "initial", "expansion", "expanded", "update", "updated"}
    if not (predicate_tokens & temporal):
        return False
    if predicate_tokens & recallish:
        return True
    if arg_tokens & recallish:
        return True
    return bool(arg_tokens & priorish)


def _fact_preserves_prior_public_recall_date(predicate: str, args: list[str], *, date_atom: str) -> bool:
    non_date_args = [arg for arg in args if _date_atom_from_text(arg) != date_atom]
    predicate_tokens = _tokens(predicate)
    non_date_tokens = _tokens(" ".join(non_date_args))
    priorish = {"original", "prior", "previous", "earlier", "initial"}
    currentish = {
        "announcement",
        "current",
        "expanded",
        "expanding",
        "expansion",
        "publish",
        "published",
        "update",
        "updated",
    }
    if non_date_tokens & priorish:
        return True
    if non_date_tokens & currentish:
        return False
    return bool(predicate_tokens & {"recall", "event", "notice", "advisory"})


def _date_atom_from_text(value: str) -> str:
    atoms = _date_atoms_from_text(value)
    return sorted(atoms)[0] if atoms else ""


def _date_atoms_from_text(value: str) -> set[str]:
    text = str(value or "").strip().casefold()
    if not text:
        return set()
    atoms: set[str] = set()
    for iso in ISO_DATE_ATOM_RE.finditer(text):
        atom = _date_atom_from_parts(iso.group("year"), iso.group("month"), iso.group("day"))
        if atom:
            atoms.add(atom)
    for month_date in MONTH_DATE_RE.finditer(text.replace("_", " ")):
        month = MONTH_ALIASES.get(month_date.group("month").casefold(), 0)
        atom = _date_atom_from_parts(month_date.group("year"), str(month), month_date.group("day"))
        if atom:
            atoms.add(atom)
    return atoms


def _date_atom_from_parts(year: str, month: str, day: str) -> str:
    try:
        year_i = int(year)
        month_i = int(month)
        day_i = int(day)
    except ValueError:
        return ""
    if not (1900 <= year_i <= 2099 and 1 <= month_i <= 12 and 1 <= day_i <= 31):
        return ""
    return f"{year_i:04d}_{month_i:02d}_{day_i:02d}"


def _table_list_surface_flags(payload: dict[str, Any]) -> list[str]:
    facts = _surface_facts_from_compile(payload)
    source_facts = [str(fact) for fact in facts if _predicate_name(str(fact)).startswith("source_record")]
    direct_facts = [str(fact) for fact in facts if not _predicate_name(str(fact)).startswith("source_record")]
    if not source_facts or not direct_facts:
        return []

    candidate_predicates = _candidate_predicate_names(payload)
    if candidate_predicates and not any(
        any(marker in name for marker in DISTRIBUTION_DIRECT_PREDICATE_MARKERS)
        for name in candidate_predicates
    ):
        return []

    source_rows = _source_record_rows_by_ref(source_facts)
    source_states: set[str] = set()
    for row in source_rows.values():
        atoms = {str(atom) for atom in row.get("atoms", set())}
        row_text = " ".join(sorted(atoms))
        row_tokens = _tokens(row_text)
        if not row_tokens.intersection(DISTRIBUTION_TABLE_MARKERS):
            continue
        source_states.update(_state_atoms_from_text(row_text, include_abbreviations=False))

    if len(source_states) < 8:
        return []

    direct_states: set[str] = set()
    subject_states: dict[str, set[str]] = {}
    for fact in direct_facts:
        predicate = _predicate_name(fact)
        if not any(marker in predicate for marker in DISTRIBUTION_DIRECT_PREDICATE_MARKERS):
            continue
        args = _fact_args(fact)
        fact_states = _state_atoms_from_text(" ".join(args), include_abbreviations=True)
        direct_states.update(fact_states)
        if fact_states and args:
            subject = _normalized_slot_atom(args[0])
            if subject:
                subject_states.setdefault(subject, set()).update(fact_states)

    flags: list[str] = []
    pair_flags = _distribution_state_retailer_pair_flags(
        source_facts=source_facts,
        direct_facts=direct_facts,
    )
    scaffold_states = {state for state, _retailer in _distribution_scaffold_state_retailer_pairs(source_facts)}
    covered_states = direct_states | scaffold_states
    if len(direct_states) >= len(source_states):
        flags.extend(_distribution_subject_granularity_flags(source_states=source_states, subject_states=subject_states))
        flags.extend(pair_flags)
        return flags
    missing_states = sorted(source_states - covered_states)
    if not missing_states:
        flags.extend(_distribution_subject_granularity_flags(source_states=source_states, subject_states=subject_states))
        flags.extend(pair_flags)
        return flags
    flags.append(
        "distribution_state_table_underpreserved:"
        f"source_states={len(source_states)}:direct_states={len(covered_states)}:missing={len(missing_states)}"
        f":missing_states={','.join(missing_states[:8])}"
    )
    flags.extend(_distribution_subject_granularity_flags(source_states=source_states, subject_states=subject_states))
    flags.extend(pair_flags)
    return flags


def _table_list_surface_coverage_flags(payload: dict[str, Any]) -> list[str]:
    facts = _surface_facts_from_compile(payload)
    source_facts = [str(fact) for fact in facts if _predicate_name(str(fact)).startswith("source_record")]
    direct_facts = [str(fact) for fact in facts if not _predicate_name(str(fact)).startswith("source_record")]
    if not source_facts or not direct_facts:
        return []
    source_pairs = _distribution_source_state_retailer_pairs(source_facts)
    if len(source_pairs) < 8:
        return []
    direct_pairs = _distribution_direct_state_retailer_pairs(direct_facts)
    missing_pairs = source_pairs - direct_pairs
    if not missing_pairs:
        return []
    scaffold_pairs = _distribution_scaffold_state_retailer_pairs(source_facts)
    covered_pairs = missing_pairs & scaffold_pairs
    if missing_pairs - scaffold_pairs:
        return []
    sample = ",".join(f"{state}:{retailer}" for state, retailer in sorted(covered_pairs)[:8])
    return [
        "distribution_state_retailer_pair_scaffold_covered:"
        f"source_pairs={len(source_pairs)}:direct_pairs={len(direct_pairs)}:"
        f"covered_pairs={len(covered_pairs)}:missing_direct={len(missing_pairs)}"
        f":sample={sample}"
    ]


def _distribution_state_retailer_pair_flags(
    *,
    source_facts: list[str],
    direct_facts: list[str],
) -> list[str]:
    source_pairs = _distribution_source_state_retailer_pairs(source_facts)
    if len(source_pairs) < 8:
        return []
    direct_pairs = _distribution_direct_state_retailer_pairs(direct_facts)
    missing_pairs = sorted(source_pairs - direct_pairs)
    if not missing_pairs:
        return []
    scaffold_pairs = _distribution_scaffold_state_retailer_pairs(source_facts)
    if set(missing_pairs).issubset(scaffold_pairs):
        return []
    missing_share = len(missing_pairs) / max(1, len(source_pairs))
    if missing_share < 0.15 and len(missing_pairs) < 4:
        return []
    sample = ",".join(f"{state}:{retailer}" for state, retailer in missing_pairs[:8])
    return [
        "distribution_state_retailer_pair_underpreserved:"
        f"source_pairs={len(source_pairs)}:direct_pairs={len(direct_pairs)}:missing={len(missing_pairs)}"
        f":missing_pairs={sample}"
    ]


def _distribution_source_state_retailer_pairs(source_facts: list[str]) -> set[tuple[str, str]]:
    row_atoms = _source_record_rows_by_ref(source_facts)
    row_cells: dict[str, dict[int, set[str]]] = {}
    for fact in source_facts:
        predicate = _predicate_name(fact)
        if predicate != "source_record_cell_item":
            continue
        args = _fact_args(fact)
        if len(args) < 3:
            continue
        ref = _normalized_slot_atom(args[0])
        try:
            column = int(str(args[1]).strip())
        except ValueError:
            continue
        item = _normalized_slot_atom(args[2])
        if not ref or not item:
            continue
        row_cells.setdefault(ref, {}).setdefault(column, set()).add(item)

    pairs: set[tuple[str, str]] = set()
    for ref, cells in row_cells.items():
        row = row_atoms.get(ref, {"atoms": set()})
        row_text = " ".join(sorted(str(atom) for atom in row.get("atoms", set())))
        if not _tokens(row_text).intersection(DISTRIBUTION_TABLE_MARKERS):
            continue
        states: set[str] = set()
        retailers: set[str] = set()
        for column, items in cells.items():
            for item in items:
                item_states = _state_atoms_from_text(item, include_abbreviations=False)
                if item_states:
                    states.update(item_states)
                    continue
                if column > 1:
                    retailer = _retailer_key(item)
                    if retailer:
                        retailers.add(retailer)
        for state in states:
            for retailer in retailers:
                pairs.add((state, retailer))
    return pairs


def _distribution_scaffold_state_retailer_pairs(source_facts: list[str]) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    for fact in source_facts:
        predicate = _predicate_name(fact)
        if predicate not in {"source_record_cell_item_pair", "source_record_field_item_pair"}:
            continue
        args = _fact_args(fact)
        if len(args) < 5:
            continue
        left = _normalized_slot_atom(args[2])
        right = _normalized_slot_atom(args[4])
        pairs.update(_state_retailer_pairs_from_items(left, right))
    return pairs


def _state_retailer_pairs_from_items(left: str, right: str) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    left_states = _state_atoms_from_text(left, include_abbreviations=False)
    right_states = _state_atoms_from_text(right, include_abbreviations=False)
    left_retailer = _retailer_key(left)
    right_retailer = _retailer_key(right)
    for state in left_states:
        if right_retailer:
            pairs.add((state, right_retailer))
    for state in right_states:
        if left_retailer:
            pairs.add((state, left_retailer))
    return pairs


def _distribution_direct_state_retailer_pairs(direct_facts: list[str]) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    for fact in direct_facts:
        predicate = _predicate_name(fact)
        if not any(marker in predicate for marker in DISTRIBUTION_DIRECT_PREDICATE_MARKERS):
            continue
        args = _fact_args(fact)
        states = _state_atoms_from_text(" ".join(args), include_abbreviations=True)
        if not states:
            continue
        retailers = {_retailer_key(arg) for arg in args}
        retailers.discard("")
        for state in states:
            for retailer in retailers:
                pairs.add((state, retailer))
    return pairs


def _retailer_key(value: str) -> str:
    text = _normalized_slot_atom(value)
    if text.startswith("retailer_"):
        text = text.removeprefix("retailer_")
    compact = re.sub(r"[^a-z0-9]+", "", text)
    if not compact:
        return ""
    if compact in {"state", "states"} or compact in US_STATE_ALIASES:
        return ""
    if "walmart" in compact:
        return "walmart"
    if compact in {"savealot", "savelot"}:
        return "save_a_lot"
    if "shop" in compact and "save" in compact:
        return "shop_n_save"
    if "kroger" in compact:
        return "kroger"
    if "aldi" in compact:
        return "aldi"
    if "foodland" in compact:
        return "foodland"
    if "faschek" in compact:
        return "fas_chek"
    if "shoppersvalue" in compact:
        return "shoppers_value"
    if "franklinfoods" in compact:
        return "franklin_foods"
    if "pechin" in compact:
        return "pechin"
    if "marketbasket" in compact:
        return "market_basket"
    if "foodbank" in compact:
        return "foodbank"
    if "retail" in compact or "store" in compact:
        return compact
    return ""


def _distribution_subject_granularity_flags(
    *,
    source_states: set[str],
    subject_states: dict[str, set[str]],
) -> list[str]:
    if len(source_states) < 8 or len(subject_states) < 2:
        return []
    category_subjects = [
        subject
        for subject in subject_states
        if _tokens(subject).intersection({"bulk", "category", "distribution", "items", "retail"})
    ]
    if not category_subjects:
        return []
    max_state_count = max(len(states) for states in subject_states.values())
    if max_state_count < max(8, len(source_states) - 1):
        return []
    weakest_category = min(category_subjects, key=lambda subject: len(subject_states.get(subject, set())))
    weakest_count = len(subject_states.get(weakest_category, set()))
    if weakest_count >= max_state_count:
        return []
    return [
        "distribution_subject_granularity_split:"
        f"subjects={len(subject_states)}:category={weakest_category}:category_states={weakest_count}:"
        f"max_subject_states={max_state_count}:source_states={len(source_states)}"
    ]


def _identity_canonicality_flags(payload: dict[str, Any]) -> list[str]:
    facts = _surface_facts_from_compile(payload)
    direct_facts = [str(fact) for fact in facts if not _predicate_name(str(fact)).startswith("source_record")]
    if not direct_facts:
        return []

    subjects_by_label: dict[tuple[str, str], set[str]] = {}
    for fact in direct_facts:
        predicate = _predicate_name(fact)
        if predicate not in IDENTITY_NAME_PREDICATES:
            continue
        args = _fact_args(fact)
        if len(args) < 2:
            continue
        subject = _normalized_slot_atom(args[0])
        label = _normalized_slot_atom(args[1])
        if not subject or not label:
            continue
        subjects_by_label.setdefault((predicate, label), set()).add(subject)

    duplicate_groups = {
        key: subjects
        for key, subjects in subjects_by_label.items()
        if len(subjects) > 1
        and not _identity_subjects_have_equivalence_row(direct_facts, subjects)
        and _identity_subjects_split_join_risk(direct_facts, subjects)
    }
    if not duplicate_groups:
        return []

    predicate_counts: dict[str, int] = {}
    sample_predicate = ""
    sample_label = ""
    sample_count = 0
    for (predicate, label), subjects in sorted(duplicate_groups.items()):
        predicate_counts[predicate] = predicate_counts.get(predicate, 0) + 1
        if not sample_label:
            sample_predicate = predicate
            sample_label = label
            sample_count = len(subjects)
    predicate_label = ",".join(f"{predicate}={count}" for predicate, count in sorted(predicate_counts.items())[:4])
    return [
        "duplicate_named_subjects_without_alias:"
        f"groups={len(duplicate_groups)}:predicates={predicate_label}:sample={sample_predicate}:{sample_label}:{sample_count}"
    ]


def _detail_wrapper_drift_flags(payload: dict[str, Any]) -> list[str]:
    source_compile = payload.get("source_compile", {}) if isinstance(payload.get("source_compile"), dict) else {}
    facts = source_compile.get("facts", []) if isinstance(source_compile.get("facts"), list) else []
    source_facts = [str(fact) for fact in facts if _predicate_name(str(fact)).startswith("source_record")]
    direct_facts = [str(fact) for fact in facts if not _predicate_name(str(fact)).startswith("source_record")]
    direct_predicates = {_predicate_name(fact) for fact in direct_facts if _predicate_name(fact)}
    backbone_facts = [fact for fact in direct_facts if _predicate_name(fact) not in VAGUE_DETAIL_WRAPPER_PREDICATES]
    wrapper_hits = sorted(direct_predicates & VAGUE_DETAIL_WRAPPER_PREDICATES)
    if not wrapper_hits:
        return []
    direct_groups = _fact_slot_groups(backbone_facts)
    source_groups = _source_record_slot_groups_linked_to_wrappers(source_facts, direct_facts)
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


def _state_atoms_from_text(text: str, *, include_abbreviations: bool) -> set[str]:
    normalized = re.sub(r"[^a-z0-9]+", " ", str(text or "").casefold().replace("_", " "))
    padded = f" {normalized} "
    tokens = set(TOKEN_RE.findall(normalized))
    states: set[str] = set()
    for state, aliases in US_STATE_ALIASES.items():
        full_name = aliases[0]
        if f" {full_name} " in padded:
            states.add(state)
            continue
        if include_abbreviations and any(alias in tokens for alias in aliases[1:]):
            states.add(state)
    return states


def _identity_subjects_have_equivalence_row(facts: list[str], subjects: set[str]) -> bool:
    if len(subjects) < 2:
        return True
    for fact in facts:
        predicate = _predicate_name(fact)
        if not any(marker in predicate for marker in IDENTITY_EQUIVALENCE_PREDICATE_MARKERS):
            continue
        row_subjects = {_normalized_slot_atom(arg) for arg in _fact_args(fact)}
        if len(subjects.intersection(row_subjects)) >= 2:
            return True
    return False


def _identity_subjects_split_join_risk(facts: list[str], subjects: set[str]) -> bool:
    predicate_sets: dict[str, set[str]] = {subject: set() for subject in subjects}
    for fact in facts:
        predicate = _predicate_name(fact)
        args = {_normalized_slot_atom(arg) for arg in _fact_args(fact)}
        for subject in subjects:
            if subject in args:
                predicate_sets.setdefault(subject, set()).add(predicate)
    distinct_shapes = {tuple(sorted(predicates)) for predicates in predicate_sets.values() if predicates}
    if len(distinct_shapes) <= 1:
        return False
    return any(
        any(marker in predicate for marker in IDENTITY_JOIN_RISK_PREDICATE_MARKERS)
        for predicates in predicate_sets.values()
        for predicate in predicates
    )


def _slot_groups_for_text(text: str) -> set[str]:
    tokens = _tokens(text)
    groups: set[str] = set()
    for group, markers in BACKBONE_SURFACE_SLOT_GROUPS.items():
        if tokens.intersection(markers):
            groups.add(group)
    return groups


def _source_record_slot_groups_linked_to_wrappers(source_facts: list[str], direct_facts: list[str]) -> set[str]:
    source_rows = _source_record_rows_by_ref(source_facts)
    if not source_rows:
        return set()
    wrapper_atoms = _emitted_wrapper_atoms(direct_facts)
    groups: set[str] = set()
    for row in source_rows.values():
        if row["groups"] and row["atoms"] & wrapper_atoms:
            groups.update(row["groups"])
    return groups


def _source_record_rows_by_ref(source_facts: list[str]) -> dict[str, dict[str, set[str]]]:
    rows: dict[str, dict[str, set[str]]] = {}
    for fact in source_facts:
        predicate = _predicate_name(fact)
        args = _fact_args(fact)
        if not args:
            continue
        ref = _normalized_slot_atom(args[0])
        if not ref:
            continue
        row = rows.setdefault(ref, {"groups": set(), "atoms": set()})
        row["atoms"].add(ref)
        row["atoms"].update(_source_record_link_atoms(predicate, args))
        if predicate == "source_record_field" and len(args) >= 2:
            row["groups"].update(_slot_groups_for_text(args[1]))
        elif predicate == "source_record_cell" and len(args) >= 3:
            row["groups"].update(_slot_groups_for_text(args[2]))
        elif predicate == "source_record_label" and len(args) >= 2:
            row["groups"].update(_slot_groups_for_text(args[1]))
    return rows


def _source_record_link_atoms(predicate: str, args: list[str]) -> set[str]:
    value_args: list[str]
    if predicate == "source_record_field" and len(args) >= 3:
        value_args = args[2:]
    elif predicate in {"source_record_cell", "source_record_label", "source_record_text_atom"} and len(args) >= 2:
        value_args = args[1:]
    elif predicate == "source_record_row" and len(args) >= 4:
        value_args = args[3:]
    else:
        value_args = args[1:]
    return {_normalized_slot_atom(arg) for arg in value_args if _normalized_slot_atom(arg)}


def _emitted_wrapper_atoms(direct_facts: list[str]) -> set[str]:
    atoms: set[str] = set()
    for fact in direct_facts:
        if _predicate_name(fact) not in VAGUE_DETAIL_WRAPPER_PREDICATES:
            continue
        atoms.update(_normalized_slot_atom(arg) for arg in _fact_args(fact))
    return {atom for atom in atoms if atom}


def _normalized_slot_atom(value: str) -> str:
    return str(value or "").strip().strip("'\"").casefold()


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
    public_recall_flags = [
        str(flag)
        for flag in item.get("public_recall_surface_flags", [])
        if str(flag).strip()
    ] if isinstance(item.get("public_recall_surface_flags"), list) else []
    if public_recall_flags:
        reasons.extend(f"public_recall_surface:{flag}" for flag in public_recall_flags)
    table_list_flags = [
        str(flag)
        for flag in item.get("table_list_surface_flags", [])
        if str(flag).strip()
    ] if isinstance(item.get("table_list_surface_flags"), list) else []
    table_list_coverage_flags = [
        str(flag)
        for flag in item.get("table_list_surface_coverage_flags", [])
        if str(flag).strip()
    ] if isinstance(item.get("table_list_surface_coverage_flags"), list) else []
    if table_list_flags:
        reasons.extend(f"table_list_surface:{flag}" for flag in table_list_flags)
    identity_flags = [
        str(flag)
        for flag in item.get("identity_canonicality_flags", [])
        if str(flag).strip()
    ] if isinstance(item.get("identity_canonicality_flags"), list) else []
    if identity_flags:
        reasons.extend(f"identity_canonicality:{flag}" for flag in identity_flags)
    admitted = _optional_int(item.get("compile_admitted")) or 0
    skipped = _optional_int(item.get("compile_skipped")) or 0
    effective_admitted = _optional_int(item.get("compile_effective_admitted"))
    if effective_admitted is None:
        effective_admitted = admitted
    effective_skipped = _optional_int(item.get("compile_effective_skipped"))
    if effective_skipped is None:
        effective_skipped = skipped
    diagnostic_rejected_skipped = _optional_int(item.get("compile_diagnostic_rejected_skipped")) or 0
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
        "compile_effective_admitted": effective_admitted,
        "compile_effective_skipped": effective_skipped,
        "compile_diagnostic_rejected_skipped": diagnostic_rejected_skipped,
        "compile_raw_skipped_share": round(skipped / max(1, admitted + skipped), 4),
        "compile_skipped_share": round(effective_skipped / max(1, effective_admitted + effective_skipped), 4),
        "candidate_predicates": _optional_int(item.get("candidate_predicates")) or 0,
        "compile_json": str(result.get("compile_json", "")),
        "detail_wrapper_drift_flags": detail_wrapper_flags,
        "compile_surface_contract_flags": contract_flags,
        "profile_delivery_flags": profile_delivery_flags,
        "public_recall_surface_flags": public_recall_flags,
        "table_list_surface_coverage_flags": table_list_coverage_flags,
        "table_list_surface_flags": table_list_flags,
        "identity_canonicality_flags": identity_flags,
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
        "compile_effective_admitted": 0,
        "compile_effective_skipped": 0,
        "compile_diagnostic_rejected_skipped": 0,
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
        f"- Effective admitted / skipped: `{totals.get('compile_effective_admitted', 0)} / {totals.get('compile_effective_skipped', 0)}`",
        f"- Diagnostic rejected flat-pass skips: `{totals.get('compile_diagnostic_rejected_skipped', 0)}`",
        "",
        "| Fixture | Return | Predicates | Admitted | Skipped | Effective Skipped | Diagnostic Skips | Rough | Compile JSON |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for result in summary.get("results", []):
        item = result.get("summary", {}) if isinstance(result, dict) else {}
        lines.append(
            "| `{fixture}` | `{returncode}` | {predicates} | {admitted} | {skipped} | {effective_skipped} | {diagnostic_skipped} | {rough} | `{compile_json}` |".format(
                fixture=result.get("fixture", ""),
                returncode=result.get("returncode", ""),
                predicates=item.get("candidate_predicates", 0),
                admitted=item.get("compile_admitted", 0),
                skipped=item.get("compile_skipped", 0),
                effective_skipped=item.get("compile_effective_skipped", item.get("compile_skipped", 0)),
                diagnostic_skipped=item.get("compile_diagnostic_rejected_skipped", 0),
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
                "| Fixture | Decision | Reasons | Rough | Risk | Admitted | Skipped | Effective Skipped | Diagnostic Skips | Effective Skipped Share |",
                "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in quality_gate.get("rows", []):
            if not isinstance(row, dict):
                continue
            reasons = ", ".join(str(item) for item in row.get("reasons", [])) or "n/a"
            lines.append(
                "| `{fixture}` | `{decision}` | {reasons} | {rough} | {risk} | {admitted} | {skipped} | {effective_skipped} | {diagnostic_skipped} | {share} |".format(
                    fixture=row.get("fixture", ""),
                    decision=row.get("decision", ""),
                    reasons=reasons,
                    rough=row.get("rough_score", ""),
                    risk=row.get("risk_count", ""),
                    admitted=row.get("compile_admitted", 0),
                    skipped=row.get("compile_skipped", 0),
                    effective_skipped=row.get("compile_effective_skipped", row.get("compile_skipped", 0)),
                    diagnostic_skipped=row.get("compile_diagnostic_rejected_skipped", 0),
                    share=row.get("compile_skipped_share", 0),
                )
            )
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
