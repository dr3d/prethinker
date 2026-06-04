#!/usr/bin/env python3
"""Summarize retained compile evidence for domain-predicate proposals.

This report is intentionally not a promotion gate. It answers a narrower
question: for each candidate predicate proposal, do retained typed compile
artifacts show predeclared oracle support, forbidden support, or merely stable
same-signature emissions that still need independent oracle review?
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.summarize_typed_micro_series import build_report as build_series_report  # noqa: E402
from scripts.summarize_typed_micro_series import _fact_supported  # noqa: E402
from scripts.validate_typed_micro_fixtures import _facts_from_compile_json  # noqa: E402
from scripts.validate_domain_predicate_proposals import DEFAULT_ROOT as DEFAULT_PROPOSAL_ROOT  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", help="Typed micro-fixture id.")
    parser.add_argument("--proposal-root", type=Path, default=DEFAULT_PROPOSAL_ROOT)
    parser.add_argument("--proposal", action="append", default=[], type=Path)
    parser.add_argument("--micro-root", type=Path, default=ROOT / "datasets" / "compile_micro_fixtures")
    parser.add_argument("--compile-root", type=Path, default=None)
    parser.add_argument("--compile-json", action="append", default=[], type=Path)
    parser.add_argument(
        "--candidate-review-root",
        type=Path,
        default=ROOT / "datasets" / "candidate_oracle_reviews",
        help="Root containing independent candidate oracle reviews. Reviews do not mutate fixture oracles.",
    )
    parser.add_argument("--candidate-review", action="append", default=[], type=Path)
    parser.add_argument("--support-threshold", type=int, default=2)
    parser.add_argument("--matcher", choices=("unification", "constant_slot"), default="constant_slot")
    parser.add_argument("--apply-domain-reducers", action="store_true")
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument("--exit-zero", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    compile_paths = _compile_paths(args.compile_root, args.compile_json)
    fixture_id = args.fixture or _fixture_from_compile_root(args.compile_root)
    report = build_report(
        fixture_id=fixture_id,
        proposal_paths=_proposal_paths(root=args.proposal_root, explicit=args.proposal),
        micro_root=args.micro_root,
        compile_paths=compile_paths,
        support_threshold=args.support_threshold,
        matcher=args.matcher,
        apply_domain_reducers=args.apply_domain_reducers,
        compile_root=args.compile_root,
        candidate_review_paths=_candidate_review_paths(root=args.candidate_review_root, explicit=args.candidate_review),
    )
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    if args.exit_zero:
        return 0
    return 0 if report["summary"]["status"] == "pass" else 1


def build_report(
    *,
    fixture_id: str,
    proposal_paths: list[Path],
    micro_root: Path,
    compile_paths: list[Path],
    support_threshold: int = 2,
    matcher: str = "constant_slot",
    apply_domain_reducers: bool = False,
    compile_root: Path | None = None,
    candidate_review_paths: list[Path] | None = None,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    if not fixture_id:
        errors.append("missing_fixture")
    if not compile_paths:
        errors.append("missing_compile_artifacts")
    if not proposal_paths:
        errors.append("missing_proposal_files")
    for path in proposal_paths:
        data = _load_json(path)
        signature = str(data.get("candidate_signature") or "").strip()
        proposal_id = str(data.get("proposal_id") or path.stem).strip()
        row_errors: list[str] = []
        if not signature:
            row_errors.append("missing_candidate_signature")
        series_report: dict[str, Any] = {}
        if fixture_id and compile_paths and signature:
            series_report = build_series_report(
                fixture_id=fixture_id,
                root=micro_root,
                compile_paths=compile_paths,
                support_threshold=support_threshold,
                matcher=matcher,
                apply_domain_reducers=apply_domain_reducers,
                expected_signatures={signature},
                report_unexpected=True,
            )
            _apply_candidate_reviews_to_series_report(
                series_report,
                proposal_id=proposal_id,
                signature=signature,
                candidate_review_paths=candidate_review_paths or [],
                matcher=matcher,
            )
        state = _candidate_state(series_report) if series_report else "unmeasured"
        row = {
            "proposal_id": proposal_id,
            "status": str(data.get("status") or "").strip(),
            "candidate_signature": signature,
            "proposal_path": _rel(path),
            "state": state,
            "errors": row_errors,
            "summary": series_report.get("summary", {}) if series_report else {},
            "candidate_reviews": series_report.get("candidate_reviews", []) if series_report else [],
            "supported_unexpected_examples": _supported_unexpected_examples(series_report),
            "supported_forbidden_examples": _supported_forbidden_examples(series_report),
        }
        rows.append(row)
        errors.extend(f"{proposal_id}:{error}" for error in row_errors)
    return {
        "schema_version": "domain_predicate_proposal_evidence_v1",
        "fixture_id": fixture_id,
        "compile_root": _rel(compile_root) if compile_root else "",
        "compile_count": len(compile_paths),
        "support_threshold": support_threshold,
        "matcher": matcher,
        "domain_reducers_applied": bool(apply_domain_reducers),
        "candidate_review_count": len(candidate_review_paths or []),
        "summary": {
            "proposal_count": len(rows),
            "blocking_errors": len(errors),
            "status": "fail" if errors else "pass",
            "states": _state_counts(rows),
        },
        "errors": errors,
        "proposals": rows,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Domain Predicate Proposal Evidence",
        "",
        "This report reads proposal files, typed fixture oracles, and retained",
        "compile artifacts only. Stable unexpected facts are candidate evidence,",
        "not score credit and not promoted claims.",
        "",
        f"- Fixture: `{report.get('fixture_id', '')}`",
        f"- Compile root: `{report.get('compile_root', '') or 'explicit compile-json list'}`",
        f"- Compiles: `{report.get('compile_count', 0)}`",
        f"- Support threshold: `{report.get('support_threshold', 0)}`",
        f"- Matcher: `{report.get('matcher', '')}`",
        f"- Domain reducers applied: `{report.get('domain_reducers_applied', False)}`",
        f"- Candidate review files: `{report.get('candidate_review_count', 0)}`",
        f"- Proposals: `{summary.get('proposal_count', 0)}`",
        f"- Blocking errors: `{summary.get('blocking_errors', 0)}`",
        f"- Status: `{summary.get('status', '')}`",
        f"- States: `{summary.get('states', {})}`",
        "",
        "| Proposal | Signature | State | Expected | Supported | Forbidden Supported | Unexpected >= threshold |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in report.get("proposals", []):
        row_summary = row.get("summary") or {}
        unexpected_supported = _unexpected_supported_count(row_summary, row)
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                row.get("proposal_id", ""),
                row.get("candidate_signature", ""),
                row.get("state", ""),
                row_summary.get("expected_fact_count", 0),
                row_summary.get("supported_fact_count", 0),
                row_summary.get("supported_forbidden_fact_count", 0),
                unexpected_supported,
            )
        )
    for row in report.get("proposals", []):
        examples = row.get("supported_unexpected_examples") or []
        if not examples:
            continue
        if row.get("state") == "blocked_forbidden":
            lines.extend(["", f"## Stable Emissions Later Blocked: {row.get('proposal_id', '')}", ""])
            lines.append(
                "These same-signature facts were stable before review, but independent review now marks matching boundaries as forbidden."
            )
        else:
            lines.extend(["", f"## Candidate Signal: {row.get('proposal_id', '')}", ""])
            lines.append("Supported unexpected facts require independent oracle review before any score claim.")
        lines.append("")
        for item in examples[:8]:
            runs = ", ".join(item.get("support_runs", []))
            lines.append(f"- {item.get('support_count', 0)} run(s): `{item.get('fact', '')}` [{runs}]")
    for row in report.get("proposals", []):
        examples = row.get("supported_forbidden_examples") or []
        if not examples:
            continue
        lines.extend(["", f"## Blocking Forbidden Support: {row.get('proposal_id', '')}", ""])
        for item in examples[:8]:
            runs = ", ".join(item.get("support_runs", []))
            lines.append(f"- {item.get('support_count', 0)} run(s): `{item.get('forbidden_fact', '')}` [{runs}]")
    return "\n".join(lines) + "\n"


def _candidate_state(series_report: dict[str, Any]) -> str:
    summary = series_report.get("summary") or {}
    if int(summary.get("supported_forbidden_fact_count") or 0):
        return "blocked_forbidden"
    expected = int(summary.get("expected_fact_count") or 0)
    supported = int(summary.get("supported_fact_count") or 0)
    unsupported = int(summary.get("unsupported_fact_count") or 0)
    unexpected_supported = sum(
        1 for row in series_report.get("unexpected_rows", []) if int(row.get("support_count") or 0) >= int(series_report.get("support_threshold") or 2)
    )
    if expected and supported and not unsupported:
        return "oracle_supported"
    if expected and supported:
        return "partial_oracle_support"
    if unexpected_supported and not expected:
        return "candidate_signal_no_oracle"
    if unexpected_supported:
        return "candidate_extra_signal"
    return "no_signal"


def _apply_candidate_reviews_to_series_report(
    series_report: dict[str, Any],
    *,
    proposal_id: str,
    signature: str,
    candidate_review_paths: list[Path],
    matcher: str,
) -> None:
    reviews = [
        review
        for path in candidate_review_paths
        for review in [_load_candidate_review(path)]
        if review
        and (not review.get("proposal_id") or review.get("proposal_id") == proposal_id)
        and review.get("candidate_signature") == signature
        and review.get("fixture_id") == series_report.get("fixture_id")
    ]
    if not reviews:
        return
    compile_facts_by_run = _compile_facts_by_run(series_report)
    forbidden_rows = list(series_report.get("forbidden_rows") or [])
    expected_rows = list(series_report.get("rows") or [])
    expected_facts = {str(row.get("expected_fact") or "") for row in expected_rows}
    forbidden_facts = {str(row.get("forbidden_fact") or "") for row in forbidden_rows}
    for review in reviews:
        for fact in review.get("expected_facts", []):
            if fact in expected_facts:
                continue
            run_ids = _supporting_runs(fact, compile_facts_by_run, matcher=matcher)
            expected_rows.append(
                {
                    "expected_fact": fact,
                    "support_count": len(run_ids),
                    "support_runs": run_ids,
                    "meets_threshold": len(run_ids) >= int(series_report.get("support_threshold") or 2),
                    "same_predicate_variants": [],
                    "candidate_review_id": review.get("review_id", ""),
                }
            )
            expected_facts.add(fact)
        for fact in review.get("forbidden_facts", []):
            if fact in forbidden_facts:
                continue
            run_ids = _supporting_runs(fact, compile_facts_by_run, matcher=matcher)
            forbidden_rows.append(
                {
                    "forbidden_fact": fact,
                    "support_count": len(run_ids),
                    "support_runs": run_ids,
                    "supported": bool(run_ids),
                    "candidate_review_id": review.get("review_id", ""),
                }
            )
            forbidden_facts.add(fact)
    supported_rows = [
        row for row in expected_rows if int(row.get("support_count") or 0) >= int(series_report.get("support_threshold") or 2)
    ]
    supported_forbidden = [row for row in forbidden_rows if row.get("supported")]
    series_report["rows"] = expected_rows
    series_report["forbidden_rows"] = forbidden_rows
    series_report["candidate_reviews"] = [
        {
            "review_id": review.get("review_id", ""),
            "path": _rel(review.get("path")) if isinstance(review.get("path"), Path) else "",
            "expected_fact_count": len(review.get("expected_facts", [])),
            "forbidden_fact_count": len(review.get("forbidden_facts", [])),
            "reviewer_blind_to_model_outputs": review.get("reviewer_blind_to_model_outputs"),
            "reviewer_read_forbidden_inputs": review.get("reviewer_read_forbidden_inputs"),
            "context_caveat": review.get("context_caveat", ""),
        }
        for review in reviews
    ]
    summary = series_report.setdefault("summary", {})
    summary["expected_fact_count"] = len(expected_rows)
    summary["supported_fact_count"] = len(supported_rows)
    summary["unsupported_fact_count"] = len(expected_rows) - len(supported_rows)
    summary["forbidden_fact_count"] = len(forbidden_rows)
    summary["supported_forbidden_fact_count"] = len(supported_forbidden)


def _compile_facts_by_run(series_report: dict[str, Any]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for run in series_report.get("runs", []):
        path = Path(str(run.get("compile_json") or ""))
        if not path.exists():
            continue
        facts = _facts_from_compile_json(path)
        out[str(run.get("run_id") or path.parent.name or path.stem)] = facts
    return out


def _supporting_runs(fact: str, compile_facts_by_run: dict[str, list[str]], *, matcher: str) -> list[str]:
    return [
        run_id
        for run_id, compile_facts in compile_facts_by_run.items()
        if _fact_supported(fact, compile_facts, matcher=matcher)
    ]


def _supported_unexpected_examples(series_report: dict[str, Any]) -> list[dict[str, Any]]:
    threshold = int(series_report.get("support_threshold") or 2) if series_report else 2
    rows = [
        row for row in series_report.get("unexpected_rows", []) if int(row.get("support_count") or 0) >= threshold
    ]
    return rows[:20]


def _supported_forbidden_examples(series_report: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in series_report.get("forbidden_rows", []) if row.get("supported")][:20]


def _unexpected_supported_count(summary: dict[str, Any], row: dict[str, Any]) -> int:
    _ = summary
    return len(row.get("supported_unexpected_examples") or [])


def _state_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        state = str(row.get("state") or "unknown")
        counts[state] = counts.get(state, 0) + 1
    return counts


def _proposal_paths(*, root: Path, explicit: list[Path]) -> list[Path]:
    paths = [path.resolve() for path in explicit]
    if root.exists():
        paths.extend(sorted(root.rglob("*.json")))
    unique: dict[str, Path] = {}
    for path in paths:
        unique[str(path)] = path
    return list(unique.values())


def _candidate_review_paths(*, root: Path, explicit: list[Path]) -> list[Path]:
    paths = [path.resolve() for path in explicit]
    if root.exists():
        paths.extend(sorted(path.resolve() for path in root.rglob("manifest.json")))
    unique: dict[str, Path] = {}
    for path in paths:
        unique[str(path)] = path
    return list(unique.values())


def _load_candidate_review(path: Path) -> dict[str, Any]:
    manifest_path = path
    if path.is_dir():
        manifest_path = path / "manifest.json"
    manifest = _load_json(manifest_path)
    if not manifest:
        return {}
    review_dir = manifest_path.parent
    expected_path = review_dir / "candidate_expected_facts.pl"
    forbidden_path = review_dir / "candidate_forbidden_facts.pl"
    predicate = str(manifest.get("predicate") or "").strip()
    return {
        "path": manifest_path,
        "review_id": str(manifest.get("review_id") or review_dir.name).strip(),
        "fixture_id": str(manifest.get("fixture_id") or "").strip(),
        "proposal_id": str(manifest.get("proposal_id") or "").strip(),
        "candidate_signature": predicate,
        "expected_facts": _review_fact_lines(expected_path),
        "forbidden_facts": _review_fact_lines(forbidden_path),
        "reviewer_blind_to_model_outputs": manifest.get("reviewer_blind_to_model_outputs"),
        "reviewer_read_forbidden_inputs": manifest.get("reviewer_read_forbidden_inputs"),
        "context_caveat": str(manifest.get("reviewer_context_caveat") or "").strip(),
    }


def _review_fact_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    lines: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        text = raw.strip()
        if not text or text.startswith("%"):
            continue
        if not text.endswith(".") or "(" not in text:
            continue
        lines.append(text)
    return lines


def _compile_paths(compile_root: Path | None, explicit: list[Path]) -> list[Path]:
    paths = [path.resolve() for path in explicit]
    if compile_root is not None and compile_root.exists():
        union_paths = sorted((compile_root / "unions").glob("run*/*.json"))
        paths.extend(path.resolve() for path in union_paths)
        if not union_paths:
            paths.extend(path.resolve() for path in sorted(compile_root.rglob("compile.json")))
    unique: dict[str, Path] = {}
    for path in paths:
        unique[str(path)] = path
    return list(unique.values())


def _fixture_from_compile_root(compile_root: Path | None) -> str:
    if compile_root is None:
        return ""
    manifest = _load_json(compile_root / "manifest.json")
    return str(manifest.get("fixture") or "").strip()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _rel(path: Path | None) -> str:
    if path is None:
        return ""
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except Exception:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
