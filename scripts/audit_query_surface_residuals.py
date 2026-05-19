"""Audit query-surface residuals in QA runs.

This is a post-hoc diagnostic. It does not alter answers. It asks whether
non-exact rows already show evidence of query-layer fallback behavior such as
lowercase slot labels being relaxed into variables or source-text contains
filters being repaired into broad source-record scans.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


QUERY_RESIDUAL_SURFACES = {"query_surface_gap", "hybrid_join_gap"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qa-json", action="append", type=Path, default=[])
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = audit_paths(args.qa_json)
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(json.dumps(report["summary"], sort_keys=True))
    return 0


def audit_paths(paths: list[Path]) -> dict[str, Any]:
    runs = []
    rows = []
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        run_rows = _audit_run(path=path, payload=payload)
        runs.append(
            {
                "qa_json": str(path),
                "row_count": len(payload.get("rows", []) if isinstance(payload.get("rows"), list) else []),
                "residual_count": len(run_rows),
            }
        )
        rows.extend(run_rows)
    return {
        "schema_version": "query_surface_residual_audit_v1",
        "run_count": len(paths),
        "residual_count": len(rows),
        "summary": _summarize(rows),
        "runs": runs,
        "rows": rows,
    }


def _audit_run(*, path: Path, payload: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    rows = payload.get("rows", [])
    if not isinstance(rows, list):
        return out
    for row in rows:
        if not isinstance(row, dict):
            continue
        verdict = _row_verdict(row)
        surface = _row_surface(row)
        if verdict == "exact" or surface not in QUERY_RESIDUAL_SURFACES:
            continue
        signals = _query_fallback_signals(row.get("query_results", []))
        out.append(
            {
                "qa_json": str(path),
                "id": str(row.get("id") or ""),
                "verdict": verdict,
                "surface": surface,
                "utterance": str(row.get("utterance") or ""),
                "signals": signals,
                "signal_classes": sorted({signal["class"] for signal in signals}),
                "query_count": len(row.get("queries", []) if isinstance(row.get("queries"), list) else []),
            }
        )
    return out


def _row_verdict(row: dict[str, Any]) -> str:
    judge = row.get("reference_judge") if isinstance(row.get("reference_judge"), dict) else {}
    verdict = str(judge.get("verdict") or "").strip()
    if verdict:
        return verdict
    legacy = row.get("judge") if isinstance(row.get("judge"), dict) else {}
    return str(legacy.get("label") or legacy.get("verdict") or "").strip()


def _row_surface(row: dict[str, Any]) -> str:
    surface = row.get("failure_surface") if isinstance(row.get("failure_surface"), dict) else {}
    return str(surface.get("surface") or surface.get("class") or "").strip()


def _query_fallback_signals(query_results: Any) -> list[dict[str, Any]]:
    if not isinstance(query_results, list):
        return []
    signals: list[dict[str, Any]] = []
    for item in query_results:
        if not isinstance(item, dict):
            continue
        result = item.get("result") if isinstance(item.get("result"), dict) else {}
        basis = result.get("reasoning_basis") if isinstance(result.get("reasoning_basis"), dict) else {}
        note = str(basis.get("note") or "")
        query = str(item.get("query") or result.get("prolog_query") or "")
        if "placeholder query repair" in note:
            signals.append(
                {
                    "class": "placeholder_repair_used",
                    "query": query,
                    "repairs": basis.get("repairs", []),
                }
            )
        if "diagnostic relaxed query" in note:
            signals.append(
                {
                    "class": "relaxed_overbound_used",
                    "query": query,
                    "original_query": basis.get("original_query", ""),
                    "relaxed_constants": result.get("relaxed_constants", []),
                }
            )
        if basis.get("validation") == "source_text_contains_filter_repaired":
            signals.append(
                {
                    "class": "source_text_filter_repaired",
                    "query": query,
                    "contains_needles": basis.get("contains_needles", []),
                }
            )
    return signals


def _summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    surface_counts = Counter(str(row.get("surface") or "") for row in rows)
    verdict_counts = Counter(str(row.get("verdict") or "") for row in rows)
    signal_counts: Counter[str] = Counter()
    for row in rows:
        for cls in row.get("signal_classes", []):
            signal_counts[str(cls)] += 1
    return {
        "surface_counts": dict(sorted(surface_counts.items())),
        "verdict_counts": dict(sorted(verdict_counts.items())),
        "signal_class_counts": dict(sorted(signal_counts.items())),
        "rows_with_fallback_signal": sum(1 for row in rows if row.get("signals")),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Query Surface Residual Audit",
        "",
        f"- Runs: `{report['run_count']}`",
        f"- Residual rows: `{report['residual_count']}`",
        f"- Rows with fallback signal: `{report['summary']['rows_with_fallback_signal']}`",
        f"- Surface counts: `{report['summary']['surface_counts']}`",
        f"- Signal class counts: `{report['summary']['signal_class_counts']}`",
        "",
        "| Row | Verdict | Surface | Signals | Question |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in report["rows"]:
        lines.append(
            f"| `{row['id']}` | `{row['verdict']}` | `{row['surface']}` | "
            f"`{row['signal_classes']}` | {row['utterance']} |"
        )
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
