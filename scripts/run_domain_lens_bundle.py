#!/usr/bin/env python3
"""Run a closed domain registry as a lens-scoped compile bundle.

This harness is an orchestrator, not a compiler. It does not read source prose,
derive predicates, inspect answers, or create facts. For each repeat cycle it:

1. runs one source compile per selected registry lens;
2. deterministically unions mapper-admitted lens outputs from the same cycle;
3. scores the union against the typed micro-fixture oracle when requested;
4. runs atom-shape/signature and carrier value-domain governance audits over
   lens and union artifacts.
5. optionally reconciles typed union facts across repeats as a source-only
   stability diagnostic.

The point is to make a lens-bundle result reproducible instead of assembled by
hand from a worksheet.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_ROOT = REPO_ROOT / "tmp" / "domain_lens_bundle"


@dataclass(frozen=True)
class LensSpec:
    lens_id: str
    purpose: str
    allowed_signatures: tuple[str, ...] = ()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", required=True, help="Typed micro-fixture id.")
    parser.add_argument(
        "--text-file",
        type=Path,
        default=None,
        help="Source file. Defaults to datasets/compile_micro_fixtures/<fixture>/source.md.",
    )
    parser.add_argument("--profile-registry", type=Path, required=True)
    parser.add_argument(
        "--lens",
        action="append",
        default=[],
        help="Lens id to run. Repeat or comma-separate. Defaults to every registry lens.",
    )
    parser.add_argument(
        "--lens-domain-hint",
        action="append",
        default=[],
        help="Per-lens hint in lens_id=hint form. Repeat for multiple lenses.",
    )
    parser.add_argument(
        "--domain-hint",
        default="",
        help="Base domain hint included in every lens compile.",
    )
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT)
    parser.add_argument("--label", default="")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--backend", choices=["lmstudio"], default="lmstudio")
    parser.add_argument("--model", default="qwen/qwen3.6-35b-a3b")
    parser.add_argument("--base-url", default="http://127.0.0.1:1234")
    parser.add_argument("--timeout", type=int, default=420)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument("--num-ctx", type=int, default=65536)
    parser.add_argument("--max-tokens", type=int, default=12000)
    parser.add_argument(
        "--support-threshold",
        type=int,
        default=2,
        help="Support threshold for summarize_typed_micro_series.py.",
    )
    parser.add_argument(
        "--matcher",
        choices=("unification", "constant_slot"),
        default="constant_slot",
        help="Matcher for summarize_typed_micro_series.py.",
    )
    parser.add_argument(
        "--skip-score",
        action="store_true",
        help="Do not run summarize_typed_micro_series.py.",
    )
    parser.add_argument(
        "--skip-audit",
        action="store_true",
        help="Do not run audit_kb_atom_inventory.py.",
    )
    parser.add_argument(
        "--reconcile-unions",
        action="store_true",
        help=(
            "Run reconcile_typed_micro_compiles.py over union artifacts as a "
            "source-only typed stability diagnostic. This does not score an oracle."
        ),
    )
    parser.add_argument(
        "--no-apply-domain-reducers",
        action="store_true",
        help="Do not apply deterministic typed-domain reducers during union/scoring.",
    )
    parser.add_argument(
        "--focused-pass-ops-schema",
        action="store_true",
        help=(
            "Pass --focused-pass-ops-schema through to each lens compile so source compiles use "
            "source_pass_ops_v1 candidate operations instead of the legacy draft-profile path."
        ),
    )
    parser.add_argument(
        "--compile-plan-passes",
        action="store_true",
        help=(
            "Pass --compile-plan-passes through to each lens compile. Use with "
            "--focused-pass-ops-schema when testing plan-pass source_ops delivery."
        ),
    )
    parser.add_argument(
        "--profile-registry-lens-plan",
        action="store_true",
        help=(
            "Pass --profile-registry-lens-plan through to each lens compile so plan passes use "
            "the active registry lens instead of the source-wide intake plan."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    fixture = str(args.fixture).strip()
    if not fixture:
        raise SystemExit("--fixture must be non-empty")
    repeat = max(1, int(args.repeat))
    profile_registry = _resolve_path(args.profile_registry)
    text_file = _resolve_path(
        args.text_file
        if args.text_file is not None
        else REPO_ROOT / "datasets" / "compile_micro_fixtures" / fixture / "source.md"
    )
    registry_lenses = _load_registry_lenses(profile_registry)
    selected_lenses = _selected_lenses(registry_lenses, _split_csv_values(args.lens))
    lens_hints = _parse_lens_domain_hints(args.lens_domain_hint)
    label = _slug(args.label or f"{fixture}_lens_bundle")
    out_root = _resolve_out_root(args.out_root) / label
    if out_root.exists():
        if not args.overwrite:
            raise SystemExit(f"output already exists: {out_root}; pass --overwrite to replace it")
        shutil.rmtree(out_root)
    lens_root = out_root / "lens_compiles"
    union_root = out_root / "unions"
    report_root = out_root / "reports"
    report_root.mkdir(parents=True, exist_ok=True)

    run_reports: list[dict[str, Any]] = []
    for cycle in range(1, repeat + 1):
        print(f"cycle {cycle}/{repeat}: lens compiles", flush=True)
        cycle_lens_paths: list[Path] = []
        cycle_report: dict[str, Any] = {"cycle": cycle, "lenses": [], "union_json": ""}
        for lens in selected_lenses:
            lens_out = lens_root / f"run{cycle}" / lens.lens_id
            lens_out.mkdir(parents=True, exist_ok=True)
            command = _build_lens_compile_command(
                text_file=text_file,
                profile_registry=profile_registry,
                lens=lens,
                lens_hint=lens_hints.get(lens.lens_id, ""),
                args=args,
            ) + ["--out-dir", str(lens_out)]
            started = datetime.now(timezone.utc)
            _run(command)
            compile_json = _latest_compile_json(lens_out)
            cycle_lens_paths.append(compile_json)
            cycle_report["lenses"].append(
                {
                    "lens_id": lens.lens_id,
                    "compile_json": str(compile_json),
                    "started_at": started.isoformat(timespec="seconds"),
                    "finished_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                }
            )
        print(f"cycle {cycle}/{repeat}: deterministic union", flush=True)
        union_out = union_root / f"run{cycle}"
        union_out.mkdir(parents=True, exist_ok=True)
        union_command = _build_union_command(
            run_jsons=cycle_lens_paths,
            out_dir=union_out,
            label=f"{label}_run{cycle}",
            apply_domain_reducers=not bool(args.no_apply_domain_reducers),
        )
        _run(union_command)
        union_json = _latest_compile_json(union_out)
        cycle_report["union_json"] = str(union_json)
        run_reports.append(cycle_report)

    union_jsons = [Path(item["union_json"]) for item in run_reports]
    lens_audit_path = None
    union_audit_path = None
    lens_value_audit_path = None
    union_value_audit_path = None
    reconcile_path = None
    score_path = None
    score_exit_code = None
    if not bool(args.skip_score):
        print("scoring lens bundle union", flush=True)
        score_path = report_root / "typed_micro_series_summary.json"
        score_exit_code = _run_report_command(
            _build_score_command(
                fixture=fixture,
                union_jsons=union_jsons,
                out_json=score_path,
                out_md=report_root / "typed_micro_series_summary.md",
                support_threshold=int(args.support_threshold),
                matcher=str(args.matcher),
                apply_domain_reducers=not bool(args.no_apply_domain_reducers),
            ),
            report_path=score_path,
        )
    if not bool(args.skip_audit):
        print("auditing lens and union atoms", flush=True)
        lens_audit_path = report_root / "lens_atom_audit.json"
        _run(
            _build_atom_audit_command(
                compile_root=lens_root,
                out_json=lens_audit_path,
                out_md=report_root / "lens_atom_audit.md",
                enforce_lens_scope=True,
            )
        )
        union_audit_path = report_root / "union_atom_audit.json"
        _run(
            _build_atom_audit_command(
                compile_root=union_root,
                out_json=union_audit_path,
                out_md=report_root / "union_atom_audit.md",
                enforce_lens_scope=False,
            )
        )
        lens_value_audit_path = report_root / "lens_carrier_value_domains.json"
        _run(
            _build_value_domain_audit_command(
                compile_root=lens_root,
                out_json=lens_value_audit_path,
                out_md=report_root / "lens_carrier_value_domains.md",
            )
        )
        union_value_audit_path = report_root / "union_carrier_value_domains.json"
        _run(
            _build_value_domain_audit_command(
                compile_root=union_root,
                out_json=union_value_audit_path,
                out_md=report_root / "union_carrier_value_domains.md",
            )
        )
    if bool(args.reconcile_unions):
        print("reconciling typed union support", flush=True)
        reconcile_path = report_root / f"typed_reconcile_support_ge{int(args.support_threshold)}_value.json"
        _run(
            _build_reconcile_command(
                fixture=fixture,
                union_jsons=union_jsons,
                out_json=reconcile_path,
                out_md=report_root / f"typed_reconcile_support_ge{int(args.support_threshold)}_value.md",
                min_support=int(args.support_threshold),
            )
        )

    manifest = {
        "schema_version": "domain_lens_bundle_run_v1",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fixture": fixture,
        "text_file": str(text_file),
        "profile_registry": str(profile_registry),
        "label": label,
        "out_root": str(out_root),
        "repeat": repeat,
        "lenses": [lens.lens_id for lens in selected_lenses],
        "lens_scopes": _lens_scope_manifest(selected_lenses),
        "settings": {
            "backend": str(args.backend),
            "model": str(args.model),
            "base_url": str(args.base_url),
            "temperature": float(args.temperature),
            "top_p": float(args.top_p),
            "top_k": int(args.top_k),
            "num_ctx": int(args.num_ctx),
            "max_tokens": int(args.max_tokens),
            "timeout": int(args.timeout),
            "support_threshold": int(args.support_threshold),
            "matcher": str(args.matcher),
            "apply_domain_reducers": not bool(args.no_apply_domain_reducers),
            "focused_pass_ops_schema": bool(args.focused_pass_ops_schema),
            "compile_plan_passes": bool(args.compile_plan_passes),
            "profile_registry_lens_plan": bool(args.profile_registry_lens_plan),
            "reconcile_unions": bool(args.reconcile_unions),
        },
        "policy": [
            "The harness does not read source prose or oracle answers.",
            "Each lens compile is LLM-owned and restricted by profile-registry lens scope.",
            "The union step reads only mapper-admitted compile artifacts and infers no new facts.",
            "Scoring, atom audits, and carrier value-domain audits use existing governance scripts.",
            "Typed union reconciliation is source-only when enabled and does not inspect oracle answers.",
        ],
        "runs": run_reports,
        "reports": {
            "score_json": str(score_path or ""),
            "score_exit_code": score_exit_code,
            "lens_atom_audit_json": str(lens_audit_path or ""),
            "union_atom_audit_json": str(union_audit_path or ""),
            "lens_carrier_value_domains_json": str(lens_value_audit_path or ""),
            "union_carrier_value_domains_json": str(union_value_audit_path or ""),
            "typed_reconcile_json": str(reconcile_path or ""),
        },
    }
    if score_path and score_path.exists():
        manifest["score_summary"] = _load_summary(score_path)
    if lens_audit_path and lens_audit_path.exists():
        manifest["lens_atom_audit_summary"] = _load_summary(lens_audit_path)
    if union_audit_path and union_audit_path.exists():
        manifest["union_atom_audit_summary"] = _load_summary(union_audit_path)
    if lens_value_audit_path and lens_value_audit_path.exists():
        manifest["lens_carrier_value_domain_summary"] = _load_summary(lens_value_audit_path)
    if union_value_audit_path and union_value_audit_path.exists():
        manifest["union_carrier_value_domain_summary"] = _load_summary(union_value_audit_path)
    if reconcile_path and reconcile_path.exists():
        manifest["typed_reconcile_summary"] = _load_summary(reconcile_path)
    manifest_path = out_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(str(manifest_path))
    if "score_summary" in manifest:
        print(json.dumps(manifest["score_summary"], sort_keys=True))
    return 0


def _resolve_path(path: Path) -> Path:
    return path if path.is_absolute() else (REPO_ROOT / path).resolve()


def _resolve_out_root(path: Path) -> Path:
    return path if path.is_absolute() else (REPO_ROOT / path).resolve()


def _load_registry_lenses(path: Path) -> list[LensSpec]:
    data = json.loads(path.read_text(encoding="utf-8"))
    raw_lenses = data.get("lenses")
    if not isinstance(raw_lenses, list):
        raise ValueError(f"registry has no lenses list: {path}")
    lenses: list[LensSpec] = []
    for item in raw_lenses:
        if not isinstance(item, dict):
            continue
        lens_id = str(item.get("id", "")).strip()
        if not lens_id:
            continue
        allowed_signatures = tuple(
            sorted(
                str(signature).strip()
                for signature in item.get("allowed_signatures", [])
                if isinstance(item.get("allowed_signatures"), list) and str(signature).strip()
            )
        )
        lenses.append(
            LensSpec(
                lens_id=lens_id,
                purpose=str(item.get("purpose", "")).strip(),
                allowed_signatures=allowed_signatures,
            )
        )
    if not lenses:
        raise ValueError(f"registry has no named lenses: {path}")
    return lenses


def _lens_scope_manifest(lenses: list[LensSpec]) -> list[dict[str, Any]]:
    return [
        {
            "id": lens.lens_id,
            "purpose": lens.purpose,
            "offered_signatures": list(lens.allowed_signatures),
        }
        for lens in lenses
    ]


def _selected_lenses(registry_lenses: list[LensSpec], requested_ids: list[str]) -> list[LensSpec]:
    by_id = {lens.lens_id: lens for lens in registry_lenses}
    if not requested_ids:
        return registry_lenses
    selected: list[LensSpec] = []
    for lens_id in requested_ids:
        if lens_id not in by_id:
            available = ", ".join(sorted(by_id))
            raise ValueError(f"unknown lens {lens_id!r}; available lenses: {available}")
        selected.append(by_id[lens_id])
    return selected


def _split_csv_values(values: list[str]) -> list[str]:
    out: list[str] = []
    for value in values:
        for part in str(value or "").split(","):
            part = part.strip()
            if part:
                out.append(part)
    return out


def _parse_lens_domain_hints(values: list[str]) -> dict[str, str]:
    hints: dict[str, str] = {}
    for value in values:
        text = str(value or "").strip()
        if not text:
            continue
        if "=" not in text:
            raise ValueError("--lens-domain-hint must be in lens_id=hint form")
        lens_id, hint = text.split("=", 1)
        lens_id = lens_id.strip()
        if not lens_id:
            raise ValueError("--lens-domain-hint has empty lens id")
        hints[lens_id] = hint.strip()
    return hints


def _build_lens_compile_command(
    *,
    text_file: Path,
    profile_registry: Path,
    lens: LensSpec,
    lens_hint: str,
    args: argparse.Namespace,
) -> list[str]:
    domain_hint = _lens_domain_hint(base_hint=str(args.domain_hint), lens=lens, override= lens_hint)
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "run_domain_bootstrap_file.py"),
        "--text-file",
        str(text_file),
        "--profile-registry",
        str(profile_registry),
        "--use-profile-registry-direct",
        "--profile-registry-lens",
        lens.lens_id,
        "--domain-hint",
        domain_hint,
        "--compile-source",
        "--require-source-compile-ok",
        "--backend",
        str(args.backend),
        "--model",
        str(args.model),
        "--base-url",
        str(args.base_url),
        "--temperature",
        str(args.temperature),
        "--top-p",
        str(args.top_p),
        "--top-k",
        str(args.top_k),
        "--num-ctx",
        str(args.num_ctx),
        "--max-tokens",
        str(args.max_tokens),
        "--timeout",
        str(args.timeout),
    ]
    if bool(getattr(args, "focused_pass_ops_schema", False)):
        command.append("--focused-pass-ops-schema")
    if bool(getattr(args, "compile_plan_passes", False)):
        command.append("--compile-plan-passes")
    if bool(getattr(args, "profile_registry_lens_plan", False)):
        command.append("--profile-registry-lens-plan")
    return command


def _lens_domain_hint(*, base_hint: str, lens: LensSpec, override: str) -> str:
    if override.strip():
        return override.strip()
    parts = [base_hint.strip()] if base_hint.strip() else []
    parts.append(f"Lens {lens.lens_id}: {lens.purpose}".strip())
    parts.append(
        "Emit only offered profile-registry lens carriers and domain_omission rows when allowed. "
        "Keep facts compact, typed, source-grounded, and inside the lens predicate set. "
        "Do not place source prose in typed slots."
    )
    return " ".join(part for part in parts if part)


def _build_union_command(
    *,
    run_jsons: list[Path],
    out_dir: Path,
    label: str,
    apply_domain_reducers: bool,
) -> list[str]:
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "union_domain_bootstrap_compiles.py"),
    ]
    for path in run_jsons:
        command.extend(["--run-json", str(path)])
    command.extend(["--out-dir", str(out_dir), "--label", label])
    if apply_domain_reducers:
        command.append("--apply-domain-reducers")
    return command


def _build_score_command(
    *,
    fixture: str,
    union_jsons: list[Path],
    out_json: Path,
    out_md: Path,
    support_threshold: int,
    matcher: str,
    apply_domain_reducers: bool,
) -> list[str]:
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "summarize_typed_micro_series.py"),
        "--fixture",
        fixture,
        "--support-threshold",
        str(support_threshold),
        "--matcher",
        matcher,
        "--report-unexpected",
        "--enforce-no-forbidden",
        "--out-json",
        str(out_json),
        "--out-md",
        str(out_md),
    ]
    if apply_domain_reducers:
        command.append("--apply-domain-reducers")
    for path in union_jsons:
        command.extend(["--compile-json", str(path)])
    return command


def _build_atom_audit_command(
    *,
    compile_root: Path,
    out_json: Path,
    out_md: Path,
    enforce_lens_scope: bool,
) -> list[str]:
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "audit_kb_atom_inventory.py"),
        "--compile-root",
        str(compile_root),
        "--enforce-atom-shape",
        "--enforce-registered-signatures",
        "--out-json",
        str(out_json),
        "--out-md",
        str(out_md),
    ]
    if enforce_lens_scope:
        command.append("--enforce-lens-scope")
    return command


def _build_value_domain_audit_command(*, compile_root: Path, out_json: Path, out_md: Path) -> list[str]:
    return [
        sys.executable,
        str(REPO_ROOT / "scripts" / "audit_carrier_value_domains.py"),
        "--compile-root",
        str(compile_root),
        "--out-json",
        str(out_json),
        "--out-md",
        str(out_md),
    ]


def _build_reconcile_command(
    *,
    fixture: str,
    union_jsons: list[Path],
    out_json: Path,
    out_md: Path,
    min_support: int,
) -> list[str]:
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "reconcile_typed_micro_compiles.py"),
        "--fixture-id",
        fixture,
        "--min-support",
        str(min_support),
        "--support-mode",
        "value",
        "--out-json",
        str(out_json),
        "--out-md",
        str(out_md),
    ]
    for path in union_jsons:
        command.extend(["--compile-json", str(path)])
    return command


def _run(command: list[str]) -> None:
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def _run_report_command(command: list[str], *, report_path: Path) -> int:
    completed = subprocess.run(command, cwd=REPO_ROOT)
    if completed.returncode != 0 and not report_path.exists():
        completed.check_returncode()
    return completed.returncode


def _latest_compile_json(path: Path) -> Path:
    candidates = sorted(
        item
        for item in path.glob("*.json")
        if _has_source_compile(item)
    )
    if not candidates:
        raise FileNotFoundError(f"no compile JSON found under {path}")
    return candidates[-1]


def _has_source_compile(path: Path) -> bool:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False
    return isinstance(data, dict) and isinstance(data.get("source_compile"), dict)


def _load_summary(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    summary = data.get("summary")
    if isinstance(summary, dict):
        return summary
    source_compile = data.get("source_compile")
    if isinstance(source_compile, dict):
        reconciliation = source_compile.get("governed_reconciliation")
        if isinstance(reconciliation, dict):
            conflicts = reconciliation.get("conflicts")
            fact_support = reconciliation.get("fact_support")
            return {
                "fixture_id": reconciliation.get("fixture_id"),
                "input_count": reconciliation.get("input_count"),
                "min_support": reconciliation.get("min_support"),
                "support_mode": reconciliation.get("support_mode"),
                "reconciled_fact_count": int(source_compile.get("unique_fact_count") or 0),
                "singleton_fact_count": reconciliation.get("singleton_fact_count"),
                "conflict_count": len(conflicts) if isinstance(conflicts, list) else 0,
                "skipped_count": reconciliation.get("skipped_count"),
                "fact_support_count": len(fact_support) if isinstance(fact_support, list) else 0,
            }
    return {}


def _slug(value: str) -> str:
    out = "".join(ch.lower() if ch.isalnum() else "-" for ch in str(value or "").strip())
    out = "-".join(part for part in out.split("-") if part)
    return out[:96] or "lens-bundle"


if __name__ == "__main__":
    raise SystemExit(main())
